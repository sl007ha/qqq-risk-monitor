# iteration_004_fd001 Evidence Analysis

## Executive Readout

This closed-loop dry run tested four FD_001-derived research-only hypotheses from the frozen `FD_001_combined` feature snapshot.

Only `FD001_H002_VOL_TERM_PERSISTENT_ACUTE_STRESS` produced a clearly positive aggregate lift, with 1.46x alert hit-rate lift, 66.06% event coverage, and 1BD median lead time. However, alert burden was 17.39%, positive-lift folds were only 8/19, and coverage starts in the VIX9D-era sample. This is useful research evidence, but not enough for production or a shadow dashboard candidate.

The false-calm hypotheses did not improve hit-rate lift:

- `FD001_H001_FALSE_CALM_CONFIRMED_DOWNSIDE`: 0.80x lift, 13.93% burden, 48.78% event coverage.
- `FD001_H004_FALSE_CALM_VOL_DISAGREEMENT_CONFIRMATION`: 0.87x lift, 2.26% burden, 17.65% event coverage.

`FD001_H003_VOL_DISAGREEMENT_REGIME_SHIFT` was low burden and had long median lead time, but aggregate lift was weak at 1.08x and only 4/19 folds had positive lift.

## Summary Metrics

| Hypothesis | Lift | Burden | Event coverage | Positive lift folds | Median lead |
|---|---:|---:|---:|---:|---:|
| `FD001_H002_VOL_TERM_PERSISTENT_ACUTE_STRESS` | 1.46 | 17.39% | 66.06% | 8/19 | 1BD |
| `FD001_H003_VOL_DISAGREEMENT_REGIME_SHIFT` | 1.08 | 5.07% | 31.76% | 4/19 | 10BD |
| `FD001_H004_FALSE_CALM_VOL_DISAGREEMENT_CONFIRMATION` | 0.87 | 2.26% | 17.65% | 4/19 | 12BD |
| `FD001_H001_FALSE_CALM_CONFIRMED_DOWNSIDE` | 0.80 | 13.93% | 48.78% | 7/19 | 3BD |

## Pass / Fail Decisions

### Keep For Rewrite: FD001_H002

H002 passed aggregate lift and event coverage, but failed stability and burden standards for direct dashboard consideration.

Reasons to keep:

- Best aggregate lift: 1.46x.
- Strong event coverage: 72/109 events, or 66.06%.
- False-calm events reduced by the same event-coverage share.
- Acute-shock target is mechanistically consistent with vol-term persistence.

Reasons not to promote:

- Alert burden is 17.39%, above a comfortable dashboard candidate threshold.
- Only 8/19 yearly folds had positive lift.
- Median lead is only 1BD.
- Source coverage is 56.43%, concentrated after VIX9D history begins.

### Rewrite / Context Only: FD001_H003

H003 is potentially useful as path-risk context because it had 5.07% burden and 10BD median lead time, but aggregate lift was only 1.08x and positive-lift folds were 4/19.

This should not become a direct alert. A future rewrite could use volatility disagreement as a confirmation overlay for an already-stronger risk trigger.

### Drop As Direct Triggers: FD001_H001 And FD001_H004

Both false-calm variants failed the primary lift test.

H001 had reasonable event coverage but weak lift and high burden. H004 had low burden and longer lead time but too little coverage and sub-base hit rate. FD_001 false-calm features did not improve false-calm detection as direct triggers in this test.

## Research Questions Answered

Did FD_001 experimental features improve false-calm detection?

No. The two false-calm direct triggers had lift below 1.0. H004 may be useful as a diagnostic or rewrite ingredient because it is low burden and has longer lead among covered events, but it should not be used as a direct alert.

Did FD_001 experimental features improve path-risk detection?

Only weakly. H003 had low burden and long lead, but event coverage and fold stability were insufficient. Treat volatility disagreement as context or an overlay candidate, not a standalone alert.

Did FD_001 experimental features improve acute-shock detection?

Partially. H002 improved aggregate acute-shock lift and event coverage, but the burden and fold stability are not strong enough for dashboard proposal.

Are results stable across yearly folds?

No candidate had enough yearly stability. H002 had positive lift in 8/19 folds; H001 had 7/19; H003 and H004 each had 4/19.

Are results regime-concentrated?

Likely yes for H002 because source coverage begins in 2011 and relies on volatility-term data. The volatility disagreement candidates begin earlier but still show uneven yearly fold performance.

Did alert burden remain acceptable?

H003 and H004 had acceptable burden, but weak lift and coverage. H002 and H001 were too high-burden for dashboard use.

Did event coverage improve?

H002 achieved strong event coverage at 66.06%. H001 covered 48.78% but with lift below 1.0. H003 and H004 did not provide enough coverage.

Did median lead time improve?

H003 and H004 had longer median lead times among covered events, but coverage and stability were weak. H002 had only 1BD median lead.

Which results are context / diagnostic only?

- H003 should be context-only or rewrite-only.
- H004 should be diagnostic/rewrite-only.
- FREQ_004 repair columns remained diagnostics-only throughout and were not used as direct triggers.

Should any hypothesis move to shadow dashboard candidate?

No. H002 is the best candidate for a rewrite, but not for shadow dashboard evaluation yet.

Why not production yet?

This was a research-only dry run. No candidate passed a combined bar for aggregate lift, burden, event coverage, fold stability, and lead time. Production promotion remains human-approval-gated and was not attempted.
