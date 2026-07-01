# Iteration 003 Prior Results Summary

## Starting State

Iteration 003 starts from `research_loop/research_state.yaml`, which defines the allowed research-only scope:

- `research_iterations/iteration_003/`
- `qqq_autoresearch/hypothesis_tests_iteration_003.py`
- `run_hypothesis_tests_iteration_003.py`

Protected scope remains unchanged:

- `qqq_autoresearch/data_sources.py`
- `qqq_autoresearch/features.py`
- `qqq_autoresearch/config.py`
- production dashboard logic

## Iteration 002 Evidence

The prior evidence comes from `research_iterations/iteration_002/analysis.md` and `research_iterations/iteration_002/tests/iteration_002_hypothesis_test_summary.csv`.

| Hypothesis | Mechanism | Alert burden | Base hit rate | Alert hit rate | Lift | Event coverage | False calm events | Positive lift folds | Median lead |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| I002_H001 | Downside volatility / short-trend pressure | 7.50% | 15.29% | 39.54% | 2.59x | 40.00% | 51 | 5/19 | 3.0BD |
| I002_H002 | Cross-asset acute shock | 16.04% | 18.79% | 37.00% | 1.97x | 52.24% | 64 | 11/19 | 0.0BD |
| I002_H003 | Narrow-leadership non-confirmation | 5.16% | 17.46% | 39.17% | 2.24x | 31.03% | 40 | 6/19 | 13.5BD |
| I002_H005 | R2 quiet / MMDI accelerating false calm | 24.64% | 15.29% | 15.27% | 1.00x | 62.35% | 32 | 8/19 | 2.0BD |
| I002_H004 | Indicator repair / unresolved damage / renewed stress | 1.08% | 15.29% | 0.00% | 0.00x | 0.00% | 85 | 0/19 | n/a |

## Lessons Carried Forward

1. **Keep the downside-volatility mechanism, but test a less brittle trend-pressure condition.** I002_H001 had the strongest aggregate lift but only 5/19 positive-lift folds.
2. **Keep the cross-asset mechanism, but split early deterioration from same-day shock confirmation.** I002_H002 had the best fold stability but high alert burden and 0BD median lead time.
3. **Keep narrow-leadership fragility, but test a coverage companion.** I002_H003 had useful lift and lead time but only 31.03% event coverage.
4. **Rewrite false repair instead of dropping the economic idea.** I002_H004 was over-constrained and produced no hits.
5. **Demote broad false calm to a second-stage overlay.** I002_H005 covered many events but had no lift as a standalone alert.

## Iteration 003 Research Design

Iteration 003 generates five pre-declared hypotheses. It does not optimize thresholds. Trigger thresholds are deterministic training-window quantiles or fixed economic constants. No live sentiment or headline features are used.
