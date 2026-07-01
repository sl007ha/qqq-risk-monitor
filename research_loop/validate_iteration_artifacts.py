#!/usr/bin/env python
"""Validate required research-iteration artifacts.

Usage:
    python research_loop/validate_iteration_artifacts.py research_iterations/iteration_003
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_ROOT_FILES = [
    "prior_results_summary.md",
    "HYPOTHESES.md",
    "hypotheses.yaml",
    "analysis.md",
    "decision_log.md",
    "next_iteration_plan.md",
]

REQUIRED_TEST_PATTERNS = {
    "tests summary CSV": "*hypothesis_test_summary.csv",
    "tests daily signal CSV": "*hypothesis_test_daily_signals.csv",
    "tests events CSV": "*hypothesis_test_events.csv",
}


def validate_iteration(iteration_dir: Path) -> tuple[bool, list[str], list[str]]:
    missing: list[str] = []
    present: list[str] = []

    if not iteration_dir.exists():
        return False, [f"{iteration_dir}"], []
    if not iteration_dir.is_dir():
        return False, [f"{iteration_dir} is not a directory"], []

    for rel_path in REQUIRED_ROOT_FILES:
        path = iteration_dir / rel_path
        if path.is_file():
            present.append(rel_path)
        else:
            missing.append(rel_path)

    tests_dir = iteration_dir / "tests"
    if not tests_dir.is_dir():
        missing.append("tests/")
    else:
        present.append("tests/")
        for label, pattern in REQUIRED_TEST_PATTERNS.items():
            matches = sorted(tests_dir.glob(pattern))
            if matches:
                present.append(str(matches[0].relative_to(iteration_dir)))
            else:
                missing.append(f"{label} matching tests/{pattern}")

    return not missing, missing, present


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate required research iteration artifacts.")
    parser.add_argument("iteration_dir", help="Path to an iteration folder, for example research_iterations/iteration_003.")
    args = parser.parse_args()

    iteration_dir = Path(args.iteration_dir)
    ok, missing, present = validate_iteration(iteration_dir)

    if ok:
        print(f"PASS: {iteration_dir} contains all required artifacts.")
    else:
        print(f"FAIL: {iteration_dir} is missing required artifacts.")

    print("Present files:")
    for item in present:
        print(f"  - {item}")

    print("Missing files:")
    if missing:
        for item in missing:
            print(f"  - {item}")
    else:
        print("  - none")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
