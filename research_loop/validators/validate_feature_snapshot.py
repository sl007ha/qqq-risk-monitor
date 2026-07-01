#!/usr/bin/env python
"""Validate a feature_lab experimental feature snapshot directory."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from pandas.api.types import is_bool_dtype, is_numeric_dtype


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_FILES = [
    "experimental_feature_snapshot.csv",
    "experimental_feature_inventory.csv",
    "coverage_summary.csv",
    "validation_summary.md",
    "feature_snapshot_manifest.yaml",
]
ALLOWED_ROLES = {
    "candidate_hypothesis_design",
    "context_only",
    "descriptive_only",
    "episode_diagnostics_only",
}
SUSPICIOUS_NAME_TOKENS = [
    "future",
    "forward",
    "fwd",
    "target",
    "label",
    "outcome",
    "next_",
    "mdd_forward",
    "future_mdd",
    "forward_mdd",
    "ret_fwd",
    "return_fwd",
    "hit_",
]
NUMERIC_OR_BOOL_ROLES = {
    "candidate_hypothesis_design",
    "descriptive_only",
    "episode_diagnostics_only",
}
FALSE_MANIFEST_KEYS = [
    "hypothesis_tests_run",
    "production_files_modified",
    "production_outputs_written",
    "forbidden_inputs_used",
]


def fail(message: str, warnings: list[str] | None = None) -> int:
    print("FEATURE_SNAPSHOT_CHECK_FAILED")
    print(message)
    for warning in warnings or []:
        print(f"WARNING: {warning}")
    return 1


def role_column(inventory: pd.DataFrame) -> str | None:
    for candidate in ["feature_role", "classification", "role"]:
        if candidate in inventory.columns:
            return candidate
    return None


def read_manifest(path: Path) -> dict[str, Any] | None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return data
    return None


def parse_dates(snapshot: pd.DataFrame) -> tuple[pd.Series | None, str | None]:
    if "date" not in snapshot.columns:
        return None, "experimental_feature_snapshot.csv must contain date column"
    dates = pd.to_datetime(snapshot["date"], errors="coerce")
    if dates.isna().any():
        return None, "date column contains values that cannot parse as datetime"
    if snapshot["date"].duplicated().any():
        duplicates = snapshot.loc[snapshot["date"].duplicated(), "date"].head(5).tolist()
        return None, f"date column contains duplicate dates, examples: {duplicates}"
    if not dates.is_monotonic_increasing:
        return None, "date column must be sorted ascending"
    return dates, None


def is_numeric_or_bool_like(series: pd.Series) -> bool:
    if is_numeric_dtype(series) or is_bool_dtype(series):
        return True
    non_null = series.dropna()
    if non_null.empty:
        return False
    as_text = non_null.astype(str).str.strip().str.lower()
    bool_values = {"true", "false", "0", "1", "0.0", "1.0", "yes", "no"}
    if as_text.isin(bool_values).all():
        return True
    parsed = pd.to_numeric(non_null, errors="coerce")
    return bool(parsed.notna().all())


def validate_coverage_values(coverage: pd.DataFrame) -> str | None:
    candidate_columns = [
        column
        for column in coverage.columns
        if column.lower() in {"coverage", "coverage_pct", "non_null_pct", "recent_1y_coverage_pct"}
    ]
    for column in candidate_columns:
        values = pd.to_numeric(coverage[column], errors="coerce").dropna()
        if values.empty:
            continue
        if (values < 0).any():
            return f"{column} contains negative coverage values"
        max_value = float(values.max())
        min_value = float(values.min())
        if max_value <= 1.0:
            continue
        if min_value >= 0.0 and max_value <= 100.0:
            continue
        return f"{column} contains coverage values outside 0-1 or 0-100 range"
    return None


def validate_manifest(
    manifest: dict[str, Any] | None,
    snapshot_rows: int,
    strict_row_count: bool,
) -> tuple[str | None, list[str]]:
    warnings: list[str] = []
    if manifest is None:
        return "feature_snapshot_manifest.yaml must parse as a mapping", warnings
    for key in FALSE_MANIFEST_KEYS:
        if key in manifest and manifest.get(key) is not False:
            return f"manifest must set {key}: false", warnings
        if key in {"hypothesis_tests_run", "production_files_modified"} and manifest.get(key) is not False:
            return f"manifest must set {key}: false", warnings

    input_sources = manifest.get("input_sources") or []
    if isinstance(input_sources, str):
        input_sources = [input_sources]
    for source in input_sources:
        source_path = REPO_ROOT / str(source)
        if not source_path.exists():
            warnings.append(f"input source not found locally: {source}")

    original_source = manifest.get("original_feature_input_source")
    if original_source:
        source_path = REPO_ROOT / str(original_source)
        if source_path.exists():
            try:
                source_rows = len(pd.read_csv(source_path, usecols=[0]))
            except Exception as exc:  # pragma: no cover - defensive CLI guard
                warnings.append(f"could not read original_feature_input_source row count: {exc}")
            else:
                if source_rows != snapshot_rows:
                    message = (
                        f"original_feature_input_source row count {source_rows} "
                        f"does not match snapshot row count {snapshot_rows}"
                    )
                    if strict_row_count:
                        return message, warnings
                    warnings.append(message)
        else:
            warnings.append(f"original_feature_input_source not found locally: {original_source}")
    return None, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-dir", required=True, type=Path)
    parser.add_argument("--strict-row-count", action="store_true")
    args = parser.parse_args()

    snapshot_dir = args.snapshot_dir
    warnings: list[str] = []
    missing_files = [name for name in REQUIRED_FILES if not (snapshot_dir / name).exists()]
    if missing_files:
        return fail(f"Missing files in {snapshot_dir}: {missing_files}")

    snapshot = pd.read_csv(snapshot_dir / "experimental_feature_snapshot.csv")
    inventory = pd.read_csv(snapshot_dir / "experimental_feature_inventory.csv")
    coverage = pd.read_csv(snapshot_dir / "coverage_summary.csv")
    manifest = read_manifest(snapshot_dir / "feature_snapshot_manifest.yaml")
    validation_text = (snapshot_dir / "validation_summary.md").read_text(encoding="utf-8").strip()

    dates, date_error = parse_dates(snapshot)
    if date_error:
        return fail(date_error)

    feature_columns = [column for column in snapshot.columns if column != "date"]
    if not feature_columns:
        return fail("experimental_feature_snapshot.csv has no experimental feature columns")
    if "column" not in inventory.columns:
        return fail("experimental_feature_inventory.csv must contain column")
    if "column" not in coverage.columns:
        return fail("coverage_summary.csv must contain column")
    roles = role_column(inventory)
    if roles is None:
        return fail("experimental_feature_inventory.csv must contain feature_role, classification, or role")

    inventory_columns = inventory["column"].dropna().astype(str)
    duplicate_inventory = sorted(
        column for column, count in inventory_columns.value_counts().items() if count > 1
    )
    if duplicate_inventory:
        return fail(f"Inventory contains duplicate column rows: {duplicate_inventory}")

    inventory_by_column = inventory.set_index("column", drop=False)
    coverage_columns = set(coverage["column"].dropna().astype(str))
    duplicate_coverage = sorted(
        column for column, count in coverage["column"].dropna().astype(str).value_counts().items() if count > 1
    )
    if duplicate_coverage:
        return fail(f"Coverage summary contains duplicate column rows: {duplicate_coverage}")
    missing_inventory = sorted(set(feature_columns) - set(inventory_columns))
    missing_coverage = sorted(set(feature_columns) - coverage_columns)
    if missing_inventory:
        return fail(f"Feature columns missing from inventory: {missing_inventory}")
    if missing_coverage:
        return fail(f"Feature columns missing from coverage summary: {missing_coverage}")

    role_values = inventory_by_column.loc[feature_columns, roles].astype(str)
    invalid_roles = sorted(role_values.loc[~role_values.isin(ALLOWED_ROLES)].index.tolist())
    if invalid_roles:
        return fail(f"Feature columns with invalid roles: {invalid_roles}")

    null_feature_columns = [column for column in feature_columns if not snapshot[column].notna().any()]
    if null_feature_columns:
        return fail(f"Feature columns are entirely null: {null_feature_columns}")

    coverage_error = validate_coverage_values(coverage.loc[coverage["column"].isin(feature_columns)])
    if coverage_error:
        return fail(coverage_error)

    coverage_by_column = coverage.set_index("column", drop=False)
    coverage_value_columns = [
        column
        for column in coverage.columns
        if column.lower() in {"coverage", "coverage_pct", "non_null_pct"}
    ]
    for column in feature_columns:
        if coverage_value_columns:
            values = pd.to_numeric(coverage_by_column.loc[column, coverage_value_columns], errors="coerce")
            if values.notna().any() and float(values.max()) <= 0:
                return fail(f"Coverage is not greater than zero for {column}")
        elif not snapshot[column].notna().any():
            return fail(f"Coverage is not greater than zero for {column}")

    suspicious_columns = [
        column
        for column in feature_columns
        if any(token in column.lower() for token in SUSPICIOUS_NAME_TOKENS)
    ]
    if suspicious_columns:
        return fail(f"Feature columns contain suspicious target/leakage tokens: {suspicious_columns}")

    dtype_failures: list[str] = []
    for column in feature_columns:
        role = str(inventory_by_column.loc[column, roles])
        if role in NUMERIC_OR_BOOL_ROLES and not is_numeric_or_bool_like(snapshot[column]):
            dtype_failures.append(f"{column} ({role}, dtype={snapshot[column].dtype})")
    if dtype_failures:
        return fail(f"Feature columns have invalid dtype for role: {dtype_failures}")

    manifest_error, manifest_warnings = validate_manifest(manifest, len(snapshot), args.strict_row_count)
    warnings.extend(manifest_warnings)
    if manifest_error:
        return fail(manifest_error, warnings)
    if not validation_text:
        return fail("validation_summary.md is empty", warnings)

    role_counts = role_values.value_counts().to_dict()
    print("FEATURE_SNAPSHOT_CHECK_PASSED")
    print(f"snapshot_dir {snapshot_dir}")
    print(f"rows {len(snapshot)}")
    print(f"feature_columns {len(feature_columns)}")
    print(f"role_column {roles}")
    print(f"role_counts {role_counts}")
    print(f"latest_date {dates.max().date().isoformat() if dates is not None else 'unknown'}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
