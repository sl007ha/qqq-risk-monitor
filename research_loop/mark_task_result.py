#!/usr/bin/env python
"""Update the research task queue and research_state.yaml after a task result."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE = REPO_ROOT / "research_loop" / "research_state.yaml"
DEFAULT_QUEUE = REPO_ROOT / "research_loop" / "task_queue.yaml"
VALID_STATUSES = {"completed", "failed", "blocked", "needs_patch"}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def find_task(tasks: list[dict[str, Any]], task_id: str) -> dict[str, Any]:
    for task in tasks:
        if task.get("task_id") == task_id:
            return task
    raise ValueError(f"Task not found: {task_id}")


def completed_task_ids(tasks: list[dict[str, Any]]) -> set[str]:
    return {str(task.get("task_id")) for task in tasks if task.get("status") == "completed"}


def maybe_unblock_tasks(tasks: list[dict[str, Any]]) -> list[str]:
    completed = completed_task_ids(tasks)
    unblocked: list[str] = []
    for task in tasks:
        if task.get("status") != "blocked":
            continue
        dependencies = set(task.get("blocked_by") or [])
        if dependencies and dependencies <= completed:
            task["status"] = "ready"
            task["unblocked_at"] = now_utc()
            unblocked.append(str(task.get("task_id")))
    return unblocked


def append_next_task(tasks: list[dict[str, Any]], path: Path) -> str:
    data = read_yaml(path)
    task = data.get("task", data)
    if not isinstance(task, dict) or "task_id" not in task:
        raise ValueError("--append-next-task must point to a YAML mapping with task_id")
    existing_ids = {task_item.get("task_id") for task_item in tasks}
    if task["task_id"] in existing_ids:
        raise ValueError(f"Task already exists: {task['task_id']}")
    tasks.append(task)
    return str(task["task_id"])


def update_research_state(
    state: dict[str, Any],
    task_id: str,
    status: str,
    note: str | None,
    unblocked: list[str],
    appended_task_id: str | None,
) -> None:
    state["as_of"] = datetime.now(timezone.utc).date().isoformat()
    orchestrator = state.setdefault("orchestrator", {})
    history = orchestrator.setdefault("task_history", [])
    event = {
        "task_id": task_id,
        "status": status,
        "recorded_at_utc": now_utc(),
    }
    if note:
        event["note"] = note
    if unblocked:
        event["unblocked_tasks"] = unblocked
    if appended_task_id:
        event["appended_task_id"] = appended_task_id
    history.append(event)
    orchestrator["last_task_result"] = event
    if status in {"failed", "blocked", "needs_patch"}:
        orchestrator["attention_required"] = True
    elif status == "completed":
        orchestrator["attention_required"] = False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id")
    parser.add_argument("status", choices=sorted(VALID_STATUSES))
    parser.add_argument("--note", default=None)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--append-next-task", type=Path, default=None)
    args = parser.parse_args()

    queue = read_yaml(args.queue)
    state = read_yaml(args.state)
    tasks = queue.get("tasks", [])
    if not isinstance(tasks, list):
        raise ValueError("task_queue.yaml must contain a list at tasks")

    task = find_task(tasks, args.task_id)
    task["status"] = args.status
    task["last_result_at_utc"] = now_utc()
    if args.note:
        task["last_result_note"] = args.note

    appended_task_id = append_next_task(tasks, args.append_next_task) if args.append_next_task else None
    unblocked = maybe_unblock_tasks(tasks) if args.status == "completed" else []
    update_research_state(state, args.task_id, args.status, args.note, unblocked, appended_task_id)

    write_yaml(args.queue, queue)
    write_yaml(args.state, state)
    print(f"marked {args.task_id} {args.status}")
    if unblocked:
        print("unblocked " + ", ".join(unblocked))
    if appended_task_id:
        print(f"appended {appended_task_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
