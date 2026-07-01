# Research Orchestrator v1 Setup Summary

## What Was Added

Research Orchestrator v1 now has a machine-readable queue, stage contracts, prompt rendering, result marking, validators, reviewers, and reusable stage prompts.

Created or updated:

- `research_loop/task_queue.yaml`
- `research_loop/stage_definitions.yaml`
- `research_loop/run_next_task.py`
- `research_loop/mark_task_result.py`
- `research_loop/validators/validate_no_protected_diff.py`
- `research_loop/validators/validate_feature_snapshot.py`
- `research_loop/reviewers/feature_formula_review.md`
- `research_loop/reviewers/evidence_review.md`
- `research_loop/orchestrator_readme.md`
- `research_loop/next_codex_task.md`
- `prompts/stage_*.md`

## Queue Initialization

The first ready task is:

- `FD_001_BATCH_B_V2_QA_AND_COMBINED_SNAPSHOT`
- Stage: `FEATURE_LAB_REVIEW`
- Purpose: run FD_001 Batch B v2 QA patch and create the FD_001 combined experimental snapshot.

The next task is blocked:

- `FD_001_FEATURE_TO_HYPOTHESIS_PLANNING`
- Stage: `FEATURE_TO_HYPOTHESIS_PLANNING`
- Blocked by: `FD_001_BATCH_B_V2_QA_AND_COMBINED_SNAPSHOT`

## Stage Coverage

`research_loop/stage_definitions.yaml` defines 14 stages:

- `FEATURE_RESEARCH`
- `FEATURE_FEASIBILITY_AUDIT`
- `FEATURE_LAB_IMPLEMENTATION`
- `FEATURE_LAB_REVIEW`
- `FEATURE_SNAPSHOT_FREEZE`
- `FEATURE_TO_HYPOTHESIS_PLANNING`
- `HYPOTHESIS_VALIDATION`
- `TEST_IMPLEMENTATION`
- `WALK_FORWARD_TEST`
- `EVIDENCE_ANALYSIS`
- `REGISTRY_UPDATE`
- `DASHBOARD_CANDIDATE`
- `SHADOW_DASHBOARD_EVALUATION`
- `PRODUCTION_PROPOSAL`

Each stage includes objective, required inputs, required outputs, allowed files, blocked files, validators, next stage on pass, next stage on fail, and whether human approval is required.

## How To Run

Render the next task:

```bash
python research_loop/run_next_task.py
```

Then send `research_loop/next_codex_task.md` to Codex.

After Codex completes the task, run the validators listed in `task_queue.yaml`, then mark the result:

```bash
python research_loop/mark_task_result.py FD_001_BATCH_B_V2_QA_AND_COMBINED_SNAPSHOT completed --note "Validators passed."
```

## Verification Evidence

Fresh checks run during setup:

- `py_compile` succeeded for:
  - `research_loop/run_next_task.py`
  - `research_loop/mark_task_result.py`
  - `research_loop/validators/validate_no_protected_diff.py`
  - `research_loop/validators/validate_feature_snapshot.py`
- YAML parsed successfully:
  - stage count: 14
  - task count: 2
- Stage prompt templates created:
  - `prompts/stage_*.md` count: 14
- `python research_loop/run_next_task.py` wrote:
  - `research_loop/next_codex_task.md`
  - task id: `FD_001_BATCH_B_V2_QA_AND_COMBINED_SNAPSHOT`
  - stage: `FEATURE_LAB_REVIEW`
  - template: `prompts/stage_feature_lab_review.md`

## Guardrail Status

This setup did not run feature labs, hypothesis tests, walk-forward tests, or research experiments.

This setup did not modify production dashboard logic or production feature construction.
