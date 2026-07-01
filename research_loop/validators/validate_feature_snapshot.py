#!/usr/bin/env python
"""Validate a feature_lab experimental feature snapshot directory."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml


REQUIRED_FILES = [
    "experimental_feature_snapshot.csv",
    "experimental_feature_inventory.csv",
    "coverage_summary.csv",
    "validation_summary.md",
    "feature_snapshot_manifest.yaml",
]


def fail(message: str) -> int:
    print("FEATURE_SNAPSHOT_CHECK_FAILED")
    print(message)
    return 1


def role_column(inventory: pd.DataFrame) -> str | None:
    for candidate in ["feature_role", "classification", "role"]:
        if candidate in inventory.columns:
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-dir", required=True, type=Path)
    args = parser.parse_args()

    snapshot_dir = args.snapshot_dir
    missing_files = [name for name in REQUIRED_FILES if not (snapshot_dir / name).exists()]
    if missing_files:
        return fail(f"Missing files in {snapshot_dir}: {missing_files}")

    snapshot = pd.read_csv(snapshot_dir / "experimental_feature_snapshot.csv")
    inventory = pd.read_csv(snapshot_dir / "experimental_feature_inventory.csv")
    coverage = pd.read_csv(snapshot_dir / "coverage_summary.csv")
    manifest = yaml.safe_load((snapshot_dir / "feature_snapshot_manifest.yaml").read_text(encoding="utf-8"))
    validation_text = (snapshot_dir / "validation_summary.md").read_text(encoding="utf-8").strip()

    if "date" not in snapshot.columns:
        return fail("experimental_feature_snapshot.csv must contain date column")
    feature_columns = [column for column in snapshot.columns if column != "date"]
    if not feature_columns:
        return fail("experimental_feature_snapshot.csv has no experimental feature columns")
    if "column" not in inventory.columns:
        return fail("experimental_feature_inventory.csv must contain column")
    roles = role_column(inventory)
    if roles is None:
        return fail("experimental_feature_inventory.csv must contain feature_role, classification, or role")

    inventory_columns = set(inventory["column"].dropna().astype(str))
    coverage_columns = set(coverage["column"].dropna().astype(str)) if "column" in coverage.columns else set()
    missing_inventory = sorted(set(feature_columns) - inventory_columns)
    missing_roles = sorted(inventory.loc[inventory["column"].isin(feature_columns) & inventory[roles].isna(), "column"].tolist())
    missing_coverage = sorted(set(feature_columns) - coverage_columns)
    if missing_inventory:
        return fail(f"Feature columns missing from inventory: {missing_inventory}")
    if missing_roles:
        return fail(f"Feature columns missing roles: {missing_roles}")
    if missing_coverage:
        return fail(f"Feature columns missing from coverage summary: {missing_coverage}")
    if not isinstance(manifest, dict):
        return fail("feature_snapshot_manifest.yaml must parse as a mapping")
    if manifest.get("hypothesis_tests_run") is not False:
        return fail("manifest must set hypothesis_tests_run: false")
    if manifest.get("production_files_modified") is not False:
        return fail("manifest must set production_files_modified: false")
    if not validation_text:
        return fail("validation_summary.md is empty")

    print("FEATURE_SNAPSHOT_CHECK_PASSED")
    print(f"snapshot_dir {snapshot_dir}")
    print(f"rows {len(snapshot)}")
    print(f"feature_columns {len(feature_columns)}")
    print(f"role_column {roles}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
