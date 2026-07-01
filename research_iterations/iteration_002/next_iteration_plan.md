# Iteration 003 Plan

## Objective

Use iteration_002 evidence to improve event coverage, false calm reduction, and fold stability without optimizing thresholds or modifying production dashboard logic.

## Carry forward

1. **Carry forward I002_H001 as the primary downside-volatility candidate.**
   - Rationale: 2.59x lift, 7.50% alert burden, 40.00% event coverage.
   - Next question: can fold stability improve without raising alert burden materially?

2. **Carry forward I002_H002 as the primary cross-asset acute-shock candidate.**
   - Rationale: 1.97x lift, 52.24% event coverage, 11/19 positive-lift folds.
   - Next question: can lead time improve beyond same-day detection?

3. **Carry forward I002_H003 as the low-burden narrow-leadership candidate.**
   - Rationale: 2.24x lift, 5.16% alert burden, 13.5BD median lead time.
   - Next question: can a companion early-warning version restore some event coverage?

## Reject or demote

1. **Reject I002_H004 in its current form.**
   - Evidence: 0.00x lift, 0.00% event coverage, 0/19 positive-lift folds.
   - Next version should remove at least one gating condition before testing, but that change should be declared before the next run.

2. **Demote I002_H005 to contextual overlay.**
   - Evidence: 62.35% event coverage but 24.64% alert burden and 1.00x lift.
   - Next version should use R2-quiet / MMDI acceleration only with an independent confirming stress channel.

## Candidate iteration_003 hypotheses

1. **Downside-volatility early warning split**
   - Keep I002_H001's core, but separate "early warning above MA20" from "confirmed warning below MA20".
   - Test both as pre-declared variants, not optimized thresholds.

2. **Cross-asset lead-time filter**
   - Separate credit/rates deterioration from same-day front-vol confirmation.
   - Target: improve median lead time while keeping event coverage above 40%.

3. **Narrow-leadership coverage companion**
   - Use H002-style coverage logic but require lower alert persistence or episode-level deduplication.
   - Target: recover coverage without returning to 12%+ alert burden.

4. **Simpler false-repair formulation**
   - Test apparent MMDI repair plus unresolved price damage without requiring renewed tape stress at the same time.
   - Target: avoid the zero-hit overconstraint seen in I002_H004.

5. **False-calm second-stage filter**
   - Use R2 quiet + MMDI acceleration only when confirmed by downside volatility or credit stress.
   - Target: reduce I002_H005 alert burden below 12% while preserving some event coverage.

## Required evaluation gates

Each iteration_003 candidate should report:

- alert burden
- base hit rate
- alert hit rate
- base-rate lift
- event coverage
- false calm events and days
- yearly fold stability
- lead-time distribution
- comparison against the closest iteration_002 predecessor

## Guardrails

- Do not use live sentiment for historical tests.
- Do not use placeholder future-data columns.
- Do not change `qqq_autoresearch/data_sources.py`, `qqq_autoresearch/features.py`, or `qqq_autoresearch/config.py`.
- Do not alter production dashboard logic.
- Do not tune thresholds after seeing results.
