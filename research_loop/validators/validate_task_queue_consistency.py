#!/usr/bin/env python
"""Validate research_loop/task_queue.yaml has coherent task state."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_QUEUE = REPO_ROOT / "research_loop" / "task_queue.yaml"


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


def output_exists(output: str) -> bool:
    if any(char in output for char in "*?[]"):
        return bool(list(REPO_ROOT.glob(output)))
    return (REPO_ROOT / output).exists()


def required_outputs(task: dict[str, Any]) -> list[str]:
    return [str(item) for item in as_list(task.get("outputs")) if str(item).strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    queue = read_yaml(args.queue)
    tasks = queue.get("tasks", [])
    if not isinstance(tasks, list):
        print("TASK_QUEUE_CONSISTENCY_CHECK_FAILED")
        print("task_queue.yaml must contain a list at tasks")
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    task_ids = [str(task.get("task_id")) for task in tasks]
    duplicate_ids = sorted(task_id for task_id, count in Counter(task_ids).items() if count > 1)
    if duplicate_ids:
        errors.append(f"Duplicate task_id values: {duplicate_ids}")

    by_id = {str(task.get("task_id")): task for task in tasks}
    completed = {task_id for task_id, task in by_id.items() if task.get("status") == "completed"}

    ready_by_priority: dict[Any, list[str]] = defaultdict(list)
    for task in tasks:
        task_id = str(task.get("task_id"))
        status = task.get("status")
        outputs = required_outputs(task)
        existing_outputs = [output for output in outputs if output_exists(output)]
        missing_outputs = [output for output in outputs if not output_exists(output)]

        if status == "ready":
            ready_by_priority[task.get("priority", 9999)].append(task_id)
            dependencies = set(str(item) for item in as_list(task.get("blocked_by")))
            missing_dependencies = sorted(dep for dep in dependencies if dep not in completed)
            if missing_dependencies:
                errors.append(f"{task_id} is ready but blocked_by is not completed: {missing_dependencies}")
            if outputs and len(existing_outputs) == len(outputs):
                errors.append(f"{task_id} is ready but all required outputs already exist")

        if status == "blocked":
            dependencies = set(str(item) for item in as_list(task.get("blocked_by")))
            unknown_dependencies = sorted(dep for dep in dependencies if dep not in by_id)
            if unknown_dependencies:
                errors.append(f"{task_id} is blocked by unknown task ids: {unknown_dependencies}")
            if dependencies and dependencies <= completed:
                errors.append(f"{task_id} is blocked even though all dependencies are completed")

        if status == "completed" and missing_outputs:
            errors.append(f"{task_id} is completed but required outputs are missing: {missing_outputs}")

    for priority, ids in sorted(ready_by_priority.items(), key=lambda item: str(item[0])):
        if len(ids) > 1:
            message = f"More than one ready task has priority {priority}: {ids}"
            if args.strict:
                errors.append(message)
            else:
                warnings.append(message)

    if errors:
        print("TASK_QUEUE_CONSISTENCY_CHECK_FAILED")
        for error in errors:
            print(f"- {error}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        return 1

    print("TASK_QUEUE_CONSISTENCY_CHECK_PASSED")
    print(f"task_count {len(tasks)}")
    print(f"ready_count {sum(1 for task in tasks if task.get('status') == 'ready')}")
    print(f"completed_count {sum(1 for task in tasks if task.get('status') == 'completed')}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
