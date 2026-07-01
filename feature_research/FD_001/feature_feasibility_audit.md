# FD_001 Feature Feasibility Audit

## Scope And Guardrails

This audit evaluates the 10 promoted FD_001 feature specs for feasibility. It does not implement features, run hypothesis tests, modify production feature construction, or change dashboard logic.

Protected files remain out of scope:

- `qqq_autoresearch/data_sources.py`
- `qqq_autoresearch/features.py`
- `qqq_autoresearch/config.py`
- `qqq_autoresearch/pipeline.py`
- `qqq_autoresearch/render.py`
- `run_dashboard.py`

Live news, headline, and LLM-derived features remain current-context-only unless a historical point-in-time archive exists. None of the 10 promoted specs uses live text inputs.

## Evidence Used

Read inputs:

- `feature_research/FD_001/feature_discovery_report.md`
- `feature_research/FD_001/extracted_feature_ideas.yaml`
- `feature_specs/FREQ_001_cross_asset_stress_sequence.yaml`
- `feature_specs/FREQ_002_funding_liquidity_pressure_bundle.yaml`
- `feature_specs/FREQ_003_false_calm_internal_deterioration_count.yaml`
- `feature_specs/FREQ_004_repair_episode_quality_score.yaml`
- `feature_specs/FREQ_005_downside_volatility_persistence_ratio.yaml`
- `feature_specs/FREQ_006_leadership_context_gate.yaml`
- `feature_specs/FREQ_007_vol_term_structure_stress_persistence.yaml`
- `feature_specs/FREQ_008_regime_shift_volatility_disagreement.yaml`
- `feature_specs/FREQ_009_macro_liquidity_drain_acceleration.yaml`
- `feature_specs/FREQ_010_safe_haven_rotation_confirmation.yaml`
- `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv`
- `outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv`
- `research_loop/feature_promotion_gates.yaml`

Inventory evidence:

- Current inventory shape: 342 rows and 8 metadata columns.
- Daily wide data columns: 343 including `date`.
- All 10 promoted specs have all declared raw input columns present in the daily wide CSV.

## Ranking Summary

| Rank | Feature | Decision | Key reason |
|---|---|---|---|
| 1 | FREQ_003 false-calm internal deterioration count | implement_now | Direct active rewrite need, all inputs present, latest non-null, simple feature_lab implementation. |
| 2 | FREQ_008 regime-shift volatility disagreement | implement_now | Clean coverage, low leakage risk, low implementation complexity. |
| 3 | FREQ_007 volatility term-structure stress persistence | implement_now | Current/recent availability is complete, and persistence adds non-redundant information. |
| 4 | FREQ_010 safe-haven rotation confirmation | implement_now | Good coverage, low complexity, useful cross-asset context. |
| 5 | FREQ_004 repair episode quality score | implement_now | Excellent coverage and important prior failure, but needs careful trailing-only episode logic. |
| 6 | FREQ_001 cross-asset stress sequence score | design_more_first | Strong concept, but IG OAS coverage starts in 2023 and sequence rules need legacy-compatible design. |
| 7 | FREQ_009 macro liquidity drain acceleration | design_more_first | Good coverage but macro release-lag handling must be specified first. |
| 8 | FREQ_006 leadership context gate | design_more_first | Relevant but depends on another accepted feature and has QQQE/Mag7 proxy caveats. |
| 9 | FREQ_005 downside-volatility persistence ratio | design_more_first | Important theme but key ratio fields are sparse and some latest values are missing. |
| 10 | FREQ_002 funding liquidity pressure bundle | defer | Too dependent on short-history SOFR and HY/IG spread fields for immediate implementation. |

No feature is rejected in this audit. FREQ_002 is deferred because it needs a two-tier legacy/recent design before implementation.

## Implement Now

### FREQ_003 - False-Calm Internal Deterioration Count

Raw input availability:

- Exact inputs present: `R2_ACTIVE`, `R2_STRESS_COUNT`, `MMDI`, `MMDI_10D_CHANGE`, `mmdi_20d_change`, `downside_vol_20d`, `price_vs_ma50`, `qqq_dd_20d`
- Missing inputs: none
- Minimum full-sample coverage: 41.21%, driven by `downside_vol_20d`
- Minimum recent one-year coverage: 29.37%, also driven by `downside_vol_20d`
- Latest non-null inputs: 8/8

Feasibility verdict: pass with explicit missing handling.

Audit notes:

- Point-in-time risk is low because fields are market-derived and trailing.
- Leakage risk is low if thresholds are fixed or training-window-only.
- Redundancy is low because the quiet-state conditional count does not already exist.
- Dashboard relevance is high because it targets the false-calm blind spot.
- Candidate hypothesis relevance is high for `RQ004_FALSE_CALM_BURDEN_REDUCTION`.

### FREQ_004 - Repair Episode Quality Score

Raw input availability:

- Exact inputs present: `qqq_close`, `qqq_dd_20d`, `qqq_dd_60d`, `rebound_from_trough_20d`, `failed_reclaim_ma50`, `failed_reclaim_ma200`, `lower_high_flag`, `lower_low_flag`, `mmdi_low_after_high`
- Missing inputs: none
- Minimum full-sample coverage: 99.14%
- Minimum recent one-year coverage: 100.00%
- Latest non-null inputs: 9/9

Feasibility verdict: pass, with leakage-sensitive episode design.

Audit notes:

- Point-in-time risk is low because inputs are trailing price and MMDI-derived fields.
- Leakage risk is medium only because episode logic can accidentally use future troughs or future repair outcomes.
- Redundancy is partial: daily repair ingredients exist, but episode-level repair quality does not.
- Dashboard relevance is medium; this is not ready for dashboard framing, but it addresses a preserved failure.
- Candidate hypothesis relevance is high for future repair-failure work.

### FREQ_007 - Volatility Term-Structure Stress Persistence

Raw input availability:

- Exact inputs present: `vix9d_vs_vix`, `vix3m_vs_vix`, `vol_term_inversion_flag`, `vvix_level`, `skew_index`, `panic_vol_flag`
- Missing inputs: none
- Minimum full-sample coverage: 56.70%, driven by `vix9d_vs_vix`
- Minimum recent one-year coverage: 100.00%
- Latest non-null inputs: 6/6

Feasibility verdict: pass.

Audit notes:

- Point-in-time risk is low to medium because histories start at different dates, but inputs are market-derived.
- Leakage risk is low if persistence windows are trailing-only.
- Redundancy is low because term-structure daily fields exist but persistence does not.
- Dashboard relevance is medium-high as a volatility stress explanation.
- Candidate hypothesis relevance is medium-high for false-calm and downside-vol confirmation.

### FREQ_008 - Regime-Shift Volatility Disagreement

Raw input availability:

- Exact inputs present: `qqq_vol_10d`, `qqq_vol_20d`, `qqq_vol_60d`, `realized_vol_252d`, `vix`, `vxn`, `vol_20d_vs_252d`
- Missing inputs: none
- Minimum full-sample coverage: 93.11%, driven by `vxn`
- Minimum recent one-year coverage: 100.00%
- Latest non-null inputs: 7/7

Feasibility verdict: pass.

Audit notes:

- Point-in-time risk is low because fields are market-derived.
- Leakage risk is low if ranks and changes use only past data.
- Redundancy is low to medium: current ratios exist, but multi-proxy disagreement and rank-change score does not.
- Dashboard relevance is medium.
- Candidate hypothesis relevance is medium-high for downside-volatility comparison and false-calm confirmation.

### FREQ_010 - Safe-Haven Rotation Confirmation

Raw input availability:

- Exact inputs present: `tlt_ret_20d`, `ief_ret_20d`, `tlt_ief_rel_3m`, `xlu_vs_spy_3m`, `xlp_vs_spy_3m`, `ust10y_change_20d`
- Missing inputs: none
- Minimum full-sample coverage: 86.74%, driven by `tlt_ief_rel_3m`
- Minimum recent one-year coverage: 100.00%
- Latest non-null inputs: 6/6

Feasibility verdict: pass.

Audit notes:

- Point-in-time risk is low to medium because ETF and Treasury data are date-local but histories start at different dates.
- Leakage risk is low if only trailing returns and same-date yield changes are used.
- Redundancy is partial because the inputs exist, but risk-off versus rates-led stress classification does not.
- Dashboard relevance is medium as context for cross-asset stress.
- Candidate hypothesis relevance is medium for acute-shock and leadership context work.

## Design More First

### FREQ_001 - Cross-Asset Stress Sequence Score

All six inputs are present and recent coverage is complete, but `ig_oas_change_20d` has only 10.64% full-sample coverage and begins in 2023. `vix9d_vs_vix` starts in 2011. This feature should be redesigned before implementation with either:

- a legacy-compatible core sequence excluding short-history inputs, plus an optional recent-era extension; or
- a recent-era-only scope explicitly marked as limited coverage.

FRED credit and rates fields require release-lag notes before any historical use.

### FREQ_005 - Downside-Volatility Persistence Ratio

All six inputs exist, but `downside_upside_vol_ratio` has only 13.38% full-sample coverage and 17.86% recent one-year coverage. `upside_vol_20d` and `downside_upside_vol_ratio` are not non-null on the latest date. This needs a redesign that avoids making sparse component availability look like calm.

### FREQ_006 - Leadership Context Gate

All inputs exist and recent coverage is complete. The limiting issues are design dependencies:

- `qqq_vs_qqqe_3m` begins in 2012 and has 51.38% full-sample coverage.
- Mag7 features are fixed-basket proxies, not historical constituent-universe breadth.
- The gate needs a parent signal, such as FREQ_003 or FREQ_008, before it can be implemented meaningfully.

### FREQ_009 - Macro Liquidity Drain Acceleration

Coverage is good and all inputs are latest non-null, but macro release-lag handling is not optional. `walcl`, `fedfunds`, and `nfci` should be aligned to release availability before any historical implementation.

## Defer

### FREQ_002 - Funding Liquidity Pressure Bundle

All six inputs are present and latest non-null, but this feature is too short-history-heavy for immediate implementation:

- `hy_ig_spread` has 10.93% full-sample coverage and begins in 2023.
- `sofr_spread_proxy` has 30.16% full-sample coverage and begins in 2018.
- FRED release-lag and revision handling is required.

Defer until a two-tier design separates long-history funding proxies from recent high-frequency funding extensions.

## Reject

No promoted FD_001 feature is rejected in this audit.

## Hard-Rule Check

- No features were implemented.
- No hypothesis tests were run.
- No features were added to `qqq_autoresearch/features.py`.
- No production dashboard logic was modified.
- Macro/FRED candidates include release-lag notes.
- Live news/headline/LLM outputs remain current-context-only and are not part of the implement-now set.
