#!/usr/bin/env python
"""Validate protected production files are absent from the committed PR diff."""
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


def normalize(path: str) -> str:
    return path.replace("\\", "/").strip()


def changed_files(base_ref: str) -> tuple[int, list[str], str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    files = [normalize(line) for line in proc.stdout.splitlines() if line.strip()]
    return proc.returncode, files, proc.stderr.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--protected", nargs="*", default=DEFAULT_PROTECTED)
    args = parser.parse_args()

    protected = {normalize(path) for path in args.protected}
    return_code, files, stderr = changed_files(args.base_ref)
    if return_code != 0:
        print("PROTECTED_PR_DIFF_CHECK_FAILED")
        print(f"Could not compute git diff against {args.base_ref!r}.")
        if stderr:
            print(stderr)
        return return_code or 1

    hits = sorted(path for path in files if path in protected)
    if hits:
        print("PROTECTED_PR_DIFF_CHECK_FAILED")
        print("Changed protected files:")
        for hit in hits:
            print(f"- {hit}")
        return 1

    print("PROTECTED_PR_DIFF_CHECK_PASSED")
    print(f"base_ref {args.base_ref}")
    print("protected_hits 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
