"""Dashboard table, chart, and single-HTML rendering layer."""
from __future__ import annotations

import html
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

from .candidate import MMDI_COMPONENTS, R2_COMPONENTS
from .data_sources import load_fred_series
from .utils import bool_badge, money_fmt, num_fmt, pct_fmt, safe_float

R2_META = {
    "r2_price_below_200dma": {
        "display_name": "Price vs 200DMA",
        "current_value_func": lambda r: r["dist_200dma"] * 100,
        "current_value_label": "Distance to 200DMA (%)",
        "threshold_label": "Trigger if < -3%",
        "direction": "Lower / more negative = worse",
        "high_low_meaning": "High positive distance = trend cushion; deep negative distance = trend damage.",
        "chart_cols": ["dist_200dma"],
        "chart_title": "QQQ distance to 200DMA",
        "trigger_col": "r2_price_below_200dma",
    },
    "r2_6m_momentum_negative": {
        "display_name": "6M Momentum",
        "current_value_func": lambda r: r["ret_126d"] * 100,
        "current_value_label": "126BD return (%)",
        "threshold_label": "Trigger if < -5%",
        "direction": "Lower / negative = worse",
        "high_low_meaning": "High = medium-term trend still healthy; low/negative = momentum deterioration.",
        "chart_cols": ["ret_126d"],
        "chart_title": "QQQ 126BD return",
        "trigger_col": "r2_6m_momentum_negative",
    },
    "r2_drawdown_active": {
        "display_name": "Drawdown Damage",
        "current_value_func": lambda r: min(r["dd_from_126d_high"], r["dd_from_252d_high"]) * 100,
        "current_value_label": "Worst of 126D/252D high DD (%)",
        "threshold_label": "Trigger if 126D DD < -10% OR 252D DD < -12%",
        "direction": "Lower / more negative = worse",
        "high_low_meaning": "Near 0 = close to highs; deeply negative = drawdown already established.",
        "chart_cols": ["dd_from_126d_high", "dd_from_252d_high"],
        "chart_title": "QQQ drawdown from 126D / 252D highs",
        "trigger_col": "r2_drawdown_active",
    },
    "r2_short_momentum_shock": {
        "display_name": "1M Shock",
        "current_value_func": lambda r: r["ret_21d"] * 100,
        "current_value_label": "21BD return (%)",
        "threshold_label": "Trigger if < -5%",
        "direction": "Lower / fast negative move = worse",
        "high_low_meaning": "High/positive = no short shock; sharp negative = fast selloff pressure.",
        "chart_cols": ["ret_21d"],
        "chart_title": "QQQ 21BD return",
        "trigger_col": "r2_short_momentum_shock",
    },
    "r2_vol_stress": {
        "display_name": "Volatility Stress",
        "current_value_func": lambda r: r["vix"],
        "current_value_label": "VIX level",
        "threshold_label": "Trigger if VIX > 25 OR VIX/RV percentile > 80%",
        "direction": "Higher = worse",
        "high_low_meaning": "Low = calm volatility regime; high = option/implied or realized stress.",
        "chart_cols": ["vix", "vix_pctile_3y", "realized_vol_21d_pctile_3y"],
        "chart_title": "VIX and volatility percentiles",
        "trigger_col": "r2_vol_stress",
    },
    "r2_credit_stress": {
        "display_name": "Credit Stress",
        "current_value_func": lambda r: r["credit_spread"],
        "current_value_label": "Credit spread (%)",
        "threshold_label": "Trigger if spread percentile > 80% OR 20D spread change > +0.25pp",
        "direction": "Higher = worse",
        "high_low_meaning": "Low/tight spreads = credit market calm; high/widening spreads = funding/liquidity stress.",
        "chart_cols": ["credit_spread", "credit_spread_level_pctile", "credit_spread_20d_change"],
        "chart_title": "Credit spread level / percentile / 20D change",
        "trigger_col": "r2_credit_stress",
    },
}

MMDI_META = {
    "mmdi_vix_stress": {
        "display_name": "VIX Stress Percentile",
        "source_metric": "VIX rolling 3Y percentile × 100",
        "direction": "Higher = worse",
        "high_low_meaning": "High means VIX is high relative to its own 3Y history; low means volatility is calm.",
    },
    "mmdi_vxn_stress": {
        "display_name": "VXN Stress Percentile",
        "source_metric": "Nasdaq vol index VXN rolling 3Y percentile × 100",
        "direction": "Higher = worse",
        "high_low_meaning": "High means Nasdaq-specific implied volatility stress; low means calm.",
    },
    "mmdi_drawdown_stress": {
        "display_name": "Drawdown Stress",
        "source_metric": "Abs(252D drawdown) rolling 3Y percentile × 100",
        "direction": "Higher = worse",
        "high_low_meaning": "High means drawdown depth is high relative to the last 3Y; low means price is close to highs.",
    },
    "mmdi_trend_damage": {
        "display_name": "Trend Damage",
        "source_metric": "Negative distance to 200DMA rolling 3Y percentile × 100",
        "direction": "Higher = worse",
        "high_low_meaning": "High means QQQ is meaningfully below trend; low means trend is intact.",
    },
    "mmdi_realized_vol_stress": {
        "display_name": "Realized Vol Stress",
        "source_metric": "21BD realized vol rolling 3Y percentile × 100",
        "direction": "Higher = worse",
        "high_low_meaning": "High means realized volatility has already picked up; low means realized path is calm.",
    },
    "mmdi_leadership_narrowing_stress": {
        "display_name": "Leadership Narrowing",
        "source_metric": "Abs(QQQE/QQQ ratio drawdown) rolling 3Y percentile × 100",
        "direction": "Higher = worse",
        "high_low_meaning": "High means equal-weight Nasdaq is lagging cap-weight QQQ, i.e. breadth/leadership is narrow.",
    },
}


def _style_df(df: pd.DataFrame) -> str:
    return df.to_html(index=False, border=0, classes="dataframe dashboard-table", na_rep="N/A", escape=True)


def build_current_dashboard(work: pd.DataFrame, config: dict) -> pd.DataFrame:
    latest = work.dropna(subset=["qqq_close"]).iloc[-1]
    return pd.DataFrame([{
        "date": latest.name.date(),
        "qqq_close": latest["qqq_close"],
        "ndx_close": latest.get("ndx_close", np.nan),
        "current_state": latest["COMBINED_STATE"],
        "combined_signal": latest["COMBINED_SIGNAL"],
        "interpretation": latest["COMBINED_INTERPRETATION"],
        "R2_ACTIVE": bool(latest["R2_ACTIVE"]),
        "R2_STRESS_COUNT": int(latest["R2_STRESS_COUNT"]),
        "R2_TRIGGER_THRESHOLD": f">= {config['r2_active_stress_count_threshold']} of 6 components",
        "R2_ACTIVE_RUN_LENGTH_BD": int(latest["R2_ACTIVE_RUN_LENGTH"]),
        "MMDI": latest["MMDI"],
        "MMDI_ZONE": latest["MMDI_ZONE"],
        "MMDI_HIGH_THRESHOLD": config["mmdi_high_threshold"],
        "MMDI_EXTREME_THRESHOLD": config["mmdi_extreme_threshold"],
        "MMDI_10D_CHANGE": latest["MMDI_10D_CHANGE"],
        "US10Y_YIELD_%": latest["us10y_yield"],
        "US10Y_SOURCE": latest["us10y_source"],
        "CREDIT_SOURCE": latest["credit_source"],
        "CREDIT_DATA_AVAILABLE": bool(latest.get("credit_data_available", False)),
    }])


def build_r2_component_table(work: pd.DataFrame) -> pd.DataFrame:
    latest = work.dropna(subset=["qqq_close"]).iloc[-1]
    rows = []
    for comp, meta in R2_META.items():
        value = meta["current_value_func"](latest)
        if comp == "r2_drawdown_active":
            detail = f"126D DD={latest['dd_from_126d_high']*100:.2f}%; 252D DD={latest['dd_from_252d_high']*100:.2f}%"
        elif comp == "r2_vol_stress":
            detail = f"VIX={latest['vix']:.2f}; VIX pctile={latest['vix_pctile_3y']:.1%}; RV pctile={latest['realized_vol_21d_pctile_3y']:.1%}"
        elif comp == "r2_credit_stress":
            if not bool(latest.get("credit_data_available", False)) or pd.isna(latest["credit_spread"]):
                detail = "Credit data unavailable this run; component disabled/degraded"
                value = np.nan
            else:
                detail = f"Spread={latest['credit_spread']:.2f}%; pctile={latest['credit_spread_level_pctile']:.1%}; 20D chg={latest['credit_spread_20d_change']:.2f}pp"
        else:
            detail = f"{meta['current_value_label']}={value:.2f}"
        status = (
            "DATA_UNAVAILABLE"
            if comp == "r2_credit_stress" and (not bool(latest.get("credit_data_available", False)) or pd.isna(latest["credit_spread"]))
            else bool_badge(latest[meta["trigger_col"]])
        )
        rows.append({
            "component": comp,
            "name": meta["display_name"],
            "status": status,
            "current_value": value,
            "current_detail": detail,
            "trigger_threshold": meta["threshold_label"],
            "direction": meta["direction"],
            "meaning": meta["high_low_meaning"],
        })
    return pd.DataFrame(rows)


def build_mmdi_component_table(work: pd.DataFrame, config: dict) -> pd.DataFrame:
    latest = work.dropna(subset=["qqq_close"]).iloc[-1]
    rows = []
    for comp in MMDI_COMPONENTS:
        meta = MMDI_META[comp]
        val = latest[comp]
        rows.append({
            "component": comp,
            "name": meta["display_name"],
            "current_value_0_100": val,
            "zone_hint": "HIGH-like" if val >= config["mmdi_high_threshold"] else ("ELEVATED-like" if val >= 35 else "LOW-like"),
            "component_formula": meta["source_metric"],
            "direction": meta["direction"],
            "meaning": meta["high_low_meaning"],
        })
    return pd.DataFrame(rows)


def build_threshold_table() -> pd.DataFrame:
    return pd.DataFrame([
        {"signal": "R2 active", "threshold": "R2_STRESS_COUNT >= 3", "meaning": "At least 3 of 6 stress blocks are active."},
        {"signal": "MMDI high", "threshold": "MMDI >= 50", "meaning": "Market internals stress is high enough to confirm an active R2 warning."},
        {"signal": "MMDI extreme", "threshold": "MMDI >= 80", "meaning": "Stress intensity is extreme; not a standalone sell trigger."},
        {"signal": "Price vs 200DMA", "threshold": "QQQ < 200DMA by more than 3%", "meaning": "Trend damage."},
        {"signal": "6M momentum", "threshold": "126BD return < -5%", "meaning": "Medium-term momentum deterioration."},
        {"signal": "Drawdown", "threshold": "126D DD < -10% OR 252D DD < -12%", "meaning": "Drawdown damage is established."},
        {"signal": "1M shock", "threshold": "21BD return < -5%", "meaning": "Fast negative price shock."},
        {"signal": "Vol stress", "threshold": "VIX > 25 OR vol percentile > 80%", "meaning": "Implied/realized volatility stress."},
        {"signal": "Credit stress", "threshold": "Credit spread pctile > 80% OR 20D spread widening > 0.25pp", "meaning": "Credit/funding stress."},
    ])


def build_macro_table(work: pd.DataFrame) -> pd.DataFrame:
    latest = work.dropna(subset=["qqq_close"]).iloc[-1]
    return pd.DataFrame([{
        "date": latest.name.date(),
        "US_10Y_yield_%": latest["us10y_yield"],
        "US_10Y_20BD_change_pp": latest["us10y_20d_change"],
        "US_10Y_63BD_change_pp": latest["us10y_63d_change"],
        "source": latest["us10y_source"],
        "credit_source": latest["credit_source"],
        "credit_data_available": bool(latest.get("credit_data_available", False)),
    }])


def safe_ticker_info(ticker: str) -> dict:
    try:
        info = yf.Ticker(ticker).get_info()
        return info if isinstance(info, dict) else {}
    except Exception:
        return {}


def pick_row(df_fin: pd.DataFrame | None, row_candidates: list[str]):
    if df_fin is None or df_fin.empty:
        return None
    idx_map = {str(i).lower().strip(): i for i in df_fin.index}
    for cand in row_candidates:
        key = cand.lower().strip()
        if key in idx_map:
            return idx_map[key]
    for actual in df_fin.index:
        low = str(actual).lower()
        for cand in row_candidates:
            if cand.lower() in low:
                return actual
    return None


def get_quarterly_growth_from_yfinance(ticker: str) -> dict:
    out = {
        "latest_quarter_period_end": None,
        "latest_revenue": np.nan,
        "latest_net_income": np.nan,
        "revenue_yoy_growth": np.nan,
        "net_income_yoy_growth": np.nan,
        "financials_source": "yfinance quarterly_income_stmt",
    }
    try:
        tk = yf.Ticker(ticker)
        q = tk.quarterly_income_stmt
        if q is None or q.empty:
            return out
        q = q.copy()
        q.columns = pd.to_datetime(q.columns)
        cols = sorted(q.columns, reverse=True)
        latest_col = cols[0]
        yoy_col = cols[4] if len(cols) >= 5 else None
        if yoy_col is None:
            older = [c for c in cols[1:] if (latest_col - c).days >= 330]
            yoy_col = older[0] if older else None
        revenue_row = pick_row(q, ["Total Revenue", "Operating Revenue", "Revenue"])
        ni_row = pick_row(q, ["Net Income", "Net Income Common Stockholders", "Net Income From Continuing Operation Net Minority Interest"])
        latest_rev = safe_float(q.loc[revenue_row, latest_col]) if revenue_row is not None else np.nan
        latest_ni = safe_float(q.loc[ni_row, latest_col]) if ni_row is not None else np.nan
        prev_rev = safe_float(q.loc[revenue_row, yoy_col]) if (revenue_row is not None and yoy_col is not None) else np.nan
        prev_ni = safe_float(q.loc[ni_row, yoy_col]) if (ni_row is not None and yoy_col is not None) else np.nan
        out["latest_quarter_period_end"] = latest_col.date()
        out["latest_revenue"] = latest_rev
        out["latest_net_income"] = latest_ni
        out["revenue_yoy_growth"] = (latest_rev / prev_rev - 1) if not pd.isna(prev_rev) and prev_rev != 0 else np.nan
        out["net_income_yoy_growth"] = (latest_ni / prev_ni - 1) if not pd.isna(prev_ni) and prev_ni != 0 else np.nan
    except Exception:
        pass
    return out


def get_next_earnings_date(ticker: str):
    try:
        tk = yf.Ticker(ticker)
        ed = tk.get_earnings_dates(limit=12)
        if ed is not None and not ed.empty:
            idx = pd.to_datetime(ed.index)
            try:
                idx = idx.tz_localize(None)
            except Exception:
                pass
            future = [d for d in idx if d.date() >= date.today()]
            if future:
                return min(future).date(), "yfinance earnings calendar"
    except Exception:
        pass
    try:
        info = safe_ticker_info(ticker)
        ed = info.get("earningsDate", None)
        if isinstance(ed, (list, tuple)) and len(ed) > 0:
            vals = []
            for x in ed:
                try:
                    vals.append(pd.to_datetime(x).date())
                except Exception:
                    pass
            vals = [x for x in vals if x >= date.today()]
            if vals:
                return min(vals), "yfinance info.earningsDate"
    except Exception:
        pass
    return None, "N/A"


def build_mag7_table(tickers: list[str]) -> pd.DataFrame:
    rows = []
    for t in tickers:
        print(f"Fetching Mag7 valuation/financials: {t}")
        info = safe_ticker_info(t)
        growth = get_quarterly_growth_from_yfinance(t)
        next_ed, next_src = get_next_earnings_date(t)
        rows.append({
            "ticker": t,
            "company": info.get("shortName", t),
            "price": safe_float(info.get("currentPrice", info.get("regularMarketPrice", np.nan))),
            "market_cap": safe_float(info.get("marketCap", np.nan)),
            "trailing_PE": safe_float(info.get("trailingPE", np.nan)),
            "forward_PE": safe_float(info.get("forwardPE", np.nan)),
            "latest_quarter_period_end": growth["latest_quarter_period_end"],
            "latest_revenue": growth["latest_revenue"],
            "revenue_yoy_growth": growth["revenue_yoy_growth"],
            "latest_net_income": growth["latest_net_income"],
            "net_income_yoy_growth": growth["net_income_yoy_growth"],
            "next_earnings_date": next_ed,
            "next_earnings_date_source": next_src,
            "data_source": "yfinance/Yahoo Finance; cross-check before investment use",
        })
    return pd.DataFrame(rows)


def build_cape_table(work: pd.DataFrame, config: dict) -> pd.DataFrame:
    latest = work.dropna(subset=["qqq_close"]).iloc[-1]
    manual = config.get("ndx_cape_manual_value", None)
    if manual is not None:
        return pd.DataFrame([{
            "metric": "NASDAQ-100 CAPE",
            "value": manual,
            "as_of": config.get("ndx_cape_manual_asof", None),
            "method": "Manual input from trusted external data source",
            "important_caveat": "CAPE = price / 10Y average inflation-adjusted earnings. Verify source methodology.",
        }])
    return pd.DataFrame([{
        "metric": "NASDAQ-100 CAPE",
        "value": np.nan,
        "as_of": latest.name.date(),
        "method": "Not computed by default",
        "important_caveat": (
            "No robust free official NASDAQ-100 CAPE API is used here. Enter ndx_cape_manual_value "
            "from a trusted source, or extend the proxy in a separate research branch."
        ),
    }])


def _add_hline(fig, y, row, label=None):
    if y is None or pd.isna(y):
        return
    fig.add_hline(y=y, line_dash="dash", row=row, col=1, annotation_text=label, annotation_position="top left")


def make_r2_component_charts(work: pd.DataFrame, config: dict) -> go.Figure:
    d = work.tail(config["component_chart_days"]).copy()
    fig = make_subplots(
        rows=6,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.035,
        subplot_titles=[R2_META[c]["chart_title"] for c in R2_COMPONENTS],
    )
    for i, comp in enumerate(R2_COMPONENTS, start=1):
        cols = R2_META[comp]["chart_cols"]
        for col in cols:
            if col not in d.columns:
                continue
            y = d[col]
            if col in ["dist_200dma", "ret_126d", "dd_from_126d_high", "dd_from_252d_high", "ret_21d", "vix_pctile_3y", "realized_vol_21d_pctile_3y", "credit_spread_level_pctile"]:
                y = y * 100
                name = col + " (%)"
            else:
                name = col
            fig.add_trace(go.Scatter(x=d.index, y=y, mode="lines", name=name), row=i, col=1)
        if comp == "r2_price_below_200dma":
            _add_hline(fig, config["r2_price_below_200dma_threshold"] * 100, i, "-3%")
        elif comp == "r2_6m_momentum_negative":
            _add_hline(fig, config["r2_6m_momentum_threshold"] * 100, i, "-5%")
        elif comp == "r2_drawdown_active":
            _add_hline(fig, config["r2_126d_drawdown_threshold"] * 100, i, "126D -10%")
            _add_hline(fig, config["r2_252d_drawdown_threshold"] * 100, i, "252D -12%")
        elif comp == "r2_short_momentum_shock":
            _add_hline(fig, config["r2_21d_shock_threshold"] * 100, i, "-5%")
        elif comp == "r2_vol_stress":
            _add_hline(fig, config["r2_vix_level_threshold"], i, "VIX 25")
            _add_hline(fig, config["r2_vix_pctile_threshold"] * 100, i, "80% pctile")
        elif comp == "r2_credit_stress":
            _add_hline(fig, config["r2_credit_pctile_threshold"] * 100, i, "80% pctile")
            _add_hline(fig, config["r2_credit_20d_change_threshold"], i, "+0.25pp")
    fig.update_layout(height=1350, title=f"R2 component values — last {config['component_chart_days']} trading days", showlegend=True)
    return fig


def make_mmdi_component_charts(work: pd.DataFrame, config: dict) -> go.Figure:
    d = work.tail(config["component_chart_days"]).copy()
    fig = make_subplots(
        rows=7,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.035,
        subplot_titles=["MMDI aggregate"] + [MMDI_META[c]["display_name"] for c in MMDI_COMPONENTS],
    )
    fig.add_trace(go.Scatter(x=d.index, y=d["MMDI"], mode="lines", name="MMDI"), row=1, col=1)
    _add_hline(fig, config["mmdi_high_threshold"], 1, "MMDI High 50")
    _add_hline(fig, config["mmdi_extreme_threshold"], 1, "MMDI Extreme 80")
    for i, comp in enumerate(MMDI_COMPONENTS, start=2):
        fig.add_trace(go.Scatter(x=d.index, y=d[comp], mode="lines", name=comp), row=i, col=1)
        _add_hline(fig, config["mmdi_high_threshold"], i, "50")
        _add_hline(fig, config["mmdi_extreme_threshold"], i, "80")
    fig.update_layout(height=1500, title=f"MMDI component values — last {config['component_chart_days']} trading days", showlegend=True)
    fig.update_yaxes(range=[0, 100])
    return fig


def make_macro_chart(work: pd.DataFrame, config: dict) -> go.Figure:
    d = work.tail(config["component_chart_days"]).copy()
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06, subplot_titles=["QQQ close", "US 10Y yield (%)", "Credit spread (%)"])
    fig.add_trace(go.Scatter(x=d.index, y=d["qqq_close"], mode="lines", name="QQQ"), row=1, col=1)
    fig.add_trace(go.Scatter(x=d.index, y=d["us10y_yield"], mode="lines", name="US10Y"), row=2, col=1)
    fig.add_trace(go.Scatter(x=d.index, y=d["credit_spread"], mode="lines", name="Credit spread"), row=3, col=1)
    fig.update_layout(height=750, title=f"Market / rate / credit context — last {config['component_chart_days']} trading days", showlegend=True)
    return fig


def build_all_dashboard_artifacts(work: pd.DataFrame, availability: pd.DataFrame, config: dict) -> dict:
    mag7_table = build_mag7_table(config["mag7_tickers"])
    mag7_display = mag7_table.copy()
    for c in ["market_cap", "latest_revenue", "latest_net_income"]:
        mag7_display[c] = mag7_display[c].apply(money_fmt)
    for c in ["trailing_PE", "forward_PE", "price"]:
        mag7_display[c] = mag7_display[c].apply(lambda x: num_fmt(x, 2))
    for c in ["revenue_yoy_growth", "net_income_yoy_growth"]:
        mag7_display[c] = mag7_display[c].apply(lambda x: pct_fmt(x, 1))

    return {
        "current_dashboard": build_current_dashboard(work, config),
        "r2_component_table": build_r2_component_table(work),
        "mmdi_component_table": build_mmdi_component_table(work, config),
        "threshold_table": build_threshold_table(),
        "macro_table": build_macro_table(work),
        "cape_table": build_cape_table(work, config),
        "mag7_table": mag7_table,
        "mag7_display": mag7_display,
        "availability": availability,
        "r2_fig": make_r2_component_charts(work, config),
        "mmdi_fig": make_mmdi_component_charts(work, config),
        "macro_fig": make_macro_chart(work, config),
    }


def write_csv_outputs(work: pd.DataFrame, artifacts: dict, output_dir: Path, config: dict) -> None:
    prefix = config["export_prefix"]
    output_dir.mkdir(parents=True, exist_ok=True)
    work.to_csv(output_dir / f"{prefix}_full_daily_data.csv")
    for key, filename in [
        ("current_dashboard", f"{prefix}_current_dashboard.csv"),
        ("r2_component_table", f"{prefix}_r2_component_table.csv"),
        ("mmdi_component_table", f"{prefix}_mmdi_component_table.csv"),
        ("threshold_table", f"{prefix}_threshold_table.csv"),
        ("macro_table", f"{prefix}_macro_table.csv"),
        ("cape_table", f"{prefix}_ndx_cape_table.csv"),
        ("mag7_table", f"{prefix}_mag7_fundamentals_raw.csv"),
        ("availability", f"{prefix}_data_availability.csv"),
    ]:
        artifacts[key].to_csv(output_dir / filename, index=False)


def write_dashboard_html(work: pd.DataFrame, artifacts: dict, output_path: Path, config: dict) -> None:
    latest = work.dropna(subset=["qqq_close"]).iloc[-1]
    title = "QQQ Risk Monitor — R2 × MMDI Dashboard v1.3.1"
    state = str(latest["COMBINED_STATE"])
    signal = str(latest["COMBINED_SIGNAL"])
    interpretation = str(latest["COMBINED_INTERPRETATION"])

    r2_html = artifacts["r2_fig"].to_html(full_html=False, include_plotlyjs="cdn")
    mmdi_html = artifacts["mmdi_fig"].to_html(full_html=False, include_plotlyjs=False)
    macro_html = artifacts["macro_fig"].to_html(full_html=False, include_plotlyjs=False)

    sections = [
        ("Current Dashboard Snapshot", artifacts["current_dashboard"]),
        ("Data Availability Check", artifacts["availability"]),
        ("R2 Components — Current Value / Meaning / Threshold", artifacts["r2_component_table"]),
        ("MMDI Components — Current Value / Meaning", artifacts["mmdi_component_table"]),
        ("Trigger Thresholds", artifacts["threshold_table"]),
        ("Rate / Macro Panel", artifacts["macro_table"]),
        ("NASDAQ-100 CAPE Panel", artifacts["cape_table"]),
        ("MAG7 Valuation + Latest Quarter Growth + Next Earnings", artifacts["mag7_display"]),
    ]
    table_html = "\n".join([f"<section><h2>{html.escape(name)}</h2>{_style_df(df)}</section>" for name, df in sections])

    status_class = "normal" if state == "NORMAL" else "warning"
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; margin: 32px; color: #17212b; background: #f7f9fb; }}
    h1 {{ margin-bottom: 4px; }}
    h2 {{ margin-top: 34px; border-bottom: 1px solid #dde3ea; padding-bottom: 8px; }}
    .card {{ background: white; border: 1px solid #dde3ea; border-radius: 14px; padding: 18px 22px; margin: 18px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }}
    .badge {{ display: inline-block; padding: 6px 10px; border-radius: 999px; font-weight: 700; }}
    .normal {{ background: #e6f4ea; color: #137333; }}
    .warning {{ background: #fce8e6; color: #a50e0e; }}
    table.dashboard-table {{ border-collapse: collapse; width: 100%; font-size: 13px; background: white; }}
    .dashboard-table th, .dashboard-table td {{ border: 1px solid #e3e7ec; padding: 8px 10px; vertical-align: top; }}
    .dashboard-table th {{ background: #eef3f8; text-align: left; }}
    .note {{ color: #56616d; font-size: 13px; }}
    section {{ overflow-x: auto; }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <p class="note">Local autoresearch-style port. This is a decision-support dashboard, not an automatic trading signal.</p>
  <div class="card">
    <p><strong>Latest data date:</strong> {latest.name.date()}</p>
    <p><strong>Current state:</strong> <span class="badge {status_class}">{html.escape(state)}</span></p>
    <p><strong>Combined signal:</strong> {html.escape(signal)}</p>
    <p><strong>Interpretation:</strong> {html.escape(interpretation)}</p>
    <p class="note">Core rule: R2_ACTIVE = at least 3 of 6 R2 components triggered. MMDI confirms risk when MMDI ≥ 50 and marks extreme stress when MMDI ≥ 80.</p>
  </div>
  {table_html}
  <h2>R2 Component Charts</h2>
  {r2_html}
  <h2>MMDI Component Charts</h2>
  {mmdi_html}
  <h2>Market / Rate / Credit Context</h2>
  {macro_html}
</body>
</html>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(doc, encoding="utf-8")
