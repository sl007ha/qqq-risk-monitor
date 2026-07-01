# Research Orchestrator v1

Research Orchestrator v1 turns the research loop into a machine-readable queue plus reusable stage prompts. It does not execute experiments by itself.

## Core Files

- `research_loop/task_queue.yaml` stores queued tasks, dependencies, gates, validators, allowed files, and blocked files.
- `research_loop/stage_definitions.yaml` defines the stage contract from feature research through production proposal.
- `research_loop/run_next_task.py` renders the first ready task into `research_loop/next_codex_task.md`.
- `research_loop/mark_task_result.py` records task outcomes and can unblock dependent tasks.
- `research_loop/validators/` contains local validators.
- `research_loop/reviewers/` contains human/Codex review checklists.
- `prompts/stage_*.md` contains reusable templates for each stage.

## Run The Next Task

```bash
python research_loop/run_next_task.py
```

Then send `research_loop/next_codex_task.md` to Codex.

The script only reads YAML and prompt templates, then writes one Markdown task file. It does not call external services, run feature labs, run hypothesis tests, or modify production files.

## Validate A Completed Task

Run the validators listed in the task queue entry. For the current first task, the validators are:

```bash
python research_loop/validators/validate_no_protected_diff.py
python research_loop/validators/validate_feature_snapshot.py --snapshot-dir feature_lab/FD_001_batch_B_v2
python research_loop/validators/validate_feature_snapshot.py --snapshot-dir feature_lab/FD_001_combined
```

Validators are evidence checks. They do not promote research to production.

## Mark The Result

After Codex finishes and validators pass, mark the task completed:

```bash
python research_loop/mark_task_result.py FD_001_BATCH_B_V2_QA_AND_COMBINED_SNAPSHOT completed --note "Validators passed."
```

If the task fails or needs a patch:

```bash
python research_loop/mark_task_result.py FD_001_BATCH_B_V2_QA_AND_COMBINED_SNAPSHOT needs_patch --note "Validation failed: explain the failure."
```

When a task is marked completed, dependent blocked tasks are unblocked automatically if all their dependencies are complete.

## Append A New Task

Prepare a YAML file containing a single task mapping, then run:

```bash
python research_loop/mark_task_result.py <task_id> completed --append-next-task path/to/new_task.yaml
```

The appended task must include a unique `task_id`.

## Guardrails

- Do not modify production dashboard logic.
- Do not modify `qqq_autoresearch/features.py`, `data_sources.py`, `config.py`, `pipeline.py`, `render.py`, or `run_dashboard.py`.
- Do not write to production `outputs/` from orchestrator tasks unless a stage explicitly allows it.
- Do not run hypothesis tests unless the queued stage explicitly requires it.
- Treat production promotion as human-approved only.
