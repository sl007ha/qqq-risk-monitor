# Hypothesis Registry

The hypothesis registry tracks the lifecycle of QQQ Risk Monitor research hypotheses across iterations.

## Lifecycle States

- `draft`: proposed but not implemented.
- `active`: tested and worth keeping for another iteration.
- `rewrite`: mechanism remains plausible, but trigger logic or target definition needs revision.
- `promoted_candidate`: strong enough to become a shadow dashboard candidate, pending human review.
- `rejected`: exact formulation should not be reused.
- `context_only`: useful as explanatory context, but not selective enough as an alert.

## Required Metadata

Each registered hypothesis should preserve:

- hypothesis ID
- source iteration
- title
- mechanism
- exact feature columns used
- target horizon and target type
- trigger summary
- latest test evidence
- lifecycle state
- rewrite/drop/promotion rationale
- future data requirements

## Feature Integrity

`exact_feature_columns_used` must only contain columns copied verbatim from:

```text
outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv
```

Unavailable desired features belong in `future_data_requirement`, not in exact feature lists.

## Failure Preservation

Rejected hypotheses should remain in the registry with their failure reason. Do not delete poor performers. Their main value is to prevent repeated dead ends and hidden survivorship bias.
