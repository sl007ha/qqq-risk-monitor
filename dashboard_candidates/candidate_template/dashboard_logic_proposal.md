# Dashboard Logic Proposal Template

## Candidate ID

`YYYY-MM-DD_candidate_name`

## Source Hypotheses

- `HYPOTHESIS_ID`: short role in candidate

## Research Evidence

| Metric | Value | Source file |
|---|---:|---|
| alert_days |  |  |
| alert_burden |  |  |
| base_rate_lift |  |  |
| event_coverage |  |  |
| positive_lift_folds |  |  |
| median_lead |  |  |

## Candidate Rule Summary

Describe the deterministic shadow rule in plain English. Do not change production dashboard logic in this proposal.

## Exact Feature Columns

List only feature columns verified against `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv`.

## Dashboard Display Proposal

Describe where the shadow signal would appear, what label it would use, and how it should be interpreted by a human user.

## Comparison Versus Current Dashboard

Explain how this candidate differs from the current R2/MMDI dashboard and what incremental decision-support value it adds.

## Known Failure Modes

List conditions where the candidate may over-alert, under-alert, or lag the risk event.

## Human Approval Status

Production implementation approval: not requested.
