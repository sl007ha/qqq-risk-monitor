# Research Orchestrator v1

Research Orchestrator v1 turns the research loop into a machine-readable queue plus reusable stage prompts. It renders the next task and records task outcomes; it does not run experiments by itself.

## Core Files

- `research_loop/task_queue.yaml` stores queued tasks, dependencies, gates, validators, allowed files, and blocked files.
- `research_loop/stage_definitions.yaml` defines the stage contract from feature research through production proposal.
- `research_loop/run_next_task.py` renders the first ready task into `research_loop/next_codex_task.md`.
- `research_loop/mark_task_result.py` records task outcomes, runs declared validators when requested, and only unblocks dependent tasks after validation passes.
- `research_loop/validators/` contains local and PR-level guardrail validators.
- `research_loop/reviewers/` contains human/Codex review checklists.
- `research_loop/artifact_policy.yaml` and `research_loop/artifact_policy.md` define which research artifacts should be committed.
- `prompts/stage_*.md` contains reusable templates for each stage.

## Recommended Workflow

1. Render the next task:

```bash
python research_loop/run_next_task.py
```

2. Send `research_loop/next_codex_task.md` to Codex.

3. After Codex completes, mark the result with validators:

```bash
python research_loop/mark_task_result.py <TASK_ID> completed --run-validators
```

4. If validators pass:

- the task is completed;
- dependent tasks are unblocked;
- `research_loop/research_state.yaml` is updated;
- the next task can be rendered.

5. If validators fail:

- the task becomes `needs_patch`;
- downstream tasks remain blocked;
- validator reports are written to `research_loop/task_results/<TASK_ID>/`.

## Render The Current Next Task

The current active next task is FD_001 feature-to-hypothesis planning:

```bash
python research_loop/run_next_task.py
```

The script only reads YAML and prompt templates, then writes one Markdown task file. It does not call external services, run feature labs, run hypothesis tests, or modify production files.

## Validate And Mark A Completed Task

Use the task's declared validators:

```bash
python research_loop/mark_task_result.py FD_001_FEATURE_TO_HYPOTHESIS_PLANNING completed --run-validators
```

To use a different PR base:

```bash
python research_loop/mark_task_result.py FD_001_FEATURE_TO_HYPOTHESIS_PLANNING completed --run-validators --base-ref origin/main
```

If you must record a result without validators, the script allows it but prints a warning. A completed status without `--run-validators` does not imply validation passed.

## Research, Shadow, And Production Separation

- Feature research and feature lab snapshots are research-only.
- Feature-to-hypothesis planning may create plans, not tests.
- Hypothesis validation may validate plans, not run tests.
- Walk-forward testing is the first stage allowed to run research tests.
- Dashboard candidate and shadow dashboard stages may create research artifacts only.
- Production proposal creates a human-reviewable proposal and does not implement production changes.

## Human Approval Gates

`PRODUCTION_PROPOSAL` remains `human_approval_required: true`. No production dashboard modification, production feature construction change, or dashboard promotion is allowed without explicit human approval.

## Artifact Policy

Small review artifacts should remain in git: source scripts, YAML manifests, inventories, coverage summaries, validation summaries, prompt templates, reviewers, and validators.

Large regenerated snapshots, repeated intermediate snapshots, raw production outputs, scratch files, and secrets should not be committed by default after the current FD_001 baseline policy is decided.

## Guardrails

- Do not modify production dashboard logic.
- Do not modify `qqq_autoresearch/features.py`, `data_sources.py`, `config.py`, `pipeline.py`, `render.py`, or `run_dashboard.py`.
- Do not write to production `outputs/` from orchestrator tasks unless a stage explicitly allows it.
- Do not run hypothesis tests unless the queued stage explicitly requires it.
- Treat live sentiment or headline-derived features as current-context-only unless historical point-in-time archives exist.
