# No Shadow Dashboard Candidate From iteration_004_fd001

## Decision

No FD_001-derived hypothesis from `iteration_004_fd001` qualifies for a shadow dashboard candidate.

## Evidence

The strongest candidate was `FD001_H002_VOL_TERM_PERSISTENT_ACUTE_STRESS`:

- lift: 1.46x
- alert burden: 17.39%
- event coverage: 66.06%
- positive-lift folds: 8/19
- median lead time: 1BD

This is useful research evidence, but the burden is high, fold stability is weak, and lead time is short.

Other candidates did not qualify:

- `FD001_H003_VOL_DISAGREEMENT_REGIME_SHIFT`: weak lift and only 4/19 positive-lift folds.
- `FD001_H004_FALSE_CALM_VOL_DISAGREEMENT_CONFIRMATION`: lift below base rate and low event coverage.
- `FD001_H001_FALSE_CALM_CONFIRMED_DOWNSIDE`: lift below base rate and high burden.

## Why Not Production

This was a research-only dry run. No candidate met combined evidence gates for lift, alert burden, event coverage, fold stability, and lead time.

Production dashboard promotion remains human-approval-gated and was not attempted.

## Next Recommended Action

Rewrite `FD001_H002_VOL_TERM_PERSISTENT_ACUTE_STRESS` to reduce burden and improve yearly fold stability while preserving acute-shock event coverage.
