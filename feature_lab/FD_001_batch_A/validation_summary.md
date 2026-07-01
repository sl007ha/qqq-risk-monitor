# FD_001 Batch A Validation Summary

## Run Evidence

- Generated at UTC: 2026-07-01T06:06:34+00:00
- Input rows: 6,869
- Input latest date: 2026-06-30
- Experimental feature columns: 12
- Input file: `outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv`
- Output directory: `feature_lab/FD_001_batch_A/`
- Hypothesis tests run: no
- Production files modified: no

## Formula Review Compliance

- FREQ_008 averages rolling percentile-normalized components, not raw-scale components.
- FREQ_007 keeps early missing VIX9D/VIX3M/VVIX history missing rather than non-stress.
- FREQ_010 emits mutually exclusive states: mixed_defensive_rates_stress, rates_led_stress, riskoff_confirmed, unconfirmed.
- Rolling percentile and median calculations are trailing-only.
- No future target, future return, forward drawdown, event file, or hypothesis test output is read.

## Latest Experimental Values

| Column | Latest value | First valid date | Coverage |
|---|---:|---:|---:|
| `freq_008_vol_disagreement_score` | 0.8938492063492064 | 2002-01-25 | 0.8947 |
| `freq_008_vol_disagreement_score_pct` | 0.9523809523809523 | 2002-07-25 | 0.8765 |
| `freq_008_vol_disagreement_rank_change_20d` | 0.5912698412698412 | 2002-08-22 | 0.8736 |
| `freq_008_vol_disagreement_flag` | 1.0 | 2002-07-25 | 0.8765 |
| `freq_007_vol_term_daily_stress_count` | 1.0 | 2011-01-03 | 0.5670 |
| `freq_007_vol_term_stress_persistence_5d` | 0.2 | 2011-01-07 | 0.5665 |
| `freq_007_vol_term_stress_persistence_20d` | 0.35 | 2011-01-31 | 0.5643 |
| `freq_007_vol_term_persistent_stress_flag` | 0.0 | 2011-01-31 | 0.5643 |
| `freq_010_safe_haven_confirmation_score` | 1.0 | 2002-10-23 | 0.8674 |
| `freq_010_rates_led_stress_flag` | 0.0 | 2002-10-23 | 0.8674 |
| `freq_010_riskoff_confirmation_flag` | 1.0 | 2002-10-23 | 0.8674 |
| `freq_010_safe_haven_rotation_state` | riskoff_confirmed | 2002-10-23 | 0.8674 |

## FREQ_007 Pre/Post VIX9D Coverage

| Scope | Coverage | First valid | Last valid |
|---|---:|---:|---:|
| pre_vix9d_history | 0.0000 |  |  |
| post_vix9d_history | 1.0000 | 2011-01-03 | 2026-06-30 |

## Descriptive Overlap With Existing Columns

These checks use same-date related columns only. No target labels are used.

FREQ_008 score correlations:
- `vol_20d_vs_252d`: 0.13965524531760223
- `vix`: 0.1609387710582997
- `vxn`: 0.07712392699732958

FREQ_007 persistent-stress overlap when the experimental flag is true:
- `panic_vol_flag`: 0.1971311475409836
- `vol_term_inversion_flag`: 0.33319672131147543

FREQ_010 state counts:
- `riskoff_confirmed`: 4570
- `<NA>`: 911
- `unconfirmed`: 536
- `rates_led_stress`: 441
- `mixed_defensive_rates_stress`: 411

## Validation Checks

- Required input columns were present.
- Experimental outputs were written only under `feature_lab/FD_001_batch_A/`.
- Early-history missingness is preserved for Batch A outputs.
- Latest values and first valid dates are recorded in `experimental_feature_inventory.csv`.
