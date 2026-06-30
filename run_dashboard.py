#!/usr/bin/env python
"""Run the full local QQQ Risk Monitor dashboard pipeline.

Usage:
    python run_dashboard.py --output-dir outputs
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
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nDashboard HTML written to: {summary['dashboard_html']}")


if __name__ == "__main__":
    main()
