# Iteration 002 Analysis

## Commands run

```text
.\.venv\Scripts\python.exe run_dashboard.py --output-dir outputs
.\.venv\Scripts\python.exe run_hypothesis_tests_iteration_002.py --output-dir outputs --test-output-dir research_iterations\iteration_002\tests
```

`run_dashboard.py` completed with exit code 0 and refreshed the feature outputs through latest date 2026-06-30. It used FRED graph CSV fallback because no `FRED_API_KEY` was present. One FRED fallback request retried after a connection reset, then succeeded. The pandas fragmentation warnings are performance warnings in the feature-universe extension, not test failures.

`run_hypothesis_tests_iteration_002.py` completed with exit code 0 and wrote:

- `research_iterations/iteration_002/tests/iteration_002_hypothesis_test_summary.csv`
- `research_iterations/iteration_002/tests/iteration_002_hypothesis_test_folds.csv`
- `research_iterations/iteration_002/tests/iteration_002_hypothesis_test_daily_signals.csv`
- `research_iterations/iteration_002/tests/iteration_002_hypothesis_test_events.csv`
- `research_iterations/iteration_002/tests/iteration_002_hypothesis_test_report.html`
- `research_iterations/iteration_002/tests/iteration_002_hypothesis_test_summary.json`

## Summary table

| Hypothesis | Target | Alert burden | Base hit rate | Alert hit rate | Lift | Event coverage | False calm events | Positive lift folds | Median lead |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| I002_H001 | 30BD MDD <= -8% | 7.50% | 15.29% | 39.54% | 2.59x | 40.00% | 51 | 5/19 | 3.0BD |
| I002_H003 | 60BD MDD <= -10% | 5.16% | 17.46% | 39.17% | 2.24x | 31.03% | 40 | 6/19 | 13.5BD |
| I002_H002 | 15BD MDD <= -5% | 16.04% | 18.79% | 37.00% | 1.97x | 52.24% | 64 | 11/19 | 0.0BD |
| I002_H005 | 30BD MDD <= -8% | 24.64% | 15.29% | 15.27% | 1.00x | 62.35% | 32 | 8/19 | 2.0BD |
| I002_H004 | 30BD MDD <= -8% | 1.08% | 15.29% | 0.00% | 0.00x | 0.00% | 85 | 0/19 | n/a |

## Readout by hypothesis

### I002_H001

The revised downside range-expansion hypothesis improved the prior H001 lift profile. Prior H001 had 9.59% alert burden and 2.29x lift; I002_H001 reduced burden to 7.50% and increased lift to 2.59x. Event coverage also moved from 37.65% to 40.00%.

The weak point is yearly stability: only 5 of 19 yearly folds had lift above 1.0, and median fold lift was 0.92. This is a strong aggregate signal but still regime-concentrated.

Research interpretation: keep this hypothesis. It is the strongest iteration_002 candidate, but next work should focus on fold stability and event timing rather than increasing aggregate lift.

### I002_H002

The revised cross-asset acute shock hypothesis preserved the prior H004 theme. It produced 1.97x lift, 52.24% event coverage, and the best yearly stability among iteration_002 candidates with 11 of 19 positive-lift folds.

The cost is alert burden: 16.04%, higher than prior H004's 9.55%. Median lead time is 0BD, which means many covered events are detected at or near the event start, not comfortably ahead of it.

Research interpretation: keep the cross-asset theme, but the next iteration should separate early-warning credit/rates stress from same-day vol shock confirmation. This may improve lead time and reduce burden.

### I002_H003

The tightened narrow-leadership hypothesis reduced alert burden from prior H002's 12.64% to 5.16% and increased aggregate lift from 1.87x to 2.24x. It also had useful median event lead time of 13.5BD.

The trade-off is event coverage: prior H002 covered 62.07% of events; I002_H003 covered 31.03%. Positive-lift folds improved only modestly to 6 of 19.

Research interpretation: keep as a high-quality, lower-burden narrow-leadership warning. A future companion hypothesis may be needed to recover event coverage without returning to prior H002's burden.

### I002_H004

The false-repair revision failed. It fired on only 1.08% of eligible days and produced zero alert hits, zero event coverage, and zero positive-lift folds.

Research interpretation: reject this exact trigger. The failure likely comes from over-constraining apparent repair, unresolved damage, bounce context, and renewed tape stress. The false-repair idea remains economically plausible, but this deterministic formulation is too narrow.

### I002_H005

The R2-quiet / MMDI-accelerating false-calm replacement covered 62.35% of events and reduced false-calm events to 32, but alert burden was 24.64% and lift was effectively 1.00x. It is an event-coverage overlay, not a selective risk signal.

Research interpretation: do not promote it as a standalone alert. It may be useful only as context or as an input to a stricter second-stage filter.

## Cross-hypothesis conclusions

- Strongest aggregate candidate: I002_H001.
- Best stability candidate: I002_H002.
- Best low-burden leadership candidate: I002_H003.
- Failed candidate: I002_H004.
- Coverage-only overlay: I002_H005.

## Evidence discipline notes

- No live sentiment or headline features were used.
- No placeholder future-data columns were used.
- All exact feature columns were verified against `all_feature_inventory.csv`.
- No threshold search was run after seeing results.
- The analysis above is based on the generated CSV evidence, not visual inspection of charts.
