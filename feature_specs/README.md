# Feature Spec Schema

Feature specs are the durable contracts for proposed research-only features. A spec must be complete before a feature can pass `feasibility_passed` in `research_loop/feature_promotion_gates.yaml`.

Specs should be stored as YAML files under this directory:

```text
feature_specs/<feature_id>.yaml
```

## Required Schema

```yaml
version: 1
feature_id: FD000_SHORT_NAME
title: Human-readable feature title
status: proposed_feature
source_type: prior_iteration_failure
source_references:
  - research_iterations/iteration_00N/analysis.md
source_hypotheses:
  - I000_H000

economic_mechanism: Plain-English mechanism connecting the feature to QQQ drawdown risk.
raw_inputs:
  - input name, exact inventory column, or future data requirement
formula: Deterministic construction with windows, signs, and missing-data handling.
data_source: Current inventory, exported CSV, public source, or future data requirement.
point_in_time_risk: Release lag, restatement, survivorship, current-only, or no-known-risk assessment.
expected_direction: Higher/lower feature value should imply what risk direction and why.
candidate_hypothesis_use: How this feature would be used in a later hypothesis.

leakage_risks:
  - risk and mitigation
redundancy_check:
  inventory_file: outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv
  related_existing_columns:
    - exact_existing_column_name
  result: pending | distinct | partially_redundant | redundant
  notes: Why the feature is or is not redundant.
coverage_requirement:
  minimum_start_date: YYYY-MM-DD
  minimum_non_null_fraction: 0.80
  minimum_event_coverage_review: required

implementation_plan:
  allowed_location: feature_lab/<feature_id>/
  production_files_touched: []
  experimental_outputs:
    - feature_lab/<feature_id>/accepted_snapshot.csv

validation_plan:
  - coverage, missingness, and first/latest valid date
  - leakage audit
  - redundancy audit
  - expected direction review

classification:
  historical_use: safe_for_backtest | research_only | current_context_only
  live_sentiment_or_headline: false
  point_in_time_archive_required: false

production_promotion_status:
  allowed_without_human_approval: false
  human_approval_required_for:
    - production feature construction
    - dashboard integration
    - protected file edits
```

## Field Rules

- `feature_id` must match a backlog entry in `feature_backlog/feature_ideas.yaml`.
- `source_type` must be one of `prior_iteration_failure`, `dashboard_blind_spot`, `research_source`, or `market_mechanism`.
- `raw_inputs` must distinguish exact existing inventory columns from desired future data.
- `formula` must be deterministic and must not rely on future returns or future event membership.
- `data_source` must state whether the source is already available, experimental-only, or a future requirement.
- `point_in_time_risk` must explicitly discuss release timing, revisions, survivorship, and current-only data.
- `redundancy_check.related_existing_columns` must use exact current inventory column names when known.
- Live sentiment or headline-derived features must set `historical_use: current_context_only` unless a historical point-in-time archive exists.
- `production_files_touched` must remain empty unless a human has explicitly approved production scope.

## Promotion Boundary

A complete feature spec can support feasibility review and experimental work. It cannot authorize production dashboard or production feature-construction changes. Human approval is required before any accepted feature moves into protected production code.
