# Iteration 004 Plan

## Objective

Use iteration 003 evidence to reduce false-calm alert burden and improve event-level usefulness without optimizing thresholds or modifying production dashboard logic.

## Carry Forward

1. **Carry forward I002_H001 and I003_H001 as the downside-volatility comparison pair.**
   - I002_H001 remains the cleaner aggregate candidate: 2.59x lift, 7.50% burden, 40.00% coverage.
   - I003_H001 modestly improved positive-lift folds to 6/19 but raised burden and reduced lead time.
   - Next question: can event-level combination logic use the stricter I002 version as the primary alert and the I003 version only as context?

2. **Carry forward I003_H005 as the main rewrite candidate.**
   - Evidence: lift improved from 1.00x to 1.45x versus I002_H005, burden fell from 24.64% to 16.08%, coverage rose to 67.06%, and median lead improved to 5.0BD.
   - Next question: can burden fall below roughly 12% through a pre-declared second-stage confirmation rule rather than threshold search?

3. **Carry forward I002_H003, not I003_H003, as the low-burden leadership baseline.**
   - I003_H003 proved coverage exists but was too broad.
   - Next question: can leadership evidence act as context for false-calm or downside-volatility alerts rather than a standalone trigger?

## Drop Or Deprioritize

1. **Drop I003_H002.**
   - It reduced burden but did not improve lead time, lift, coverage, or stability versus I002_H002.

2. **Reject I003_H004.**
   - It produced 0.00% event coverage and 0/19 positive-lift folds. Do not retest the same false-repair structure on the same target.

## Candidate Iteration 004 Tests

1. **False-calm stricter confirmation rewrite**
   - Keep R2 quiet plus MMDI elevated/accelerating.
   - Replace broad independent confirmation with a stricter pre-declared interaction such as credit confirmation OR both range and volatility confirmation.
   - Do not search thresholds after seeing results.

2. **Downside-volatility episode comparison**
   - Compare I002_H001 and I003_H001 at the event level.
   - Focus on event coverage, false calm, and lead time rather than trying to maximize daily lift.

3. **Leadership as context, not alert**
   - Test whether I002_H003 or selected I003_H003 components improve false-calm or downside-volatility alerts when used as a context overlay.
   - Avoid using the high-burden I003_H003 trigger as a standalone alert.

## Required Evaluation Metrics

- alert burden
- base hit rate
- alert hit rate
- base-rate lift
- event coverage
- false calm events and days
- yearly fold stability
- median and mean lead time
- comparison to the closest prior iteration predecessor

## Guardrails

- Do not use live sentiment or headline features for historical backtests.
- Do not invent feature columns.
- Do not optimize thresholds.
- Do not modify production dashboard logic.
- Do not modify `qqq_autoresearch/data_sources.py`, `qqq_autoresearch/features.py`, or `qqq_autoresearch/config.py`.
