#!/usr/bin/env python
"""Validate that protected production files are not changed in git status."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTECTED = [
    "qqq_autoresearch/features.py",
    "qqq_autoresearch/data_sources.py",
    "qqq_autoresearch/config.py",
    "qqq_autoresearch/pipeline.py",
    "qqq_autoresearch/render.py",
    "run_dashboard.py",
]


def porcelain_status() -> list[str]:
    output = subprocess.check_output(["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True)
    return output.splitlines()


def normalize(line: str) -> str:
    return line.replace("\\", "/").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protected", nargs="*", default=DEFAULT_PROTECTED)
    args = parser.parse_args()

    status_lines = porcelain_status()
    hits = []
    for line in status_lines:
        normalized = normalize(line)
        for protected in args.protected:
            if protected in normalized:
                hits.append(line)
                break
    if hits:
        print("PROTECTED_DIFF_CHECK_FAILED")
        for hit in hits:
            print(hit)
        return 1
    print("PROTECTED_DIFF_CHECK_PASSED")
    print(f"protected_hits 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
