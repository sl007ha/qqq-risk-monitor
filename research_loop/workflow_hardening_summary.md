# Workflow Hardening Summary

## Scope

This hardening pass created machine-readable infrastructure for future Codex research iterations. It did not generate new hypotheses, did not run iteration_004, did not run new hypothesis tests, and did not modify production dashboard logic.

## Infrastructure Added Or Updated

- `research_loop/research_state.yaml`
  - Tracks current iteration, last completed iteration, next planned iteration, active hypotheses, rejected hypotheses, rewrite queue, dashboard candidates, next required action, protected files, and allowed research files.
  - Initialized from `research_iterations/iteration_003/decision_log.md` and `research_iterations/iteration_003/next_iteration_plan.md`.

- `research_loop/promotion_gates.yaml`
  - Defines machine-readable gates for keep, rewrite, drop, promote_to_combination_test, promote_to_shadow_dashboard, and production_dashboard_candidate.
  - Includes required metrics: alert_burden, base_rate_lift, event_coverage, positive_lift_folds, median_lead, and alert_days.

- `research_loop/validate_iteration_artifacts.py`
  - Validates required iteration documents and test CSVs.
  - Prints pass/fail, present files, and missing files.
  - Exits with code 0 on pass and 1 on fail.

- `hypothesis_registry/active_hypotheses.yaml`
  - Tracks active hypotheses from iteration_003 decisions: I002_H001, I002_H002, I002_H003, and I003_H005.

- `hypothesis_registry/rejected_hypotheses.yaml`
  - Tracks dropped or failed formulations: I003_H002, I003_H004, and I003_H003 as a rejected standalone alert.
  - Preserves lessons from I002/I003 false-repair attempts.

- `hypothesis_registry/rewrite_queue.yaml`
  - Tracks the iteration_004 rewrite queue:
    - I003_H005 false-calm burden reduction
    - I002_H001 versus I003_H001 downside-volatility comparison
    - leadership-as-context overlay from I002_H003 and I003_H003 evidence

- `feature_backlog/feature_requests_from_hypotheses.yaml`
  - Captures feature requests implied by iteration_003:
    - earlier cross-asset lead-time features
    - event-based repair features if false repair is revisited
    - leadership context features for false-calm filtering

- `dashboard_candidates/README.md`
  - Defines the shadow dashboard candidate workflow:
    research signal -> candidate rules -> shadow report -> comparison vs current dashboard -> human approval.

- `dashboard_candidates/candidate_template/`
  - Adds reusable candidate templates:
    - `dashboard_logic_proposal.md`
    - `candidate_rules.yaml`
    - `approval_checklist.md`

- `prompts/codex_run_full_iteration.md`
  - Reusable prompt for iteration_004 and later full research-loop runs.

- `prompts/codex_create_dashboard_candidate.md`
  - Reusable prompt for creating shadow dashboard candidate packages from promoted hypotheses.

## How Future Codex Iterations Should Use This

1. Start with `AGENTS.md`, then read `research_loop/research_state.yaml`, `research_loop/promotion_gates.yaml`, and the three hypothesis registry YAML files.
2. Validate the latest completed iteration with:

   ```text
   python research_loop/validate_iteration_artifacts.py research_iterations/iteration_003
   ```

3. Use `rewrite_queue.yaml` to define the next iteration scope.
4. Generate hypotheses only when explicitly asked to run the next iteration.
5. Keep new iteration work under the allowed research files for that iteration.
6. Preserve failed hypotheses and lessons in the registries.
7. Apply promotion gates using generated evidence files, not narrative judgment alone.
8. Create dashboard candidates only as shadow packages under `dashboard_candidates/`.

## Validation Evidence

Command run:

```text
.\.venv\Scripts\python.exe research_loop\validate_iteration_artifacts.py research_iterations\iteration_003
```

Output:

```text
PASS: research_iterations\iteration_003 contains all required artifacts.
Present files:
  - prior_results_summary.md
  - HYPOTHESES.md
  - hypotheses.yaml
  - analysis.md
  - decision_log.md
  - next_iteration_plan.md
  - tests/
  - tests\iteration_003_hypothesis_test_summary.csv
  - tests\iteration_003_hypothesis_test_daily_signals.csv
  - tests\iteration_003_hypothesis_test_events.csv
Missing files:
  - none
```

## Manual / Human-Approved Items

- Human approval is required before any production dashboard implementation.
- Human approval is required before changing protected files:
  - `qqq_autoresearch/data_sources.py`
  - `qqq_autoresearch/features.py`
  - `qqq_autoresearch/config.py`
  - `qqq_autoresearch/candidate.py`
  - `qqq_autoresearch/pipeline.py`
  - `qqq_autoresearch/render.py`
  - `run_dashboard.py`
- Human approval is required before threshold optimization.
- Human approval is required before adding new data sources or using any live sentiment/headline data historically.
- Production dashboard candidates must go through the shadow candidate workflow before implementation.
