# Hypothesis Plan Validator Summary

## Files Changed

- `.github/workflows/research-loop-checks.yml`
- `research_loop/validators/validate_hypothesis_plan.py`
- `research_loop/task_queue.yaml`
- `research_loop/stage_definitions.yaml`
- `research_loop/orchestrator_readme.md`
- `research_loop/next_codex_task.md`
- `research_loop/hypothesis_plan_validator_summary.md`

## Validator Behavior

`research_loop/validators/validate_hypothesis_plan.py` validates the output of `FEATURE_TO_HYPOTHESIS_PLANNING` before downstream hypothesis implementation or testing is allowed.

The validator:

- accepts either a top-level hypothesis list or a mapping with `hypotheses`;
- enforces 1 to 5 candidates by default;
- loads role-approved columns from `feature_lab/FD_001_combined/experimental_feature_inventory.csv`;
- requires each candidate to reference only `candidate_hypothesis_design` columns as source trigger columns;
- allows `context_only`, `descriptive_only`, and `episode_diagnostics_only` columns only in their matching companion fields;
- requires target, deterministic trigger-rule, no-threshold-optimization, validation-plan, dashboard relevance, and duplicate-avoidance fields;
- rejects suspicious future/target/leakage-like feature column names;
- prints `HYPOTHESIS_PLAN_CHECK_PASSED` with candidate count and ids on success;
- prints `HYPOTHESIS_PLAN_CHECK_FAILED` with a clear reason on failure.

## Queue And State

Existing queue/state still point to `FD_001_FEATURE_TO_HYPOTHESIS_PLANNING` as the next ready task.

Evidence from `python research_loop/run_next_task.py`:

- wrote `research_loop/next_codex_task.md`;
- task id `FD_001_FEATURE_TO_HYPOTHESIS_PLANNING`;
- stage `FEATURE_TO_HYPOTHESIS_PLANNING`;
- template `prompts/stage_feature_to_hypothesis_planning.md`.

The rendered next task includes:

- `research_loop/validators/validate_hypothesis_plan.py --plan-yaml hypothesis_registry/fd_001_feature_to_hypothesis_plan.yaml --snapshot-dir feature_lab/FD_001_combined`

## CI Behavior

CI now compiles `validate_hypothesis_plan.py` on every pull request and manual run.

CI does not run the hypothesis plan validator unless `hypothesis_registry/fd_001_feature_to_hypothesis_plan.yaml` exists. In the current baseline, that file is absent, so CI will skip the validator execution cleanly.

## Verification Commands

Verification was run with the repository virtualenv prepended to PATH so `python` resolved in this Windows shell.

| Command | Result |
|---|---|
| `python -m py_compile research_loop/validators/validate_hypothesis_plan.py` | exit 0 |
| `python research_loop/validators/validate_feature_snapshot.py --snapshot-dir feature_lab/FD_001_combined` | `FEATURE_SNAPSHOT_CHECK_PASSED`; rows 6869; feature columns 22; latest date 2026-06-30; exit 0 |
| `python research_loop/validators/validate_task_queue_consistency.py` | `TASK_QUEUE_CONSISTENCY_CHECK_PASSED`; task count 2; ready count 1; completed count 1; exit 0 |
| `python research_loop/run_next_task.py` | rendered `FD_001_FEATURE_TO_HYPOTHESIS_PLANNING`; exit 0 |
| `python research_loop/validators/validate_no_protected_diff.py` | `PROTECTED_DIFF_CHECK_PASSED`; protected hits 0; exit 0 |
| `python research_loop/validators/validate_no_protected_pr_diff.py --base-ref origin/main` | `PROTECTED_PR_DIFF_CHECK_PASSED`; protected hits 0; exit 0 |

## Guardrail Statement

- No hypotheses were generated.
- No hypothesis tests were run.
- No test runners were implemented.
- No threshold optimization was performed.
- No production dashboard logic was modified.
- No production feature construction files were modified.
