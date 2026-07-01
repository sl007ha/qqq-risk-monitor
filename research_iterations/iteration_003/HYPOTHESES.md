# Iteration 003 Hypotheses

Iteration 003 uses iteration 002 evidence as the prior. It generates five pre-declared, research-only hypotheses. Thresholds are deterministic training-window quantiles or fixed economic constants. No threshold optimization is performed. No live sentiment or headline features are used.

## I003_H001 - Downside volatility with flexible trend pressure predicts 30BD path risk

**Thesis:** When QQQ range and realized volatility expand while downside tape pressure is visible, future 30-business-day drawdown risk should rise even if QQQ has not fully broken below its short trend.

**Mechanism:** Range expansion and realized-volatility expansion indicate unstable price discovery. Negative skew, gap-down frequency, or large red days show that volatility is being expressed asymmetrically. Requiring either MA20 or MA50 pressure makes the test less brittle than I002_H001.

**Exact feature columns used:** `range_20d_vs_252d`, `vol_20d_vs_252d`, `realized_skew_20d`, `gap_down_count_20d`, `large_red_day_count_20d`, `price_vs_ma20`, `price_vs_ma50`

**Target:** future 30BD maximum drawdown <= -8%

**Trigger pseudocode:** high 20D range, high 20D volatility, downside tape stress, and either weak MA20 or weak MA50 relative pressure.

**Validation:** future MDD hit rate, base-rate lift, alert burden, event coverage, false calm / false repair evidence, purged walk-forward folds, and lead-time distribution.

**Priority:** 9

## I003_H002 - Early cross-asset deterioration plus restrained vol confirmation predicts acute shock

**Thesis:** When credit or funding stress deteriorates while rates, dollar, or volatility pressure confirms the stress, QQQ should face elevated 15-business-day acute drawdown risk.

**Mechanism:** Credit and funding stress can lead equity drawdowns, while front-vol, rate-vol, and dollar pressure often confirm that stress is becoming urgent. This iteration asks whether macro confirmation improves lead time relative to I002_H002.

**Exact feature columns used:** `credit_worsening_equity_up`, `credit_not_confirming_equity`, `hy_oas_change_20d`, `hyg_vs_lqd_20d`, `rate_vol_proxy`, `dxy_change_20d`, `usd_yield_shock`, `vix_percentile_252d`, `vix9d_vs_vix`

**Target:** future 15BD maximum drawdown <= -5%

**Trigger pseudocode:** credit stress plus macro pressure plus restrained volatility confirmation.

**Validation:** future MDD hit rate, base-rate lift, alert burden, event coverage, false calm episodes, purged walk-forward folds, and lead-time distribution versus I002_H002.

**Priority:** 8

## I003_H003 - Narrow-leadership coverage companion predicts 60BD fragility

**Thesis:** When cap-weighted QQQ leadership stays ahead of equal-weight or broad-market proxies while semiconductors or breadth fail to confirm, the index should face higher 60-business-day fragility risk.

**Mechanism:** Narrow leadership can hide weakening market participation. This version relaxes the final confirmation gate from I002_H003 to test whether coverage can improve without returning to a high-burden alert.

**Exact feature columns used:** `qqq_vs_qqqe_3m`, `qqq_vs_rsp_3m`, `qqq_vs_soxx_3m`, `smh_vs_qqq_3m`, `semis_failure_flag`, `qqq_up_soxx_down_20d`, `mag7_breadth`, `mmdi_leadership_narrowing_stress`

**Target:** future 60BD maximum drawdown <= -10%

**Trigger pseudocode:** cap-weight divergence plus either semiconductor non-confirmation or weak breadth / MMDI leadership stress.

**Validation:** future MDD hit rate, base-rate lift, alert burden, event coverage, false calm episodes, purged walk-forward folds, and lead-time distribution.

**Priority:** 8

## I003_H004 - Simplified false repair with unresolved damage predicts 30BD repair failure

**Thesis:** When MMDI appears to be repairing after stress but price damage remains unresolved and QQQ is bouncing from a trough, the market may be vulnerable to failed repair and renewed drawdown.

**Mechanism:** I002_H004 was over-constrained and produced no hits. This version removes the renewed-stress gate to test whether the false-repair mechanism has any signal before adding complexity back.

**Exact feature columns used:** `mmdi_falling_from_high`, `mmdi_low_after_high`, `MMDI_HIGH`, `failed_reclaim_ma50`, `failed_reclaim_ma200`, `price_vs_ma50`, `dist_52w_high`, `rebound_from_trough_20d`

**Target:** future 30BD maximum drawdown <= -8%

**Trigger pseudocode:** apparent MMDI repair plus unresolved price damage plus a bounce-from-trough context.

**Validation:** future MDD hit rate, base-rate lift, alert burden, event coverage, false repair and false calm episodes, purged walk-forward folds, and yearly stability.

**Priority:** 6

## I003_H005 - R2 quiet plus MMDI stress confirmed by volatility or credit predicts false calm

**Thesis:** When R2 is quiet but MMDI remains elevated or accelerating, QQQ false-calm risk should rise only if an independent volatility or credit channel confirms the stress.

**Mechanism:** I002_H005 covered many events but had no lift as a standalone alert. This stricter second-stage filter tests whether independent confirmation can reduce alert burden while preserving useful event coverage.

**Exact feature columns used:** `R2_ACTIVE`, `R2_STRESS_COUNT`, `MMDI`, `MMDI_10D_CHANGE`, `MMDI_HIGH`, `range_20d_vs_252d`, `vol_20d_vs_252d`, `credit_not_confirming_equity`, `hy_oas_change_20d`

**Target:** future 30BD maximum drawdown <= -8%

**Trigger pseudocode:** R2 quiet, MMDI elevated or accelerating, and independent confirmation from volatility/range expansion or credit deterioration.

**Validation:** future MDD hit rate, base-rate lift, alert burden, event coverage, false calm episodes, purged walk-forward folds, and lead-time distribution.

**Priority:** 7
