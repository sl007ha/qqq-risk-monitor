# Codex Prompt — Superpowers-style Hypothesis Generation Test

Use this prompt in Codex after installing / enabling Superpowers.

Superpowers skills that are relevant for this task:

- brainstorming: clarify the objective and avoid jumping directly to implementation;
- writing-plans: create a compact plan before writing outputs;
- systematic-debugging / evidence-over-claims discipline: verify feature names against the inventory;
- verification-before-completion: check that every feature in `exact_feature_columns_used` exists.

## Task

Work in the `qqq-risk-monitor` repository.

Read:

```text
program_hypothesis_generation.md
FEATURE_UNIVERSE.md
outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv
outputs/qqq_r2_mmdi_v1_3_1_feature_catalog.csv
outputs/qqq_r2_mmdi_v1_3_1_feature_snapshot_latest.csv
outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv
```

Write exactly 5 high-quality QQQ drawdown-risk hypotheses.

Output:

```text
hypotheses/CODEX_SUPERPOWERS_TEST.md
```

## Hard constraints

- Use exact feature column names copied from `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv`.
- Do not invent features.
- Do not use external one-off event narratives.
- Do not use ETF inflow, AI-sector index, or custom risk-appetite index unless the exact column exists.
- Each hypothesis must target future drawdown risk, path-risk, repair failure, acute shock, or narrow leadership fragility.
- Each hypothesis must contain: target, thesis, mechanism, exact features, expected direction, trigger pseudocode, failure mode, data/leakage risk, validation plan, dashboard implication, priority score.
- Sentiment may be used only as current-context overlay unless historical point-in-time archives exist.

## Quality bar

Reject any hypothesis if:

- any feature name is not in the inventory;
- target is outperformance or momentum rather than drawdown/path-risk;
- expected direction still contains placeholder text;
- validation plan does not include event coverage, alert burden, base-rate lift, false repair, false calm, or walk-forward validation;
- thesis cannot be explained in plain English.
