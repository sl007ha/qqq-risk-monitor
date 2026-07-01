# Task Output Validator Summary

## Files Changed

- `.github/workflows/research-loop-checks.yml`
- `research_loop/mark_task_result.py`
- `research_loop/orchestrator_readme.md`
- `research_loop/task_queue.yaml`
- `research_loop/validators/validate_task_outputs.py`
- `research_loop/task_output_validator_summary.md`

## Validator Behavior

`research_loop/validators/validate_task_outputs.py` reads `research_loop/task_queue.yaml`, accepts `--task-id`, and checks every declared output for that task.

It supports literal paths and glob patterns:

- success prints `TASK_OUTPUT_CHECK_PASSED` with task id and output count;
- failure prints `TASK_OUTPUT_CHECK_FAILED` with task id and missing outputs.

`research_loop/mark_task_result.py` now enforces the same declared-output check internally when `completed --run-validators` is used. Missing outputs are included in both `validator_report.yaml` and `validator_report.md`, force the task to `needs_patch`, and prevent downstream tasks from being unblocked.

The FD_001 planning task records this queue-level policy as:

```yaml
completion_output_check: enforced_by_mark_task_result_completed_run_validators
```

## Evidence From Output Checks

- `python research_loop/validators/validate_task_outputs.py --task-id FD_001_BATCH_B_V2_QA_AND_COMBINED_SNAPSHOT` returned `TASK_OUTPUT_CHECK_PASSED` with `output_count 12`.
- `python research_loop/validators/validate_task_outputs.py --task-id FD_001_FEATURE_TO_HYPOTHESIS_PLANNING` returned `TASK_OUTPUT_CHECK_FAILED` because the future planning outputs do not exist yet:
  - `hypothesis_registry/fd_001_feature_to_hypothesis_plan.yaml`
  - `feature_research/FD_001/feature_to_hypothesis_plan.md`
- A temporary `mark_task_result.py FD_001_FEATURE_TO_HYPOTHESIS_PLANNING completed --run-validators` run on copied queue/state files marked the task `needs_patch`, wrote a validator report, and included `TASK_OUTPUT_CHECK_FAILED` with the missing outputs. The real queue/state were not modified by that test.

## Verification Commands

Verification was run with the repository virtualenv prepended to PATH so `python` resolves in this Windows shell.

| Command | Result |
|---|---|
| `python -m py_compile research_loop/validators/validate_task_outputs.py` | exit 0 |
| `python -m py_compile research_loop/mark_task_result.py` | exit 0 |
| `python research_loop/validators/validate_feature_snapshot.py --snapshot-dir feature_lab/FD_001_combined` | `FEATURE_SNAPSHOT_CHECK_PASSED`; rows 6869; feature columns 22; latest date 2026-06-30; exit 0 |
| `python research_loop/validators/validate_task_queue_consistency.py` | `TASK_QUEUE_CONSISTENCY_CHECK_PASSED`; task count 2; ready count 1; completed count 1; exit 0 |
| `python research_loop/run_next_task.py` | rendered `FD_001_FEATURE_TO_HYPOTHESIS_PLANNING`; exit 0 |

## Current Next Ready Task

The next ready task remains:

- `FD_001_FEATURE_TO_HYPOTHESIS_PLANNING`

## Guardrail Statement

- No hypotheses were generated.
- No hypothesis tests were run.
- No test runners were implemented.
- No production dashboard logic was modified.
- No production feature construction files were modified.
