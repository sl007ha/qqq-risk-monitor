# Codex / Superpowers Hypothesis Test — 5 Seed Hypotheses

Purpose: create a small, high-quality hypothesis sample to compare against the free-form local Qwen output.

Method: these hypotheses are constrained to existing QQQ Risk Monitor feature names and are written in the style Codex should follow when using Superpowers-style brainstorming / evidence-over-claims discipline. They are research hypotheses only, not trading recommendations.

## Quality bar

A usable hypothesis must:

- use exact existing feature columns only;
- define future drawdown / path-risk / repair-failure target explicitly;
- explain the economic mechanism;
- distinguish path risk from bearish return;
- include failure modes and validation plan;
- avoid current-event narrative unless marked as current-context only.

---

## H001 — Range expansion plus semiconductor non-confirmation predicts 30BD path risk

**Target type:** path_risk  
**Target horizon:** 30BD  
**Target definition:** future 30BD maximum drawdown <= -8% or -10%.

**Thesis:** When QQQ trading range expands while semiconductor leadership stops confirming QQQ strength, the index may look resilient but the future path becomes more fragile.

**Mechanism:** QQQ drawdowns often emerge when the headline index remains supported by large-cap concentration while its leadership engine weakens underneath. Expanding realized range suggests unstable price discovery; weak semiconductor confirmation suggests that core Nasdaq risk appetite is no longer broad or durable.

**Exact feature columns:**

- `range_20d_vs_252d`
- `qqq_vs_soxx_3m`
- `qqq_vs_soxx_6m`
- `soxx_ret_3m`
- `smh_vs_qqq_3m`
- `vix_change_20d`

**Expected direction:**

- `range_20d_vs_252d`: higher_is_worse
- `qqq_vs_soxx_3m`: higher_is_worse
- `qqq_vs_soxx_6m`: higher_is_worse
- `soxx_ret_3m`: lower_is_worse
- `smh_vs_qqq_3m`: lower_is_worse
- `vix_change_20d`: higher_is_worse

**Trigger logic pseudocode:**

```text
high(range_20d_vs_252d) AND
(high(qqq_vs_soxx_3m) OR high(qqq_vs_soxx_6m)) AND
(weak(soxx_ret_3m) OR weak(smh_vs_qqq_3m))
```

**Why this should work:** Semiconductors are a key confirmation layer for Nasdaq / AI leadership. If QQQ outperforms semiconductors while realized range expands, QQQ strength may be narrower and more vulnerable to a sharp path reversal.

**When it may fail:** In liquidity-driven melt-ups, QQQ can continue rising despite semiconductor underperformance, especially if mega-cap software or platform stocks absorb leadership.

**Data / leakage risk:** Low, because all required inputs are market prices available at close. Avoid using same-day close to trade same-day signal.

**Validation plan:**

- single-feature lift for `range_20d_vs_252d`;
- pairwise interaction lift with `qqq_vs_soxx_3m` / `qqq_vs_soxx_6m`;
- 30BD future MDD hit rate;
- alert burden and base-rate lift;
- period concentration check around 2000, 2008, 2020, 2022.

**Dashboard implication:** Candidate for a “semiconductor non-confirmation path-risk” warning track, not an automatic bearish signal.

**Priority score:** 9/10

---

## H002 — MMDI repair without credit confirmation predicts false repair

**Target type:** repair_failure  
**Target horizon:** 30BD / 60BD  
**Target definition:** after MMDI improves from a high-stress zone, future 30BD or 60BD maximum drawdown still breaches -8% / -10%.

**Thesis:** When MMDI falls from high stress but credit spreads continue to deteriorate, the apparent equity-market repair may be false.

**Mechanism:** Equity internals and volatility can improve quickly after a selloff, but credit markets often provide a slower-moving confirmation of whether systemic risk is actually healing. If MMDI improves while credit keeps worsening, equity repair may be tactical rather than durable.

**Exact feature columns:**

- `mmdi_10d_change`
- `mmdi_falling_from_high`
- `mmdi_low_after_high`
- `credit_spread_20d_change`
- `hy_oas_change_20d`
- `credit_spread_accel_20d`
- `hyg_vs_lqd_20d`

**Expected direction:**

- `mmdi_10d_change`: lower_is_repair_signal
- `mmdi_falling_from_high`: lower_is_repair_signal
- `mmdi_low_after_high`: true_is_repair_signal
- `credit_spread_20d_change`: higher_is_worse
- `hy_oas_change_20d`: higher_is_worse
- `credit_spread_accel_20d`: higher_is_worse
- `hyg_vs_lqd_20d`: lower_is_worse

**Trigger logic pseudocode:**

```text
(mmdi_10d_change < 0 OR mmdi_low_after_high == true) AND
(credit_spread_20d_change > 0 OR hy_oas_change_20d > 0 OR credit_spread_accel_20d > 0 OR hyg_vs_lqd_20d < 0)
```

**Why this should work:** A genuine repair should show confirmation across equity internals, volatility, and credit. If only equity internals improve while credit stress persists, drawdown risk may remain elevated.

**When it may fail:** Credit spreads can lag equity recovery in strong policy-easing regimes; the signal may be too conservative after central-bank intervention.

**Data / leakage risk:** Medium. FRED credit data can have publication timing and revision issues. Use close-to-close alignment and conservative lagging if needed.

**Validation plan:**

- isolate MMDI high-to-lower transitions;
- compare outcomes with and without credit confirmation;
- measure false-repair rate;
- measure 30BD / 60BD future MDD hit rate;
- purged walk-forward validation.

**Dashboard implication:** Candidate for a “repair quality” module that prevents premature risk-normalization when credit does not confirm.

**Priority score:** 10/10

---

## H003 — Cap-weight strength without equal-weight or small-cap confirmation predicts narrow-leadership fragility

**Target type:** narrow_leadership_fragility  
**Target horizon:** 60BD  
**Target definition:** future 60BD maximum drawdown <= -10% or high path-risk alert burden-adjusted lift.

**Thesis:** When QQQ rises but equal-weight Nasdaq, equal-weight S&P, and small caps fail to confirm, the rally is more concentrated and vulnerable to reversal.

**Mechanism:** Cap-weighted QQQ can remain strong when a few mega-cap names dominate index performance. If equal-weight and small-cap proxies lag, risk appetite is not broadening. Narrow leadership can persist, but when it breaks, drawdowns may be sharper because support is concentrated in fewer names.

**Exact feature columns:**

- `qqq_ret_1m`
- `qqq_ret_3m`
- `qqq_vs_qqqe_3m`
- `qqq_vs_rsp_3m`
- `qqq_vs_iwm_3m`
- `qqq_vs_iwm_6m`
- `mag7_breadth`
- `range_20d_vs_252d`

**Expected direction:**

- `qqq_ret_1m`: higher_can_be_crowding_context
- `qqq_ret_3m`: higher_can_be_crowding_context
- `qqq_vs_qqqe_3m`: higher_is_worse
- `qqq_vs_rsp_3m`: higher_is_worse
- `qqq_vs_iwm_3m`: higher_is_worse
- `qqq_vs_iwm_6m`: higher_is_worse
- `mag7_breadth`: lower_is_worse
- `range_20d_vs_252d`: higher_is_worse

**Trigger logic pseudocode:**

```text
positive(qqq_ret_1m OR qqq_ret_3m) AND
high(qqq_vs_qqqe_3m) AND
(high(qqq_vs_iwm_3m) OR high(qqq_vs_rsp_3m)) AND
(low(mag7_breadth) OR high(range_20d_vs_252d))
```

**Why this should work:** A rally supported by broad participation is usually healthier than one driven by a shrinking group of mega-cap leaders. Narrow participation increases vulnerability to leader-specific shocks.

**When it may fail:** Narrow mega-cap leadership can be rational and persistent when earnings concentration is real; signal may fire early in durable platform-led bull markets.

**Data / leakage risk:** Low to medium. Price data are available at close; `mag7_breadth` is derived from constituent prices but depends on static Mag7 definition.

**Validation plan:**

- compare high-concentration vs normal-concentration regimes;
- 60BD future MDD hit rate;
- severe-event recall under fixed alert burden;
- separate 2020–2026 mega-cap regime from earlier periods;
- check if signal adds value beyond R2 / MMDI.

**Dashboard implication:** Candidate for a “leadership quality” panel and a possible warning overlay during strong but narrow rallies.

**Priority score:** 8/10

---

## H004 — Rate and dollar shock during QQQ resilience predicts growth-duration stress

**Target type:** cross_asset_stress  
**Target horizon:** 30BD  
**Target definition:** future 30BD maximum drawdown <= -8% or materially elevated path-risk relative to base rate.

**Thesis:** When QQQ remains resilient while long rates, real yields, and the dollar rise together, duration-sensitive growth assets may face delayed downside pressure.

**Mechanism:** QQQ is valuation-sensitive because much of its value is tied to long-duration earnings growth. A combined rate / real-yield / dollar shock can tighten financial conditions even before equity prices fully react. Equity resilience during that shock may reflect delayed repricing rather than genuine strength.

**Exact feature columns:**

- `qqq_ret_1m`
- `price_vs_ma50`
- `ust10y_change_20d`
- `real_yield_10y_change_20d`
- `dxy_change_20d`
- `usd_yield_shock`
- `tlt_ret_20d`
- `financial_conditions_index`

**Expected direction:**

- `qqq_ret_1m`: higher_is_resilience_context
- `price_vs_ma50`: higher_is_resilience_context
- `ust10y_change_20d`: higher_is_worse
- `real_yield_10y_change_20d`: higher_is_worse
- `dxy_change_20d`: higher_is_worse
- `usd_yield_shock`: true_is_worse
- `tlt_ret_20d`: lower_is_worse
- `financial_conditions_index`: higher_is_worse

**Trigger logic pseudocode:**

```text
positive(qqq_ret_1m) AND price_vs_ma50 > 0 AND
(ust10y_change_20d > 0 OR real_yield_10y_change_20d > 0) AND
(dxy_change_20d > 0 OR usd_yield_shock == true)
```

**Why this should work:** Rate and dollar shocks can compress growth equity valuations with a lag. If QQQ initially ignores the shock, subsequent path risk may rise once valuation pressure catches up.

**When it may fail:** If higher yields reflect stronger growth rather than tighter financial conditions, QQQ can absorb rate increases without drawdown.

**Data / leakage risk:** Medium. FRED real-yield and financial-conditions data may have timing differences. Use publication lag assumptions in formal testing.

**Validation plan:**

- event study around 20D rate/dollar shock windows;
- compare QQQ resilience vs QQQ weakness during shock;
- 30BD future MDD and realized volatility outcomes;
- walk-forward validation across inflation / disinflation regimes;
- check orthogonality vs VIX and credit features.

**Dashboard implication:** Candidate for a “duration shock despite equity resilience” risk note.

**Priority score:** 8/10

---

## H005 — Vol-term inversion plus credit worsening predicts acute shock risk

**Target type:** acute_shock  
**Target horizon:** 15BD / 30BD  
**Target definition:** future 15BD or 30BD maximum drawdown <= -6% / -8%, or sharp volatility expansion with elevated realized drawdown.

**Thesis:** When the volatility curve inverts and credit spreads worsen at the same time, market stress is more likely to become acute rather than a simple equity-only volatility spike.

**Mechanism:** A VIX curve inversion indicates near-term option-market stress. Credit spread widening indicates deterioration in risk-bearing capacity. When both happen together, stress is cross-asset and therefore more likely to produce a sharp equity drawdown.

**Exact feature columns:**

- `vol_term_inversion_flag`
- `vix9d_vs_vix`
- `vix3m_vs_vix`
- `vix_change_5d`
- `vix_percentile_252d`
- `credit_spread_20d_change`
- `hy_oas_change_20d`
- `hyg_vs_lqd_20d`

**Expected direction:**

- `vol_term_inversion_flag`: true_is_worse
- `vix9d_vs_vix`: higher_is_worse
- `vix3m_vs_vix`: lower_is_worse
- `vix_change_5d`: higher_is_worse
- `vix_percentile_252d`: higher_is_worse
- `credit_spread_20d_change`: higher_is_worse
- `hy_oas_change_20d`: higher_is_worse
- `hyg_vs_lqd_20d`: lower_is_worse

**Trigger logic pseudocode:**

```text
vol_term_inversion_flag == true AND
(vix_change_5d > 0 OR high(vix_percentile_252d)) AND
(credit_spread_20d_change > 0 OR hy_oas_change_20d > 0 OR hyg_vs_lqd_20d < 0)
```

**Why this should work:** Equity volatility spikes are common and often mean-revert. But volatility stress confirmed by credit tends to be more persistent and more dangerous.

**When it may fail:** In very fast policy-response environments, volatility and credit stress can reverse before equity drawdown materializes.

**Data / leakage risk:** Medium. VIX curve data availability may be shorter; credit data timing must be aligned conservatively.

**Validation plan:**

- 15BD / 30BD future MDD hit rate;
- compare vol-only vs vol-plus-credit conditions;
- alert burden and false-positive rate;
- COVID / 2011 / 2015 / 2018 / 2022 stress-period diagnostics;
- purged walk-forward test.

**Dashboard implication:** Candidate for an “acute cross-asset shock” warning module.

**Priority score:** 9/10
