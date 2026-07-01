# Iteration 002 Prior Results Summary

## Source files read

- `README.md`
- `FEATURE_UNIVERSE.md`
- `program_hypothesis_generation.md`
- `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv`
- `outputs/qqq_r2_mmdi_v1_3_1_feature_catalog.csv`
- `outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv`
- `outputs/hypothesis_tests/hypothesis_test_summary.csv`
- `outputs/hypothesis_tests/hypothesis_test_folds.csv`

`outputs/hypothesis_combinations/combination_test_summary.csv` was requested if present, but the directory/file was not present at iteration start.

## Evidence-over-claims snapshot

Prior hypothesis tests covered 4,651 eligible validation days from 2008-01-02 through 2026-06-29. The prior runner used purged yearly folds with expanding training windows and fixed hypothesis trigger templates.

| Hypothesis | Theme | Horizon | Alert burden | Base hit rate | Alert hit rate | Lift | Event coverage | False calm days |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| H001 | Downside range/volatility path risk | 30BD | 9.59% | 15.29% | 34.98% | 2.29x | 37.65% | 555 |
| H004 | Cross-asset acute shock | 15BD | 9.55% | 18.79% | 38.06% | 2.03x | 42.54% | 705 |
| H002 | Narrow leadership fragility | 60BD | 12.64% | 17.46% | 32.65% | 1.87x | 62.07% | 620 |
| H003 | False repair | 30BD | 3.96% | 15.29% | 17.93% | 1.17x | 17.65% | 678 |
| H005 | Distribution/liquidity after advance | 60BD | 0.28% | 17.46% | 0.00% | 0.00x | 5.17% | 812 |

## Yearly fold stability evidence

The yearly fold table showed uneven stability. H004 had positive lift in 9 of 19 folds and H002 also had positive lift in 9 of 19 folds. H001 had positive lift in 5 of 19 folds. H003 had positive lift in 4 of 19 folds. H005 had no positive-lift folds among 19 yearly folds and should be treated as failed in its prior form.

## Map-territory corrections

- The map: the drafted hypotheses suggested all five mechanisms were plausible.
- The territory: prior test output shows only H001, H004, and H002 had meaningful lift or event coverage. H003 was weak, and H005 was ineffective.
- Updated model: iteration_002 should keep the high-signal volatility and cross-asset themes, tighten the high-burden narrow-leadership theme, and replace or materially revise false-repair and distribution ideas.

## Pre-mortem risks for iteration_002

This research iteration would fail if:

- It copied the best prior triggers unchanged and called that learning.
- It searched thresholds after seeing results, creating hidden optimization.
- It used placeholder breadth or live sentiment columns as historical features.
- It improved alert hit rate by making alerts too rare to cover events.
- It reported row-level lift without event coverage, false calm, and yearly stability.

Mitigations used in this iteration:

- Keep all feature names copied from `all_feature_inventory.csv`.
- Use deterministic quantile logic only inside training folds; no parameter search.
- Require event coverage, false calm, lead time, and yearly stability in output metrics.
- Keep all new code in `qqq_autoresearch/hypothesis_tests_iteration_002.py` plus a separate CLI.

## Design direction for iteration_002

1. Revise H001 into a downside-volatility continuation signal by requiring short trend pressure in addition to range/volatility stress.
2. Revise H004 into a cross-asset acute-shock signal that separates credit stress from the confirming vol/rates/dollar shock.
3. Revise H002 into a tighter narrow-leadership signal that requires leadership divergence plus semiconductor or MMDI leadership non-confirmation.
4. Revise H003 into a false-repair signal that requires indicator repair, unresolved price damage, and renewed tape stress.
5. Replace H005 with an R2 false-calm / MMDI acceleration hypothesis, because the prior distribution/liquidity version had essentially no useful hit rate.
