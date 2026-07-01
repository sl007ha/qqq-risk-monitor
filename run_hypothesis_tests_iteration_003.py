#!/usr/bin/env python
"""Run QQQ Risk Monitor iteration 003 research-only hypothesis tests.

Usage:
    python run_hypothesis_tests_iteration_003.py --output-dir outputs --test-output-dir research_iterations/iteration_003/tests
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from qqq_autoresearch.hypothesis_tests_iteration_003 import PREFIX, run_tests


def main() -> None:
    parser = argparse.ArgumentParser(description="Run iteration 003 QQQ hypothesis diagnostics.")
    parser.add_argument("--output-dir", default="outputs", help="Directory containing dashboard feature outputs.")
    parser.add_argument(
        "--hypotheses",
        default="research_iterations/iteration_003/hypotheses.yaml",
        help="Iteration 003 hypothesis YAML file.",
    )
    parser.add_argument("--data", default=None, help="Override daily wide feature CSV path.")
    parser.add_argument(
        "--test-output-dir",
        default="research_iterations/iteration_003/tests",
        help="Where to write iteration 003 test reports.",
    )
    parser.add_argument("--min-train-years", type=int, default=8, help="Minimum expanding-window training history before a yearly test fold.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    data_path = Path(args.data) if args.data else output_dir / f"{PREFIX}_all_features_daily_wide.csv"
    summary = run_tests(
        data_path=data_path,
        hypotheses_path=Path(args.hypotheses),
        output_dir=Path(args.test_output_dir),
        min_train_years=args.min_train_years,
    )
    printable = {k: v for k, v in summary.items() if k != "summary"}
    print(json.dumps(printable, indent=2, ensure_ascii=False))
    print("\nIteration 003 top-line summary:")
    for row in summary["summary"]:
        print(
            f"{row['hypothesis_id']}: lift={row.get('base_rate_lift')}, "
            f"alert_burden={row.get('alert_burden')}, "
            f"event_coverage={row.get('event_coverage')}, "
            f"positive_lift_folds={row.get('positive_lift_folds')}/{row.get('folds_total')}, "
            f"median_lead_time_bd={row.get('median_lead_time_bd')}"
        )


if __name__ == "__main__":
    main()
