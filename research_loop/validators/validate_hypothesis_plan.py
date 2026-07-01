#!/usr/bin/env python
"""Validate a FEATURE_TO_HYPOTHESIS_PLANNING output before testing can proceed."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PLAN = REPO_ROOT / "hypothesis_registry" / "fd_001_feature_to_hypothesis_plan.yaml"
DEFAULT_SNAPSHOT_DIR = REPO_ROOT / "feature_lab" / "FD_001_combined"
EXPECTED_PARENT_SNAPSHOT_ID = "FD_001_combined"
ROLE_COLUMN_CANDIDATES = ["feature_role", "classification", "role"]
REQUIRED_FIELDS = [
    "hypothesis_id",
    "parent_feature_snapshot_id",
    "source_feature_columns",
    "context_columns",
    "descriptive_columns",
    "diagnostics_columns",
    "parent_hypothesis_or_rewrite_queue_item",
    "economic_mechanism",
    "target",
    "trigger_rule",
    "expected_direction",
    "validation_plan",
    "sample_and_coverage_caveats",
    "why_not_duplicate_of_rejected_hypothesis",
    "dashboard_relevance",
    "not_to_do",
]
TARGET_REQUIRED_FIELDS = ["horizon_bd", "event_definition", "threshold"]
VALIDATION_PLAN_TERMS = [
    ("walk-forward", ["walk-forward", "walk forward", "walk_forward"]),
    ("purge or embargo", ["purge", "purging", "embargo"]),
    ("alert burden", ["alert burden", "alert_burden"]),
    ("base hit rate", ["base hit rate", "base_hit_rate"]),
    ("alert hit rate", ["alert hit rate", "alert_hit_rate"]),
    ("lift", ["lift"]),
    ("event coverage", ["event coverage", "event_coverage"]),
    ("false calm", ["false calm", "false_calm"]),
    ("fold stability", ["fold stability", "fold_stability"]),
    ("median lead time", ["median lead time", "median_lead_time"]),
]
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


def fail(message: str) -> int:
    print("HYPOTHESIS_PLAN_CHECK_FAILED")
    print(message)
    return 1


def repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def to_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{key} {to_text(item)}" for key, item in value.items())
    if isinstance(value, list):
        return " ".join(to_text(item) for item in value)
    return "" if value is None else str(value)


def normalize_columns(value: Any) -> list[str]:
    columns = as_list(value)
    return [str(column).strip() for column in columns if str(column).strip()]


def read_hypotheses(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        hypotheses = data
    elif isinstance(data, dict) and isinstance(data.get("hypotheses"), list):
        hypotheses = data["hypotheses"]
    else:
        raise ValueError("Plan YAML must be a top-level list or a mapping with a hypotheses list")
    if not all(isinstance(item, dict) for item in hypotheses):
        raise ValueError("Every hypothesis candidate must be a YAML mapping")
    return hypotheses


def role_column(inventory: pd.DataFrame) -> str:
    for candidate in ROLE_COLUMN_CANDIDATES:
        if candidate in inventory.columns:
            return candidate
    raise ValueError("Inventory must contain feature_role, classification, or role")


def load_columns_by_role(snapshot_dir: Path) -> dict[str, set[str]]:
    inventory_path = snapshot_dir / "experimental_feature_inventory.csv"
    if not inventory_path.exists():
        raise FileNotFoundError(inventory_path)
    inventory = pd.read_csv(inventory_path)
    if "column" not in inventory.columns:
        raise ValueError("experimental_feature_inventory.csv must contain column")
    roles = role_column(inventory)
    columns_by_role: dict[str, set[str]] = {
        "candidate_hypothesis_design": set(),
        "context_only": set(),
        "descriptive_only": set(),
        "episode_diagnostics_only": set(),
    }
    for _, row in inventory.iterrows():
        role = str(row.get(roles, "")).strip()
        column = str(row.get("column", "")).strip()
        if role in columns_by_role and column:
            columns_by_role[role].add(column)
    return columns_by_role


def missing_required_fields(hypothesis: dict[str, Any]) -> list[str]:
    return [field for field in REQUIRED_FIELDS if not non_empty(hypothesis.get(field))]


def validate_target(hypothesis_id: str, target: Any) -> str | None:
    if not isinstance(target, dict):
        return f"{hypothesis_id}: target must be a mapping"
    missing = [field for field in TARGET_REQUIRED_FIELDS if not non_empty(target.get(field))]
    if missing:
        return f"{hypothesis_id}: target missing required fields {missing}"
    return None


def trigger_rule_has_no_threshold_optimization(trigger_rule: Any) -> bool:
    if isinstance(trigger_rule, dict):
        for key, value in trigger_rule.items():
            normalized_key = str(key).lower().replace("-", "_").replace(" ", "_")
            if normalized_key in {"no_threshold_optimization", "thresholds_predeclared_not_optimized"}:
                if value is True or str(value).strip().lower() in {"true", "yes", "required"}:
                    return True
    text = to_text(trigger_rule).lower().replace("_", " ").replace("-", " ")
    return any(
        phrase in text
        for phrase in [
            "no threshold optimization",
            "no threshold optimisation",
            "thresholds predeclared",
            "thresholds are predeclared",
            "pre declared thresholds",
        ]
    )


def trigger_rule_has_deterministic_formula(trigger_rule: Any) -> bool:
    if isinstance(trigger_rule, dict):
        keys = {str(key).lower().replace("-", "_").replace(" ", "_") for key in trigger_rule}
        if {"formula", "deterministic_formula"} & keys:
            return True
    text = to_text(trigger_rule).lower().replace("_", " ").replace("-", " ")
    return "formula" in text and "deterministic" in text


def validate_trigger_rule(hypothesis_id: str, trigger_rule: Any) -> str | None:
    if not non_empty(trigger_rule):
        return f"{hypothesis_id}: trigger_rule must be non-empty"
    if not trigger_rule_has_deterministic_formula(trigger_rule):
        return f"{hypothesis_id}: trigger_rule must include a deterministic formula"
    if not trigger_rule_has_no_threshold_optimization(trigger_rule):
        return f"{hypothesis_id}: trigger_rule must explicitly ban threshold optimization"
    return None


def validate_validation_plan(hypothesis_id: str, validation_plan: Any) -> str | None:
    text = to_text(validation_plan).lower().replace("_", " ").replace("-", " ")
    missing = [
        label
        for label, variants in VALIDATION_PLAN_TERMS
        if not any(variant.replace("_", " ").replace("-", " ") in text for variant in variants)
    ]
    if missing:
        return f"{hypothesis_id}: validation_plan missing required terms {missing}"
    return None


def suspicious_referenced_columns(columns: list[str]) -> list[str]:
    return sorted(
        column
        for column in columns
        if any(token in column.lower() for token in SUSPICIOUS_NAME_TOKENS)
    )


def validate_column_subset(
    hypothesis_id: str,
    field: str,
    columns: list[str],
    allowed: set[str],
    allow_empty: bool = True,
) -> str | None:
    if not allow_empty and not columns:
        return f"{hypothesis_id}: {field} must be non-empty"
    unknown = sorted(set(columns) - allowed)
    if unknown:
        return f"{hypothesis_id}: {field} contains columns not allowed for that role: {unknown}"
    return None


def validate_hypothesis(
    hypothesis: dict[str, Any],
    columns_by_role: dict[str, set[str]],
) -> str | None:
    hypothesis_id = str(hypothesis.get("hypothesis_id", "<missing_hypothesis_id>"))
    missing = missing_required_fields(hypothesis)
    if missing:
        return f"{hypothesis_id}: missing required fields {missing}"
    if hypothesis.get("parent_feature_snapshot_id") != EXPECTED_PARENT_SNAPSHOT_ID:
        return f"{hypothesis_id}: parent_feature_snapshot_id must equal {EXPECTED_PARENT_SNAPSHOT_ID}"

    source_columns = normalize_columns(hypothesis.get("source_feature_columns"))
    context_columns = normalize_columns(hypothesis.get("context_columns"))
    descriptive_columns = normalize_columns(hypothesis.get("descriptive_columns"))
    diagnostics_columns = normalize_columns(hypothesis.get("diagnostics_columns"))

    checks = [
        validate_column_subset(
            hypothesis_id,
            "source_feature_columns",
            source_columns,
            columns_by_role["candidate_hypothesis_design"],
            allow_empty=False,
        ),
        validate_column_subset(
            hypothesis_id,
            "context_columns",
            context_columns,
            columns_by_role["context_only"],
        ),
        validate_column_subset(
            hypothesis_id,
            "descriptive_columns",
            descriptive_columns,
            columns_by_role["descriptive_only"],
        ),
        validate_column_subset(
            hypothesis_id,
            "diagnostics_columns",
            diagnostics_columns,
            columns_by_role["episode_diagnostics_only"],
        ),
    ]
    for check in checks:
        if check:
            return check

    forbidden_sources = sorted(
        set(source_columns)
        & (columns_by_role["context_only"] | columns_by_role["episode_diagnostics_only"])
    )
    if forbidden_sources:
        return f"{hypothesis_id}: source_feature_columns contains context or diagnostics-only columns: {forbidden_sources}"

    suspicious = suspicious_referenced_columns(
        source_columns + context_columns + descriptive_columns + diagnostics_columns
    )
    if suspicious:
        return f"{hypothesis_id}: referenced columns contain suspicious leakage tokens: {suspicious}"

    for check in [
        validate_target(hypothesis_id, hypothesis.get("target")),
        validate_trigger_rule(hypothesis_id, hypothesis.get("trigger_rule")),
        validate_validation_plan(hypothesis_id, hypothesis.get("validation_plan")),
    ]:
        if check:
            return check

    if not non_empty(hypothesis.get("why_not_duplicate_of_rejected_hypothesis")):
        return f"{hypothesis_id}: why_not_duplicate_of_rejected_hypothesis must be non-empty"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan-yaml", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--snapshot-dir", type=Path, default=DEFAULT_SNAPSHOT_DIR)
    parser.add_argument("--max-candidates", type=int, default=5)
    args = parser.parse_args()

    plan_path = repo_path(args.plan_yaml)
    snapshot_dir = repo_path(args.snapshot_dir)
    try:
        hypotheses = read_hypotheses(plan_path)
        columns_by_role = load_columns_by_role(snapshot_dir)
    except Exception as exc:
        return fail(str(exc))

    candidate_count = len(hypotheses)
    if candidate_count == 0:
        return fail("Candidate count is 0")
    if candidate_count > args.max_candidates:
        return fail(f"Candidate count {candidate_count} exceeds max-candidates {args.max_candidates}")

    seen_ids: set[str] = set()
    for hypothesis in hypotheses:
        hypothesis_id = str(hypothesis.get("hypothesis_id", "")).strip()
        if hypothesis_id in seen_ids:
            return fail(f"Duplicate hypothesis_id: {hypothesis_id}")
        seen_ids.add(hypothesis_id)
        error = validate_hypothesis(hypothesis, columns_by_role)
        if error:
            return fail(error)

    print("HYPOTHESIS_PLAN_CHECK_PASSED")
    print(f"candidate_count {candidate_count}")
    print("hypothesis_ids " + ", ".join(sorted(seen_ids)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
