# QQQ Risk Monitor - Codex Draft Hypotheses

Source discipline: these five hypotheses use only feature columns present in `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv`. No backtests, threshold optimization, production dashboard changes, or sentiment backtest assumptions were made. Threshold language below is intended for future purged walk-forward validation, using training-window quantiles or fixed economic levels specified before each validation fold.

## H001 - Range Expansion With Downside Tape Damage Predicts 30BD Path Risk

**hypothesis_id:** H001

**title:** Range expansion with downside tape damage predicts 30BD path risk

**plain_english_thesis:** When QQQ's recent range and realized volatility expand while the daily tape shows more downside gaps, large red days, and negative skew, future drawdown path risk should rise even if the medium-term trend has not yet broken.

**economic_market_mechanism:** Range expansion and rising short-run volatility imply less stable price discovery. Downside gaps, large red days, and negative realized skew indicate that sellers are increasingly controlling the left tail. Together they should identify fragile paths where a modest catalyst can become a larger drawdown.

**feature_families_used:**
- C. Volatility / Range / Path Risk

**exact_feature_columns_used:**
- range_20d_vs_252d
- vol_20d_vs_252d
- gap_down_count_20d
- large_red_day_count_20d
- realized_skew_20d

**expected_direction:**
- range_20d_vs_252d: higher_is_worse
- vol_20d_vs_252d: higher_is_worse
- gap_down_count_20d: higher_is_worse
- large_red_day_count_20d: higher_is_worse
- realized_skew_20d: lower_is_worse

**target_horizon:** 30BD

**target_type:** path_risk

**target_definition:** Future 30BD maximum drawdown is computed from the forward path of `qqq_close` after the signal date. A hit is `future_30bd_mdd <= -8%`; a secondary severity cut can track `future_30bd_mdd <= -10%`.

**trigger_logic_pseudocode:**

```text
range_stress = range_20d_vs_252d >= training_window_q80
vol_stress = vol_20d_vs_252d >= training_window_q80
downside_tape = (
  gap_down_count_20d >= training_window_q80
  OR large_red_day_count_20d >= training_window_q80
  OR realized_skew_20d <= training_window_q20
)
trigger = range_stress AND vol_stress AND downside_tape
```

**why_this_should_work:** QQQ drawdowns often begin with instability before a clean trend break. This combination looks for unstable realized range plus evidence that the volatility is downside-led, which is more directly tied to future maximum drawdown than a plain momentum or return signal.

**when_this_may_fail:** It may over-alert during orderly volatility expansions in strong bull markets, around earnings-heavy periods, or when large ranges resolve upward because liquidity remains abundant.

**data_quality_or_leakage_risks:** The features are price-derived and have high historical coverage. Leakage risk is low if all rolling features are computed using data available at or before the signal close. Quantile thresholds must be estimated only on each training window.

**minimum_data_coverage_requirement:** Require at least 10 years of non-null observations for all five features and at least five distinct future 30BD drawdown episodes at the selected severity threshold in the validation sample.

**validation_plan:**
- future_mdd_hit_rate: Compare future 30BD MDD hit rate on alert days versus all eligible days.
- base_rate_lift: Report hit-rate lift over the unconditional base rate and over single-feature alerts.
- alert_burden: Report percent of eligible days alerted, contiguous alert episodes per year, and median alert duration.
- event_coverage: For each severe 30BD drawdown episode, measure whether an alert occurred in the prior 1 to 20 business days.
- false_calm_false_repair: Count future 30BD MDD hits with no prior alert as false calm; separately flag alerts after apparent volatility relief that still lead to drawdown.
- purged_walk_forward: Use rolling or expanding train/test splits with a purge and embargo at least equal to 30BD so overlapping forward paths do not leak.

**dashboard_implication:** Add a path-risk warning strip that highlights whether volatility expansion is downside-led rather than treating all high volatility as equivalent.

**future_data_requirement:** None.

**priority_score:** 9

## H002 - Cap-Weighted Strength With Weak Breadth And Semiconductor Non-Confirmation Predicts Narrow-Leadership Fragility

**hypothesis_id:** H002

**title:** Cap-weighted strength with weak breadth and semiconductor non-confirmation predicts narrow-leadership fragility

**plain_english_thesis:** When QQQ outperforms equal-weight and broad-market proxies while Mag7 breadth weakens and semiconductor confirmation fades, the index may be more vulnerable to a future 60BD drawdown because leadership is too narrow.

**economic_market_mechanism:** QQQ can remain strong while fewer components and leadership groups carry the index. If cap-weight QQQ is ahead of equal-weight or broad proxies and semiconductors stop confirming, the rally depends on a smaller leadership base. Narrow leadership can unwind quickly when crowded winners stop absorbing risk.

**feature_families_used:**
- E. Breadth / Market Internals
- F. Leadership / Relative Strength
- G. Semiconductor / AI / Tech Confirmation

**exact_feature_columns_used:**
- qqq_vs_qqqe_3m
- qqq_vs_rsp_3m
- mag7_breadth
- semis_failure_flag
- qqq_up_soxx_down_20d
- smh_vs_qqq_3m

**expected_direction:**
- qqq_vs_qqqe_3m: higher_is_worse
- qqq_vs_rsp_3m: higher_is_worse
- mag7_breadth: lower_is_worse
- semis_failure_flag: true_is_worse
- qqq_up_soxx_down_20d: true_is_worse
- smh_vs_qqq_3m: lower_is_worse

**target_horizon:** 60BD

**target_type:** narrow_leadership_fragility

**target_definition:** Future 60BD maximum drawdown is computed from the forward path of `qqq_close` after the signal date. A hit is `future_60bd_mdd <= -10%`; event coverage should also track whether the signal appears before severe drawdown episodes.

**trigger_logic_pseudocode:**

```text
cap_weight_leadership = (
  qqq_vs_qqqe_3m >= training_window_q80
  OR qqq_vs_rsp_3m >= training_window_q80
)
leadership_thinning = mag7_breadth <= training_window_q30
semis_non_confirmation = (
  semis_failure_flag == True
  OR qqq_up_soxx_down_20d == True
  OR smh_vs_qqq_3m <= training_window_q30
)
trigger = cap_weight_leadership AND (leadership_thinning OR semis_non_confirmation)
```

**why_this_should_work:** Narrow leadership is not the same as a bearish return call. The thesis is that the forward path becomes more fragile when the index's apparent strength is less broadly confirmed and when semiconductor leadership is no longer reinforcing the QQQ advance.

**when_this_may_fail:** It may fail during durable mega-cap led markets where passive flows, AI-capex optimism, or index concentration keep QQQ resilient despite weak equal-weight participation.

**data_quality_or_leakage_risks:** `qqq_vs_qqqe_3m` begins later than most price-derived features because QQQE history starts in 2012. Placeholder breadth fields such as point-in-time percent above moving averages should not be used unless real historical component-level data is added.

**minimum_data_coverage_requirement:** Validate the full feature set only from the first date with non-null `qqq_vs_qqqe_3m`; require enough 60BD drawdown episodes after 2012 to avoid a single-regime result. A longer-history variant may drop `qqq_vs_qqqe_3m`.

**validation_plan:**
- future_mdd_hit_rate: Compare future 60BD MDD hit rate on narrow-leadership alerts versus all eligible post-2012 days.
- base_rate_lift: Report lift versus unconditional 60BD MDD base rate and versus semiconductor-only or breadth-only alerts.
- alert_burden: Measure alert days, alert episodes per year, and whether signals cluster into a small number of long warnings.
- event_coverage: Measure coverage of major QQQ drawdown episodes with a 5 to 40BD lead window.
- false_calm_false_repair: Count severe 60BD drawdowns missed by the leadership-fragility alert as false calm; count alerts followed by broadening leadership and no drawdown as repair cases.
- purged_walk_forward: Use post-2012 purged walk-forward splits with at least 60BD purge and embargo; compute thresholds only within each training split.

**dashboard_implication:** Add a narrow-leadership diagnostic that separates cap-weight outperformance from healthy broad confirmation.

**future_data_requirement:** Point-in-time Nasdaq component breadth would improve this hypothesis. Placeholder columns `pct_above_50dma` and `new_highs_lows_20d` were not used because the catalog shows zero coverage.

**priority_score:** 8

## H003 - Apparent MMDI Repair Without Price Repair Predicts False Repair

**hypothesis_id:** H003

**title:** Apparent MMDI repair without price repair predicts false repair

**plain_english_thesis:** When MMDI stress appears to be falling from a prior high but QQQ has not reclaimed trend levels and remains meaningfully below its 52-week high, the improvement may be a false repair that precedes renewed drawdown risk.

**economic_market_mechanism:** Risk indicators can cool after an initial stress burst while price damage remains unresolved. If volatility or breadth stress improves but price fails to reclaim trend, the market may be pausing rather than repairing. Such pauses can reset hedges and confidence before the next downside leg.

**feature_families_used:**
- MMDI signal layer
- A. Price / Trend Structure
- B. Drawdown / Distance from High

**exact_feature_columns_used:**
- mmdi_falling_from_high
- mmdi_low_after_high
- mmdi_20d_change
- failed_reclaim_ma50
- price_vs_ma50
- dist_52w_high
- rebound_from_trough_20d

**expected_direction:**
- mmdi_falling_from_high: more_negative_is_repair_context
- mmdi_low_after_high: true_is_repair_context
- mmdi_20d_change: lower_is_repair_context
- failed_reclaim_ma50: true_is_worse
- price_vs_ma50: lower_is_worse
- dist_52w_high: lower_is_worse
- rebound_from_trough_20d: higher_with_failed_reclaim_is_worse

**target_horizon:** 30BD

**target_type:** repair_failure

**target_definition:** A repair-failure hit occurs when an apparent repair trigger is followed by `future_30bd_mdd <= -8%`, computed from the forward path of `qqq_close`. A secondary audit should track whether the future 30BD path makes a lower low than the signal date.

**trigger_logic_pseudocode:**

```text
stress_cooling = (
  mmdi_falling_from_high <= training_window_q20
  OR mmdi_low_after_high == True
  OR mmdi_20d_change <= training_window_q20
)
price_not_repaired = (
  failed_reclaim_ma50 == True
  OR price_vs_ma50 <= 0
  OR dist_52w_high <= -0.05
)
bounce_context = rebound_from_trough_20d >= training_window_q60
trigger = stress_cooling AND price_not_repaired AND bounce_context
```

**why_this_should_work:** Repair failure is explicitly about the gap between indicator relief and price confirmation. The hypothesis should catch periods where risk gauges look better but the market has not actually regained durable trend structure.

**when_this_may_fail:** It may fail when price repair lags indicator repair but eventually catches up, especially after policy support, earnings surprises, or broad liquidity easing.

**data_quality_or_leakage_risks:** MMDI-derived features must be computed exactly as they would have been known at the signal close. The target must not use future MMDI values; only the forward QQQ path should define the outcome.

**minimum_data_coverage_requirement:** Require non-null MMDI repair features back to at least 2002 and enough high-to-low-to-repair cycles to evaluate false-repair behavior across multiple drawdown regimes.

**validation_plan:**
- future_mdd_hit_rate: Compare future 30BD MDD hit rate after repair-failure alerts versus all apparent-repair days.
- base_rate_lift: Report lift against the base rate for all days and against the base rate for stress-cooling days alone.
- alert_burden: Report how often the combined false-repair trigger fires and the median number of alert days per repair episode.
- event_coverage: For each renewed drawdown after a stress peak, measure whether the alert appeared before the second leg lower.
- false_calm_false_repair: Explicitly classify false calm as drawdown after no alert and false repair as stress-cooling with no price confirmation followed by a drawdown hit.
- purged_walk_forward: Use walk-forward folds purged by at least 30BD, with repair-context quantiles estimated only on the training side.

**dashboard_implication:** Add a "repair quality" panel that distinguishes cooling stress from confirmed trend repair.

**future_data_requirement:** None.

**priority_score:** 9

## H004 - Credit, Dollar, Rates, And Front-Vol Stress Predict Acute QQQ Shock Risk

**hypothesis_id:** H004

**title:** Credit, dollar, rates, and front-vol stress predict acute QQQ shock risk

**plain_english_thesis:** When credit stops confirming an equity rally and front-end volatility, the dollar, or rate-vol proxies are stressed, QQQ should have elevated 15BD acute shock risk.

**economic_market_mechanism:** QQQ is long-duration and liquidity-sensitive. Acute downside can emerge when credit risk widens, lower-quality credit lags higher-quality credit, the dollar or yields shock higher, and short-dated volatility reprices. Cross-asset confirmation matters because it suggests stress is not just an equity-tape fluctuation.

**feature_families_used:**
- I. Credit / Funding Stress
- J. Vol / Options / Tail Stress
- H. Rates / Yield Curve

**exact_feature_columns_used:**
- credit_worsening_equity_up
- credit_not_confirming_equity
- hy_oas_change_20d
- hyg_vs_lqd_20d
- vix9d_vs_vix
- usd_yield_shock
- rate_vol_proxy
- dxy_change_20d

**expected_direction:**
- credit_worsening_equity_up: true_is_worse
- credit_not_confirming_equity: true_is_worse
- hy_oas_change_20d: higher_is_worse
- hyg_vs_lqd_20d: lower_is_worse
- vix9d_vs_vix: higher_is_worse
- usd_yield_shock: true_is_worse
- rate_vol_proxy: higher_is_worse
- dxy_change_20d: higher_is_worse

**target_horizon:** 15BD

**target_type:** acute_shock

**target_definition:** Future 15BD maximum drawdown is computed from the forward path of `qqq_close`. A hit is `future_15bd_mdd <= -5%`; a secondary confirmation target is `future_30bd_mdd <= -8%`.

**trigger_logic_pseudocode:**

```text
credit_stress = (
  credit_worsening_equity_up == True
  OR credit_not_confirming_equity == True
  OR hy_oas_change_20d >= training_window_q80
  OR hyg_vs_lqd_20d <= training_window_q20
)
front_vol_or_macro_shock = (
  vix9d_vs_vix >= training_window_q80
  OR usd_yield_shock == True
  OR (rate_vol_proxy >= training_window_q80 AND dxy_change_20d >= training_window_q70)
)
trigger = credit_stress AND front_vol_or_macro_shock
```

**why_this_should_work:** Fast QQQ drawdowns are often cross-asset events rather than isolated equity weakness. Credit, dollar, rates, and short-vol stress can identify the pressure points that force de-risking before the QQQ price trend fully reflects it.

**when_this_may_fail:** It may fail when credit or rate stress is idiosyncratic, when central-bank liquidity offsets the shock, or when QQQ earnings momentum dominates macro pressure.

**data_quality_or_leakage_risks:** Some series have shorter histories, especially `vix9d_vs_vix`. Credit proxies may rely on end-of-day or revised source timing; validation should align feature availability to the signal close and avoid same-day publication leakage where relevant.

**minimum_data_coverage_requirement:** Require validation both on the full available cross-asset window and on a common-history subset beginning when `vix9d_vs_vix` is non-null.

**validation_plan:**
- future_mdd_hit_rate: Measure future 15BD MDD hit rate for acute-shock alerts versus all eligible days.
- base_rate_lift: Report lift versus unconditional 15BD shock base rate and versus credit-only or vol-only alerts.
- alert_burden: Report alert-day share, number of acute alert episodes per year, and median lead time to the worst forward drawdown.
- event_coverage: Measure coverage of known acute QQQ drawdown episodes with alerts in the prior 1 to 10BD.
- false_calm_false_repair: Count acute shocks without prior cross-asset alert as false calm; count alerts followed by falling credit stress and no drawdown as repaired stress.
- purged_walk_forward: Use purged walk-forward splits with at least 15BD purge and embargo; all quantiles must be fit only inside training windows.

**dashboard_implication:** Add a cross-asset acute-shock tile separate from slower R2/MMDI fragility states.

**future_data_requirement:** None.

**priority_score:** 8

## H005 - Distribution And Illiquidity After A Strong Advance Predict 60BD Path Risk

**hypothesis_id:** H005

**title:** Distribution and illiquidity after a strong advance predict 60BD path risk

**plain_english_thesis:** After a strong QQQ advance, negative OBV behavior, abnormal volume or dollar volume, and rising illiquidity should signal that accumulation is weakening and future 60BD drawdown path risk is higher.

**economic_market_mechanism:** Late-stage advances can mask distribution. If QQQ has recently rallied but volume/OBV deteriorates and illiquidity rises, marginal buyers may be less willing or able to absorb selling. That creates path fragility without requiring an immediate bearish return forecast.

**feature_families_used:**
- D. Momentum / Reversal
- B. Drawdown / Distance from High
- L. Liquidity / Volume / Flow
- C. Volatility / Range / Path Risk

**exact_feature_columns_used:**
- qqq_ret_3m
- dist_52w_high
- qqq_volume_z_20d
- dollar_volume_z_20d
- obv_20d_chg
- obv_60d_chg
- amihud_illiquidity_proxy

**expected_direction:**
- qqq_ret_3m: higher_is_advance_context_not_bullish_signal
- dist_52w_high: higher_or_near_zero_is_advance_context
- qqq_volume_z_20d: higher_with_negative_obv_is_worse
- dollar_volume_z_20d: higher_with_negative_obv_is_worse
- obv_20d_chg: lower_is_worse
- obv_60d_chg: lower_is_worse
- amihud_illiquidity_proxy: higher_is_worse

**target_horizon:** 60BD

**target_type:** path_risk

**target_definition:** Future 60BD maximum drawdown is computed from the forward path of `qqq_close`. A hit is `future_60bd_mdd <= -10%`; a softer secondary target is `future_30bd_mdd <= -8%`.

**trigger_logic_pseudocode:**

```text
advance_context = (
  qqq_ret_3m >= training_window_q70
  AND dist_52w_high >= -0.05
)
distribution = (
  obv_20d_chg <= training_window_q30
  OR obv_60d_chg <= training_window_q30
)
abnormal_activity = (
  qqq_volume_z_20d >= 1.0
  OR dollar_volume_z_20d >= 1.0
)
liquidity_friction = amihud_illiquidity_proxy >= training_window_q80
trigger = advance_context AND distribution AND (abnormal_activity OR liquidity_friction)
```

**why_this_should_work:** This is not a momentum hypothesis. The recent advance and near-high state define the setup; the actual risk signal is distribution and liquidity friction. That mix should identify rallies vulnerable to a sharper forward path if selling pressure appears.

**when_this_may_fail:** It may fail when high volume reflects healthy institutional accumulation, when OBV weakness is temporary, or when liquidity improves quickly after a short consolidation.

**data_quality_or_leakage_risks:** Volume-derived features are point-in-time if computed from historical OHLCV through the signal close. `amihud_illiquidity_proxy` should be checked for extreme outliers and split-adjustment artifacts.

**minimum_data_coverage_requirement:** Require at least 10 years of non-null volume and OBV features and at least five 60BD drawdown episodes to judge event-level coverage.

**validation_plan:**
- future_mdd_hit_rate: Compare future 60BD MDD hit rate on distribution/liquidity alerts versus all advance-context days.
- base_rate_lift: Report lift over the unconditional 60BD drawdown base rate and over advance-context days alone.
- alert_burden: Measure alert frequency, contiguous episode count, and whether alerts are concentrated near market highs.
- event_coverage: For major 60BD drawdown episodes, measure whether distribution/liquidity alerts appeared within the prior 10 to 40BD.
- false_calm_false_repair: Count drawdowns after strong advances with no distribution alert as false calm; count alerts followed by positive OBV repair and no drawdown as repaired distribution.
- purged_walk_forward: Use training-window quantiles for OBV and illiquidity, with a purge and embargo of at least 60BD around validation splits.

**dashboard_implication:** Add a distribution/liquidity subpanel that warns when a rally's participation quality is deteriorating.

**future_data_requirement:** Point-in-time ETF flow and true up/down volume would strengthen this hypothesis. Placeholder columns `up_down_volume_ratio_20d`, `volume_on_down_days`, and `volume_on_up_days` were not used because the catalog shows zero coverage.

**priority_score:** 8
