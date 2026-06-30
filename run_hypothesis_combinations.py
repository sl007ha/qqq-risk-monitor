#!/usr/bin/env python
"""Run combination tests for H001/H002/H004 hypothesis alerts.

Run the standalone hypothesis tests first, then run this script.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from qqq_autoresearch.hypothesis_combinations import run_combination_tests
from qqq_autoresearch.hypothesis_tests import PREFIX


def main() -> None:
    parser = argparse.ArgumentParser(description="Run QQQ hypothesis combination diagnostics.")
    parser.add_argument("--output-dir", default="outputs", help="Dashboard output directory.")
    parser.add_argument("--hypothesis-test-dir", default="outputs/hypothesis_tests", help="Directory containing hypothesis_test_daily_signals.csv.")
    parser.add_argument("--test-output-dir", default="outputs/hypothesis_combinations", help="Where to write combination reports.")
    parser.add_argument("--data", default=None, help="Override daily wide feature CSV path.")
    parser.add_argument("--signals", default=None, help="Override standalone daily signals CSV path.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    data_path = Path(args.data) if args.data else output_dir / f"{PREFIX}_all_features_daily_wide.csv"
    signals_path = Path(args.signals) if args.signals else Path(args.hypothesis_test_dir) / "hypothesis_test_daily_signals.csv"
    summary = run_combination_tests(data_path=data_path, signals_path=signals_path, output_dir=Path(args.test_output_dir))
    print(json.dumps({k: v for k, v in summary.items() if k != "summary"}, indent=2, ensure_ascii=False))
    print("\nTop-line combination summary:")
    for row in summary["summary"]:
        if row["signal"].startswith("RISK_SCORE_EQ_") or row["target"] != "30BD_-8pct":
            continue
        print(
            f"{row['signal']} / {row['target']}: lift={row.get('base_rate_lift')}, "
            f"alert_burden={row.get('alert_burden')}, event_coverage={row.get('event_coverage')}"
        )


if __name__ == "__main__":
    main()
