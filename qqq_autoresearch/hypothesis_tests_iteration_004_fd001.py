"""Research-only tests for iteration_004_fd001 FD_001 hypotheses.

This module joins the frozen FD_001 experimental feature snapshot to the
exported daily-wide feature table, applies deterministic pre-declared triggers,
and writes walk-forward diagnostic outputs. It does not modify production
dashboard logic and does not optimize thresholds.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from qqq_autoresearch.hypothesis_tests_iteration_002 import (
    PREFIX,
    _num,
    _prior_alert_window,
    _rate,
    _summarize_events,
    add_forward_mdd_labels,
    load_daily_wide,
    load_hypotheses,
    make_folds,
)


FEATURE_SNAPSHOT_ID = "FD_001_combined"


SOURCE_COLUMNS = {
    "FD001_H001_FALSE_CALM_CONFIRMED_DOWNSIDE": [
        "freq_003_false_calm_confirmed_flag",
        "freq_003_false_calm_internal_deterioration_count",
    ],
    "FD001_H002_VOL_TERM_PERSISTENT_ACUTE_STRESS": [
        "freq_007_vol_term_daily_stress_count",
        "freq_007_vol_term_stress_persistence_5d",
        "freq_007_vol_term_stress_persistence_20d",
    ],
    "FD001_H003_VOL_DISAGREEMENT_REGIME_SHIFT": [
        "freq_008_vol_disagreement_score_pct",
        "freq_008_vol_disagreement_rank_change_20d",
        "freq_008_vol_disagreement_flag",
    ],
    "FD001_H004_FALSE_CALM_VOL_DISAGREEMENT_CONFIRMATION": [
        "freq_003_false_calm_possible_flag",
        "freq_003_false_calm_internal_deterioration_count",
        "freq_008_vol_disagreement_score_pct",
    ],
}


TARGETS = {
    "FD001_H001_FALSE_CALM_CONFIRMED_DOWNSIDE": (30, -0.08),
    "FD001_H002_VOL_TERM_PERSISTENT_ACUTE_STRESS": (15, -0.05),
    "FD001_H003_VOL_DISAGREEMENT_REGIME_SHIFT": (30, -0.08),
    "FD001_H004_FALSE_CALM_VOL_DISAGREEMENT_CONFIRMATION": (30, -0.08),
}


def _ge_fixed(df: pd.DataFrame, col: str, threshold: float) -> pd.Series:
    if col not in df:
        return pd.Series(False, index=df.index)
    return _num(df, col) >= threshold


def _available(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    if not columns:
        return pd.Series(True, index=df.index)
    availability = pd.Series(True, index=df.index)
    for column in columns:
        availability &= column in df and _num(df, column).notna()
    return availability


def load_experimental_snapshot(path: Path) -> pd.DataFrame:
    snapshot = pd.read_csv(path)
    if "date" not in snapshot.columns:
        raise ValueError(f"{path} must contain a date column")
    snapshot["date"] = pd.to_datetime(snapshot["date"])
    return snapshot.set_index("date").sort_index()


def load_joined_frame(data_path: Path, snapshot_path: Path) -> pd.DataFrame:
    raw = load_daily_wide(data_path)
    labelled = add_forward_mdd_labels(raw)
    snapshot = load_experimental_snapshot(snapshot_path)
    overlap = [column for column in snapshot.columns if column in labelled.columns]
    if overlap:
        raise ValueError(f"Experimental snapshot columns already exist in daily-wide input: {overlap}")
    joined = labelled.join(snapshot, how="left")
    return joined.sort_index()


def trigger_fd001_h001(test: pd.DataFrame, train: pd.DataFrame) -> pd.Series:
    del train
    return (
        _ge_fixed(test, "freq_003_false_calm_confirmed_flag", 1.0)
        & _ge_fixed(test, "freq_003_false_calm_internal_deterioration_count", 3.0)
    )


def trigger_fd001_h002(test: pd.DataFrame, train: pd.DataFrame) -> pd.Series:
    del train
    return (
        _ge_fixed(test, "freq_007_vol_term_daily_stress_count", 2.0)
        & _ge_fixed(test, "freq_007_vol_term_stress_persistence_5d", 0.60)
        & _ge_fixed(test, "freq_007_vol_term_stress_persistence_20d", 0.35)
    )


def trigger_fd001_h003(test: pd.DataFrame, train: pd.DataFrame) -> pd.Series:
    del train
    return (
        _ge_fixed(test, "freq_008_vol_disagreement_flag", 1.0)
        & _ge_fixed(test, "freq_008_vol_disagreement_score_pct", 0.90)
        & _ge_fixed(test, "freq_008_vol_disagreement_rank_change_20d", 0.50)
    )


def trigger_fd001_h004(test: pd.DataFrame, train: pd.DataFrame) -> pd.Series:
    del train
    return (
        _ge_fixed(test, "freq_003_false_calm_possible_flag", 1.0)
        & _ge_fixed(test, "freq_003_false_calm_internal_deterioration_count", 2.0)
        & _ge_fixed(test, "freq_008_vol_disagreement_score_pct", 0.85)
    )


TRIGGERS: dict[str, Callable[[pd.DataFrame, pd.DataFrame], pd.Series]] = {
    "FD001_H001_FALSE_CALM_CONFIRMED_DOWNSIDE": trigger_fd001_h001,
    "FD001_H002_VOL_TERM_PERSISTENT_ACUTE_STRESS": trigger_fd001_h002,
    "FD001_H003_VOL_DISAGREEMENT_REGIME_SHIFT": trigger_fd001_h003,
    "FD001_H004_FALSE_CALM_VOL_DISAGREEMENT_CONFIRMATION": trigger_fd001_h004,
}


def run_tests(
    data_path: Path,
    snapshot_path: Path,
    hypotheses_path: Path,
    output_dir: Path,
    min_train_years: int = 8,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    df = load_joined_frame(data_path, snapshot_path)
    hypotheses = load_hypotheses(hypotheses_path)
    meta = {h.get("hypothesis_id"): h for h in hypotheses}
    folds = make_folds(df, min_train_years=min_train_years)

    summary_rows: list[dict] = []
    fold_rows: list[dict] = []
    event_rows: list[dict] = []
    signal_frames: list[pd.DataFrame] = []

    for hypothesis_id, trigger_fn in TRIGGERS.items():
        horizon, threshold = TARGETS[hypothesis_id]
        target_col = f"future_{horizon}bd_mdd"
        source_columns = SOURCE_COLUMNS[hypothesis_id]
        all_alert = pd.Series(False, index=df.index, name=f"{hypothesis_id}_alert")
        all_fold = pd.Series(pd.NA, index=df.index, name=f"{hypothesis_id}_fold")
        all_eligible = pd.Series(False, index=df.index, name=f"{hypothesis_id}_eligible")

        for start, end in folds:
            train_end = start - pd.offsets.BDay(horizon)
            train = df[df.index < train_end]
            test = df[(df.index >= start) & (df.index <= end)]
            if len(train) < 252 * min_train_years or test.empty:
                continue
            source_available = _available(test, source_columns)
            eligible = test[target_col].notna() & source_available
            raw_alert = trigger_fn(test, train).reindex(test.index).fillna(False).astype(bool)
            alert = raw_alert & eligible
            hit = (test[target_col] <= threshold) & eligible
            base_hit_rate = hit[eligible].mean() if eligible.sum() else np.nan
            alert_hit_rate = hit[alert].mean() if alert.sum() else np.nan
            lift = alert_hit_rate / base_hit_rate if pd.notna(alert_hit_rate) and base_hit_rate and base_hit_rate > 0 else np.nan
            event_stats, fold_event_rows = _summarize_events(test[eligible], hit[eligible], alert[eligible], horizon, hypothesis_id, start.year)
            prior_alert = _prior_alert_window(alert[eligible], horizon)

            fold_rows.append({
                "hypothesis_id": hypothesis_id,
                "year": start.year,
                "horizon_bd": horizon,
                "mdd_threshold": threshold,
                "eligible_days": int(eligible.sum()),
                "alert_days": int(alert.sum()),
                "alert_burden": _rate(int(alert.sum()), int(eligible.sum())),
                "base_hit_rate": float(base_hit_rate) if pd.notna(base_hit_rate) else np.nan,
                "alert_hit_rate": float(alert_hit_rate) if pd.notna(alert_hit_rate) else np.nan,
                "base_rate_lift": float(lift) if pd.notna(lift) else np.nan,
                "hit_days": int(hit.sum()),
                "false_calm_days": int((hit[eligible] & ~prior_alert).sum()),
                "false_calm_day_rate": _rate(int((hit[eligible] & ~prior_alert).sum()), int(hit[eligible].sum())),
                **event_stats,
                "false_calm_event_reduction": event_stats.get("event_coverage", np.nan),
            })
            event_rows.extend(fold_event_rows)
            all_alert.loc[test.index] = alert
            all_fold.loc[test.index] = start.year
            all_eligible.loc[test.index] = eligible

        valid = all_fold.notna() & df[target_col].notna() & _available(df, source_columns)
        alert = all_alert & valid
        hit = (df[target_col] <= threshold) & valid
        base_hit_rate = hit[valid].mean() if valid.sum() else np.nan
        alert_hit_rate = hit[alert].mean() if alert.sum() else np.nan
        lift = alert_hit_rate / base_hit_rate if pd.notna(alert_hit_rate) and base_hit_rate and base_hit_rate > 0 else np.nan
        event_stats, summary_event_rows = _summarize_events(df[valid], hit[valid], alert[valid], horizon, hypothesis_id)
        prior_alert = _prior_alert_window(alert[valid], horizon)
        per_fold = pd.DataFrame([row for row in fold_rows if row["hypothesis_id"] == hypothesis_id])
        lift_values = pd.to_numeric(per_fold.get("base_rate_lift", pd.Series(dtype=float)), errors="coerce")
        event_coverages = pd.to_numeric(per_fold.get("event_coverage", pd.Series(dtype=float)), errors="coerce")
        folds_total = int(len(per_fold))
        positive_lift_folds = int((lift_values > 1.0).sum()) if folds_total else 0
        folds_with_alerts = int((per_fold["alert_days"] > 0).sum()) if folds_total else 0
        folds_with_event_coverage = int((event_coverages > 0).sum()) if folds_total else 0
        false_calm_days = int((hit[valid] & ~prior_alert).sum())

        summary_rows.append({
            "hypothesis_id": hypothesis_id,
            "title": meta.get(hypothesis_id, {}).get("title", hypothesis_id),
            "parent_feature_snapshot_id": FEATURE_SNAPSHOT_ID,
            "target_type": meta.get(hypothesis_id, {}).get("target_type", ""),
            "horizon_bd": horizon,
            "mdd_threshold": threshold,
            "valid_start": str(df[valid].index.min().date()) if valid.any() else "",
            "valid_end": str(df[valid].index.max().date()) if valid.any() else "",
            "eligible_days": int(valid.sum()),
            "alert_days": int(alert.sum()),
            "alert_burden": _rate(int(alert.sum()), int(valid.sum())),
            "base_hit_rate": float(base_hit_rate) if pd.notna(base_hit_rate) else np.nan,
            "alert_hit_rate": float(alert_hit_rate) if pd.notna(alert_hit_rate) else np.nan,
            "base_rate_lift": float(lift) if pd.notna(lift) else np.nan,
            "hit_days": int(hit.sum()),
            "false_calm_days": false_calm_days,
            "false_calm_day_rate": _rate(false_calm_days, int(hit[valid].sum())),
            **event_stats,
            "false_calm_event_reduction": event_stats.get("event_coverage", np.nan),
            "folds_total": folds_total,
            "folds_with_alerts": folds_with_alerts,
            "positive_lift_folds": positive_lift_folds,
            "positive_lift_fold_share": _rate(positive_lift_folds, folds_total),
            "folds_with_event_coverage": folds_with_event_coverage,
            "median_fold_lift": float(lift_values.median()) if lift_values.notna().any() else np.nan,
            "mean_fold_lift": float(lift_values.mean()) if lift_values.notna().any() else np.nan,
            "fold_lift_std": float(lift_values.std()) if lift_values.notna().sum() > 1 else np.nan,
            "source_coverage_ratio": _rate(int(_available(df, source_columns).sum()), len(df)),
            "sample_coverage_caveat": "Eligible days require non-null source columns and non-null target labels.",
        })
        for row in summary_event_rows:
            row["year"] = "all"
            event_rows.append(row)
        signal_frames.append(
            pd.DataFrame({
                f"{hypothesis_id}_alert": all_alert,
                f"{hypothesis_id}_eligible": all_eligible,
                f"{hypothesis_id}_fold": all_fold,
            })
        )

    summary = pd.DataFrame(summary_rows).sort_values(["base_rate_lift", "event_coverage"], ascending=False, na_position="last")
    folds_df = pd.DataFrame(fold_rows)
    events_df = pd.DataFrame(event_rows)
    signals = pd.concat(signal_frames, axis=1) if signal_frames else pd.DataFrame(index=df.index)

    paths = {
        "summary_path": output_dir / "hypothesis_test_summary.csv",
        "folds_path": output_dir / "hypothesis_test_folds.csv",
        "signals_path": output_dir / "hypothesis_test_daily_signals.csv",
        "events_path": output_dir / "hypothesis_test_events.csv",
        "html_path": output_dir / "hypothesis_test_report.html",
        "json_path": output_dir / "hypothesis_test_summary.json",
    }
    summary.to_csv(paths["summary_path"], index=False)
    folds_df.to_csv(paths["folds_path"], index=False)
    signals.to_csv(paths["signals_path"])
    events_df.to_csv(paths["events_path"], index=False)
    paths["json_path"].write_text(json.dumps(summary.to_dict(orient="records"), indent=2), encoding="utf-8")
    write_html_report(summary, folds_df, events_df, paths["html_path"])
    return {key: str(path) for key, path in paths.items()} | {"summary": summary.to_dict(orient="records")}


def write_html_report(summary: pd.DataFrame, folds: pd.DataFrame, events: pd.DataFrame, path: Path) -> None:
    css = """
    <style>
    body{font-family:Arial,sans-serif;margin:24px;color:#222}
    table{border-collapse:collapse;width:100%;font-size:12px;margin-bottom:24px}
    th,td{border:1px solid #ddd;padding:6px;text-align:right}
    th{text-align:center;background:#f3f5f7}
    td:first-child,td:nth-child(2),td:nth-child(3){text-align:left}
    .note{color:#555;max-width:960px;line-height:1.45}
    </style>
    """
    body = [
        "<h1>QQQ Hypothesis Test Report - iteration_004_fd001</h1>",
        "<p class='note'>Research-only diagnostic. FD_001 experimental features are joined from the frozen combined snapshot. Thresholds are deterministic and pre-declared. No threshold optimization is performed.</p>",
        "<h2>Summary</h2>",
        summary.to_html(index=False, escape=True, border=0),
        "<h2>Yearly folds</h2>",
        folds.to_html(index=False, escape=True, border=0),
        "<h2>Event details</h2>",
        events.head(500).to_html(index=False, escape=True, border=0),
    ]
    doc = "<html><head><meta charset='utf-8'>" + css + "</head><body>" + "\n".join(body) + "</body></html>"
    path.write_text(doc, encoding="utf-8")
