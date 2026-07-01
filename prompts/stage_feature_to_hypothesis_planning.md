# Codex Stage Task: {{stage}}

Use Superpowers and evidence-over-claims.

Task ID: {{task_id}}
Title: {{title}}

## Objective

{{objective}}

## Inputs

{{inputs}}

## Required Outputs

{{outputs}}

## Allowed Files

{{allowed_files}}

## Blocked Files

{{blocked_files}}

## Gates

{{gates}}

## Validators

{{validators}}

## Hard Contract

- Generate planning artifacts only.
- Generate at most 5 hypothesis candidates.
- Do not run hypothesis tests.
- Do not implement test runners.
- Do not modify production dashboard logic.
- Do not modify production feature construction.
- Do not optimize thresholds.
- Use only frozen `candidate_hypothesis_design` columns as trigger candidates.
- Carry `context_only`, `descriptive_only`, and `episode_diagnostics_only` columns only as companions.
- Do not use context-only features as standalone triggers.
- Do not use diagnostics-only features as direct triggers.
- Do not use live sentiment historically.
- Do not use future labels, future returns, future drawdowns, event files, or hypothesis outputs as inputs.

## Required Hypothesis Candidate Schema

Each candidate in `hypothesis_registry/fd_001_feature_to_hypothesis_plan.yaml` must include:

- `hypothesis_id`
- `parent_feature_snapshot_id`
- `source_feature_columns`
- `context_columns`
- `descriptive_columns`
- `diagnostics_columns`
- `parent_hypothesis_or_rewrite_queue_item`
- `economic_mechanism`
- `target`
  - `horizon_bd`
  - `event_definition`
  - `threshold`
- `trigger_rule`
  - deterministic formula
  - thresholds predeclared
  - no threshold optimization
- `expected_direction`
- `validation_plan`
  - walk-forward design
  - purging / embargo assumptions
  - metrics:
    - alert burden
    - base hit rate
    - alert hit rate
    - lift
    - event coverage
    - false calm reduction
    - fold stability
    - median lead time
- `sample_and_coverage_caveats`
- `why_not_duplicate_of_rejected_hypothesis`
- `dashboard_relevance`
- `not_to_do`
  - do not use context-only as standalone trigger
  - do not use diagnostics-only as direct trigger
  - do not use live sentiment historically
  - do not use future labels

## Required Outputs

Write exactly these planning artifacts:

- `hypothesis_registry/fd_001_feature_to_hypothesis_plan.yaml`
- `feature_research/FD_001/feature_to_hypothesis_plan.md`

The Markdown plan must summarize:

- the frozen parent snapshot id and date range;
- which candidate columns were used;
- which context/descriptive/diagnostic columns were carried only as companions;
- why each candidate is not a duplicate of a rejected hypothesis;
- what a later validation stage would test;
- confirmation that no tests were run.

## Machine Context

Task YAML:

```yaml
{{task_yaml}}
```

Research state summary:

```yaml
{{research_state_summary}}
```
