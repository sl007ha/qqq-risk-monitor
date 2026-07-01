#!/usr/bin/env python
"""Render the next ready Codex task from the research task queue.

This script is intentionally local-only: it reads YAML state, fills a prompt
template, and writes research_loop/next_codex_task.md. It does not call external
services, run research experiments, or modify production files.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE = REPO_ROOT / "research_loop" / "research_state.yaml"
DEFAULT_QUEUE = REPO_ROOT / "research_loop" / "task_queue.yaml"
DEFAULT_STAGES = REPO_ROOT / "research_loop" / "stage_definitions.yaml"
DEFAULT_OUTPUT = REPO_ROOT / "research_loop" / "next_codex_task.md"


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
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


def render_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        if not value:
            return "- none"
        return "\n".join(f"- {item}" for item in value)
    if isinstance(value, dict):
        return yaml.safe_dump(value, sort_keys=False).strip()
    return str(value)


def task_is_ready(task: dict[str, Any], completed_ids: set[str]) -> bool:
    if task.get("status") != "ready":
        return False
    blocked_by = set(as_list(task.get("blocked_by")))
    return blocked_by <= completed_ids


def find_next_task(queue: dict[str, Any]) -> dict[str, Any]:
    tasks = queue.get("tasks", [])
    if not isinstance(tasks, list):
        raise ValueError("task_queue.yaml must contain a list at tasks")
    completed_ids = {task.get("task_id") for task in tasks if task.get("status") == "completed"}
    ready = [task for task in tasks if task_is_ready(task, completed_ids)]
    if not ready:
        raise RuntimeError("No ready task found in research_loop/task_queue.yaml")
    return sorted(ready, key=lambda task: (int(task.get("priority", 9999)), str(task.get("task_id", ""))))[0]


def load_template(task: dict[str, Any], stages: dict[str, Any]) -> tuple[Path, str]:
    template_name = task.get("prompt_template")
    stage_name = task.get("stage")
    stage = stages.get("stages", {}).get(stage_name, {})
    if not template_name:
        template_name = stage.get("prompt_template") or f"prompts/stage_{str(stage_name).lower()}.md"
    template_path = REPO_ROOT / str(template_name)
    if not template_path.exists():
        raise FileNotFoundError(template_path)
    return template_path, template_path.read_text(encoding="utf-8")


def build_context(
    task: dict[str, Any],
    stage_definition: dict[str, Any],
    research_state: dict[str, Any],
    task_queue: dict[str, Any],
) -> dict[str, str]:
    allowed_files = task.get("allowed_files") or stage_definition.get("allowed_files") or []
    blocked_files = task.get("blocked_files") or stage_definition.get("blocked_files") or []
    validators = task.get("validators") or stage_definition.get("validators") or []
    gates = task.get("gates") or []
    if stage_definition.get("human_approval_required"):
        gates = as_list(gates) + ["human_approval_required"]

    return {
        "task_id": render_value(task.get("task_id")),
        "stage": render_value(task.get("stage")),
        "title": render_value(task.get("title")),
        "objective": render_value(task.get("objective") or stage_definition.get("objective")),
        "inputs": render_value(task.get("inputs") or stage_definition.get("required_inputs")),
        "outputs": render_value(task.get("outputs") or stage_definition.get("required_outputs")),
        "allowed_files": render_value(allowed_files),
        "blocked_files": render_value(blocked_files),
        "validators": render_value(validators),
        "gates": render_value(gates),
        "next_stage_on_pass": render_value(stage_definition.get("next_stage_on_pass")),
        "next_stage_on_fail": render_value(stage_definition.get("next_stage_on_fail")),
        "human_approval_required": render_value(stage_definition.get("human_approval_required", False)),
        "task_yaml": yaml.safe_dump(task, sort_keys=False).strip(),
        "stage_yaml": yaml.safe_dump(stage_definition, sort_keys=False).strip(),
        "research_state_summary": yaml.safe_dump(
            {
                "as_of": research_state.get("as_of"),
                "current_iteration": research_state.get("current_iteration"),
                "last_completed_iteration": research_state.get("last_completed_iteration"),
                "next_planned_iteration": research_state.get("next_planned_iteration"),
                "next_required_action": research_state.get("next_required_action"),
            },
            sort_keys=False,
        ).strip(),
        "queue_policy": yaml.safe_dump(task_queue.get("queue_policy", {}), sort_keys=False).strip(),
    }


def render_template(template: str, context: dict[str, str]) -> str:
    rendered = template
    for key, value in context.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--stages", type=Path, default=DEFAULT_STAGES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    research_state = read_yaml(args.state)
    task_queue = read_yaml(args.queue)
    stage_definitions = read_yaml(args.stages)
    task = find_next_task(task_queue)
    stage_name = task.get("stage")
    stage_definition = stage_definitions.get("stages", {}).get(stage_name)
    if not isinstance(stage_definition, dict):
        raise ValueError(f"Stage {stage_name!r} is not defined in {args.stages}")

    template_path, template = load_template(task, stage_definitions)
    context = build_context(task, stage_definition, research_state, task_queue)
    rendered = render_template(template, context)
    header = (
        "<!-- Generated by research_loop/run_next_task.py. "
        "Do not edit by hand; update task_queue.yaml or the prompt template instead. -->\n\n"
    )
    args.output.write_text(header + rendered.rstrip() + "\n", encoding="utf-8")
    print(f"wrote {args.output.relative_to(REPO_ROOT).as_posix()}")
    print(f"task_id {task.get('task_id')}")
    print(f"stage {stage_name}")
    print(f"template {template_path.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
