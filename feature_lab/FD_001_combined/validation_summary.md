# FD_001 Combined Experimental Feature Validation Summary

## Run Evidence

- Generated at UTC: 2026-07-01T06:45:51+00:00
- Combined rows: 6,869
- Latest date: 2026-06-30
- Experimental feature columns: 22
- Batch A v2 source: `feature_lab/FD_001_batch_A_v2/experimental_feature_snapshot.csv`
- Batch B v2 source: `feature_lab/FD_001_batch_B_v2/experimental_feature_snapshot.csv`
- Original feature input source: `outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv`
- Hypothesis tests run: no
- Production files modified: no
- Production output files written: no

## Classification Counts

- `candidate_hypothesis_design`: 10
- `context_only`: 4
- `descriptive_only`: 4
- `episode_diagnostics_only`: 4

## Feature Classification

| Classification | Feature ID | Column | Source batch | Latest value | First valid date | Coverage |
|---|---|---|---|---:|---:|---:|
| candidate_hypothesis_design | FREQ_003 | `freq_003_false_calm_confirmed_flag` | FD_001_batch_B_v2 | 0.0 | 1999-04-19 | 0.8816 |
| candidate_hypothesis_design | FREQ_003 | `freq_003_false_calm_internal_deterioration_count` | FD_001_batch_B_v2 | 1.0 | 1999-03-10 | 1.0000 |
| candidate_hypothesis_design | FREQ_003 | `freq_003_false_calm_possible_flag` | FD_001_batch_B_v2 | 0.0 | 1999-03-10 | 1.0000 |
| candidate_hypothesis_design | FREQ_007 | `freq_007_vol_term_daily_stress_count` | FD_001_batch_A_v2 | 1.0 | 2011-01-03 | 0.5670 |
| candidate_hypothesis_design | FREQ_007 | `freq_007_vol_term_stress_persistence_20d` | FD_001_batch_A_v2 | 0.35 | 2011-01-31 | 0.5643 |
| candidate_hypothesis_design | FREQ_007 | `freq_007_vol_term_stress_persistence_5d` | FD_001_batch_A_v2 | 0.2 | 2011-01-07 | 0.5665 |
| candidate_hypothesis_design | FREQ_008 | `freq_008_vol_disagreement_flag` | FD_001_batch_A_v2 | 1.0 | 2002-07-25 | 0.8765 |
| candidate_hypothesis_design | FREQ_008 | `freq_008_vol_disagreement_rank_change_20d` | FD_001_batch_A_v2 | 0.5912698412698412 | 2002-08-22 | 0.8736 |
| candidate_hypothesis_design | FREQ_008 | `freq_008_vol_disagreement_score` | FD_001_batch_A_v2 | 0.8938492063492064 | 2002-01-25 | 0.8947 |
| candidate_hypothesis_design | FREQ_008 | `freq_008_vol_disagreement_score_pct` | FD_001_batch_A_v2 | 0.9523809523809524 | 2002-07-25 | 0.8765 |
| context_only | FREQ_010 | `freq_010_rates_led_stress_flag` | FD_001_batch_A_v2 | 0.0 | 2002-10-23 | 0.8674 |
| context_only | FREQ_010 | `freq_010_riskoff_confirmation_flag` | FD_001_batch_A_v2 | 0.0 | 2002-10-23 | 0.8674 |
| context_only | FREQ_010 | `freq_010_safe_haven_confirmation_score` | FD_001_batch_A_v2 | 1.0 | 2002-10-23 | 0.8674 |
| context_only | FREQ_010 | `freq_010_safe_haven_rotation_state` | FD_001_batch_A_v2 | treasury_only_safe_haven | 2002-10-23 | 0.8674 |
| descriptive_only | FREQ_003 | `freq_003_false_calm_missing_component_count` | FD_001_batch_B_v2 | 1.0 | 1999-03-10 | 1.0000 |
| descriptive_only | FREQ_003 | `freq_003_false_calm_unknown_due_to_missing_flag` | FD_001_batch_B_v2 | 0.0 | 1999-03-10 | 1.0000 |
| descriptive_only | FREQ_003 | `freq_003_quiet_state` | FD_001_batch_B_v2 | 1.0 | 1999-03-10 | 1.0000 |
| descriptive_only | FREQ_007 | `freq_007_vol_term_persistent_stress_flag` | FD_001_batch_A_v2 | 0.0 | 2011-01-31 | 0.5643 |
| episode_diagnostics_only | FREQ_004 | `freq_004_repair_episode_active` | FD_001_batch_B_v2 | 0.0 | 1999-06-03 | 0.9914 |
| episode_diagnostics_only | FREQ_004 | `freq_004_repair_episode_quality_score` | FD_001_batch_B_v2 |  | 1999-06-04 | 0.1607 |
| episode_diagnostics_only | FREQ_004 | `freq_004_repair_failure_pressure_count` | FD_001_batch_B_v2 | 0.0 | 1999-06-03 | 0.9914 |
| episode_diagnostics_only | FREQ_004 | `freq_004_repair_relapse_flag` | FD_001_batch_B_v2 | 0.0 | 1999-06-03 | 0.9914 |

## FREQ_003 Missing-Uncertainty Evidence

Observed deterioration count:
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

Confirmed flag:
- `0.0`: 5286
- `1.0`: 770
- `nan`: 813

Possible flag:
- `0.0`: 5286
- `1.0`: 1583

Unknown due to missing flag:
- `0.0`: 6056
- `1.0`: 813

## Other State And Count Distributions

FREQ_010 safe-haven state:
- `defensive_only_rotation`: 353
- `mixed_defensive_rates_stress`: 362
- `rates_led_stress`: 490
- `treasury_and_defensive_bid`: 2717
- `treasury_only_safe_haven`: 1500
- `unconfirmed`: 536
- `nan`: 911

FREQ_004 repair pressure count:
- `0.0`: 5832
- `1.0`: 121
- `2.0`: 539
- `3.0`: 269
- `4.0`: 42
- `5.0`: 7
- `nan`: 59

## Validation Checks

- Batch A v2 and Batch B v2 dates matched one-to-one before combining.
- Combined snapshot contains all Batch A v2 experimental columns and all Batch B v2 experimental columns.
- Combined snapshot contains no target labels, future drawdowns, event files, or hypothesis outputs.
- Combined artifacts are written only under `feature_lab/FD_001_combined/`.
- Rolling percentile and quantile calculations were performed upstream using trailing-only windows.
