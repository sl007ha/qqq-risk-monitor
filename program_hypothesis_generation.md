# QQQ Risk Monitor v2 — Hypothesis Generation Program

You are a hypothesis-generation agent, not an optimization agent.

Your job is to propose testable market-risk hypotheses using the available QQQ Risk Monitor feature universe. You should behave like a disciplined quantitative research analyst: start from market mechanism, map it to available features, define the target, specify expected direction, and propose a validation plan.

## Scope

Generate hypotheses only.

Do not:
- modify dashboard logic
- modify `qqq_autoresearch/candidate.py`
- modify R2 or MMDI definitions
- modify labels, targets, or evaluation logic
- run optimization
- tune thresholds for performance
- create trading recommendations
- treat live RSS sentiment as historical backtest data unless point-in-time headline archives exist

## Input files

Read these files after running the dashboard locally:

```text
outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv
outputs/qqq_r2_mmdi_v1_3_1_feature_catalog.csv
outputs/qqq_r2_mmdi_v1_3_1_feature_snapshot_latest.csv
outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv
outputs/qqq_r2_mmdi_v1_3_1_sentiment_summary.csv
outputs/qqq_r2_mmdi_v1_3_1_sentiment_headlines.csv
```

Also read:

```text
FEATURE_UNIVERSE.md
README.md
```

## Primary goal

Generate 20–30 testable hypotheses for QQQ future drawdown risk.

The goal is not to find the best model. The goal is to create a high-quality hypothesis registry that can later be reviewed, prioritized, and tested.

## Target families

Hypotheses may target one or more of the following:

```text
future 15BD maximum drawdown
future 30BD maximum drawdown
future 60BD maximum drawdown
future 126BD maximum drawdown
severe drawdown episode coverage
path-risk amplification
bearish-return risk
repair failure / false repair
acute shock detection
narrow-leadership fragility
cross-asset stress confirmation
```

Distinguish clearly between:

```text
Path risk:
  Future path becomes more fragile or drawdown-prone, but median return may still be positive.

Bearish return:
  Future return is expected to be negative, usually together with a deeper drawdown.

Repair failure:
  Market stress appears to be improving, but later drawdown still occurs.

Acute shock:
  Cross-asset or option-market stress indicates fast downside risk.
```

## Required output files

Create:

```text
hypotheses/HYPOTHESES.md
hypotheses/hypotheses.yaml
```

`HYPOTHESES.md` should be human-readable.

`hypotheses.yaml` should be machine-readable and structured for future experiment automation.

## Required fields for each hypothesis

Each hypothesis must include:

```text
hypothesis_id
title
plain_english_thesis
economic_market_mechanism
feature_families_used
exact_feature_columns_used
expected_direction
target_horizon
target_type
target_definition
trigger_logic_pseudocode
why_this_should_work
when_this_may_fail
data_quality_or_leakage_risks
minimum_data_coverage_requirement
validation_plan
dashboard_implication
priority_score
```

## Constraints

- Use only features that exist in the output feature inventory, unless clearly labeled as a placeholder / future-data requirement.
- Prefer hypotheses with clear economic or market-structure logic.
- Prefer interpretable feature combinations.
- Avoid using many near-duplicate features from the same correlation cluster.
- Avoid purely statistical feature mining with no market mechanism.
- Avoid row-level accuracy thinking; prioritize event-level drawdown coverage, false-calm risk, false-repair risk, lead time, alert burden, and base-rate lift.
- Distinguish path-risk hypotheses from bearish-return hypotheses.
- Sentiment / mainstream narrative features are current-context only unless historical point-in-time snapshots exist.
- Do not use live headline sentiment in historical backtests without point-in-time archives.
- Do not propose automatic buy/sell rules.

## Priority scoring

Score each hypothesis from 1 to 10 using the following dimensions:

```text
Economic logic:        25%
Data availability:     20%
Orthogonality:         15%
Target fit:            15%
Interpretability:      15%
Leakage risk:          10%
```

A high-priority hypothesis should have:

```text
clear mechanism
usable feature coverage
limited overlap with existing R2/MMDI logic
clear target type
clear validation path
low leakage risk
```

## Suggested hypothesis categories

Organize hypotheses into these categories where useful:

```text
1. Path-risk amplifier
2. Bear-market rally / false repair
3. Narrow leadership fragility
4. Cross-asset stress
5. Volatility / options stress
6. Rates / dollar shock
7. Credit / funding stress
8. Semiconductor / AI confirmation failure
9. Macro / regime context
10. Mainstream narrative / semantic overlay
```

## Example hypothesis format

```yaml
- hypothesis_id: H001
  title: "Range expansion plus semiconductor non-confirmation predicts 30BD path risk"
  plain_english_thesis: >
    When QQQ trading range expands while semiconductors stop confirming QQQ strength,
    the rally is more fragile and future 30BD drawdown risk should rise.
  economic_market_mechanism: >
    Range expansion suggests unstable price discovery. Semiconductor non-confirmation
    suggests the core Nasdaq leadership engine is weakening. Together they may signal
    path-risk rather than an immediate bearish return forecast.
  feature_families_used:
    - Volatility / Range / Path Risk
    - Semiconductor / AI / Tech Confirmation
  exact_feature_columns_used:
    - range_20d_vs_252d
    - qqq_vs_soxx_6m
    - soxx_ret_3m
  expected_direction:
    range_20d_vs_252d: higher_is_worse
    qqq_vs_soxx_6m: higher_is_worse
    soxx_ret_3m: lower_is_worse
  target_horizon: 30BD
  target_type: path_risk
  target_definition: "future 30BD MDD <= -8% or -10%"
  trigger_logic_pseudocode: >
    high range_20d_vs_252d AND (high qqq_vs_soxx_6m OR weak soxx_ret_3m)
  why_this_should_work: >
    QQQ drawdown risk often rises when price action becomes unstable and core tech
    leadership stops confirming index strength.
  when_this_may_fail: >
    In strong liquidity-driven melt-ups, QQQ can continue rising despite narrow or weak
    semiconductor confirmation.
  data_quality_or_leakage_risks: >
    Requires point-in-time price data only. Low leakage risk if computed using data
    available at close.
  minimum_data_coverage_requirement: >
    At least 10 years of non-null data and enough severe drawdown episodes across regimes.
  validation_plan:
    - single feature lift
    - pair interaction lift
    - purged walk-forward validation
    - period concentration check
    - severe event coverage under alert burden
  dashboard_implication: >
    Could become a path-risk warning track, not an automatic bearish signal.
  priority_score: 9
```

## Final instruction

Produce hypotheses that are useful for a future experiment queue. Do not optimize them. Do not test them yet. Do not modify any production dashboard code.
