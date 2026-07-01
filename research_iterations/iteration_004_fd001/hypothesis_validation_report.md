# iteration_004_fd001 Hypothesis Validation Report

## Scope

This validation converts `hypothesis_registry/fd_001_feature_to_hypothesis_plan.yaml` into concrete research-only hypotheses for deterministic test implementation.

No hypothesis tests were run in this stage.

## Validation Checks

All four FD_001 hypothesis candidates passed:

- source columns exist in the FD_001 combined snapshot;
- source columns are all `candidate_hypothesis_design`;
- context columns are all `context_only`;
- descriptive columns are all `descriptive_only`;
- diagnostics columns are all `episode_diagnostics_only`;
- targets include horizon, event definition, and threshold;
- trigger rules are deterministic;
- thresholds are pre-declared;
- no context-only column is used as a standalone trigger;
- no diagnostics-only column is used as a direct trigger;
- no future, target, label, outcome, or forward-looking feature column is referenced as an input;
- each candidate states why it is not a duplicate of a rejected hypothesis.

## Validated Hypotheses

| Hypothesis | Target | Validation status | Notes |
|---|---|---|---|
| `FD001_H001_FALSE_CALM_CONFIRMED_DOWNSIDE` | 30BD MDD <= -8% | passed | Confirmed false-calm burden-reduction candidate |
| `FD001_H002_VOL_TERM_PERSISTENT_ACUTE_STRESS` | 15BD MDD <= -5% | passed | Acute vol-term stress candidate with shorter coverage caveat |
| `FD001_H003_VOL_DISAGREEMENT_REGIME_SHIFT` | 30BD MDD <= -8% | passed | Regime-shift volatility disagreement candidate |
| `FD001_H004_FALSE_CALM_VOL_DISAGREEMENT_CONFIRMATION` | 30BD MDD <= -8% | passed | False-calm plus vol-disagreement confirmation candidate |

## Validator Evidence

`validate_hypothesis_plan.py` passed with candidate count 4 and the expected hypothesis ids before this report was written.

The concrete hypotheses are written to `research_iterations/iteration_004_fd001/hypotheses.yaml`.
