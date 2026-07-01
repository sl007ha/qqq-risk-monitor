#!/usr/bin/env python
"""Run FD_001 Feature Lab Batch A v2 experimental feature construction.

This is a research-only QA patch for Batch A. It reads the exported daily wide
feature table and writes experimental artifacts only under this feature_lab
folder. It does not modify production feature construction or dashboard logic.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import yaml


BATCH_ID = "FD_001_batch_A_v2"
WINDOW = 252
MIN_PERIODS = 126

FREQ_008_INPUTS = [
    "qqq_vol_10d",
    "qqq_vol_20d",
    "qqq_vol_60d",
    "realized_vol_252d",
    "vix",
    "vxn",
    "vol_20d_vs_252d",
]
FREQ_007_INPUTS = [
    "vix9d_vs_vix",
    "vix3m_vs_vix",
    "vol_term_inversion_flag",
    "vvix_level",
    "skew_index",
    "panic_vol_flag",
]
FREQ_010_INPUTS = [
    "tlt_ret_20d",
    "ief_ret_20d",
    "tlt_ief_rel_3m",
    "xlu_vs_spy_3m",
    "xlp_vs_spy_3m",
    "ust10y_change_20d",
]

FEATURE_ROLES = {
    "freq_008_vol_disagreement_score": "candidate_hypothesis_design",
    "freq_008_vol_disagreement_score_pct": "candidate_hypothesis_design",
    "freq_008_vol_disagreement_rank_change_20d": "candidate_hypothesis_design",
    "freq_008_vol_disagreement_flag": "candidate_hypothesis_design",
    "freq_007_vol_term_daily_stress_count": "candidate_hypothesis_design",
    "freq_007_vol_term_stress_persistence_5d": "candidate_hypothesis_design",
    "freq_007_vol_term_stress_persistence_20d": "candidate_hypothesis_design",
    "freq_007_vol_term_persistent_stress_flag": "descriptive_only",
    "freq_010_safe_haven_confirmation_score": "context_only",
    "freq_010_rates_led_stress_flag": "context_only",
    "freq_010_riskoff_confirmation_flag": "context_only",
    "freq_010_safe_haven_rotation_state": "context_only_not_alert_ready",
}


def trailing_percentile(series: pd.Series, window: int = WINDOW, min_periods: int = MIN_PERIODS) -> pd.Series:
    """Percentile rank of the current value within a trailing window."""

    def rank_last(values: pd.Series) -> float:
        current = values.iloc[-1]
        valid = values.dropna()
        if pd.isna(current) or len(valid) < min_periods:
            return np.nan
        return float((valid <= current).mean())

    return series.rolling(window=window, min_periods=1).apply(rank_last, raw=False)


def safe_div(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denominator = denominator.replace(0, np.nan)
    return numerator / denominator


def require_columns(frame: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required input columns: {missing}")


def safe_bool_series(series: pd.Series) -> pd.Series:
    """Convert bool-like values while preserving unknowns as missing."""

    if pd.api.types.is_bool_dtype(series):
        return series.astype("boolean")
    if pd.api.types.is_numeric_dtype(series):
        values = series.map(lambda value: pd.NA if pd.isna(value) else bool(value))
        return values.astype("boolean")

    text = series.astype("string").str.strip().str.lower()
    values = text.map(
        {
            "true": True,
            "false": False,
            "1": True,
            "0": False,
            "yes": True,
            "no": False,
            "y": True,
            "n": False,
        }
    )
    return values.astype("boolean")


def bool_or_na(condition: pd.Series, available: pd.Series) -> pd.Series:
    out = pd.Series(np.nan, index=condition.index, dtype="float64")
    out.loc[available] = condition.loc[available].map({True: 1.0, False: 0.0})
    return out


def first_valid_date(frame: pd.DataFrame, column: str) -> str:
    valid = frame.loc[frame[column].notna(), "date"]
    if valid.empty:
        return ""
    return str(valid.iloc[0].date())


def last_valid_date(frame: pd.DataFrame, column: str) -> str:
    valid = frame.loc[frame[column].notna(), "date"]
    if valid.empty:
        return ""
    return str(valid.iloc[-1].date())


def latest_value(frame: pd.DataFrame, column: str):
    value = frame[column].iloc[-1]
    if pd.isna(value):
        return None
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        if math.isfinite(float(value)):
            return float(value)
        return None
    return str(value)


def feature_id_for_column(column: str) -> str:
    return f"FREQ_{column.split('_')[1]}" if column.startswith("freq_") else ""


def display_value(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value)


def build_freq_008(df: pd.DataFrame) -> pd.DataFrame:
    ratio_vxn_vix = safe_div(df["vxn"], df["vix"])
    raw = pd.DataFrame(index=df.index)
    raw["short_vs_medium"] = (safe_div(df["qqq_vol_10d"], df["qqq_vol_60d"]) - 1).abs()
    raw["short_vs_long"] = (safe_div(df["qqq_vol_20d"], df["realized_vol_252d"]) - 1).abs()
    raw["implied_cross_market"] = (ratio_vxn_vix - ratio_vxn_vix.rolling(WINDOW, min_periods=MIN_PERIODS).median()).abs()
    raw["existing_ratio_distance"] = (df["vol_20d_vs_252d"] - 1).abs()

    normalized = raw.apply(trailing_percentile)
    score = normalized.mean(axis=1, skipna=False)
    score_pct = trailing_percentile(score)
    rank_change = score_pct - score_pct.shift(20)
    flag = bool_or_na(score_pct >= 0.80, score_pct.notna())

    return pd.DataFrame(
        {
            "freq_008_vol_disagreement_score": score,
            "freq_008_vol_disagreement_score_pct": score_pct,
            "freq_008_vol_disagreement_rank_change_20d": rank_change,
            "freq_008_vol_disagreement_flag": flag,
        },
        index=df.index,
    )


def build_freq_007(df: pd.DataFrame) -> pd.DataFrame:
    vvix_pct = trailing_percentile(df["vvix_level"])
    skew_pct = trailing_percentile(df["skew_index"])

    vol_term_flag = safe_bool_series(df["vol_term_inversion_flag"])
    panic_flag = safe_bool_series(df["panic_vol_flag"])
    term_inputs_available = df[FREQ_007_INPUTS].notna().all(axis=1)
    bool_inputs_available = vol_term_flag.notna() & panic_flag.notna()
    percentile_inputs_available = vvix_pct.notna() & skew_pct.notna()
    all_available = term_inputs_available & bool_inputs_available & percentile_inputs_available

    front_vol_inverted_raw = (
        (df["vix9d_vs_vix"] > 0)
        | (df["vix3m_vs_vix"] < 0)
        | vol_term_flag.eq(True).fillna(False)
    )
    tail_demand_raw = (vvix_pct >= 0.80) | (skew_pct >= 0.80)
    panic_raw = panic_flag.eq(True).fillna(False)

    front_vol_inverted = bool_or_na(front_vol_inverted_raw, all_available)
    tail_demand = bool_or_na(tail_demand_raw, all_available)
    panic = bool_or_na(panic_raw, all_available)

    daily_stress_count = front_vol_inverted + tail_demand + panic
    daily_stress_count = daily_stress_count.where(all_available)
    stress_active = pd.Series(np.nan, index=df.index, dtype="float64")
    stress_active.loc[daily_stress_count.notna()] = (daily_stress_count.loc[daily_stress_count.notna()] > 0).map(
        {True: 1.0, False: 0.0}
    )

    persistence_5d = stress_active.rolling(5, min_periods=5).mean()
    persistence_20d = stress_active.rolling(20, min_periods=20).mean()
    persistent_flag = bool_or_na(persistence_20d >= 0.50, persistence_20d.notna())

    return pd.DataFrame(
        {
            "freq_007_vol_term_daily_stress_count": daily_stress_count,
            "freq_007_vol_term_stress_persistence_5d": persistence_5d,
            "freq_007_vol_term_stress_persistence_20d": persistence_20d,
            "freq_007_vol_term_persistent_stress_flag": persistent_flag,
        },
        index=df.index,
    )


def build_freq_010(df: pd.DataFrame) -> pd.DataFrame:
    available = df[FREQ_010_INPUTS].notna().all(axis=1)

    treasury_bid = (df["tlt_ret_20d"] > 0) | (df["ief_ret_20d"] > 0) | (df["tlt_ief_rel_3m"] > 0)
    defensive_bid = (df["xlu_vs_spy_3m"] > 0) | (df["xlp_vs_spy_3m"] > 0)
    rates_stress = df["ust10y_change_20d"] >= 0.25

    both_bids = treasury_bid & defensive_bid
    treasury_only = treasury_bid & ~defensive_bid
    defensive_only = defensive_bid & ~treasury_bid

    state = pd.Series(pd.NA, index=df.index, dtype="object")
    state.loc[available & rates_stress & defensive_bid] = "mixed_defensive_rates_stress"
    state.loc[available & rates_stress & ~defensive_bid] = "rates_led_stress"
    state.loc[available & ~rates_stress & both_bids] = "treasury_and_defensive_bid"
    state.loc[available & ~rates_stress & treasury_only] = "treasury_only_safe_haven"
    state.loc[available & ~rates_stress & defensive_only] = "defensive_only_rotation"
    state.loc[available & ~rates_stress & ~treasury_bid & ~defensive_bid] = "unconfirmed"

    score = (treasury_bid.map({True: 1, False: 0}) + defensive_bid.map({True: 1, False: 0})).where(available)
    rates_led_flag = bool_or_na(rates_stress & ~defensive_bid, available)
    riskoff_flag = bool_or_na(treasury_bid & defensive_bid, available)

    return pd.DataFrame(
        {
            "freq_010_safe_haven_confirmation_score": score,
            "freq_010_rates_led_stress_flag": rates_led_flag,
            "freq_010_riskoff_confirmation_flag": riskoff_flag,
            "freq_010_safe_haven_rotation_state": state,
        },
        index=df.index,
    )


def build_inventory(snapshot: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    rows = []
    total = len(snapshot)
    for column in feature_columns:
        non_null = int(snapshot[column].notna().sum())
        rows.append(
            {
                "feature_id": feature_id_for_column(column),
                "column": column,
                "feature_role": FEATURE_ROLES.get(column, "experimental_output"),
                "dtype": str(snapshot[column].dtype),
                "latest_value": latest_value(snapshot, column),
                "latest_non_null": bool(pd.notna(snapshot[column].iloc[-1])),
                "non_null_count": non_null,
                "coverage_pct": non_null / total if total else 0.0,
                "first_valid_date": first_valid_date(snapshot, column),
                "last_valid_date": last_valid_date(snapshot, column),
            }
        )
    return pd.DataFrame(rows)


def build_coverage_summary(df: pd.DataFrame, snapshot: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    latest_date = df["date"].max()
    recent_mask = df["date"] >= latest_date - pd.Timedelta(days=366)
    rows = []
    groups = {
        "FREQ_008": FREQ_008_INPUTS + [c for c in feature_columns if c.startswith("freq_008")],
        "FREQ_007": FREQ_007_INPUTS + [c for c in feature_columns if c.startswith("freq_007")],
        "FREQ_010": FREQ_010_INPUTS + [c for c in feature_columns if c.startswith("freq_010")],
    }
    combined = pd.concat([df, snapshot.drop(columns=["date"])], axis=1)
    for feature_id, columns in groups.items():
        for column in columns:
            kind = "experimental_output" if column.startswith("freq_") else "raw_input"
            series = combined[column]
            rows.append(
                {
                    "feature_id": feature_id,
                    "column": column,
                    "kind": kind,
                    "coverage_scope": "full_sample",
                    "coverage_pct": float(series.notna().mean()),
                    "recent_1y_coverage_pct": float(series.loc[recent_mask].notna().mean()),
                    "first_valid_date": first_valid_date(combined, column),
                    "last_valid_date": last_valid_date(combined, column),
                    "latest_value": latest_value(combined, column),
                    "latest_non_null": bool(pd.notna(series.iloc[-1])),
                }
            )

    vix9d_first_valid = df.loc[df["vix9d_vs_vix"].notna(), "date"].min()
    daily_col = "freq_007_vol_term_daily_stress_count"
    for label, mask in {
        "pre_vix9d_history": df["date"] < vix9d_first_valid,
        "post_vix9d_history": df["date"] >= vix9d_first_valid,
    }.items():
        series = snapshot.loc[mask, daily_col]
        rows.append(
            {
                "feature_id": "FREQ_007",
                "column": daily_col,
                "kind": "experimental_output",
                "coverage_scope": label,
                "coverage_pct": float(series.notna().mean()) if len(series) else 0.0,
                "recent_1y_coverage_pct": np.nan,
                "first_valid_date": first_valid_date(snapshot.loc[mask], daily_col) if len(series) else "",
                "last_valid_date": last_valid_date(snapshot.loc[mask], daily_col) if len(series) else "",
                "latest_value": None,
                "latest_non_null": False,
            }
        )
    return pd.DataFrame(rows)


def corr_pair(frame: pd.DataFrame, left: str, right: str) -> float | None:
    subset = frame[[left, right]].dropna()
    if len(subset) < 30:
        return None
    value = subset[left].corr(subset[right])
    if pd.isna(value):
        return None
    return float(value)


def true_overlap(left: pd.Series, right: pd.Series) -> float | None:
    valid = left.notna() & right.notna()
    if int(valid.sum()) == 0:
        return None
    left_true = safe_bool_series(left.loc[valid]).eq(True).fillna(False)
    right_true = safe_bool_series(right.loc[valid]).eq(True).fillna(False)
    if int(left_true.sum()) == 0:
        return 0.0
    return float((left_true & right_true).sum() / left_true.sum())


def write_validation_summary(
    output_path: Path,
    df: pd.DataFrame,
    snapshot: pd.DataFrame,
    inventory: pd.DataFrame,
    coverage: pd.DataFrame,
) -> None:
    combined = pd.concat([df, snapshot.drop(columns=["date"])], axis=1)
    vix9d_rows = coverage[
        (coverage["feature_id"] == "FREQ_007")
        & (coverage["column"] == "freq_007_vol_term_daily_stress_count")
        & (coverage["coverage_scope"].isin(["pre_vix9d_history", "post_vix9d_history"]))
    ]
    state_counts = snapshot["freq_010_safe_haven_rotation_state"].value_counts(dropna=False).to_dict()
    riskoff_by_state = (
        snapshot.loc[snapshot["freq_010_safe_haven_rotation_state"].notna()]
        .groupby("freq_010_safe_haven_rotation_state")["freq_010_riskoff_confirmation_flag"]
        .sum(min_count=1)
        .to_dict()
    )
    corr_008 = {
        "vol_20d_vs_252d": corr_pair(combined, "freq_008_vol_disagreement_score", "vol_20d_vs_252d"),
        "vix": corr_pair(combined, "freq_008_vol_disagreement_score", "vix"),
        "vxn": corr_pair(combined, "freq_008_vol_disagreement_score", "vxn"),
    }
    overlap_007 = {
        "panic_vol_flag": true_overlap(
            snapshot["freq_007_vol_term_persistent_stress_flag"],
            df["panic_vol_flag"],
        ),
        "vol_term_inversion_flag": true_overlap(
            snapshot["freq_007_vol_term_persistent_stress_flag"],
            df["vol_term_inversion_flag"],
        ),
    }

    lines = [
        "# FD_001 Batch A v2 Validation Summary",
        "",
        "## Run Evidence",
        "",
        f"- Generated at UTC: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"- Input rows: {len(df):,}",
        f"- Input latest date: {df['date'].max().date()}",
        f"- Experimental feature columns: {len(inventory)}",
        "- Input file: `outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv`",
        "- Output directory: `feature_lab/FD_001_batch_A_v2/`",
        "- Hypothesis tests run: no",
        "- Production files modified: no",
        "",
        "## QA Patch Compliance",
        "",
        "- FREQ_008 formula is unchanged from Batch A.",
        "- FREQ_007 availability now includes `vol_term_inversion_flag`.",
        "- FREQ_007 uses safe boolean conversion and does not use `Series.astype(bool)` on missing-capable data.",
        "- FREQ_007 early missing volatility-term history remains missing rather than non-stress.",
        "- FREQ_007 persistence scores remain continuous outputs; the persistent flag is descriptive only.",
        "- FREQ_010 uses the richer mutually exclusive context states requested for Batch A v2.",
        "- FREQ_010 true riskoff confirmation requires both treasury bid and defensive bid.",
        "- FREQ_010 state is context-only and not alert-ready.",
        "- Rolling percentile and median calculations are trailing-only.",
        "- No future target, future return, forward drawdown, event file, or hypothesis test output is read.",
        "",
        "## Latest Experimental Values",
        "",
        "| Column | Role | Latest value | First valid date | Coverage |",
        "|---|---|---:|---:|---:|",
    ]
    for _, row in inventory.iterrows():
        lines.append(
            f"| `{row['column']}` | {row['feature_role']} | {display_value(row['latest_value'])} | "
            f"{row['first_valid_date']} | {row['coverage_pct']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## FREQ_007 Pre/Post VIX9D Coverage",
            "",
            "| Scope | Coverage | First valid | Last valid |",
            "|---|---:|---:|---:|",
        ]
    )
    for _, row in vix9d_rows.iterrows():
        lines.append(
            f"| {row['coverage_scope']} | {row['coverage_pct']:.4f} | {row['first_valid_date']} | {row['last_valid_date']} |"
        )

    lines.extend(
        [
            "",
            "## Descriptive Overlap With Existing Columns",
            "",
            "These checks use same-date related columns only. No target labels are used.",
            "",
            "FREQ_008 score correlations:",
        ]
    )
    for column, value in corr_008.items():
        lines.append(f"- `{column}`: {value if value is not None else 'n/a'}")

    lines.append("")
    lines.append("FREQ_007 persistent-stress overlap when the descriptive flag is true:")
    for column, value in overlap_007.items():
        lines.append(f"- `{column}`: {value if value is not None else 'n/a'}")

    lines.extend(["", "FREQ_010 context state counts:"])
    for state, count in state_counts.items():
        lines.append(f"- `{state}`: {count}")

    lines.extend(["", "FREQ_010 true riskoff confirmations by state:"])
    for state, count in riskoff_by_state.items():
        lines.append(f"- `{state}`: {count}")

    lines.extend(
        [
            "",
            "## Validation Checks",
            "",
            "- Required input columns were present.",
            "- Experimental outputs were written only under `feature_lab/FD_001_batch_A_v2/`.",
            "- Latest values, first valid dates, coverage, and state distributions are recorded.",
            "- FREQ_007 pre-VIX9D output coverage is expected to remain zero because missing early history is preserved.",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest(output_path: Path, feature_columns: list[str], input_path: Path, output_dir: Path, repo_root: Path) -> None:
    manifest = {
        "version": 1,
        "batch_id": BATCH_ID,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "input_file": str(input_path.relative_to(repo_root)),
        "output_directory": str(output_dir.relative_to(repo_root)),
        "production_files_modified": False,
        "hypothesis_tests_run": False,
        "features": {
            "FREQ_008": {
                "title": "Regime-shift volatility disagreement",
                "output_columns": [c for c in feature_columns if c.startswith("freq_008")],
                "status": "candidate_hypothesis_design",
                "formula_note": "Formula unchanged from Batch A; rolling percentile-normalized components are averaged.",
            },
            "FREQ_007": {
                "title": "Volatility term-structure stress persistence",
                "output_columns": [c for c in feature_columns if c.startswith("freq_007")],
                "status": "candidate_hypothesis_design_with_descriptive_flag",
                "qa_patch_note": "Availability includes vol_term_inversion_flag; safe boolean conversion preserves missingness.",
                "descriptive_only_columns": ["freq_007_vol_term_persistent_stress_flag"],
            },
            "FREQ_010": {
                "title": "Safe-haven rotation confirmation",
                "output_columns": [c for c in feature_columns if c.startswith("freq_010")],
                "status": "context_only_not_alert_ready",
                "state_values": [
                    "treasury_and_defensive_bid",
                    "treasury_only_safe_haven",
                    "defensive_only_rotation",
                    "rates_led_stress",
                    "mixed_defensive_rates_stress",
                    "unconfirmed",
                ],
            },
        },
        "artifacts": [
            "experimental_feature_snapshot.csv",
            "experimental_feature_inventory.csv",
            "coverage_summary.csv",
            "validation_summary.md",
            "feature_snapshot_manifest.yaml",
        ],
    }
    output_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")


def main() -> None:
    output_dir = Path(__file__).resolve().parent
    repo_root = output_dir.parents[1]
    input_path = repo_root / "outputs" / "qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv"
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    input_columns = ["date"] + sorted(set(FREQ_008_INPUTS + FREQ_007_INPUTS + FREQ_010_INPUTS))
    df = pd.read_csv(input_path, usecols=input_columns)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    require_columns(df, FREQ_008_INPUTS + FREQ_007_INPUTS + FREQ_010_INPUTS)

    freq_008 = build_freq_008(df)
    freq_007 = build_freq_007(df)
    freq_010 = build_freq_010(df)

    snapshot = pd.concat([df[["date"]], freq_008, freq_007, freq_010], axis=1)
    feature_columns = [column for column in snapshot.columns if column != "date"]
    inventory = build_inventory(snapshot, feature_columns)
    coverage = build_coverage_summary(df, snapshot, feature_columns)

    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot.to_csv(output_dir / "experimental_feature_snapshot.csv", index=False)
    inventory.to_csv(output_dir / "experimental_feature_inventory.csv", index=False)
    coverage.to_csv(output_dir / "coverage_summary.csv", index=False)
    write_validation_summary(output_dir / "validation_summary.md", df, snapshot, inventory, coverage)
    write_manifest(output_dir / "feature_snapshot_manifest.yaml", feature_columns, input_path, output_dir, repo_root)

    print(f"wrote {len(feature_columns)} experimental columns")
    print(f"rows {len(snapshot)}")
    print(f"latest_date {snapshot['date'].max().date()}")
    print(f"output_dir {output_dir}")


if __name__ == "__main__":
    main()
