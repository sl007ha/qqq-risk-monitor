"""Rule-based hypothesis test runner for QQQ Risk Monitor.

This module tests the five Codex-draft hypotheses using deterministic trigger
logic, training-window quantiles, and forward maximum-drawdown labels. It is an
initial research diagnostic, not an optimized trading model.
"""
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

PREFIX = "qqq_r2_mmdi_v1_3_1"


def _to_bool(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s.fillna(False)
    if str(s.dtype).startswith("bool"):
        return s.fillna(False).astype(bool)
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def _q(train: pd.DataFrame, col: str, p: float) -> float:
    if col not in train:
        return np.nan
    return pd.to_numeric(train[col], errors="coerce").quantile(p)


def _ge(df: pd.DataFrame, col: str, val: float) -> pd.Series:
    return pd.to_numeric(df[col], errors="coerce") >= val if col in df and pd.notna(val) else pd.Series(False, index=df.index)


def _le(df: pd.DataFrame, col: str, val: float) -> pd.Series:
    return pd.to_numeric(df[col], errors="coerce") <= val if col in df and pd.notna(val) else pd.Series(False, index=df.index)


def _truth(df: pd.DataFrame, col: str) -> pd.Series:
    return _to_bool(df[col]) if col in df else pd.Series(False, index=df.index)


def add_forward_mdd_labels(df: pd.DataFrame, horizons=(15, 30, 60, 126)) -> pd.DataFrame:
    out = df.copy()
    close = pd.to_numeric(out["qqq_close"], errors="coerce")
    for h in horizons:
        vals = []
        arr = close.to_numpy(dtype=float)
        n = len(arr)
        for i in range(n):
            if not np.isfinite(arr[i]) or i + 1 >= n:
                vals.append(np.nan)
                continue
            end = min(n, i + h + 1)
            fwd = arr[i + 1 : end]
            fwd = fwd[np.isfinite(fwd)]
            if len(fwd) == 0:
                vals.append(np.nan)
            else:
                vals.append(float(np.min(fwd / arr[i] - 1.0)))
        out[f"future_{h}bd_mdd"] = vals
    return out


# --- Hypothesis trigger functions -------------------------------------------------

def trigger_h001(test: pd.DataFrame, train: pd.DataFrame) -> pd.Series:
    range_stress = _ge(test, "range_20d_vs_252d", _q(train, "range_20d_vs_252d", 0.80))
    vol_stress = _ge(test, "vol_20d_vs_252d", _q(train, "vol_20d_vs_252d", 0.80))
    downside = (
        _ge(test, "gap_down_count_20d", _q(train, "gap_down_count_20d", 0.80))
        | _ge(test, "large_red_day_count_20d", _q(train, "large_red_day_count_20d", 0.80))
        | _le(test, "realized_skew_20d", _q(train, "realized_skew_20d", 0.20))
    )
    return range_stress & vol_stress & downside


def trigger_h002(test: pd.DataFrame, train: pd.DataFrame) -> pd.Series:
    cap_weight = _ge(test, "qqq_vs_qqqe_3m", _q(train, "qqq_vs_qqqe_3m", 0.80)) | _ge(test, "qqq_vs_rsp_3m", _q(train, "qqq_vs_rsp_3m", 0.80))
    thinning = _le(test, "mag7_breadth", _q(train, "mag7_breadth", 0.30))
    semis = _truth(test, "semis_failure_flag") | _truth(test, "qqq_up_soxx_down_20d") | _le(test, "smh_vs_qqq_3m", _q(train, "smh_vs_qqq_3m", 0.30))
    return cap_weight & (thinning | semis)


def trigger_h003(test: pd.DataFrame, train: pd.DataFrame) -> pd.Series:
    cooling = _le(test, "mmdi_falling_from_high", _q(train, "mmdi_falling_from_high", 0.20)) | _truth(test, "mmdi_low_after_high") | _le(test, "mmdi_20d_change", _q(train, "mmdi_20d_change", 0.20))
    price_not_repaired = _truth(test, "failed_reclaim_ma50") | _le(test, "price_vs_ma50", 0.0) | _le(test, "dist_52w_high", -0.05)
    bounce = _ge(test, "rebound_from_trough_20d", _q(train, "rebound_from_trough_20d", 0.60))
    return cooling & price_not_repaired & bounce


def trigger_h004(test: pd.DataFrame, train: pd.DataFrame) -> pd.Series:
    credit = (
        _truth(test, "credit_worsening_equity_up")
        | _truth(test, "credit_not_confirming_equity")
        | _ge(test, "hy_oas_change_20d", _q(train, "hy_oas_change_20d", 0.80))
        | _le(test, "hyg_vs_lqd_20d", _q(train, "hyg_vs_lqd_20d", 0.20))
    )
    macro_vol = (
        _ge(test, "vix9d_vs_vix", _q(train, "vix9d_vs_vix", 0.80))
        | _truth(test, "usd_yield_shock")
        | (_ge(test, "rate_vol_proxy", _q(train, "rate_vol_proxy", 0.80)) & _ge(test, "dxy_change_20d", _q(train, "dxy_change_20d", 0.70)))
    )
    return credit & macro_vol


def trigger_h005(test: pd.DataFrame, train: pd.DataFrame) -> pd.Series:
    advance = _ge(test, "qqq_ret_3m", _q(train, "qqq_ret_3m", 0.70)) & _ge(test, "dist_52w_high", -0.05)
    distribution = _le(test, "obv_20d_chg", _q(train, "obv_20d_chg", 0.30)) | _le(test, "obv_60d_chg", _q(train, "obv_60d_chg", 0.30))
    abnormal = _ge(test, "qqq_volume_z_20d", 1.0) | _ge(test, "dollar_volume_z_20d", 1.0)
    liquidity = _ge(test, "amihud_illiquidity_proxy", _q(train, "amihud_illiquidity_proxy", 0.80))
    return advance & distribution & (abnormal | liquidity)


TRIGGERS: dict[str, Callable[[pd.DataFrame, pd.DataFrame], pd.Series]] = {
    "H001": trigger_h001,
    "H002": trigger_h002,
    "H003": trigger_h003,
    "H004": trigger_h004,
    "H005": trigger_h005,
}
TARGETS = {
    "H001": (30, -0.08),
    "H002": (60, -0.10),
    "H003": (30, -0.08),
    "H004": (15, -0.05),
    "H005": (60, -0.10),
}


def load_hypotheses(path: Path) -> list[dict]:
    if not path.exists():
        return [{"hypothesis_id": h, "title": h} for h in TRIGGERS]
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json" or yaml is None:
        obj = json.loads(text)
    else:
        obj = yaml.safe_load(text)
    if isinstance(obj, dict):
        return obj.get("hypotheses", [])
    if isinstance(obj, list):
        return obj
    return []


def make_folds(df: pd.DataFrame, min_train_years: int = 8) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    idx = pd.to_datetime(df.index)
    years = sorted(set(idx.year))
    folds = []
    for y in years:
        if y - years[0] < min_train_years:
            continue
        start = pd.Timestamp(f"{y}-01-01")
        end = pd.Timestamp(f"{y}-12-31")
        if ((idx >= start) & (idx <= end)).sum() > 80:
            folds.append((start, end))
    return folds


def _coverage_by_events(test: pd.DataFrame, hit: pd.Series, alert: pd.Series, horizon: int) -> tuple[int, int, float]:
    hit = hit.fillna(False).astype(bool)
    alert = alert.fillna(False).astype(bool)
    if hit.sum() == 0:
        return 0, 0, np.nan
    runs = (hit != hit.shift(1).fillna(False)).cumsum()
    event_starts = []
    for _, block in test[hit].groupby(runs[hit]):
        if not block.empty:
            event_starts.append(block.index[0])
    covered = 0
    for start in event_starts:
        loc = test.index.get_loc(start)
        left = max(0, loc - horizon)
        right = loc + 1
        if alert.iloc[left:right].any():
            covered += 1
    total = len(event_starts)
    return covered, total, covered / total if total else np.nan


def run_tests(data_path: Path, hypotheses_path: Path | None, output_dir: Path, min_train_years: int = 8) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(data_path, index_col=0, parse_dates=True).sort_index()
    df = add_forward_mdd_labels(df)
    hypotheses = load_hypotheses(hypotheses_path) if hypotheses_path else load_hypotheses(Path("missing.json"))
    meta = {h.get("hypothesis_id"): h for h in hypotheses}
    folds = make_folds(df, min_train_years=min_train_years)

    signal_frames = []
    fold_rows = []
    summary_rows = []

    for hid, trigger_fn in TRIGGERS.items():
        horizon, threshold = TARGETS[hid]
        target_col = f"future_{horizon}bd_mdd"
        per_h_alert = pd.Series(False, index=df.index, name=f"{hid}_alert")
        per_h_fold = pd.Series(pd.NA, index=df.index, name=f"{hid}_fold")

        for start, end in folds:
            train_end = start - pd.offsets.BDay(horizon)
            train = df[df.index < train_end]
            test = df[(df.index >= start) & (df.index <= end)].copy()
            if len(train) < 252 * min_train_years or test.empty:
                continue
            needed = meta.get(hid, {}).get("exact_feature_columns_used", [])
            if needed:
                available = [c for c in needed if c in df.columns]
                if len(available) < max(1, len(needed) // 2):
                    continue
            alert = trigger_fn(test, train).reindex(test.index).fillna(False).astype(bool)
            per_h_alert.loc[test.index] = alert
            per_h_fold.loc[test.index] = start.year

            eligible = test[target_col].notna()
            hit = (test[target_col] <= threshold) & eligible
            base = hit.mean() if eligible.sum() else np.nan
            alert_days = alert & eligible
            hit_alert = hit[alert_days].mean() if alert_days.sum() else np.nan
            lift = hit_alert / base if pd.notna(hit_alert) and base and base > 0 else np.nan
            covered, events, event_cov = _coverage_by_events(test[eligible], hit[eligible], alert[eligible], horizon)
            fold_rows.append({
                "hypothesis_id": hid, "year": start.year, "horizon_bd": horizon, "threshold": threshold,
                "eligible_days": int(eligible.sum()), "alert_days": int(alert_days.sum()),
                "alert_burden": float(alert_days.mean()) if eligible.sum() else np.nan,
                "base_hit_rate": float(base) if pd.notna(base) else np.nan,
                "alert_hit_rate": float(hit_alert) if pd.notna(hit_alert) else np.nan,
                "lift": float(lift) if pd.notna(lift) else np.nan,
                "events_covered": covered, "events_total": events, "event_coverage": event_cov,
            })

        valid = per_h_fold.notna() & df[target_col].notna()
        alert = per_h_alert & valid
        hit = (df[target_col] <= threshold) & valid
        base = hit[valid].mean() if valid.sum() else np.nan
        hit_alert = hit[alert].mean() if alert.sum() else np.nan
        lift = hit_alert / base if pd.notna(hit_alert) and base and base > 0 else np.nan
        covered, events, event_cov = _coverage_by_events(df[valid], hit[valid], alert[valid], horizon)
        false_calm = int((hit & ~per_h_alert & valid).sum())
        summary_rows.append({
            "hypothesis_id": hid,
            "title": meta.get(hid, {}).get("title", hid),
            "horizon_bd": horizon,
            "mdd_threshold": threshold,
            "valid_start": str(df[valid].index.min().date()) if valid.any() else "",
            "valid_end": str(df[valid].index.max().date()) if valid.any() else "",
            "eligible_days": int(valid.sum()),
            "alert_days": int(alert.sum()),
            "alert_burden": float(alert.sum() / valid.sum()) if valid.sum() else np.nan,
            "base_hit_rate": float(base) if pd.notna(base) else np.nan,
            "alert_hit_rate": float(hit_alert) if pd.notna(hit_alert) else np.nan,
            "base_rate_lift": float(lift) if pd.notna(lift) else np.nan,
            "events_covered": covered,
            "events_total": events,
            "event_coverage": event_cov,
            "false_calm_days": false_calm,
        })
        signal_frames.append(pd.DataFrame({f"{hid}_alert": per_h_alert, f"{hid}_fold": per_h_fold}))

    summary = pd.DataFrame(summary_rows).sort_values(["base_rate_lift", "event_coverage"], ascending=False, na_position="last")
    folds_df = pd.DataFrame(fold_rows)
    signals = pd.concat(signal_frames, axis=1) if signal_frames else pd.DataFrame(index=df.index)

    summary_path = output_dir / "hypothesis_test_summary.csv"
    folds_path = output_dir / "hypothesis_test_folds.csv"
    signals_path = output_dir / "hypothesis_test_daily_signals.csv"
    html_path = output_dir / "hypothesis_test_report.html"
    summary.to_csv(summary_path, index=False)
    folds_df.to_csv(folds_path, index=False)
    signals.to_csv(signals_path)
    write_html_report(summary, folds_df, html_path)
    return {"summary_path": str(summary_path), "folds_path": str(folds_path), "signals_path": str(signals_path), "html_path": str(html_path), "summary": summary.to_dict(orient="records")}


def write_html_report(summary: pd.DataFrame, folds: pd.DataFrame, path: Path) -> None:
    css = """
    <style>body{font-family:Arial,sans-serif;margin:24px;color:#222} table{border-collapse:collapse;width:100%;font-size:13px} th,td{border:1px solid #ddd;padding:6px;text-align:right} th{text-align:center;background:#f3f5f7} td:first-child,td:nth-child(2){text-align:left} .note{color:#555}</style>
    """
    body = ["<h1>QQQ Hypothesis Test Report</h1>", "<p class='note'>Initial diagnostic only. Thresholds are estimated within training windows; no parameter optimization is performed.</p>"]
    body.append("<h2>Summary</h2>")
    body.append(summary.to_html(index=False, escape=True, border=0))
    body.append("<h2>Yearly folds</h2>")
    body.append(folds.to_html(index=False, escape=True, border=0))
    path.write_text("<html><head><meta charset='utf-8'>" + css + "</head><body>" + "\n".join(body) + "</body></html>", encoding="utf-8")
