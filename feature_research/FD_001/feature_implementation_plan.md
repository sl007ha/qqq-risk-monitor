# FD_001 Feature Implementation Plan

This plan is a research-only plan for the five `implement_now` features from the FD_001 feasibility audit. It does not implement the features. Any implementation should occur under `feature_lab/` only unless a human later approves accepted-inventory or production scope.

## Implementation Boundary

Allowed future implementation location:

```text
feature_lab/<feature_id>/
```

Disallowed in this task and any unapproved future implementation:

- `qqq_autoresearch/features.py`
- `qqq_autoresearch/data_sources.py`
- `qqq_autoresearch/config.py`
- `qqq_autoresearch/pipeline.py`
- `qqq_autoresearch/render.py`
- `run_dashboard.py`

## Shared Inputs

Use `outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv` as the input table. Do not fetch new data for these five features.

Each future implementation should write only research outputs under its own feature lab folder:

```text
feature_lab/<feature_id>/outputs/experimental_feature_snapshot.csv
feature_lab/<feature_id>/validation_summary.md
feature_lab/<feature_id>/coverage_summary.csv
```

## FREQ_003 - False-Calm Internal Deterioration Count

Decision: `implement_now`

Initial location: `feature_lab/FREQ_003_false_calm_internal_deterioration_count/`

Later accepted inventory consideration: yes, after feature validation. Not production.

Exact input columns:

- `R2_ACTIVE`
- `R2_STRESS_COUNT`
- `MMDI`
- `MMDI_10D_CHANGE`
- `mmdi_20d_change`
- `downside_vol_20d`
- `price_vs_ma50`
- `qqq_dd_20d`

Expected output column names:

- `freq_003_false_calm_internal_deterioration_count`
- `freq_003_false_calm_internal_deterioration_flag`
- `freq_003_false_calm_missing_component_count`

Formula:

1. Define quiet state:

```text
quiet_state = (R2_ACTIVE == false) OR (R2_STRESS_COUNT <= 1)
```

2. Define trailing-only component flags:

```text
mmdi_rising = (MMDI_10D_CHANGE > 0) OR (mmdi_20d_change > 0)
mmdi_elevated = MMDI >= 50
downside_vol_present = downside_vol_20d is non-null
trend_damaged = price_vs_ma50 < 0
short_drawdown = qqq_dd_20d <= -0.03
```

3. Count only inside quiet state:

```text
freq_003_false_calm_internal_deterioration_count =
  quiet_state * sum(mmdi_rising, mmdi_elevated, downside_vol_present, trend_damaged, short_drawdown)
```

4. Flag:

```text
freq_003_false_calm_internal_deterioration_flag =
  freq_003_false_calm_internal_deterioration_count >= 3
```

Coverage expectation:

- All inputs exist.
- Minimum full-sample input coverage is 41.21%, driven by `downside_vol_20d`.
- Latest row has all 8 inputs non-null.
- Recent one-year minimum input coverage is 29.37%, driven by `downside_vol_20d`.

Leakage mitigation:

- Use only same-date R2/MMDI/trailing market fields.
- Do not tune the count threshold after seeing hypothesis outcomes.
- Treat missing `downside_vol_20d` as missing component, not automatically calm.

Validation checks:

- Verify output non-null count and latest value.
- Report missing component count distribution.
- Confirm no input outside the declared column list is used.
- Confirm feature is not written to production dashboard outputs.

## FREQ_004 - Repair Episode Quality Score

Decision: `implement_now`

Initial location: `feature_lab/FREQ_004_repair_episode_quality_score/`

Later accepted inventory consideration: yes, after feature validation. Not production.

Exact input columns:

- `qqq_close`
- `qqq_dd_20d`
- `qqq_dd_60d`
- `rebound_from_trough_20d`
- `failed_reclaim_ma50`
- `failed_reclaim_ma200`
- `lower_high_flag`
- `lower_low_flag`
- `mmdi_low_after_high`

Expected output column names:

- `freq_004_repair_episode_active`
- `freq_004_repair_failure_pressure_count`
- `freq_004_repair_episode_quality_score`
- `freq_004_repair_relapse_flag`

Formula:

1. Define repair episode active using only trailing data:

```text
freq_004_repair_episode_active =
  (qqq_dd_60d <= -0.05) AND (rebound_from_trough_20d >= 0.03)
```

2. Count repair pressure:

```text
freq_004_repair_failure_pressure_count =
  freq_004_repair_episode_active *
  sum(failed_reclaim_ma50, failed_reclaim_ma200, lower_high_flag, lower_low_flag, mmdi_low_after_high)
```

3. Score quality:

```text
freq_004_repair_episode_quality_score =
  freq_004_repair_episode_active *
  (rebound_from_trough_20d - 0.02 * freq_004_repair_failure_pressure_count)
```

4. Relapse flag:

```text
freq_004_repair_relapse_flag =
  freq_004_repair_episode_active AND (freq_004_repair_failure_pressure_count >= 2)
```

Coverage expectation:

- All inputs exist.
- Minimum full-sample input coverage is 99.14%.
- Latest row has all 9 inputs non-null.
- Recent one-year minimum input coverage is 100.00%.

Leakage mitigation:

- Do not identify troughs using future data.
- Define active repair from trailing 60D drawdown and trailing 20D rebound only.
- Do not terminate episodes using future drawdown outcomes.

Validation checks:

- Count active repair days by year.
- Report quality score non-null coverage.
- Verify no future target/event columns are read.
- Compare repair active days against prior false-repair hypotheses only in a later hypothesis task.

## FREQ_007 - Volatility Term-Structure Stress Persistence

Decision: `implement_now`

Initial location: `feature_lab/FREQ_007_vol_term_structure_stress_persistence/`

Later accepted inventory consideration: yes, after feature validation. Not production.

Exact input columns:

- `vix9d_vs_vix`
- `vix3m_vs_vix`
- `vol_term_inversion_flag`
- `vvix_level`
- `skew_index`
- `panic_vol_flag`

Expected output column names:

- `freq_007_vol_term_daily_stress_count`
- `freq_007_vol_term_stress_persistence_5d`
- `freq_007_vol_term_stress_persistence_20d`
- `freq_007_vol_term_persistent_stress_flag`

Formula:

```text
front_vol_inverted = (vix9d_vs_vix > 0) OR (vix3m_vs_vix < 0) OR vol_term_inversion_flag
tail_demand = (vvix_level >= trailing_252d_80th_percentile) OR (skew_index >= trailing_252d_80th_percentile)
panic = panic_vol_flag

freq_007_vol_term_daily_stress_count = sum(front_vol_inverted, tail_demand, panic)
freq_007_vol_term_stress_persistence_5d = rolling_5d_mean(freq_007_vol_term_daily_stress_count > 0)
freq_007_vol_term_stress_persistence_20d = rolling_20d_mean(freq_007_vol_term_daily_stress_count > 0)
freq_007_vol_term_persistent_stress_flag = freq_007_vol_term_stress_persistence_20d >= 0.50
```

Coverage expectation:

- All inputs exist.
- Minimum full-sample input coverage is 56.70%, driven by `vix9d_vs_vix`.
- Latest row has all 6 inputs non-null.
- Recent one-year minimum input coverage is 100.00%.

Leakage mitigation:

- Rolling percentiles must use trailing data only.
- Missing early volatility-index history must remain missing; do not backfill as non-stress.
- No future volatility or drawdown labels are used.

Validation checks:

- Report coverage before and after 2011-01-03.
- Report percent missing for each output.
- Verify trailing percentile windows do not include future rows.
- Compare output overlap with `panic_vol_flag` as redundancy evidence only.

## FREQ_008 - Regime-Shift Volatility Disagreement

Decision: `implement_now`

Initial location: `feature_lab/FREQ_008_regime_shift_volatility_disagreement/`

Later accepted inventory consideration: yes, after feature validation. Not production.

Exact input columns:

- `qqq_vol_10d`
- `qqq_vol_20d`
- `qqq_vol_60d`
- `realized_vol_252d`
- `vix`
- `vxn`
- `vol_20d_vs_252d`

Expected output column names:

- `freq_008_vol_disagreement_score`
- `freq_008_vol_disagreement_rank_change_20d`
- `freq_008_vol_disagreement_flag`

Formula:

```text
short_vs_medium = abs(qqq_vol_10d / qqq_vol_60d - 1)
short_vs_long = abs(qqq_vol_20d / realized_vol_252d - 1)
implied_cross_market = abs(vxn / vix - trailing_252d_median(vxn / vix))

freq_008_vol_disagreement_score =
  average(short_vs_medium, short_vs_long, implied_cross_market, vol_20d_vs_252d)

freq_008_vol_disagreement_rank_change_20d =
  trailing_252d_percentile(freq_008_vol_disagreement_score) -
  trailing_252d_percentile(freq_008_vol_disagreement_score.shift(20))

freq_008_vol_disagreement_flag =
  trailing_252d_percentile(freq_008_vol_disagreement_score) >= 0.80
```

Coverage expectation:

- All inputs exist.
- Minimum full-sample input coverage is 93.11%, driven by `vxn`.
- Latest row has all 7 inputs non-null.
- Recent one-year minimum input coverage is 100.00%.

Leakage mitigation:

- Percentiles and medians must be trailing-only.
- No future realized volatility or target outcomes are used.
- Division-by-zero and missing values must remain explicit.

Validation checks:

- Report first valid output date.
- Compare output availability against `vol_20d_vs_252d`.
- Confirm no row uses future observations in rank calculation.
- Document latest value and percentile.

## FREQ_010 - Safe-Haven Rotation Confirmation

Decision: `implement_now`

Initial location: `feature_lab/FREQ_010_safe_haven_rotation_confirmation/`

Later accepted inventory consideration: yes, after feature validation. Not production.

Exact input columns:

- `tlt_ret_20d`
- `ief_ret_20d`
- `tlt_ief_rel_3m`
- `xlu_vs_spy_3m`
- `xlp_vs_spy_3m`
- `ust10y_change_20d`

Expected output column names:

- `freq_010_safe_haven_confirmation_score`
- `freq_010_rates_led_stress_flag`
- `freq_010_riskoff_confirmation_flag`
- `freq_010_safe_haven_rotation_state`

Formula:

```text
treasury_bid = (tlt_ret_20d > 0) OR (ief_ret_20d > 0) OR (tlt_ief_rel_3m > 0)
defensive_bid = (xlu_vs_spy_3m > 0) OR (xlp_vs_spy_3m > 0)
rates_stress = ust10y_change_20d >= 0.25

freq_010_safe_haven_confirmation_score = sum(treasury_bid, defensive_bid)
freq_010_rates_led_stress_flag = rates_stress AND NOT treasury_bid
freq_010_riskoff_confirmation_flag = freq_010_safe_haven_confirmation_score >= 1

freq_010_safe_haven_rotation_state =
  "riskoff_confirmed" if freq_010_riskoff_confirmation_flag
  "rates_led_stress" if freq_010_rates_led_stress_flag
  "unconfirmed" otherwise
```

Coverage expectation:

- All inputs exist.
- Minimum full-sample input coverage is 86.74%, driven by `tlt_ief_rel_3m`.
- Latest row has all 6 inputs non-null.
- Recent one-year minimum input coverage is 100.00%.

Leakage mitigation:

- Use trailing ETF returns and same-date yield changes only.
- Do not classify based on future QQQ drawdown.
- Keep the string state research-only unless accepted inventory approval later allows it.

Validation checks:

- Report state counts by year.
- Report output coverage and latest state.
- Confirm no future returns are referenced.
- Compare state overlap with existing cross-asset stress columns only as descriptive validation.

## Features Not Planned For Immediate Implementation

`design_more_first`:

- FREQ_001: needs long-history versus recent-era branch design.
- FREQ_005: needs sparse-volatility-field missing policy redesign.
- FREQ_006: needs dependency on another accepted parent feature and Mag7 proxy framing.
- FREQ_009: needs macro release-lag alignment design.

`defer`:

- FREQ_002: needs two-tier legacy/recent funding design because SOFR and HY/IG inputs have short histories.

`reject`:

- none.
