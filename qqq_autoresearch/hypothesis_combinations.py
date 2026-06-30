"""Combination diagnostics for QQQ hypothesis alerts.

Reads the daily alert signals produced by run_hypothesis_tests.py and evaluates
simple OR/AND/risk-score combinations across 15BD, 30BD, and 60BD forward MDD
labels. This is a research triage layer, not an optimized model.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .hypothesis_tests import PREFIX, add_forward_mdd_labels


COMBINATIONS = {
    "C001_H001_OR_H004": ["H001", "H004"],
    "C002_H002_AND_H001": ["H002", "H001"],
    "C003_H002_AND_H004": ["H002", "H004"],
    "C004_H001_OR_H002_OR_H004": ["H001", "H002", "H004"],
    "C005_H001_AND_H004": ["H001", "H004"],
}

COMBO_METHOD = {
    "C001_H001_OR_H004": "or",
    "C002_H002_AND_H001": "and",
    "C003_H002_AND_H004": "and",
    "C004_H001_OR_H002_OR_H004": "or",
    "C005_H001_AND_H004": "and",
}

TARGETS = {
    "15BD_-5pct": (15, -0.05),
    "30BD_-8pct": (30, -0.08),
    "60BD_-10pct": (60, -0.10),
}


def _bool(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s.fillna(False)
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def _valid_for(signals: pd.DataFrame, parts: list[str]) -> pd.Series:
    valid = pd.Series(True, index=signals.index)
    for h in parts:
        col = f"{h}_fold"
        if col in signals:
            valid &= signals[col].notna()
        else:
            valid &= False
    return valid


def _combo_alert(signals: pd.DataFrame, name: str, parts: list[str]) -> pd.Series:
    cols = [f"{h}_alert" for h in parts]
    frame = pd.DataFrame({c: _bool(signals[c]) if c in signals else False for c in cols}, index=signals.index)
    if COMBO_METHOD[name] == "and":
        return frame.all(axis=1)
    return frame.any(axis=1)


def _event_coverage(df: pd.DataFrame, hit: pd.Series, alert: pd.Series, lead_window: int) -> tuple[int, int, float]:
    hit = hit.fillna(False).astype(bool)
    alert = alert.fillna(False).astype(bool)
    if hit.sum() == 0:
        return 0, 0, np.nan
    runs = (hit != hit.shift(1).fillna(False)).cumsum()
    starts = []
    for _, block in df[hit].groupby(runs[hit]):
        if not block.empty:
            starts.append(block.index[0])
    covered = 0
    for start in starts:
        loc = df.index.get_loc(start)
        left = max(0, loc - lead_window)
        right = loc + 1
        if alert.iloc[left:right].any():
            covered += 1
    total = len(starts)
    return covered, total, covered / total if total else np.nan


def _summarize_signal(df: pd.DataFrame, alert: pd.Series, valid: pd.Series, horizon: int, threshold: float, name: str, target_name: str) -> dict:
    target_col = f"future_{horizon}bd_mdd"
    eligible = valid & df[target_col].notna()
    alert = alert & eligible
    hit = (df[target_col] <= threshold) & eligible
    base = hit[eligible].mean() if eligible.sum() else np.nan
    alert_hit = hit[alert].mean() if alert.sum() else np.nan
    lift = alert_hit / base if pd.notna(alert_hit) and pd.notna(base) and base > 0 else np.nan
    covered, events, cov = _event_coverage(df[eligible], hit[eligible], alert[eligible], horizon)
    return {
        "signal": name,
        "target": target_name,
        "horizon_bd": horizon,
        "mdd_threshold": threshold,
        "eligible_days": int(eligible.sum()),
        "alert_days": int(alert.sum()),
        "alert_burden": float(alert.sum() / eligible.sum()) if eligible.sum() else np.nan,
        "base_hit_rate": float(base) if pd.notna(base) else np.nan,
        "alert_hit_rate": float(alert_hit) if pd.notna(alert_hit) else np.nan,
        "base_rate_lift": float(lift) if pd.notna(lift) else np.nan,
        "events_covered": covered,
        "events_total": events,
        "event_coverage": cov,
        "false_calm_days": int((hit & ~alert & eligible).sum()),
    }


def _score_summary(df: pd.DataFrame, signals: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    parts = ["H001", "H002", "H004"]
    valid = _valid_for(signals, parts)
    score = sum(_bool(signals.get(f"{h}_alert", pd.Series(False, index=signals.index))) for h in parts)
    rows = []
    for bucket in [0, 1, 2, 3]:
        bucket_alert = score == bucket
        for target_name, (horizon, threshold) in TARGETS.items():
            row = _summarize_signal(df, bucket_alert, valid, horizon, threshold, f"RISK_SCORE_EQ_{bucket}", target_name)
            row["risk_score_bucket"] = bucket
            rows.append(row)
    score_df = pd.DataFrame(rows)
    daily = pd.DataFrame({"risk_score_h001_h002_h004": score.where(valid), "valid_risk_score": valid}, index=df.index)
    daily.to_csv(output_dir / "combination_risk_score_daily.csv")
    return score_df


def run_combination_tests(data_path: Path, signals_path: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(data_path, index_col=0, parse_dates=True).sort_index()
    df = add_forward_mdd_labels(df)
    signals = pd.read_csv(signals_path, index_col=0, parse_dates=True).sort_index()
    signals = signals.reindex(df.index)

    daily_out = pd.DataFrame(index=df.index)
    summary_rows = []
    for name, parts in COMBINATIONS.items():
        valid = _valid_for(signals, parts)
        alert = _combo_alert(signals, name, parts) & valid
        daily_out[f"{name}_alert"] = alert
        daily_out[f"{name}_valid"] = valid
        for target_name, (horizon, threshold) in TARGETS.items():
            summary_rows.append(_summarize_signal(df, alert, valid, horizon, threshold, name, target_name))

    summary = pd.DataFrame(summary_rows)
    score_summary = _score_summary(df, signals, output_dir)
    full_summary = pd.concat([summary, score_summary], ignore_index=True)
    full_summary = full_summary.sort_values(["target", "base_rate_lift", "event_coverage"], ascending=[True, False, False], na_position="last")

    summary_path = output_dir / "combination_test_summary.csv"
    daily_path = output_dir / "combination_test_daily_signals.csv"
    html_path = output_dir / "combination_test_report.html"
    full_summary.to_csv(summary_path, index=False)
    daily_out.to_csv(daily_path)
    write_html_report(full_summary, html_path)
    return {
        "summary_path": str(summary_path),
        "daily_path": str(daily_path),
        "html_path": str(html_path),
        "summary": full_summary.to_dict(orient="records"),
    }


def write_html_report(summary: pd.DataFrame, path: Path) -> None:
    css = """
    <style>body{font-family:Arial,sans-serif;margin:24px;color:#222} table{border-collapse:collapse;width:100%;font-size:13px} th,td{border:1px solid #ddd;padding:6px;text-align:right} th{text-align:center;background:#f3f5f7} td:first-child,td:nth-child(2){text-align:left}.note{color:#555}</style>
    """
    body = [
        "<h1>QQQ Hypothesis Combination Test Report</h1>",
        "<p class='note'>Initial diagnostics only. Combination alerts are built from H001/H002/H004 standalone signals.</p>",
        "<h2>Combination and risk-score summary</h2>",
        summary.to_html(index=False, escape=True, border=0),
    ]
    path.write_text("<html><head><meta charset='utf-8'>" + css + "</head><body>" + "\n".join(body) + "</body></html>", encoding="utf-8")
