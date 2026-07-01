# FD_001 Batch A v2 Validation Summary

## Run Evidence

- Generated at UTC: 2026-07-01T06:23:21+00:00
- Input rows: 6,869
- Input latest date: 2026-06-30
- Experimental feature columns: 12
- Input file: `outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv`
- Output directory: `feature_lab/FD_001_batch_A_v2/`
- Hypothesis tests run: no
- Production files modified: no

## QA Patch Compliance

- FREQ_008 formula is unchanged from Batch A.
- FREQ_007 availability now includes `vol_term_inversion_flag`.
- FREQ_007 uses safe boolean conversion and does not use `Series.astype(bool)` on missing-capable data.
- FREQ_007 early missing volatility-term history remains missing rather than non-stress.
- FREQ_007 persistence scores remain continuous outputs; the persistent flag is descriptive only.
- FREQ_010 uses the richer mutually exclusive context states requested for Batch A v2.
- FREQ_010 true riskoff confirmation requires both treasury bid and defensive bid.
- FREQ_010 state is context-only and not alert-ready.
- Rolling percentile and median calculations are trailing-only.
- No future target, future return, forward drawdown, event file, or hypothesis test output is read.

## Latest Experimental Values

| Column | Role | Latest value | First valid date | Coverage |
|---|---|---:|---:|---:|
| `freq_008_vol_disagreement_score` | candidate_hypothesis_design | 0.8938492063492064 | 2002-01-25 | 0.8947 |
| `freq_008_vol_disagreement_score_pct` | candidate_hypothesis_design | 0.9523809523809523 | 2002-07-25 | 0.8765 |
| `freq_008_vol_disagreement_rank_change_20d` | candidate_hypothesis_design | 0.5912698412698412 | 2002-08-22 | 0.8736 |
| `freq_008_vol_disagreement_flag` | candidate_hypothesis_design | 1.0 | 2002-07-25 | 0.8765 |
| `freq_007_vol_term_daily_stress_count` | candidate_hypothesis_design | 1.0 | 2011-01-03 | 0.5670 |
| `freq_007_vol_term_stress_persistence_5d` | candidate_hypothesis_design | 0.2 | 2011-01-07 | 0.5665 |
| `freq_007_vol_term_stress_persistence_20d` | candidate_hypothesis_design | 0.35 | 2011-01-31 | 0.5643 |
| `freq_007_vol_term_persistent_stress_flag` | descriptive_only | 0.0 | 2011-01-31 | 0.5643 |
| `freq_010_safe_haven_confirmation_score` | context_only | 1.0 | 2002-10-23 | 0.8674 |
| `freq_010_rates_led_stress_flag` | context_only | 0.0 | 2002-10-23 | 0.8674 |
| `freq_010_riskoff_confirmation_flag` | context_only | 0.0 | 2002-10-23 | 0.8674 |
| `freq_010_safe_haven_rotation_state` | context_only_not_alert_ready | treasury_only_safe_haven | 2002-10-23 | 0.8674 |

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

FREQ_007 persistent-stress overlap when the descriptive flag is true:
- `panic_vol_flag`: 0.1971311475409836
- `vol_term_inversion_flag`: 0.33319672131147543

FREQ_010 context state counts:
- `treasury_and_defensive_bid`: 2717
- `treasury_only_safe_haven`: 1500
- `<NA>`: 911
- `unconfirmed`: 536
- `rates_led_stress`: 490
- `mixed_defensive_rates_stress`: 362
- `defensive_only_rotation`: 353

FREQ_010 true riskoff confirmations by state:
- `defensive_only_rotation`: 0.0
- `mixed_defensive_rates_stress`: 120.0
- `rates_led_stress`: 0.0
- `treasury_and_defensive_bid`: 2717.0
- `treasury_only_safe_haven`: 0.0
- `unconfirmed`: 0.0

## Validation Checks

- Required input columns were present.
- Experimental outputs were written only under `feature_lab/FD_001_batch_A_v2/`.
- Latest values, first valid dates, coverage, and state distributions are recorded.
- FREQ_007 pre-VIX9D output coverage is expected to remain zero because missing early history is preserved.
