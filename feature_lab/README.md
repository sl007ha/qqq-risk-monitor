# Feature Lab Rules

`feature_lab/` is the research-only workspace for experimental feature implementation. It exists so Codex can test feature construction mechanics without modifying production dashboard logic or production feature construction.

## Allowed Work

- Implement experimental features from approved feature specs.
- Read exported dashboard and feature CSVs from `outputs/`.
- Write research-only outputs under `feature_lab/<feature_id>/` or an iteration folder.
- Produce coverage, leakage, redundancy, and accepted-snapshot artifacts.
- Document implementation assumptions and reproducibility steps.

## Disallowed Work Without Human Approval

- Do not modify `qqq_autoresearch/data_sources.py`.
- Do not modify `qqq_autoresearch/features.py`.
- Do not modify `qqq_autoresearch/config.py`.
- Do not modify production dashboard logic.
- Do not wire experimental features into `run_dashboard.py`.
- Do not add experimental columns to production dashboard HTML or production CSV exports.
- Do not treat an experimental feature as eligible for hypotheses until it reaches `accepted_to_inventory` and `eligible_for_hypothesis`.

## Experimental Feature Implementation Contract

Each experimental feature implementation should have:

- a feature spec in `feature_specs/`
- a local implementation folder, usually `feature_lab/<feature_id>/`
- declared input files and columns
- deterministic formula
- missing-data policy
- point-in-time and leakage notes
- redundancy audit against the current feature inventory
- validation summary
- output snapshot with exact experimental column names

## Recommended Folder Shape

```text
feature_lab/<feature_id>/
  README.md
  build_experimental_feature.py
  validation_summary.md
  redundancy_audit.md
  outputs/
    experimental_feature_snapshot.csv
    experimental_feature_coverage.csv
```

This shape is recommended, not required. Iteration-specific feature work may live under `research_iterations/iteration_00N/feature_lab/` if that keeps evidence closer to the research task.

## Validation Before Acceptance

Before a feature can be accepted into a research inventory, validation must document:

- first valid date
- latest valid date
- non-null count and missingness
- source columns or future data requirements
- leakage audit result
- redundancy audit result
- expected direction
- whether historical use is safe, research-only, or current-context-only

Acceptance into a research snapshot does not approve production use.
