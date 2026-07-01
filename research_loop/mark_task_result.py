#!/usr/bin/env python
"""Update the research task queue and research_state.yaml after a task result."""
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE = REPO_ROOT / "research_loop" / "research_state.yaml"
DEFAULT_QUEUE = REPO_ROOT / "research_loop" / "task_queue.yaml"
DEFAULT_REPORT_DIR = REPO_ROOT / "research_loop" / "task_results"
VALID_STATUSES = {"completed", "failed", "blocked", "needs_patch"}
GLOB_CHARS = set("*?[]")


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


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def declared_outputs(task: dict[str, Any]) -> list[str]:
    return [str(output).strip() for output in as_list(task.get("outputs")) if str(output).strip()]


def output_exists(output: str) -> bool:
    if any(char in output for char in GLOB_CHARS):
        return bool(list(REPO_ROOT.glob(output)))
    return (REPO_ROOT / output).exists()


def build_output_check_result(task: dict[str, Any]) -> dict[str, Any]:
    task_id = str(task.get("task_id"))
    outputs = declared_outputs(task)
    missing = [output for output in outputs if not output_exists(output)]
    if missing:
        stdout_lines = [
            "TASK_OUTPUT_CHECK_FAILED",
            f"task_id {task_id}",
            "missing_outputs",
            *[f"- {output}" for output in missing],
        ]
        return {
            "command": f"declared task output check for {task_id}",
            "argv": ["internal_output_check", "--task-id", task_id],
            "return_code": 1,
            "stdout": "\n".join(stdout_lines) + "\n",
            "stderr": "",
            "passed": False,
            "missing_outputs": missing,
            "output_count": len(outputs),
        }
    stdout = f"TASK_OUTPUT_CHECK_PASSED\ntask_id {task_id}\noutput_count {len(outputs)}\n"
    return {
        "command": f"declared task output check for {task_id}",
        "argv": ["internal_output_check", "--task-id", task_id],
        "return_code": 0,
        "stdout": stdout,
        "stderr": "",
        "passed": True,
        "missing_outputs": [],
        "output_count": len(outputs),
    }


def normalize_validator_command(command: str, base_ref: str) -> list[str]:
    parts = shlex.split(command)
    if not parts:
        raise ValueError("Empty validator command")
    script = parts[0].replace("\\", "/")
    if script.endswith(".py"):
        parts = [sys.executable, *parts]
    if script.endswith("validate_no_protected_pr_diff.py") and "--base-ref" not in parts:
        parts.extend(["--base-ref", base_ref])
    return parts


def run_validators(
    task: dict[str, Any],
    base_ref: str,
    report_dir: Path,
    include_output_check: bool = False,
) -> tuple[bool, Path, Path]:
    validators = [str(item) for item in task.get("validators") or []]
    task_id = str(task.get("task_id"))
    task_report_dir = report_dir / task_id
    task_report_dir.mkdir(parents=True, exist_ok=True)
    started_at = now_utc()
    results: list[dict[str, Any]] = []

    for command in validators:
        argv = normalize_validator_command(command, base_ref)
        proc = subprocess.run(
            argv,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        results.append(
            {
                "command": command,
                "argv": argv,
                "return_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "passed": proc.returncode == 0,
            }
        )

    if include_output_check:
        results.append(build_output_check_result(task))

    all_passed = all(result["passed"] for result in results)
    report = {
        "task_id": task_id,
        "base_ref": base_ref,
        "started_at_utc": started_at,
        "finished_at_utc": now_utc(),
        "validator_count": len(results),
        "all_passed": all_passed,
        "results": results,
    }
    yaml_path = task_report_dir / "validator_report.yaml"
    md_path = task_report_dir / "validator_report.md"
    yaml_path.write_text(yaml.safe_dump(report, sort_keys=False), encoding="utf-8")
    md_path.write_text(render_validator_markdown(report), encoding="utf-8")
    return all_passed, yaml_path, md_path


def render_validator_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Validator Report: {report['task_id']}",
        "",
        f"- Base ref: `{report['base_ref']}`",
        f"- Started UTC: {report['started_at_utc']}",
        f"- Finished UTC: {report['finished_at_utc']}",
        f"- Validator count: {report['validator_count']}",
        f"- All passed: {str(report['all_passed']).lower()}",
        "",
    ]
    for index, result in enumerate(report["results"], start=1):
        lines.extend(
            [
                f"## {index}. `{result['command']}`",
                "",
                f"- Return code: {result['return_code']}",
                f"- Passed: {str(result['passed']).lower()}",
                "",
                "### stdout",
                "",
                "```text",
                result["stdout"].rstrip(),
                "```",
                "",
                "### stderr",
                "",
                "```text",
                result["stderr"].rstrip(),
                "```",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def update_research_state(
    state: dict[str, Any],
    task_id: str,
    status: str,
    note: str | None,
    unblocked: list[str],
    appended_task_id: str | None,
    validator_report: Path | None,
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
    if validator_report:
        event["validator_report"] = display_path(validator_report)
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
    parser.add_argument("--run-validators", action="store_true")
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--validator-report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    args = parser.parse_args()

    queue = read_yaml(args.queue)
    state = read_yaml(args.state)
    tasks = queue.get("tasks", [])
    if not isinstance(tasks, list):
        raise ValueError("task_queue.yaml must contain a list at tasks")

    task = find_task(tasks, args.task_id)
    effective_status = args.status
    validator_report: Path | None = None
    validator_report_md: Path | None = None

    if args.status == "completed" and args.run_validators:
        validators_passed, validator_report, validator_report_md = run_validators(
            task,
            args.base_ref,
            repo_path(args.validator_report_dir),
            include_output_check=True,
        )
        if not validators_passed:
            effective_status = "needs_patch"
            args.note = (
                (args.note + " " if args.note else "")
                + "Validator or output failure blocked completion."
            )
    elif args.status == "completed":
        print("WARNING: marking completed without --run-validators; validator pass is not implied.")

    task["status"] = effective_status
    task["last_result_at_utc"] = now_utc()
    if args.note:
        task["last_result_note"] = args.note
    if validator_report:
        task["last_validator_report"] = display_path(validator_report)
    if validator_report_md:
        task["last_validator_report_md"] = display_path(validator_report_md)

    appended_task_id = None
    if args.append_next_task:
        if effective_status == "completed":
            appended_task_id = append_next_task(tasks, args.append_next_task)
        else:
            print("WARNING: --append-next-task ignored because task did not complete.")

    unblocked = maybe_unblock_tasks(tasks) if effective_status == "completed" else []
    update_research_state(
        state,
        args.task_id,
        effective_status,
        args.note,
        unblocked,
        appended_task_id,
        validator_report,
    )

    write_yaml(args.queue, queue)
    write_yaml(args.state, state)
    print(f"marked {args.task_id} {effective_status}")
    if args.status == "completed" and effective_status != "completed":
        print("completion blocked by validator failure")
    if validator_report:
        print(f"validator_report {display_path(validator_report)}")
    if unblocked:
        print("unblocked " + ", ".join(unblocked))
    if appended_task_id:
        print(f"appended {appended_task_id}")
    return 0 if effective_status == args.status else 1


if __name__ == "__main__":
    raise SystemExit(main())
