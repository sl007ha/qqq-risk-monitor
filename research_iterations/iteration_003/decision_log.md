# Iteration 003 Decision Log

## Decision Summary

| Hypothesis | Decision | Evidence | Next action |
|---|---|---|---|
| I003_H001 | Keep as comparison candidate, but do not replace I002_H001 | 2.45x lift, 9.65% burden, 40.00% coverage, 6/19 positive-lift folds | Compare against I002_H001 in future combination or episode-level tests |
| I003_H002 | Drop this exact variant | Burden fell to 11.70%, but lift, coverage, stability, and lead time all worsened versus I002_H002 | Preserve cross-asset theme, rewrite from mechanism if revisited |
| I003_H003 | Demote to coverage overlay / rewrite candidate | 77.59% event coverage but 23.67% burden and only 1.55x lift | Use only as evidence that relaxed leadership logic sees events; require a stricter second-stage gate if retested |
| I003_H004 | Reject | 0.19x lift, 0.00% event coverage, 0/19 positive-lift folds | Stop retesting this same false-repair structure against the same target |
| I003_H005 | Keep as active rewrite candidate | Improved predecessor: 1.45x lift, 16.08% burden, 67.06% coverage, 10/19 positive-lift folds, 5.0BD median lead | Focus next iteration on reducing burden without threshold optimization |

## Promotion Status

No hypothesis is promoted to production dashboard logic. Human approval remains required before any dashboard candidate becomes production work.

## Preserved Failed Lessons

- I003_H004 shows that removing the renewed-tape-stress gate did not rescue the false-repair idea. The failure is not just over-constraint; the current feature/target pairing appears anti-predictive or poorly timed.
- I003_H003 shows that leadership breadth relaxation can cover many drawdown events, but broad coverage alone is not enough when alert burden overwhelms selectivity.
- I003_H002 shows that lowering alert burden in cross-asset stress is not useful if lead time remains 0BD and stability worsens.

## Active Research Queue After Iteration 003

1. I002_H001 / I003_H001 downside-volatility comparison.
2. I002_H002 cross-asset acute-shock baseline, but not the I003_H002 rewrite.
3. I002_H003 low-burden narrow-leadership baseline.
4. I003_H005 stricter false-calm overlay as the main iteration 004 rewrite candidate.

## Dashboard Candidate Status

No dashboard candidate is created in this iteration. The closest shadow candidate is I003_H005 as a contextual false-calm overlay, but burden remains too high for promotion discussion.
