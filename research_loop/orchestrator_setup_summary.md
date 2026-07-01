# Research Orchestrator v1 Setup Summary

Research Orchestrator v1 now has a machine-readable queue, stage contracts, prompt rendering, validator-enforced result marking, validators, reviewers, artifact policy files, CI guardrails, and reusable stage prompts.

## Current Queue State

Completed:

- `FD_001_BATCH_B_V2_QA_AND_COMBINED_SNAPSHOT`
- Stage: `FEATURE_LAB_REVIEW`
- Evidence: `feature_lab/FD_001_combined/validation_summary.md` and `feature_lab/FD_001_combined/next_step_recommendation.md`

Next ready task:

- `FD_001_FEATURE_TO_HYPOTHESIS_PLANNING`
- Stage: `FEATURE_TO_HYPOTHESIS_PLANNING`
- Purpose: generate FD_001-derived hypothesis planning artifacts from the frozen combined experimental feature snapshot.

## Active Research Snapshot

- Snapshot id: `FD_001_combined`
- Status: `frozen_research_snapshot`
- Path: `feature_lab/FD_001_combined/`
- Latest date: 2026-06-30
- Candidate hypothesis columns: 10
- Context-only columns: 4
- Descriptive-only columns: 4
- Episode diagnostics-only columns: 4

## Hardened Workflow

1. Render the next task:

```bash
python research_loop/run_next_task.py
```

2. Send `research_loop/next_codex_task.md` to Codex.

3. After Codex completes, mark the result with validators:

```bash
python research_loop/mark_task_result.py <TASK_ID> completed --run-validators
```

4. If validators pass, the task is completed, dependent tasks are unblocked, `research_state.yaml` is updated, and the next task can be rendered.

5. If validators fail, the task becomes `needs_patch`, downstream tasks remain blocked, and validator reports are written to `research_loop/task_results/<TASK_ID>/`.

## Guardrail Additions

- `validate_no_protected_pr_diff.py` checks committed PR diffs against protected production files.
- `validate_feature_snapshot.py` now checks date integrity, role integrity, coverage, suspicious leakage-like names, dtypes, and manifest guardrails.
- `validate_task_queue_consistency.py` catches stale ready tasks, blocked tasks whose dependencies are complete, completed tasks with missing outputs, duplicate task ids, and priority collisions.
- `.github/workflows/research-loop-checks.yml` runs compile checks and research-loop validators on pull requests and manual dispatch.

## Separation Rules

- Research stages can write research artifacts only.
- Feature-to-hypothesis planning cannot run tests.
- Walk-forward testing is the first stage allowed to run research tests.
- Dashboard candidate and shadow evaluation stages cannot modify production files.
- Production proposal remains human-approval-gated and does not implement production changes.

## Artifact Policy

The current patch does not delete FD_001 artifacts. It adds `research_loop/artifact_policy.yaml`, `research_loop/artifact_policy.md`, and `research_loop/artifact_cleanup_recommendation.md` so future cleanup can happen deliberately after the first merged baseline.

## Guardrail Status

This hardening setup did not run feature research, generate hypotheses, run hypothesis tests, run walk-forward tests, modify production dashboard logic, or modify production feature construction.
