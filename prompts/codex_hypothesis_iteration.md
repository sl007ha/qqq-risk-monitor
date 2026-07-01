# Codex Prompt: Hypothesis Iteration

Use Superpowers and evidence-over-claims.

Work in `qqq-risk-monitor`.

Goal: generate a research-only hypothesis iteration. Do not run backtests unless explicitly asked in the same task. Do not modify production dashboard logic.

Read:

- `AGENTS.md`
- `README.md`
- `FEATURE_UNIVERSE.md`
- `program_hypothesis_generation.md`
- `research_loop/program_research_loop.md`
- `research_loop/research_state.yaml`
- `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv`
- `outputs/qqq_r2_mmdi_v1_3_1_feature_catalog.csv`
- latest prior iteration analysis if present

Tasks:

1. Summarize prior results and lessons learned.
2. Generate exactly the requested number of hypotheses.
3. Use only feature columns copied verbatim from `all_feature_inventory.csv`.
4. Put unavailable desired data under `future_data_requirement`.
5. Write `hypotheses.yaml` and `HYPOTHESES.md` under the new iteration folder.

Required hypothesis fields:

- hypothesis_id
- title
- plain_english_thesis
- economic_market_mechanism
- feature_families_used
- exact_feature_columns_used
- expected_direction
- target_horizon
- target_type
- target_definition
- trigger_logic_pseudocode
- why_this_should_work
- when_this_may_fail
- data_quality_or_leakage_risks
- minimum_data_coverage_requirement
- validation_plan
- dashboard_implication
- future_data_requirement
- priority_score

Hard rules:

- Do not invent features.
- Do not optimize thresholds.
- Do not use live sentiment for historical backtests.
- Do not modify production dashboard logic.

Final response must cite file evidence and feature-column validation evidence.
