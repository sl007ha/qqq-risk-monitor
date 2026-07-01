# Codex Prompt: Test Iteration

Use Superpowers and evidence-over-claims.

Work in `qqq-risk-monitor`.

Goal: implement and run deterministic research-only tests for an existing hypothesis iteration. Do not generate new hypotheses. Do not modify production dashboard logic.

Read:

- `AGENTS.md`
- `research_loop/program_research_loop.md`
- `research_loop/promotion_gates.yaml`
- target iteration `hypotheses.yaml`
- `outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv`
- `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv`

Tasks:

1. Validate that every `exact_feature_columns_used` entry exists in `all_feature_inventory.csv`.
2. Implement deterministic research-only triggers in `qqq_autoresearch/hypothesis_tests_iteration_00N.py`.
3. Add `run_hypothesis_tests_iteration_00N.py`.
4. Run:

```text
python run_dashboard.py --output-dir outputs
python run_hypothesis_tests_iteration_00N.py --output-dir outputs --test-output-dir research_iterations/iteration_00N/tests
```

5. Generate test summary, folds, daily signals, event coverage, JSON summary, and HTML report under the iteration folder.

Metrics:

- alert burden
- base hit rate
- alert hit rate
- base-rate lift
- event coverage
- false calm
- yearly fold stability
- lead-time if available

Hard rules:

- Do not optimize thresholds.
- Do not modify `data_sources.py`, `features.py`, `config.py`, or existing pipeline/dashboard logic.
- Do not use live sentiment for historical backtests.

Final response must include terminal output or file evidence.
