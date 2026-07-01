# QQQ Risk Monitor Research Loop Program

This document defines the Codex-driven research loop for QQQ Risk Monitor. The loop is research-only until a human explicitly approves a dashboard promotion.

## Loop Overview

```text
feature pull
-> feature validation
-> hypothesis generation
-> hypothesis validation
-> trigger implementation
-> walk-forward tests
-> analysis
-> decision log
-> dashboard candidate
-> next iteration
```

## 1. Feature Pull

Run the dashboard pipeline to refresh exported feature tables:

```text
python run_dashboard.py --output-dir outputs
```

Required feature artifacts:

- `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv`
- `outputs/qqq_r2_mmdi_v1_3_1_feature_catalog.csv`
- `outputs/qqq_r2_mmdi_v1_3_1_feature_snapshot_latest.csv`
- `outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv`

## 2. Feature Validation

Before using any feature:

- confirm the column exists in `all_feature_inventory.csv`
- confirm coverage, first valid date, and latest valid date
- exclude placeholders or zero-coverage features from `exact_feature_columns_used`
- exclude live sentiment from historical testing unless point-in-time archives exist
- document any desired unavailable features as `future_data_requirement`

## 3. Hypothesis Generation

Generate hypotheses from mechanism first, feature mapping second. Each hypothesis must define:

- market mechanism
- exact feature columns
- target type and target horizon
- deterministic trigger pseudocode
- expected direction
- leakage risks
- validation plan

Hypotheses must target future QQQ drawdown risk, path risk, repair failure, acute shock, cross-asset stress, or narrow-leadership fragility.

## 4. Hypothesis Validation

Validate the hypothesis specification before implementation:

- exactly declared feature columns
- no unavailable future data
- no invented features
- no live sentiment backtest use
- no threshold optimization
- clear target definition

## 5. Trigger Implementation

Implement research-only deterministic trigger logic in a new isolated module, for example:

```text
qqq_autoresearch/hypothesis_tests_iteration_00N.py
run_hypothesis_tests_iteration_00N.py
```

Do not modify production dashboard logic or protected files.

## 6. Walk-Forward Tests

Run purged walk-forward tests. Minimum metrics:

- alert burden
- base hit rate
- alert hit rate
- base-rate lift
- event coverage
- false calm
- yearly fold stability
- lead-time if available

Test outputs should be written under the iteration folder.

## 7. Analysis

Write a plain-English analysis that separates:

- what improved
- what failed
- what is ambiguous
- what should be kept, rewritten, dropped, or promoted to shadow dashboard candidate

Claims must cite generated file or terminal evidence.

## 8. Decision Log

Each iteration should update a decision record with:

- active hypotheses
- promoted candidates
- rewritten hypotheses
- rejected hypotheses
- failed ideas and lessons learned
- next planned task

`research_loop/research_state.yaml` is the lightweight repository-level state file.

## 9. Dashboard Candidate

A dashboard candidate is not production code. It is a shadow proposal with evidence. It should include:

- candidate rationale
- source hypothesis IDs
- test evidence
- expected dashboard behavior
- risks and failure modes
- human approval status

Dashboard candidate material belongs under `dashboard_candidates/`.

## 10. Next Iteration

Every iteration ends with a next-iteration plan. The next plan should preserve evidence from failed hypotheses and state the next cheapest discriminating test.
