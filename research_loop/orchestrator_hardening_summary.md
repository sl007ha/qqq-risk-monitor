# Orchestrator v1 Hardening Summary

## Files Changed

State and queue:

- `research_loop/task_queue.yaml`
- `research_loop/research_state.yaml`
- `research_loop/next_codex_task.md`

Orchestrator scripts:

- `research_loop/run_next_task.py`
- `research_loop/mark_task_result.py`

Validators:

- `research_loop/validators/validate_feature_snapshot.py`
- `research_loop/validators/validate_no_protected_pr_diff.py`
- `research_loop/validators/validate_task_queue_consistency.py`

Stage contracts, prompts, and docs:

- `research_loop/stage_definitions.yaml`
- `prompts/stage_feature_to_hypothesis_planning.md`
- `research_loop/orchestrator_readme.md`
- `research_loop/orchestrator_setup_summary.md`
- `research_loop/artifact_policy.yaml`
- `research_loop/artifact_policy.md`
- `research_loop/artifact_cleanup_recommendation.md`
- `.github/workflows/research-loop-checks.yml`

## Validators Added Or Hardened

- Added `validate_no_protected_pr_diff.py` for committed PR-level protected-file checks against `origin/main`.
- Added `validate_task_queue_consistency.py` for duplicate task ids, stale ready tasks, completed tasks with missing outputs, and blocked tasks whose dependencies are complete.
- Hardened `validate_feature_snapshot.py` with date integrity, inventory role integrity, coverage checks, suspicious target/leakage-name guards, dtype checks, and manifest checks.
- Hardened `mark_task_result.py` so `completed --run-validators` runs declared task validators, writes YAML and Markdown reports, and only unblocks downstream tasks when all validators pass.

## Queue And State Result

- `FD_001_BATCH_B_V2_QA_AND_COMBINED_SNAPSHOT` is now `completed`.
- `FD_001_FEATURE_TO_HYPOTHESIS_PLANNING` is now the next `ready` task.
- Active feature snapshot is `FD_001_combined`, status `frozen_research_snapshot`.
- Active snapshot latest date is 2026-06-30.
- Active snapshot role counts:
  - `candidate_hypothesis_design`: 10
  - `context_only`: 4
  - `descriptive_only`: 4
  - `episode_diagnostics_only`: 4

## Verification Results

The local Windows shell did not have bare `python` on PATH initially, so verification was run with the repository virtualenv prepended to PATH. The commands below were then executed as `python ...`.

| Command | Result |
|---|---|
| `python -m py_compile research_loop/run_next_task.py` | exit 0 |
| `python -m py_compile research_loop/mark_task_result.py` | exit 0 |
| `python -m py_compile research_loop/validators/validate_no_protected_diff.py` | exit 0 |
| `python -m py_compile research_loop/validators/validate_no_protected_pr_diff.py` | exit 0 |
| `python -m py_compile research_loop/validators/validate_feature_snapshot.py` | exit 0 |
| `python -m py_compile research_loop/validators/validate_task_queue_consistency.py` | exit 0 |
| `python research_loop/validators/validate_feature_snapshot.py --snapshot-dir feature_lab/FD_001_combined` | `FEATURE_SNAPSHOT_CHECK_PASSED`; rows 6869; feature columns 22; latest date 2026-06-30; exit 0 |
| `python research_loop/validators/validate_task_queue_consistency.py` | `TASK_QUEUE_CONSISTENCY_CHECK_PASSED`; task count 2; ready count 1; completed count 1; exit 0 |
| `python research_loop/run_next_task.py` | wrote `research_loop/next_codex_task.md`; task id `FD_001_FEATURE_TO_HYPOTHESIS_PLANNING`; stage `FEATURE_TO_HYPOTHESIS_PLANNING`; exit 0 |
| `python research_loop/validators/validate_no_protected_pr_diff.py --base-ref origin/main` | `PROTECTED_PR_DIFF_CHECK_PASSED`; protected hits 0; exit 0 |

`origin/main` was available for the PR-level protected diff check.

## Current Next Ready Task

- Task id: `FD_001_FEATURE_TO_HYPOTHESIS_PLANNING`
- Stage: `FEATURE_TO_HYPOTHESIS_PLANNING`
- Required outputs:
  - `hypothesis_registry/fd_001_feature_to_hypothesis_plan.yaml`
  - `feature_research/FD_001/feature_to_hypothesis_plan.md`

## Guardrail Evidence

- No feature research was run.
- No hypotheses were generated.
- No hypothesis tests were run.
- No walk-forward tests were run.
- No production dashboard logic was modified.
- No production feature construction files were modified.
- The combined FD_001 snapshot remains a research-only frozen snapshot.

## Limitations And Manual Follow-Ups

- CI has been added but has not run remotely yet.
- Existing FD_001 batch snapshots were intentionally retained for current PR reproducibility.
- A future cleanup PR can decide whether to retain only the combined snapshot, or retain only manifests plus checksums after the first merged baseline.
- Production proposal remains human-approval-gated.
