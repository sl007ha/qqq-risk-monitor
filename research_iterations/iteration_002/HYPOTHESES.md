# Iteration 002 Hypotheses

This file defines exactly five research-only hypotheses for the second QQQ Risk Monitor research iteration. They are revised from prior test evidence and use only columns available in `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv`.

No thresholds were optimized. Trigger thresholds are deterministic training-window quantiles or explicit economic constants declared before testing. Live sentiment features are not used.

## I002_H001 - Downside range expansion plus short-trend pressure predicts 30BD path risk

Revised from prior H001.

**Thesis:** QQQ has higher 30BD drawdown path risk when range and realized volatility are elevated, downside tape damage is visible, and price has started losing short-term trend support.

**Mechanism:** Prior H001 showed strong lift but uneven yearly stability. This revision keeps the downside-volatility mechanism and adds short-trend pressure so the alert focuses on volatility that is already translating into price damage.

**Feature families:** C. Volatility / Range / Path Risk; A. Price / Trend Structure.

**Exact feature columns used:** `range_20d_vs_252d`, `vol_20d_vs_252d`, `realized_skew_20d`, `gap_down_count_20d`, `large_red_day_count_20d`, `price_vs_ma20`.

**Expected direction:** Higher range, higher vol, more gaps, more large red days, lower realized skew, and lower `price_vs_ma20` are worse.

**Target:** `future_30bd_mdd <= -8%`.

**Trigger pseudocode:**

```text
range_stress = range_20d_vs_252d >= training_q80
vol_stress = vol_20d_vs_252d >= training_q75
downside_tape = realized_skew_20d <= training_q25 OR gap_down_count_20d >= training_q75 OR large_red_day_count_20d >= training_q75
short_trend_pressure = price_vs_ma20 <= 0
trigger = range_stress AND vol_stress AND downside_tape AND short_trend_pressure
```

**Why this should work:** Downside range expansion is more dangerous when price is already losing short-term trend support.

**When this may fail:** It may miss early drawdowns that begin from above the 20-day average or over-alert in volatile but mean-reverting markets.

**Data/leakage risk:** Price-derived features have high coverage and low leakage risk when computed at the signal close.

**Minimum coverage:** At least 10 years of non-null data and multiple 30BD drawdown episodes.

**Validation plan:** Measure future MDD hit rate, base-rate lift, alert burden, event coverage, false calm, yearly fold stability, lead time, and purged walk-forward results.

**Dashboard implication:** Split volatility warnings into downside-confirmed and unconfirmed volatility.

**Priority:** 9

## I002_H002 - Credit stress confirmed by front-vol, dollar, or rate shock predicts 15BD acute shock

Revised from prior H004.

**Thesis:** QQQ has elevated 15BD acute drawdown risk when credit conditions deteriorate and the stress is confirmed by front volatility, dollar strength, or rate-vol pressure.

**Mechanism:** Prior H004 showed strong lift and relatively better yearly stability. This revision keeps the cross-asset structure but explicitly separates credit stress from a confirming macro/volatility shock.

**Feature families:** I. Credit / Funding Stress; J. Vol / Options / Tail Stress; H. Rates / Yield Curve.

**Exact feature columns used:** `credit_worsening_equity_up`, `credit_not_confirming_equity`, `hy_oas_change_20d`, `hyg_vs_lqd_20d`, `vix9d_vs_vix`, `vix_percentile_252d`, `usd_yield_shock`, `rate_vol_proxy`, `dxy_change_20d`.

**Expected direction:** Credit deterioration, higher OAS changes, weaker HYG versus LQD, higher front vol, higher VIX percentile, USD/yield shock, higher rate vol, and stronger dollar are worse.

**Target:** `future_15bd_mdd <= -5%`.

**Trigger pseudocode:**

```text
credit_stress = credit_worsening_equity_up OR credit_not_confirming_equity OR hy_oas_change_20d >= training_q80 OR hyg_vs_lqd_20d <= training_q20
confirming_shock = vix9d_vs_vix >= training_q80 OR vix_percentile_252d >= training_q80 OR usd_yield_shock OR (rate_vol_proxy >= training_q80 AND dxy_change_20d >= training_q70)
trigger = credit_stress AND confirming_shock
```

**Why this should work:** Fast Nasdaq drawdowns often occur when equity weakness is confirmed by funding, credit, volatility, and duration-pressure channels.

**When this may fail:** It may over-alert when credit stress is sector-specific or policy liquidity offsets macro pressure.

**Data/leakage risk:** Short-vol data begins later; credit timing should be aligned carefully in stricter future testing.

**Minimum coverage:** Validate both full-history and common-history windows beginning when short-vol data is available.

**Validation plan:** Measure acute-shock hit rate, lift, alert burden, event coverage, false calm, yearly fold stability, lead time, and purged walk-forward results.

**Dashboard implication:** Add a cross-asset acute shock research tile separate from slower fragility.

**Priority:** 9

## I002_H003 - Tightened narrow-leadership non-confirmation predicts 60BD fragility

Revised from prior H002.

**Thesis:** QQQ has elevated 60BD drawdown risk when cap-weighted strength is not confirmed by equal-weight, broad-market, semiconductor, or MMDI leadership measures.

**Mechanism:** Prior H002 had strong event coverage but high alert burden. This revision tightens the trigger to require multiple forms of non-confirmation.

**Feature families:** E. Breadth / Market Internals; F. Leadership / Relative Strength; G. Semiconductor / AI / Tech Confirmation; MMDI signal layer.

**Exact feature columns used:** `qqq_vs_qqqe_3m`, `qqq_vs_rsp_3m`, `qqq_vs_soxx_3m`, `smh_vs_qqq_3m`, `semis_failure_flag`, `qqq_up_soxx_down_20d`, `mag7_breadth`, `mmdi_leadership_narrowing_stress`.

**Expected direction:** Higher cap-weight divergence, higher QQQ versus SOXX divergence, lower SMH versus QQQ, semiconductor failure flags, lower Mag7 breadth, and higher MMDI leadership narrowing are worse.

**Target:** `future_60bd_mdd <= -10%`.

**Trigger pseudocode:**

```text
cap_weight_divergence = qqq_vs_qqqe_3m >= training_q75 OR qqq_vs_rsp_3m >= training_q75
semis_non_confirmation = qqq_vs_soxx_3m >= training_q75 OR smh_vs_qqq_3m <= training_q25 OR semis_failure_flag OR qqq_up_soxx_down_20d
breadth_or_mmdi_narrow = mag7_breadth <= training_q30 OR mmdi_leadership_narrowing_stress >= training_q75
trigger = cap_weight_divergence AND semis_non_confirmation AND breadth_or_mmdi_narrow
```

**Why this should work:** Narrow leadership is most fragile when broad participation and semiconductor leadership both fail to confirm cap-weight index strength.

**When this may fail:** It may fail in durable mega-cap concentration regimes.

**Data/leakage risk:** QQQE and MMDI leadership narrowing have shorter histories. Placeholder breadth features are not used.

**Minimum coverage:** Require common-history validation for QQQE and MMDI leadership data plus enough post-2014 60BD drawdown events.

**Validation plan:** Measure hit-rate lift, alert burden reduction, event coverage, false calm, lead time, yearly fold stability, and purged walk-forward results.

**Dashboard implication:** Require multi-channel non-confirmation for narrow-leadership warnings.

**Priority:** 8

## I002_H004 - Indicator repair with unresolved price damage and renewed tape stress predicts false repair

Revised from prior H003.

**Thesis:** QQQ has elevated false-repair risk when MMDI appears to be cooling, but price has not repaired trend damage and downside tape stress is returning.

**Mechanism:** Prior H003 had weak lift and low event coverage. This revision requires both apparent improvement and evidence that the market has failed to confirm that improvement.

**Feature families:** MMDI signal layer; A. Price / Trend Structure; B. Drawdown / Distance from High; C. Volatility / Range / Path Risk.

**Exact feature columns used:** `mmdi_falling_from_high`, `mmdi_low_after_high`, `MMDI_HIGH`, `failed_reclaim_ma50`, `failed_reclaim_ma200`, `price_vs_ma50`, `dist_52w_high`, `rebound_from_trough_20d`, `range_20d_vs_252d`, `large_red_day_count_20d`.

**Expected direction:** More apparent MMDI repair plus unresolved stress, failed reclaims, lower price trend, deeper distance from high, bounce context, higher range, and more large red days are worse.

**Target:** `future_30bd_mdd <= -8%`.

**Trigger pseudocode:**

```text
apparent_repair = mmdi_falling_from_high <= training_q25 OR mmdi_low_after_high
unresolved_damage = MMDI_HIGH OR failed_reclaim_ma50 OR failed_reclaim_ma200 OR price_vs_ma50 <= 0 OR dist_52w_high <= -0.05
bounce_context = rebound_from_trough_20d >= training_q60
renewed_tape_stress = range_20d_vs_252d >= training_q70 OR large_red_day_count_20d >= training_q75
trigger = apparent_repair AND unresolved_damage AND bounce_context AND renewed_tape_stress
```

**Why this should work:** False repair should require both an apparent improvement and evidence that price/tape has not confirmed repair.

**When this may fail:** It may miss slow second legs where tape stress returns only after the drawdown starts.

**Data/leakage risk:** MMDI and price features must be measured at the signal close; future MMDI values must not define the target.

**Minimum coverage:** Require MMDI history with multiple stress-cooling episodes and at least five 30BD drawdown events.

**Validation plan:** Compare hit rate after apparent-repair alerts against all apparent-repair days; track event coverage, false calm, alert burden, stability, lead time, and purged walk-forward results.

**Dashboard implication:** Show repair quality separately from falling MMDI.

**Priority:** 8

## I002_H005 - R2 quiet but MMDI accelerating predicts false-calm path risk

Replacement for prior H005.

**Thesis:** QQQ has elevated 30BD path risk when the R2 dashboard state is quiet but MMDI is high or accelerating through volatility, trend, or leadership stress components.

**Mechanism:** Prior H005 produced no useful alert hit rate. This replacement targets false calm directly: slow R2-style thresholds may remain inactive while MMDI components are already deteriorating.

**Feature families:** R2 signal layer; MMDI signal layer.

**Exact feature columns used:** `R2_ACTIVE`, `R2_STRESS_COUNT`, `MMDI`, `MMDI_10D_CHANGE`, `MMDI_HIGH`, `mmdi_vix_stress`, `mmdi_vxn_stress`, `mmdi_realized_vol_stress`, `mmdi_trend_damage`, `mmdi_leadership_narrowing_stress`.

**Expected direction:** R2 quiet is the context; higher MMDI, higher MMDI change, high MMDI flag, and higher component stresses are worse.

**Target:** `future_30bd_mdd <= -8%`.

**Trigger pseudocode:**

```text
r2_quiet = (R2_ACTIVE == False) AND R2_STRESS_COUNT <= 1
mmdi_elevated_or_accelerating = MMDI_HIGH OR MMDI >= training_q75 OR MMDI_10D_CHANGE >= training_q70
component_stress = mmdi_vix_stress >= training_q70 OR mmdi_vxn_stress >= training_q70 OR mmdi_realized_vol_stress >= training_q75 OR mmdi_trend_damage >= training_q70 OR mmdi_leadership_narrowing_stress >= training_q75
trigger = r2_quiet AND mmdi_elevated_or_accelerating AND component_stress
```

**Why this should work:** R2 and MMDI see different parts of the risk surface, so MMDI acceleration may reduce false calm when R2 is not active.

**When this may fail:** It may over-alert during benign volatility normalization or after the true danger has already passed.

**Data/leakage risk:** Uses derived dashboard state columns, but does not modify their definitions.

**Minimum coverage:** Require MMDI component coverage after 2001 and a common-history check for leadership narrowing after 2014.

**Validation plan:** Measure hit-rate lift among R2-quiet days, false-calm event reduction, alert burden, lead time, yearly stability, and purged walk-forward results.

**Dashboard implication:** Add a research-only false-calm overlay when R2 is quiet but MMDI accelerates.

**Priority:** 8
