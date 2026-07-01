# iteration_004_fd001 Decision Log

## Decisions

| Hypothesis | Decision | Rationale |
|---|---|---|
| `FD001_H002_VOL_TERM_PERSISTENT_ACUTE_STRESS` | keep_for_rewrite | Best aggregate evidence: 1.46x lift and 66.06% event coverage, but 17.39% burden and 8/19 positive-lift folds prevent dashboard candidacy. |
| `FD001_H003_VOL_DISAGREEMENT_REGIME_SHIFT` | rewrite_as_context | Low burden and 10BD median lead are interesting, but 1.08x lift and 4/19 positive-lift folds are weak. |
| `FD001_H004_FALSE_CALM_VOL_DISAGREEMENT_CONFIRMATION` | drop_as_direct_trigger | Low burden and 12BD median lead, but sub-base lift and 17.65% event coverage. |
| `FD001_H001_FALSE_CALM_CONFIRMED_DOWNSIDE` | drop_as_direct_trigger | 0.80x lift and 13.93% burden show confirmed false-calm is not useful as a direct trigger in this formulation. |

## Lessons

- FD_001 vol-term persistence is the strongest acute-shock research direction, but needs burden reduction and fold-stability improvement.
- FD_001 false-calm features did not work as direct alert triggers, even with confirmed deterioration.
- Volatility disagreement may be useful as an overlay or context surface, not a standalone trigger.
- No candidate qualifies for shadow dashboard evaluation or production proposal.
