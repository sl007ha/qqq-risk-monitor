# Codex Prompt: Feature Feasibility Audit

Use Superpowers and evidence-over-claims.

Work in `qqq-risk-monitor`.

Goal: audit proposed feature specs for data availability, leakage, coverage, redundancy, and implementation complexity. Do not run new hypothesis tests. Do not modify production dashboard logic. Do not modify `qqq_autoresearch/data_sources.py`, `qqq_autoresearch/features.py`, or `qqq_autoresearch/config.py`.

Read:

- `AGENTS.md`
- `research_loop/program_feature_discovery.md`
- `research_loop/feature_promotion_gates.yaml`
- `feature_specs/README.md`
- target feature spec file or backlog entry
- `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv`
- `outputs/qqq_r2_mmdi_v1_3_1_feature_catalog.csv`
- `outputs/qqq_r2_mmdi_v1_3_1_feature_snapshot_latest.csv`
- `outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv` if coverage checks are needed

Audit checklist:

1. Confirm the feature has a valid source: prior iteration failure, dashboard blind spot, research source, or market mechanism.
2. Confirm the feature includes economic mechanism, raw inputs, formula, data source, point-in-time risk, expected direction, and candidate hypothesis use.
3. Classify each raw input as current inventory column, exported CSV field, external public data, current-context-only input, or future data requirement.
4. Check point-in-time risk, including release lag, restatements, survivorship, current membership, and current-only snapshots.
5. Check coverage, first valid date, latest valid date, non-null count, and missingness when data exists.
6. Check redundancy against current inventory columns and document exact related columns.
7. Check whether the formula can be implemented deterministically without threshold optimization.
8. Estimate implementation complexity as low, medium, or high.
9. Assign the next gate from `research_loop/feature_promotion_gates.yaml`.

Output:

- feasibility verdict: pass, pass_with_limitations, fail, or future_data_required
- point-in-time verdict
- leakage verdict
- redundancy verdict
- coverage summary
- implementation complexity
- required revisions before experimental implementation
- updated gate status recommendation

Hard rules:

- Do not add unavailable features to `exact_feature_columns_used`.
- Live sentiment and headline-derived features are current-context-only unless historical point-in-time archives exist.
- Passing feasibility does not approve production implementation.
- Experimental implementation, if later approved, must stay under `feature_lab/` or an iteration folder.

Final response must cite the files inspected and the exact evidence supporting the verdict.
