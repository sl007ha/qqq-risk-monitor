# Iteration 003 Analysis

## Commands Run

```text
.\.venv\Scripts\python.exe -m py_compile qqq_autoresearch\hypothesis_tests_iteration_003.py run_hypothesis_tests_iteration_003.py
```

Completed with exit code 0.

```text
python validation snippet for research_iterations/iteration_003/hypotheses.yaml
```

Completed with exit code 0:

```text
hypotheses=5
missing=[]
sentiment_columns=[]
```

```text
.\.venv\Scripts\python.exe run_dashboard.py --output-dir outputs
```

Completed with exit code 0. The dashboard refresh reported latest date `2026-06-30`, feature_count `183`, all_column_count `342`, and sentiment_headline_count `100`. It used FRED graph CSV fallback because no `FRED_API_KEY` was present. The pandas fragmentation messages were performance warnings in feature construction, not test failures.

```text
.\.venv\Scripts\python.exe run_hypothesis_tests_iteration_003.py --output-dir outputs --test-output-dir research_iterations\iteration_003\tests
```

Completed with exit code 0 and wrote:

- `research_iterations/iteration_003/tests/iteration_003_hypothesis_test_summary.csv`
- `research_iterations/iteration_003/tests/iteration_003_hypothesis_test_folds.csv`
- `research_iterations/iteration_003/tests/iteration_003_hypothesis_test_daily_signals.csv`
- `research_iterations/iteration_003/tests/iteration_003_hypothesis_test_events.csv`
- `research_iterations/iteration_003/tests/iteration_003_hypothesis_test_report.html`
- `research_iterations/iteration_003/tests/iteration_003_hypothesis_test_summary.json`

## Summary Table

| Hypothesis | Target | Alert burden | Base hit rate | Alert hit rate | Lift | Event coverage | False calm events | Positive lift folds | Median lead |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| I003_H001 | 30BD MDD <= -8% | 9.65% | 15.29% | 37.42% | 2.45x | 40.00% | 51 | 6/19 | 1.5BD |
| I003_H002 | 15BD MDD <= -5% | 11.70% | 18.79% | 34.74% | 1.85x | 42.54% | 77 | 8/19 | 0.0BD |
| I003_H003 | 60BD MDD <= -10% | 23.67% | 17.46% | 27.07% | 1.55x | 77.59% | 13 | 8/19 | 3.0BD |
| I003_H005 | 30BD MDD <= -8% | 16.08% | 15.29% | 22.19% | 1.45x | 67.06% | 28 | 10/19 | 5.0BD |
| I003_H004 | 30BD MDD <= -8% | 2.21% | 15.29% | 2.91% | 0.19x | 0.00% | 85 | 0/19 | n/a |

## Comparison To Iteration 002

| Iteration 003 | Closest prior | Lift | Alert burden | Event coverage | Positive lift folds | Median lead |
|---|---|---:|---:|---:|---:|---:|
| I003_H001 | I002_H001 | 2.45x vs 2.59x | 9.65% vs 7.50% | 40.00% vs 40.00% | 6/19 vs 5/19 | 1.5BD vs 3.0BD |
| I003_H002 | I002_H002 | 1.85x vs 1.97x | 11.70% vs 16.04% | 42.54% vs 52.24% | 8/19 vs 11/19 | 0.0BD vs 0.0BD |
| I003_H003 | I002_H003 | 1.55x vs 2.24x | 23.67% vs 5.16% | 77.59% vs 31.03% | 8/19 vs 6/19 | 3.0BD vs 13.5BD |
| I003_H004 | I002_H004 | 0.19x vs 0.00x | 2.21% vs 1.08% | 0.00% vs 0.00% | 0/19 vs 0/19 | n/a vs n/a |
| I003_H005 | I002_H005 | 1.45x vs 1.00x | 16.08% vs 24.64% | 67.06% vs 62.35% | 10/19 vs 8/19 | 5.0BD vs 2.0BD |

## Readout By Hypothesis

### I003_H001

The flexible trend-pressure rewrite preserved strong aggregate lift at 2.45x and improved positive-lift folds from 5/19 to 6/19. It did not improve the overall candidate versus I002_H001 because alert burden rose from 7.50% to 9.65%, lift fell from 2.59x to 2.45x, and median lead time fell from 3.0BD to 1.5BD.

Research interpretation: keep the downside-volatility mechanism, but do not treat this rewrite as superior to I002_H001. The marginal fold-stability gain is real but small.

### I003_H002

The cross-asset lead-time rewrite reduced alert burden from 16.04% to 11.70%, but it also reduced lift, event coverage, and yearly stability. Median lead time stayed at 0.0BD, so the intended lead-time improvement did not appear.

Research interpretation: drop this exact variant. Keep the cross-asset theme through I002_H002 or a future design that separates early credit stress from same-day vol confirmation more cleanly.

### I003_H003

The leadership coverage companion achieved the intended coverage increase: event coverage rose to 77.59%. The cost was too high for an alert candidate: alert burden rose to 23.67%, lift fell to 1.55x, and median lead time fell to 3.0BD.

Research interpretation: demote this to a coverage overlay or rewrite candidate. It is useful evidence that the relaxed leadership condition sees many events, but it is too broad as a standalone warning.

### I003_H004

The simplified false-repair trigger still failed. It produced 2.21% alert burden, only 2.91% alert hit rate, 0.19x lift, 0.00% event coverage, and 0/19 positive-lift folds.

Research interpretation: reject this formulation and stop retesting this same MMDI-repair / unresolved-price-damage shape against the same 30BD MDD target unless the target definition or data source changes.

### I003_H005

The stricter false-calm overlay materially improved on I002_H005. Lift rose from 1.00x to 1.45x, alert burden fell from 24.64% to 16.08%, event coverage rose from 62.35% to 67.06%, false calm events fell from 32 to 28, positive-lift folds rose from 8/19 to 10/19, and median lead time improved from 2.0BD to 5.0BD.

Research interpretation: this is the strongest new learning from iteration 003. It is still too broad for a dashboard alert, but it is worth a focused rewrite as a contextual false-calm candidate.

## Cross-Hypothesis Conclusions

- Strongest aggregate lift in iteration 003: I003_H001.
- Best improvement versus iteration 002 predecessor: I003_H005.
- Best event coverage but too broad: I003_H003.
- Failed idea to preserve and stop retesting in current form: I003_H004.
- No iteration 003 hypothesis should be promoted to production dashboard logic without human approval.

## Evidence Discipline Notes

- All `exact_feature_columns_used` entries were validated against `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv`.
- The validation check reported `missing=[]`.
- No sentiment, headline, RSS, or narrative feature columns were used.
- No threshold optimization was run after seeing results.
- Analysis is based on generated CSV evidence from the iteration 003 test output folder.
