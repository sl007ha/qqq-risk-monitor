"""Research-only tests for QQQ Risk Monitor iteration 003 hypotheses.

This module is intentionally isolated from production dashboard logic. It reads
the exported wide feature table, applies deterministic hypothesis triggers, and
writes diagnostic research outputs. It does not optimize thresholds.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from qqq_autoresearch.hypothesis_tests_iteration_002 import (
    PREFIX,
    _ge,
    _le,
    _num,
    _prior_alert_window,
    _q,
    _rate,
    _summarize_events,
    _truth,
    add_forward_mdd_labels,
    load_daily_wide,
    load_hypotheses,
    make_folds,
)


def trigger_i003_h001(test: pd.DataFrame, train: pd.DataFrame) -> pd.Series:
    range_stress = _ge(test, "range_20d_vs_252d", _q(train, "range_20d_vs_252d", 0.80))
    vol_stress = _ge(test, "vol_20d_vs_252d", _q(train, "vol_20d_vs_252d", 0.75))
    downside_tape = (
        _le(test, "realized_skew_20d", _q(train, "realized_skew_20d", 0.25))
        | _ge(test, "gap_down_count_20d", _q(train, "gap_down_count_20d", 0.75))
        | _ge(test, "large_red_day_count_20d", _q(train, "large_red_day_count_20d", 0.75))
    )
    flexible_trend_pressure = (
        _le(test, "price_vs_ma20", _q(train, "price_vs_ma20", 0.40))
        | _le(test, "price_vs_ma50", _q(train, "price_vs_ma50", 0.45))
    )
    return range_stress & vol_stress & downside_tape & flexible_trend_pressure


def trigger_i003_h002(test: pd.DataFrame, train: pd.DataFrame) -> pd.Series:
    credit_stress = (
        _truth(test, "credit_worsening_equity_up")
        | _truth(test, "credit_not_confirming_equity")
        | _ge(test, "hy_oas_change_20d", _q(train, "hy_oas_change_20d", 0.75))
        | _le(test, "hyg_vs_lqd_20d", _q(train, "hyg_vs_lqd_20d", 0.25))
    )
    macro_pressure = (
        _ge(test, "rate_vol_proxy", _q(train, "rate_vol_proxy", 0.75))
        | _ge(test, "dxy_change_20d", _q(train, "dxy_change_20d", 0.70))
        | _truth(test, "usd_yield_shock")
    )
    restrained_vol_confirmation = (
        _ge(test, "vix_percentile_252d", _q(train, "vix_percentile_252d", 0.70))
        | _ge(test, "vix9d_vs_vix", _q(train, "vix9d_vs_vix", 0.75))
    )
    return credit_stress & macro_pressure & restrained_vol_confirmation


def trigger_i003_h003(test: pd.DataFrame, train: pd.DataFrame) -> pd.Series:
    cap_weight_divergence = (
        _ge(test, "qqq_vs_qqqe_3m", _q(train, "qqq_vs_qqqe_3m", 0.70))
        | _ge(test, "qqq_vs_rsp_3m", _q(train, "qqq_vs_rsp_3m", 0.70))
    )
    semis_non_confirmation = (
        _ge(test, "qqq_vs_soxx_3m", _q(train, "qqq_vs_soxx_3m", 0.70))
        | _le(test, "smh_vs_qqq_3m", _q(train, "smh_vs_qqq_3m", 0.30))
        | _truth(test, "semis_failure_flag")
        | _truth(test, "qqq_up_soxx_down_20d")
    )
    breadth_or_mmdi_narrow = (
        _le(test, "mag7_breadth", _q(train, "mag7_breadth", 0.40))
        | _ge(test, "mmdi_leadership_narrowing_stress", _q(train, "mmdi_leadership_narrowing_stress", 0.70))
    )
    return cap_weight_divergence & (semis_non_confirmation | breadth_or_mmdi_narrow)


def trigger_i003_h004(test: pd.DataFrame, train: pd.DataFrame) -> pd.Series:
    apparent_repair = _le(test, "mmdi_falling_from_high", _q(train, "mmdi_falling_from_high", 0.25)) | _truth(test, "mmdi_low_after_high")
    unresolved_damage = (
        _truth(test, "MMDI_HIGH")
        | _truth(test, "failed_reclaim_ma50")
        | _truth(test, "failed_reclaim_ma200")
        | _le(test, "price_vs_ma50", 0.0)
        | _le(test, "dist_52w_high", -0.05)
    )
    bounce_context = _ge(test, "rebound_from_trough_20d", _q(train, "rebound_from_trough_20d", 0.60))
    return apparent_repair & unresolved_damage & bounce_context


def trigger_i003_h005(test: pd.DataFrame, train: pd.DataFrame) -> pd.Series:
    r2_quiet = (~_truth(test, "R2_ACTIVE")) & (_num(test, "R2_STRESS_COUNT") <= 1)
    mmdi_elevated_or_accelerating = (
        _truth(test, "MMDI_HIGH")
        | _ge(test, "MMDI", _q(train, "MMDI", 0.75))
        | _ge(test, "MMDI_10D_CHANGE", _q(train, "MMDI_10D_CHANGE", 0.70))
    )
    independent_confirmation = (
        _ge(test, "range_20d_vs_252d", _q(train, "range_20d_vs_252d", 0.75))
        | _ge(test, "vol_20d_vs_252d", _q(train, "vol_20d_vs_252d", 0.75))
        | _truth(test, "credit_not_confirming_equity")
        | _ge(test, "hy_oas_change_20d", _q(train, "hy_oas_change_20d", 0.80))
    )
    return r2_quiet & mmdi_elevated_or_accelerating & independent_confirmation


TRIGGERS: dict[str, Callable[[pd.DataFrame, pd.DataFrame], pd.Series]] = {
    "I003_H001": trigger_i003_h001,
    "I003_H002": trigger_i003_h002,
    "I003_H003": trigger_i003_h003,
    "I003_H004": trigger_i003_h004,
    "I003_H005": trigger_i003_h005,
}

TARGETS = {
    "I003_H001": (30, -0.08),
    "I003_H002": (15, -0.05),
    "I003_H003": (60, -0.10),
    "I003_H004": (30, -0.08),
    "I003_H005": (30, -0.08),
}


def run_tests(data_path: Path, hypotheses_path: Path, output_dir: Path, min_train_years: int = 8) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw = load_daily_wide(data_path)
    df = add_forward_mdd_labels(raw)
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
        all_alert = pd.Series(False, index=df.index, name=f"{hypothesis_id}_alert")
        all_fold = pd.Series(pd.NA, index=df.index, name=f"{hypothesis_id}_fold")

        for start, end in folds:
            train_end = start - pd.offsets.BDay(horizon)
            train = df[df.index < train_end]
            test = df[(df.index >= start) & (df.index <= end)]
            if len(train) < 252 * min_train_years or test.empty:
                continue
            alert = trigger_fn(test, train).reindex(test.index).fillna(False).astype(bool)
            eligible = test[target_col].notna()
            hit = (test[target_col] <= threshold) & eligible
            alert_days = alert & eligible
            base_hit_rate = hit[eligible].mean() if eligible.sum() else np.nan
            alert_hit_rate = hit[alert_days].mean() if alert_days.sum() else np.nan
            lift = alert_hit_rate / base_hit_rate if pd.notna(alert_hit_rate) and base_hit_rate and base_hit_rate > 0 else np.nan
            event_stats, fold_event_rows = _summarize_events(test[eligible], hit[eligible], alert[eligible], horizon, hypothesis_id, start.year)
            prior_alert = _prior_alert_window(alert[eligible], horizon)

            fold_rows.append({
                "hypothesis_id": hypothesis_id,
                "year": start.year,
                "horizon_bd": horizon,
                "mdd_threshold": threshold,
                "eligible_days": int(eligible.sum()),
                "alert_days": int(alert_days.sum()),
                "alert_burden": _rate(int(alert_days.sum()), int(eligible.sum())),
                "base_hit_rate": float(base_hit_rate) if pd.notna(base_hit_rate) else np.nan,
                "alert_hit_rate": float(alert_hit_rate) if pd.notna(alert_hit_rate) else np.nan,
                "base_rate_lift": float(lift) if pd.notna(lift) else np.nan,
                "hit_days": int(hit.sum()),
                "false_calm_days": int((hit[eligible] & ~prior_alert).sum()),
                **event_stats,
            })
            event_rows.extend(fold_event_rows)
            all_alert.loc[test.index] = alert
            all_fold.loc[test.index] = start.year

        valid = all_fold.notna() & df[target_col].notna()
        alert = all_alert & valid
        hit = (df[target_col] <= threshold) & valid
        base_hit_rate = hit[valid].mean() if valid.sum() else np.nan
        alert_hit_rate = hit[alert].mean() if alert.sum() else np.nan
        lift = alert_hit_rate / base_hit_rate if pd.notna(alert_hit_rate) and base_hit_rate and base_hit_rate > 0 else np.nan
        event_stats, summary_event_rows = _summarize_events(df[valid], hit[valid], alert[valid], horizon, hypothesis_id)
        prior_alert = _prior_alert_window(alert[valid], horizon)
        per_fold = pd.DataFrame([row for row in fold_rows if row["hypothesis_id"] == hypothesis_id])
        lift_values = pd.to_numeric(per_fold.get("base_rate_lift", pd.Series(dtype=float)), errors="coerce")
        folds_total = int(len(per_fold))
        folds_with_alerts = int((per_fold["alert_days"] > 0).sum()) if folds_total else 0
        positive_lift_folds = int((lift_values > 1.0).sum()) if folds_total else 0
        folds_with_event_coverage = int((pd.to_numeric(per_fold.get("event_coverage", pd.Series(dtype=float)), errors="coerce") > 0).sum()) if folds_total else 0

        summary_rows.append({
            "hypothesis_id": hypothesis_id,
            "title": meta.get(hypothesis_id, {}).get("title", hypothesis_id),
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
            "false_calm_days": int((hit[valid] & ~prior_alert).sum()),
            **event_stats,
            "folds_total": folds_total,
            "folds_with_alerts": folds_with_alerts,
            "positive_lift_folds": positive_lift_folds,
            "positive_lift_fold_share": _rate(positive_lift_folds, folds_total),
            "folds_with_event_coverage": folds_with_event_coverage,
            "median_fold_lift": float(lift_values.median()) if lift_values.notna().any() else np.nan,
            "mean_fold_lift": float(lift_values.mean()) if lift_values.notna().any() else np.nan,
        })
        for row in summary_event_rows:
            row["year"] = "all"
            event_rows.append(row)
        signal_frames.append(pd.DataFrame({f"{hypothesis_id}_alert": all_alert, f"{hypothesis_id}_fold": all_fold}))

    summary = pd.DataFrame(summary_rows).sort_values(["base_rate_lift", "event_coverage"], ascending=False, na_position="last")
    folds_df = pd.DataFrame(fold_rows)
    events_df = pd.DataFrame(event_rows)
    signals = pd.concat(signal_frames, axis=1) if signal_frames else pd.DataFrame(index=df.index)

    paths = {
        "summary_path": output_dir / "iteration_003_hypothesis_test_summary.csv",
        "folds_path": output_dir / "iteration_003_hypothesis_test_folds.csv",
        "signals_path": output_dir / "iteration_003_hypothesis_test_daily_signals.csv",
        "events_path": output_dir / "iteration_003_hypothesis_test_events.csv",
        "html_path": output_dir / "iteration_003_hypothesis_test_report.html",
        "json_path": output_dir / "iteration_003_hypothesis_test_summary.json",
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
        "<h1>QQQ Hypothesis Test Report - Iteration 003</h1>",
        "<p class='note'>Research-only diagnostic. Thresholds are deterministic training-window quantiles or fixed economic constants. No threshold optimization is performed.</p>",
        "<h2>Summary</h2>",
        summary.to_html(index=False, escape=True, border=0),
        "<h2>Yearly folds</h2>",
        folds.to_html(index=False, escape=True, border=0),
        "<h2>Event details</h2>",
        events.head(500).to_html(index=False, escape=True, border=0),
    ]
    doc = "<html><head><meta charset='utf-8'>" + css + "</head><body>" + "\n".join(body) + "</body></html>"
    path.write_text(doc, encoding="utf-8")
