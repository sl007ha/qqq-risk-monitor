# FD_001 Formula Review

## Scope

This review covers Feature Lab Batch A only:

- FREQ_008 regime-shift volatility disagreement
- FREQ_007 volatility term-structure stress persistence
- FREQ_010 safe-haven rotation confirmation

It does not approve or implement FREQ_003 or FREQ_004. It does not authorize production feature construction or dashboard changes.

## Source Data Check

Input table: `outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv`

Observed source shape during review:

- rows: 6,869
- latest date: 2026-06-30

Relevant early-history coverage:

- `vix9d_vs_vix`: first valid 2011-01-03, coverage 56.70%, latest non-null.
- `vix3m_vs_vix`: first valid 2006-07-17, coverage 73.08%, latest non-null.
- `vvix_level`: first valid 2007-01-03, coverage 71.38%, latest non-null.
- `vxn`: first valid 2001-01-23, coverage 93.11%, latest non-null.
- `tlt_ief_rel_3m`: first valid 2002-10-23, coverage 86.74%, latest non-null.

## Review Checklist

### Missingness As Market Signal

Risk: Treating missing values as `False`, `0`, or non-stress can create artificial calm in early history.

Decision:

- FREQ_007 must keep missing term-structure and VVIX inputs as missing until the required inputs exist.
- FREQ_008 must keep component percentiles missing until each component has enough trailing history.
- FREQ_010 must keep state missing until all state inputs are available.

No Batch A formula may fill missing source values with `0`, `False`, forward-filled synthetic values, or non-stress defaults.

### Raw Component Scale Compatibility

Risk: FREQ_008 originally mixed raw ratios and differences on incompatible scales.

Decision:

- FREQ_008 must compute raw component distances first, then convert each raw component to a trailing rolling percentile.
- FREQ_008 score must average percentile-normalized components, not raw components.
- FREQ_007 uses boolean stress components, so scale mismatch is limited to percentile thresholds for VVIX/SKEW.
- FREQ_010 uses boolean state ingredients and does not average raw magnitudes.

### Trailing-Only Rolling Calculations

Risk: Rolling percentiles or medians could accidentally include future observations.

Decision:

- Rolling percentile and median functions must use windows ending at the current row only.
- No centered windows are allowed.
- For FREQ_008, all component percentiles and score percentiles are trailing-only.
- For FREQ_007, VVIX/SKEW percentile thresholds are trailing-only.

### Categorical State Precedence

Risk: FREQ_010 can have overlapping conditions, especially when rates stress and safe-haven demand occur together.

Decision:

FREQ_010 states must be mutually exclusive with this precedence:

1. `mixed_defensive_rates_stress`: rates stress and at least one safe-haven or defensive bid are both present.
2. `rates_led_stress`: rates stress is present and no safe-haven or defensive bid is present.
3. `riskoff_confirmed`: no rates stress, but safe-haven or defensive bid is present.
4. `unconfirmed`: all other fully observed cases.

If any required FREQ_010 input is missing, the state must remain missing.

### Early-History Missing Inputs

Risk: Existing full-coverage booleans such as `vol_term_inversion_flag` can mask the fact that specific term-structure inputs were unavailable in early history.

Decision:

- FREQ_007 must require `vix9d_vs_vix`, `vix3m_vs_vix`, `vvix_level`, `skew_index`, and `panic_vol_flag` availability before producing daily stress count.
- FREQ_007 must report pre/post `vix9d_vs_vix` coverage in validation.
- Missing early VIX9D or VIX3M history must not be interpreted as calm.

### Future Information

Risk: Feature construction could accidentally reference future targets, future returns, or forward drawdowns.

Decision:

- Batch A reads only same-date and trailing fields from the exported daily feature table.
- No target labels, future returns, forward drawdowns, event files, hypothesis outputs, or test labels are read.
- Descriptive overlap is allowed only against existing same-date related columns and cannot use target labels.

## Adjusted Formulas

### FREQ_008: Regime-Shift Volatility Disagreement

Raw components:

```text
short_vs_medium = abs(qqq_vol_10d / qqq_vol_60d - 1)
short_vs_long = abs(qqq_vol_20d / realized_vol_252d - 1)
implied_cross_market = abs((vxn / vix) - trailing_252d_median(vxn / vix))
existing_ratio_distance = abs(vol_20d_vs_252d - 1)
```

Normalize each component:

```text
component_percentile = trailing_percentile(component, window=252, min_periods=126)
```

Then average normalized components only:

```text
freq_008_vol_disagreement_score =
  mean(short_vs_medium_pct, short_vs_long_pct, implied_cross_market_pct, existing_ratio_distance_pct)
```

The mean requires all four normalized components to be present.

Flag and rank-change:

```text
freq_008_vol_disagreement_score_pct = trailing_percentile(freq_008_vol_disagreement_score, 252, 126)
freq_008_vol_disagreement_rank_change_20d =
  freq_008_vol_disagreement_score_pct - freq_008_vol_disagreement_score_pct.shift(20)
freq_008_vol_disagreement_flag =
  freq_008_vol_disagreement_score_pct >= 0.80
```

### FREQ_007: Volatility Term-Structure Stress Persistence

Availability gate:

```text
term_inputs_available =
  vix9d_vs_vix, vix3m_vs_vix, vvix_level, skew_index, panic_vol_flag are all non-null
```

Stress components:

```text
front_vol_inverted = (vix9d_vs_vix > 0) OR (vix3m_vs_vix < 0) OR vol_term_inversion_flag
tail_demand = trailing_percentile(vvix_level, 252, 126) >= 0.80
              OR trailing_percentile(skew_index, 252, 126) >= 0.80
panic = panic_vol_flag
```

If `term_inputs_available` is false, all FREQ_007 outputs remain missing.

Outputs:

```text
freq_007_vol_term_daily_stress_count = sum(front_vol_inverted, tail_demand, panic)
freq_007_vol_term_stress_persistence_5d = rolling_5d_mean(daily_stress_count > 0)
freq_007_vol_term_stress_persistence_20d = rolling_20d_mean(daily_stress_count > 0)
freq_007_vol_term_persistent_stress_flag = freq_007_vol_term_stress_persistence_20d >= 0.50
```

Persistence outputs remain missing until the corresponding rolling window is fully available.

### FREQ_010: Safe-Haven Rotation Confirmation

Availability gate:

```text
all FREQ_010 input columns must be non-null
```

State ingredients:

```text
treasury_bid = (tlt_ret_20d > 0) OR (ief_ret_20d > 0) OR (tlt_ief_rel_3m > 0)
defensive_bid = (xlu_vs_spy_3m > 0) OR (xlp_vs_spy_3m > 0)
rates_stress = ust10y_change_20d >= 0.25
safe_haven_or_defensive_bid = treasury_bid OR defensive_bid
```

Mutually exclusive state:

```text
mixed_defensive_rates_stress if rates_stress AND safe_haven_or_defensive_bid
rates_led_stress if rates_stress AND NOT safe_haven_or_defensive_bid
riskoff_confirmed if NOT rates_stress AND safe_haven_or_defensive_bid
unconfirmed otherwise
```

Flags:

```text
freq_010_rates_led_stress_flag = state == "rates_led_stress"
freq_010_riskoff_confirmation_flag = state == "riskoff_confirmed"
```

The mixed state is intentionally separate from both flags to avoid precedence conflicts.
