# FD_001 Feature-To-Hypothesis Plan

## Parent Snapshot

- Snapshot id: `FD_001_combined`
- Snapshot path: `feature_lab/FD_001_combined/`
- Latest date: 2026-06-30
- Candidate trigger columns used only from `candidate_hypothesis_design`
- Context, descriptive, and diagnostics columns carried only as companions

## Candidate Hypotheses

### FD001_H001_FALSE_CALM_CONFIRMED_DOWNSIDE

Mechanism: confirmed false-calm internal deterioration during quiet R2 states should identify under-reported downside pressure.

Source trigger columns:

- `freq_003_false_calm_confirmed_flag`
- `freq_003_false_calm_internal_deterioration_count`

Pre-declared trigger:

```text
freq_003_false_calm_confirmed_flag == 1
and freq_003_false_calm_internal_deterioration_count >= 3
```

Target: 30BD forward maximum drawdown <= -8%.

Why not duplicate: this uses the FD_001 confirmed false-calm feature instead of the broader I003_H005 independent-confirmation structure that carried high burden.

### FD001_H002_VOL_TERM_PERSISTENT_ACUTE_STRESS

Mechanism: persistent front-end volatility term stress signals acute hedging demand and unstable risk appetite.

Source trigger columns:

- `freq_007_vol_term_daily_stress_count`
- `freq_007_vol_term_stress_persistence_5d`
- `freq_007_vol_term_stress_persistence_20d`

Pre-declared trigger:

```text
freq_007_vol_term_daily_stress_count >= 2
and freq_007_vol_term_stress_persistence_5d >= 0.60
and freq_007_vol_term_stress_persistence_20d >= 0.35
```

Target: 15BD forward maximum drawdown <= -5%.

Why not duplicate: this tests a new FD_001 volatility-term persistence surface rather than a rejected false-repair or leadership standalone structure.

### FD001_H003_VOL_DISAGREEMENT_REGIME_SHIFT

Mechanism: elevated volatility disagreement can indicate a regime shift where risk pricing is unstable before price damage is obvious.

Source trigger columns:

- `freq_008_vol_disagreement_score_pct`
- `freq_008_vol_disagreement_rank_change_20d`
- `freq_008_vol_disagreement_flag`

Pre-declared trigger:

```text
freq_008_vol_disagreement_flag == 1
and freq_008_vol_disagreement_score_pct >= 0.90
and freq_008_vol_disagreement_rank_change_20d >= 0.50
```

Target: 30BD forward maximum drawdown <= -8%.

Why not duplicate: this is not the rejected I003_H002 cross-asset burden-reduction variant or the rejected I003_H003 standalone leadership trigger.

### FD001_H004_FALSE_CALM_VOL_DISAGREEMENT_CONFIRMATION

Mechanism: possible false-calm deterioration becomes more actionable when volatility disagreement confirms unstable risk pricing.

Source trigger columns:

- `freq_003_false_calm_possible_flag`
- `freq_003_false_calm_internal_deterioration_count`
- `freq_008_vol_disagreement_score_pct`

Pre-declared trigger:

```text
freq_003_false_calm_possible_flag == 1
and freq_003_false_calm_internal_deterioration_count >= 2
and freq_008_vol_disagreement_score_pct >= 0.85
```

Target: 30BD forward maximum drawdown <= -8%.

Why not duplicate: this narrows the broader false-calm theme with FD_001 volatility-disagreement confirmation and preserves missingness as uncertainty.

## Validation Plan

Each candidate will be validated with expanding yearly walk-forward folds, a target-horizon purge before each test year, and pre-declared deterministic thresholds only.

Metrics:

- alert burden
- base hit rate
- alert hit rate
- lift
- event coverage
- false calm reduction
- fold stability
- median lead time

## Not To Do

- Do not run tests during planning.
- Do not optimize thresholds.
- Do not use context-only columns as standalone triggers.
- Do not use diagnostics-only columns as direct triggers.
- Do not use live sentiment historically.
- Do not use future labels as inputs.
