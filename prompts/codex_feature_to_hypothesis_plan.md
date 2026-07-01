# Codex Prompt: Accepted Feature To Hypothesis Plan

Use Superpowers and evidence-over-claims.

Work in `qqq-risk-monitor`.

Goal: turn accepted feature specs and accepted feature snapshots into hypothesis candidates. Do not run new hypothesis tests unless explicitly asked in the same task. Do not modify production dashboard logic. Do not modify `qqq_autoresearch/data_sources.py`, `qqq_autoresearch/features.py`, or `qqq_autoresearch/config.py`.

Read:

- `AGENTS.md`
- `program_hypothesis_generation.md`
- `research_loop/program_research_loop.md`
- `research_loop/program_feature_discovery.md`
- `research_loop/feature_promotion_gates.yaml`
- `research_loop/research_state.yaml`
- accepted feature specs under `feature_specs/`
- accepted feature snapshots under `feature_lab/` or the relevant iteration folder
- latest prior iteration analysis and decision log
- current feature inventory if exact production-exported columns are also used

Tasks:

1. Confirm each feature has reached `eligible_for_hypothesis`.
2. Confirm exact experimental columns or exact inventory columns are named.
3. Keep unavailable desired data under `future_data_requirement`.
4. Draft hypothesis candidates from market mechanism first, feature mapping second.
5. Define deterministic trigger pseudocode without threshold optimization.
6. State expected direction, target type, target horizon, target definition, leakage risks, and validation plan.
7. Separate accepted experimental features from production inventory features.
8. Do not run tests or write trigger code unless the human explicitly asks.

Required hypothesis candidate fields:

- hypothesis_id
- title
- plain_english_thesis
- economic_market_mechanism
- source_feature_ids
- source_feature_specs
- feature_families_used
- exact_feature_columns_used
- experimental_feature_columns_used
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
- Do not use live sentiment for historical tests without point-in-time archives.
- Do not optimize thresholds without explicit human approval.
- Do not modify production dashboard logic.
- Do not imply accepted experimental features are production dashboard features.

Final response must cite accepted feature evidence and state which hypotheses are ready only for spec review versus ready for future test implementation.
