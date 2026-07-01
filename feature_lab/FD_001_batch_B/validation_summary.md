# FD_001 Batch B Validation Summary

## Run Evidence

- Generated at UTC: 2026-07-01T06:31:55+00:00
- Input rows: 6,869
- Input latest date: 2026-06-30
- Experimental feature columns: 8
- Input file: `outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv`
- Output directory: `feature_lab/FD_001_batch_B/`
- Hypothesis tests run: no
- Production files modified: no

## Formula Compliance

- FREQ_003 quiet state uses `(R2_ACTIVE == false) AND (R2_STRESS_COUNT <= 1)`.
- FREQ_003 downside volatility stress uses trailing 252-day Q75 of `downside_vol_20d`.
- FREQ_003 counts only inside quiet state.
- FREQ_003 missing components are counted separately and do not become calm or stress.
- FREQ_003 flag is computed as `count >= 3`; missing components are tracked separately and are not added as calm or stress.
- FREQ_004 repair episode active uses only trailing `qqq_dd_60d` and `rebound_from_trough_20d`.
- FREQ_004 is episode diagnostics only.
- No future trough, future drawdown, forward return, target label, event file, or hypothesis test output is read.

## Latest Experimental Values

| Column | Role | Latest value | First valid date | Coverage |
|---|---|---:|---:|---:|
| `freq_003_quiet_state` | descriptive_only | 1.0 | 1999-03-10 | 1.0000 |
| `freq_003_false_calm_internal_deterioration_count` | candidate_hypothesis_design | 1.0 | 1999-03-10 | 1.0000 |
| `freq_003_false_calm_missing_component_count` | descriptive_only | 1.0 | 1999-03-10 | 1.0000 |
| `freq_003_false_calm_internal_deterioration_flag` | candidate_hypothesis_design | 0.0 | 1999-03-10 | 1.0000 |
| `freq_004_repair_episode_active` | episode_diagnostics_only | 0.0 | 1999-06-03 | 0.9914 |
| `freq_004_repair_failure_pressure_count` | episode_diagnostics_only | 0.0 | 1999-06-03 | 0.9914 |
| `freq_004_repair_episode_quality_score` | episode_diagnostics_only |  | 1999-06-04 | 0.1607 |
| `freq_004_repair_relapse_flag` | episode_diagnostics_only | 0.0 | 1999-06-03 | 0.9914 |

## FREQ_003 Distributions

Quiet state:
- `0.0`: 2130
- `1.0`: 4739

Internal deterioration count:
- `0.0`: 3785
- `1.0`: 1729
- `2.0`: 585
- `3.0`: 481
- `4.0`: 286
- `5.0`: 3

Missing component count:
- `0.0`: 2264
- `1.0`: 4343
- `3.0`: 216
- `4.0`: 27
- `5.0`: 19

False-calm deterioration flag:
- `0.0`: 6099
- `1.0`: 770

FREQ_003 component missingness:
- `mmdi_rising` missing: 466
- `mmdi_elevated` missing: 450
- `downside_vol_stress` missing: 5932
- `trend_damaged` missing: 49
- `short_drawdown` missing: 19

## FREQ_004 Distributions

Repair episode active:
- `0.0`: 5706
- `1.0`: 1104
- `nan`: 59

Repair pressure count:
- `0.0`: 5832
- `1.0`: 121
- `2.0`: 539
- `3.0`: 269
- `4.0`: 42
- `5.0`: 7
- `nan`: 59

Repair relapse flag:
- `0.0`: 5953
- `1.0`: 857
- `nan`: 59

Active repair days by year:
- `1999`: 19
- `2000`: 124
- `2001`: 136
- `2002`: 118
- `2003`: 23
- `2004`: 35
- `2005`: 13
- `2006`: 12
- `2007`: 20
- `2008`: 86
- `2009`: 25
- `2010`: 39
- `2011`: 43
- `2012`: 35
- `2015`: 29
- `2016`: 31
- `2018`: 39
- `2019`: 23
- `2020`: 63
- `2021`: 15
- `2022`: 116
- `2023`: 7
- `2024`: 21
- `2025`: 27
- `2026`: 5

FREQ_004 pressure component missingness:
- `failed_reclaim_ma50` missing: 0
- `failed_reclaim_ma200` missing: 0
- `lower_high_flag` missing: 0
- `lower_low_flag` missing: 0
- `mmdi_low_after_high` missing: 0

## Validation Checks

- Required input columns were present.
- Experimental outputs were written only under `feature_lab/FD_001_batch_B/`.
- Latest values, first valid dates, coverage, and count distributions are recorded.
- All rolling quantiles are trailing-only.
- No production dashboard output file is written.
