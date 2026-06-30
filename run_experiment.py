#!/usr/bin/env python
"""Autoresearch-compatible runner.

This project is currently in dashboard-port mode, not optimization mode. The
script exists so a future agent can call a stable runner while only modifying
qqq_autoresearch/candidate.py.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from qqq_autoresearch.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs", help="Directory for dashboard HTML and CSV outputs.")
    args = parser.parse_args()
    summary = run_pipeline(output_dir=Path(args.output_dir))
    summary["mode"] = "dashboard_port_no_optimization"
    summary["pass_fail"] = "PASS" if summary.get("dashboard_html") else "FAIL"
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
