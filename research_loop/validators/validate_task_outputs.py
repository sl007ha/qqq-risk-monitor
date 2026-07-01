#!/usr/bin/env python
"""Validate that all declared outputs for a queued research task exist."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_QUEUE = REPO_ROOT / "research_loop" / "task_queue.yaml"
GLOB_CHARS = set("*?[]")


def read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def find_task(tasks: list[dict[str, Any]], task_id: str) -> dict[str, Any]:
    for task in tasks:
        if task.get("task_id") == task_id:
            return task
    raise ValueError(f"Task not found: {task_id}")


def output_exists(output: str) -> bool:
    if any(char in output for char in GLOB_CHARS):
        return bool(list(REPO_ROOT.glob(output)))
    return (REPO_ROOT / output).exists()


def declared_outputs(task: dict[str, Any]) -> list[str]:
    return [str(output).strip() for output in as_list(task.get("outputs")) if str(output).strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    args = parser.parse_args()

    try:
        queue = read_yaml(args.queue)
        tasks = queue.get("tasks", [])
        if not isinstance(tasks, list):
            raise ValueError("task_queue.yaml must contain a list at tasks")
        task = find_task(tasks, args.task_id)
    except Exception as exc:
        print("TASK_OUTPUT_CHECK_FAILED")
        print(str(exc))
        return 1

    outputs = declared_outputs(task)
    missing = [output for output in outputs if not output_exists(output)]
    if missing:
        print("TASK_OUTPUT_CHECK_FAILED")
        print(f"task_id {args.task_id}")
        print("missing_outputs")
        for output in missing:
            print(f"- {output}")
        return 1

    print("TASK_OUTPUT_CHECK_PASSED")
    print(f"task_id {args.task_id}")
    print(f"output_count {len(outputs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
