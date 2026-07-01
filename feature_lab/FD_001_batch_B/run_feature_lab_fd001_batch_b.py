#!/usr/bin/env python
"""Run FD_001 Feature Lab Batch B experimental feature construction.

This script implements FREQ_003 and FREQ_004 as research-only experimental
features. It reads one exported feature table and writes artifacts only under
feature_lab/FD_001_batch_B.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import yaml


BATCH_ID = "FD_001_batch_B"
WINDOW = 252
MIN_PERIODS = 126

FREQ_003_INPUTS = [
    "R2_ACTIVE",
    "R2_STRESS_COUNT",
    "MMDI",
    "MMDI_10D_CHANGE",
    "mmdi_20d_change",
    "downside_vol_20d",
    "price_vs_ma50",
    "qqq_dd_20d",
]
FREQ_004_INPUTS = [
    "qqq_close",
    "qqq_dd_20d",
    "qqq_dd_60d",
    "rebound_from_trough_20d",
    "failed_reclaim_ma50",
    "failed_reclaim_ma200",
    "lower_high_flag",
    "lower_low_flag",
    "mmdi_low_after_high",
]

FREQ_003_COMPONENT_COLUMNS = [
    "mmdi_rising",
    "mmdi_elevated",
    "downside_vol_stress",
    "trend_damaged",
    "short_drawdown",
]
FREQ_004_PRESSURE_COLUMNS = [
    "failed_reclaim_ma50",
    "failed_reclaim_ma200",
    "lower_high_flag",
    "lower_low_flag",
    "mmdi_low_after_high",
]

FEATURE_ROLES = {
    "freq_003_quiet_state": "descriptive_only",
    "freq_003_false_calm_internal_deterioration_count": "candidate_hypothesis_design",
    "freq_003_false_calm_missing_component_count": "descriptive_only",
    "freq_003_false_calm_internal_deterioration_flag": "candidate_hypothesis_design",
    "freq_004_repair_episode_active": "episode_diagnostics_only",
    "freq_004_repair_failure_pressure_count": "episode_diagnostics_only",
    "freq_004_repair_episode_quality_score": "episode_diagnostics_only",
    "freq_004_repair_relapse_flag": "episode_diagnostics_only",
}


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


def condition_to_boolean(condition: pd.Series, available: pd.Series) -> pd.Series:
    out = pd.Series(pd.NA, index=condition.index, dtype="boolean")
    out.loc[available] = condition.loc[available].to_numpy(dtype=bool)
    return out


def boolean_or(*components: pd.Series) -> pd.Series:
    if not components:
        raise ValueError("At least one component is required.")
    index = components[0].index
    true_mask = pd.Series(False, index=index)
    known_mask = pd.Series(True, index=index)
    for component in components:
        true_mask = true_mask | component.eq(True).fillna(False)
        known_mask = known_mask & component.notna()

    out = pd.Series(pd.NA, index=index, dtype="boolean")
    out.loc[true_mask] = True
    out.loc[(~true_mask) & known_mask] = False
    return out


def boolean_to_float(series: pd.Series) -> pd.Series:
    out = pd.Series(np.nan, index=series.index, dtype="float64")
    out.loc[series.eq(True).fillna(False)] = 1.0
    out.loc[series.eq(False).fillna(False)] = 0.0
    return out


def true_count(components: pd.DataFrame) -> pd.Series:
    count = pd.Series(0, index=components.index, dtype="int64")
    for column in components.columns:
        count = count + components[column].eq(True).fillna(False).map({True: 1, False: 0})
    return count


def missing_count(components: pd.DataFrame) -> pd.Series:
    count = pd.Series(0, index=components.index, dtype="int64")
    for column in components.columns:
        count = count + components[column].isna().map({True: 1, False: 0})
    return count


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


def build_freq_003(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    r2_active = safe_bool_series(df["R2_ACTIVE"])
    quiet_available = r2_active.notna() & df["R2_STRESS_COUNT"].notna()
    quiet_condition = r2_active.eq(False).fillna(False) & (df["R2_STRESS_COUNT"] <= 1)
    quiet_state = condition_to_boolean(quiet_condition, quiet_available)

    mmdi_10d_up = condition_to_boolean(df["MMDI_10D_CHANGE"] > 0, df["MMDI_10D_CHANGE"].notna())
    mmdi_20d_up = condition_to_boolean(df["mmdi_20d_change"] > 0, df["mmdi_20d_change"].notna())
    mmdi_rising = boolean_or(mmdi_10d_up, mmdi_20d_up)
    mmdi_elevated = condition_to_boolean(df["MMDI"] >= 50, df["MMDI"].notna())

    downside_q75 = df["downside_vol_20d"].rolling(WINDOW, min_periods=MIN_PERIODS).quantile(0.75)
    downside_vol_stress = condition_to_boolean(
        df["downside_vol_20d"] >= downside_q75,
        df["downside_vol_20d"].notna() & downside_q75.notna(),
    )
    trend_damaged = condition_to_boolean(df["price_vs_ma50"] < 0, df["price_vs_ma50"].notna())
    short_drawdown = condition_to_boolean(df["qqq_dd_20d"] <= -0.03, df["qqq_dd_20d"].notna())

    components = pd.DataFrame(
        {
            "mmdi_rising": mmdi_rising,
            "mmdi_elevated": mmdi_elevated,
            "downside_vol_stress": downside_vol_stress,
            "trend_damaged": trend_damaged,
            "short_drawdown": short_drawdown,
        },
        index=df.index,
    )
    component_true_count = true_count(components)
    component_missing_count = missing_count(components)

    quiet_true = quiet_state.eq(True).fillna(False)
    quiet_false = quiet_state.eq(False).fillna(False)

    deterioration_count = pd.Series(np.nan, index=df.index, dtype="float64")
    deterioration_count.loc[quiet_false] = 0.0
    deterioration_count.loc[quiet_true] = component_true_count.loc[quiet_true].astype(float)

    missing_components = pd.Series(np.nan, index=df.index, dtype="float64")
    missing_components.loc[quiet_false] = 0.0
    missing_components.loc[quiet_true] = component_missing_count.loc[quiet_true].astype(float)

    deterioration_flag = pd.Series(np.nan, index=df.index, dtype="float64")
    deterioration_flag.loc[quiet_false] = 0.0
    quiet_count_available = quiet_true & deterioration_count.notna()
    deterioration_flag.loc[quiet_count_available] = (
        deterioration_count.loc[quiet_count_available] >= 3
    ).map({True: 1.0, False: 0.0})

    outputs = pd.DataFrame(
        {
            "freq_003_quiet_state": boolean_to_float(quiet_state),
            "freq_003_false_calm_internal_deterioration_count": deterioration_count,
            "freq_003_false_calm_missing_component_count": missing_components,
            "freq_003_false_calm_internal_deterioration_flag": deterioration_flag,
        },
        index=df.index,
    )
    diagnostics = pd.concat([components, downside_q75.rename("downside_vol_20d_trailing_252d_q75")], axis=1)
    return outputs, diagnostics


def build_freq_004(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    active_available = df["qqq_dd_60d"].notna() & df["rebound_from_trough_20d"].notna()
    episode_active = condition_to_boolean(
        (df["qqq_dd_60d"] <= -0.05) & (df["rebound_from_trough_20d"] >= 0.03),
        active_available,
    )

    pressure_components = pd.DataFrame(
        {column: safe_bool_series(df[column]) for column in FREQ_004_PRESSURE_COLUMNS},
        index=df.index,
    )
    pressure_true_count = true_count(pressure_components)
    pressure_missing_count = missing_count(pressure_components)
    active_true = episode_active.eq(True).fillna(False)
    active_false = episode_active.eq(False).fillna(False)
    pressure_known = pressure_missing_count == 0

    pressure_count = pd.Series(np.nan, index=df.index, dtype="float64")
    pressure_count.loc[active_false] = 0.0
    pressure_count.loc[active_true & pressure_known] = pressure_true_count.loc[active_true & pressure_known].astype(float)

    quality_score = pd.Series(np.nan, index=df.index, dtype="float64")
    quality_ready = active_true & pressure_count.notna() & df["rebound_from_trough_20d"].notna()
    quality_score.loc[quality_ready] = df.loc[quality_ready, "rebound_from_trough_20d"] - (
        0.02 * pressure_count.loc[quality_ready]
    )

    relapse_flag = pd.Series(np.nan, index=df.index, dtype="float64")
    relapse_flag.loc[active_false] = 0.0
    relapse_flag.loc[active_true & pressure_count.notna()] = (pressure_count.loc[active_true & pressure_count.notna()] >= 2).map(
        {True: 1.0, False: 0.0}
    )

    outputs = pd.DataFrame(
        {
            "freq_004_repair_episode_active": boolean_to_float(episode_active),
            "freq_004_repair_failure_pressure_count": pressure_count,
            "freq_004_repair_episode_quality_score": quality_score,
            "freq_004_repair_relapse_flag": relapse_flag,
        },
        index=df.index,
    )
    diagnostics = pd.concat(
        [
            pressure_components,
            pressure_missing_count.rename("repair_pressure_missing_component_count"),
        ],
        axis=1,
    )
    return outputs, diagnostics


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
        "FREQ_003": FREQ_003_INPUTS + [c for c in feature_columns if c.startswith("freq_003")],
        "FREQ_004": FREQ_004_INPUTS + [c for c in feature_columns if c.startswith("freq_004")],
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
    return pd.DataFrame(rows)


def distribution(series: pd.Series) -> dict[str, int]:
    counts = series.value_counts(dropna=False).sort_index().to_dict()
    return {str(key): int(value) for key, value in counts.items()}


def active_days_by_year(dates: pd.Series, active: pd.Series) -> dict[int, int]:
    frame = pd.DataFrame({"date": dates, "active": active})
    frame = frame.loc[frame["active"] == 1.0].copy()
    if frame.empty:
        return {}
    frame["year"] = frame["date"].dt.year
    return {int(year): int(count) for year, count in frame.groupby("year").size().to_dict().items()}


def write_validation_summary(
    output_path: Path,
    df: pd.DataFrame,
    snapshot: pd.DataFrame,
    inventory: pd.DataFrame,
    freq_003_diagnostics: pd.DataFrame,
    freq_004_diagnostics: pd.DataFrame,
) -> None:
    quiet_dist = distribution(snapshot["freq_003_quiet_state"])
    deterioration_count_dist = distribution(snapshot["freq_003_false_calm_internal_deterioration_count"])
    missing_count_dist = distribution(snapshot["freq_003_false_calm_missing_component_count"])
    flag_dist = distribution(snapshot["freq_003_false_calm_internal_deterioration_flag"])
    repair_active_dist = distribution(snapshot["freq_004_repair_episode_active"])
    pressure_count_dist = distribution(snapshot["freq_004_repair_failure_pressure_count"])
    relapse_dist = distribution(snapshot["freq_004_repair_relapse_flag"])
    active_years = active_days_by_year(df["date"], snapshot["freq_004_repair_episode_active"])

    lines = [
        "# FD_001 Batch B Validation Summary",
        "",
        "## Run Evidence",
        "",
        f"- Generated at UTC: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"- Input rows: {len(df):,}",
        f"- Input latest date: {df['date'].max().date()}",
        f"- Experimental feature columns: {len(inventory)}",
        "- Input file: `outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv`",
        "- Output directory: `feature_lab/FD_001_batch_B/`",
        "- Hypothesis tests run: no",
        "- Production files modified: no",
        "",
        "## Formula Compliance",
        "",
        "- FREQ_003 quiet state uses `(R2_ACTIVE == false) AND (R2_STRESS_COUNT <= 1)`.",
        "- FREQ_003 downside volatility stress uses trailing 252-day Q75 of `downside_vol_20d`.",
        "- FREQ_003 counts only inside quiet state.",
        "- FREQ_003 missing components are counted separately and do not become calm or stress.",
        "- FREQ_003 flag is computed as `count >= 3`; missing components are tracked separately and are not added as calm or stress.",
        "- FREQ_004 repair episode active uses only trailing `qqq_dd_60d` and `rebound_from_trough_20d`.",
        "- FREQ_004 is episode diagnostics only.",
        "- No future trough, future drawdown, forward return, target label, event file, or hypothesis test output is read.",
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

    lines.extend(["", "## FREQ_003 Distributions", "", "Quiet state:"])
    for key, value in quiet_dist.items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    lines.append("Internal deterioration count:")
    for key, value in deterioration_count_dist.items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    lines.append("Missing component count:")
    for key, value in missing_count_dist.items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    lines.append("False-calm deterioration flag:")
    for key, value in flag_dist.items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(["", "FREQ_003 component missingness:"])
    for column in FREQ_003_COMPONENT_COLUMNS:
        lines.append(f"- `{column}` missing: {int(freq_003_diagnostics[column].isna().sum())}")

    lines.extend(["", "## FREQ_004 Distributions", "", "Repair episode active:"])
    for key, value in repair_active_dist.items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    lines.append("Repair pressure count:")
    for key, value in pressure_count_dist.items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    lines.append("Repair relapse flag:")
    for key, value in relapse_dist.items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    lines.append("Active repair days by year:")
    for year, value in active_years.items():
        lines.append(f"- `{year}`: {value}")

    lines.extend(["", "FREQ_004 pressure component missingness:"])
    for column in FREQ_004_PRESSURE_COLUMNS:
        lines.append(f"- `{column}` missing: {int(freq_004_diagnostics[column].isna().sum())}")

    lines.extend(
        [
            "",
            "## Validation Checks",
            "",
            "- Required input columns were present.",
            "- Experimental outputs were written only under `feature_lab/FD_001_batch_B/`.",
            "- Latest values, first valid dates, coverage, and count distributions are recorded.",
            "- All rolling quantiles are trailing-only.",
            "- No production dashboard output file is written.",
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
            "FREQ_003": {
                "title": "False-calm internal deterioration count",
                "output_columns": [c for c in feature_columns if c.startswith("freq_003")],
                "status": "candidate_hypothesis_design",
                "missing_policy": "Missing components are counted separately; non-flag outcomes remain missing when missing components could change the result.",
            },
            "FREQ_004": {
                "title": "Repair episode quality score",
                "output_columns": [c for c in feature_columns if c.startswith("freq_004")],
            "status": "episode_diagnostics_only",
                "leakage_mitigation": "Episode active is based only on trailing 60-day drawdown and trailing 20-day rebound.",
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

    input_columns = ["date"] + sorted(set(FREQ_003_INPUTS + FREQ_004_INPUTS))
    df = pd.read_csv(input_path, usecols=input_columns)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    require_columns(df, FREQ_003_INPUTS + FREQ_004_INPUTS)

    freq_003, freq_003_diagnostics = build_freq_003(df)
    freq_004, freq_004_diagnostics = build_freq_004(df)

    snapshot = pd.concat([df[["date"]], freq_003, freq_004], axis=1)
    feature_columns = [column for column in snapshot.columns if column != "date"]
    inventory = build_inventory(snapshot, feature_columns)
    coverage = build_coverage_summary(df, snapshot, feature_columns)

    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot.to_csv(output_dir / "experimental_feature_snapshot.csv", index=False)
    inventory.to_csv(output_dir / "experimental_feature_inventory.csv", index=False)
    coverage.to_csv(output_dir / "coverage_summary.csv", index=False)
    write_validation_summary(
        output_dir / "validation_summary.md",
        df,
        snapshot,
        inventory,
        freq_003_diagnostics,
        freq_004_diagnostics,
    )
    write_manifest(output_dir / "feature_snapshot_manifest.yaml", feature_columns, input_path, output_dir, repo_root)

    print(f"wrote {len(feature_columns)} experimental columns")
    print(f"rows {len(snapshot)}")
    print(f"latest_date {snapshot['date'].max().date()}")
    print(f"output_dir {output_dir}")


if __name__ == "__main__":
    main()
