#!/usr/bin/env python
"""Run all Codex-draft QQQ hypothesis tests.

Usage:
    python run_hypothesis_tests.py --output-dir outputs --hypotheses hypotheses/hypotheses_codex_draft.yaml
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from qqq_autoresearch.hypothesis_tests import PREFIX, run_tests


def main() -> None:
    parser = argparse.ArgumentParser(description="Run QQQ hypothesis diagnostics.")
    parser.add_argument("--output-dir", default="outputs", help="Directory containing dashboard feature outputs.")
    parser.add_argument("--hypotheses", default="hypotheses/hypotheses_codex_draft.yaml", help="Hypothesis YAML/JSON file. The runner currently implements H001-H005.")
    parser.add_argument("--data", default=None, help="Override daily wide feature CSV path.")
    parser.add_argument("--test-output-dir", default="outputs/hypothesis_tests", help="Where to write hypothesis test reports.")
    parser.add_argument("--min-train-years", type=int, default=8, help="Minimum expanding-window training history before a yearly test fold.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    data_path = Path(args.data) if args.data else output_dir / f"{PREFIX}_all_features_daily_wide.csv"
    hyp_path = Path(args.hypotheses) if args.hypotheses else None
    summary = run_tests(
        data_path=data_path,
        hypotheses_path=hyp_path,
        output_dir=Path(args.test_output_dir),
        min_train_years=args.min_train_years,
    )
    print(json.dumps({k: v for k, v in summary.items() if k != "summary"}, indent=2, ensure_ascii=False))
    print("\nTop-line summary:")
    for row in summary["summary"]:
        print(
            f"{row['hypothesis_id']}: lift={row.get('base_rate_lift')}, "
            f"alert_burden={row.get('alert_burden')}, event_coverage={row.get('event_coverage')}"
        )


if __name__ == "__main__":
    main()
