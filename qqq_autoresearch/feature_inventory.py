"""Export and append a full all-column feature inventory.

This is a diagnostic layer for testing: it lists every column currently present in
`work`, including raw downloaded series, derived features, R2/MMDI outputs, and
placeholder columns. It does not change dashboard signals.
"""
from __future__ import annotations

import html
from pathlib import Path

import numpy as np
import pandas as pd


def _family_for_column(col: str) -> str:
    c = col.lower()
    if c in {"qqq_open", "qqq_high", "qqq_low", "qqq_close", "qqq_volume"}:
        return "Raw QQQ OHLCV"
    if c.endswith("_close") or c in {"vix", "vxn", "credit_spread", "us10y_yield"}:
        return "Raw market / macro series"
    if c.startswith("r2_") or c.startswith("r2") or c in {"r2_stress_count", "r2_active", "r2_active_run_length", "r2_stress_intensity"}:
        return "R2 signal layer"
    if c.startswith("mmdi") or c in {"mmdi", "mmdi_zone", "mmdi_high", "mmdi_extreme"}:
        return "MMDI signal layer"
    if c.startswith("combined_"):
        return "Combined dashboard state"
    if "sentiment" in c or "headline" in c:
        return "Mainstream narrative / semantic"
    if "ma" in c or "trend" in c or "cross" in c or "reclaim" in c:
        return "A. Price / Trend Structure"
    if "dd" in c or "drawdown" in c or "high" in c or "low" in c or "underwater" in c:
        return "B. Drawdown / Distance"
    if "vol" in c or "range" in c or "atr" in c or "gap" in c or "kurt" in c or "skew" in c or "vix" in c or "vvix" in c:
        return "C/J. Volatility / Options"
    if "ret" in c or "mom" in c or "rsi" in c or "macd" in c or "tsmom" in c or "reversal" in c:
        return "D. Momentum / Reversal"
    if "qqqe" in c or "breadth" in c or "advance" in c or "new_highs" in c or "adv_dec" in c:
        return "E. Breadth / Internals"
    if "vs_" in c or "_vs_" in c or c.startswith(("xl", "mtum", "qual", "large_", "growth_")):
        return "F/G. Leadership / Relative Strength"
    if "soxx" in c or "smh" in c or "nvda" in c or "mag7" in c or "semis" in c or "ai_" in c:
        return "G. Semiconductor / AI"
    if "yield" in c or "ust" in c or "curve" in c or "rate" in c or "dgs" in c or "dfii" in c or "tlt" in c or "ief" in c or "dxy" in c:
        return "H. Rates / Yield Curve"
    if "credit" in c or "oas" in c or "hyg" in c or "lqd" in c or "ted" in c or "sofr" in c:
        return "I. Credit / Funding Stress"
    if "inflation" in c or "cpi" in c or "unemployment" in c or "claims" in c or "fed" in c or "liquidity" in c or "macro" in c or "nfci" in c or "walcl" in c:
        return "K. Macro / Regime Context"
    if "volume" in c or "obv" in c or "flow" in c or "amihud" in c or "liquidity" in c or "arkk" in c:
        return "L. Liquidity / Volume / Flow"
    return "Other / metadata"


def _fmt_value(x):
    if isinstance(x, (pd.Timestamp,)):
        return x.isoformat()
    if pd.isna(x):
        return np.nan
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, float, np.number)):
        try:
            return float(x)
        except Exception:
            return x
    return str(x)


def build_all_feature_inventory(work: pd.DataFrame) -> pd.DataFrame:
    latest = work.dropna(subset=["qqq_close"]).iloc[-1]
    rows = []
    for col in work.columns:
        s = work[col]
        non_null = int(s.notna().sum())
        rows.append(
            {
                "family_guess": _family_for_column(col),
                "column": col,
                "dtype": str(s.dtype),
                "latest_value": _fmt_value(latest.get(col, np.nan)),
                "non_null_count": non_null,
                "coverage_pct": non_null / len(work) if len(work) else np.nan,
                "first_valid_date": s.first_valid_index().date().isoformat() if s.first_valid_index() is not None else "",
                "last_valid_date": s.last_valid_index().date().isoformat() if s.last_valid_index() is not None else "",
            }
        )
    return pd.DataFrame(rows)


def _html_table(df: pd.DataFrame) -> str:
    return df.to_html(index=False, border=0, classes="dataframe dashboard-table", na_rep="N/A", escape=True)


def write_all_feature_inventory_outputs(work: pd.DataFrame, output_dir: str | Path, config: dict, html_path: str | Path | None = None) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = config["export_prefix"]

    inventory = build_all_feature_inventory(work)
    wide_latest = work.dropna(subset=["qqq_close"]).tail(1).T.reset_index()
    wide_latest.columns = ["column", "latest_value"]

    inventory_path = output_dir / f"{prefix}_all_feature_inventory.csv"
    wide_latest_path = output_dir / f"{prefix}_all_feature_latest_wide.csv"
    full_daily_path = output_dir / f"{prefix}_all_features_daily_wide.csv"

    inventory.to_csv(inventory_path, index=False)
    wide_latest.to_csv(wide_latest_path, index=False)
    work.to_csv(full_daily_path)

    if html_path is not None and Path(html_path).exists():
        doc = Path(html_path).read_text(encoding="utf-8")
        block = f"""
<section>
  <h2>All Pulled / Computed Features — Full Inventory</h2>
  <p class="note">
    This table lists every column currently available in the local pipeline, including raw downloaded series,
    derived v2 feature-universe columns, original R2/MMDI columns, and placeholders. The full daily wide table is
    also exported as <code>{html.escape(full_daily_path.name)}</code>.
  </p>
  {_html_table(inventory)}
</section>
"""
        if "</body>" in doc:
            doc = doc.replace("</body>", block + "\n</body>")
        else:
            doc += block
        Path(html_path).write_text(doc, encoding="utf-8")

    return {
        "all_feature_inventory": inventory,
        "all_feature_inventory_path": str(inventory_path),
        "all_feature_latest_wide_path": str(wide_latest_path),
        "all_features_daily_wide_path": str(full_daily_path),
    }
