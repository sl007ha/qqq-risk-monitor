# Codex Prompt: Feature Iteration

Use Superpowers and evidence-over-claims.

Work in `qqq-risk-monitor`.

Goal: perform a feature-inspection iteration for QQQ Risk Monitor. Do not generate hypotheses unless explicitly asked. Do not modify production dashboard logic.

Read:

- `AGENTS.md`
- `README.md`
- `FEATURE_UNIVERSE.md`
- `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv`
- `outputs/qqq_r2_mmdi_v1_3_1_feature_catalog.csv`
- `outputs/qqq_r2_mmdi_v1_3_1_feature_snapshot_latest.csv`
- `outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv`

Tasks:

1. Summarize available feature families, coverage, first/last valid dates, and missing/placeholder features.
2. Identify features that are safe for historical testing.
3. Identify features that are current-context only.
4. Identify future data requirements separately from available features.
5. Write findings to a new iteration folder under `research_iterations/iteration_00N/feature_review.md`.

Hard rules:

- Do not invent features.
- Do not place unavailable features in `exact_feature_columns_used`.
- Do not use live sentiment for historical tests without point-in-time archives.
- Do not modify `data_sources.py`, `features.py`, `config.py`, or production dashboard logic.

Output:

- `research_iterations/iteration_00N/feature_review.md`
- optional supporting CSVs under `research_iterations/iteration_00N/feature_review/`

Final response must cite terminal output or file evidence.
