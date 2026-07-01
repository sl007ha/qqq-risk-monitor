# FD_001 Batch A v2 vs Batch B Summary

## Run Evidence

- Batch A v2 script: `feature_lab/FD_001_batch_A_v2/run_feature_lab_fd001_batch_a_v2.py`
- Batch B script: `feature_lab/FD_001_batch_B/run_feature_lab_fd001_batch_b.py`
- Shared input: `outputs/qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv`
- Input rows in both runs: 6,869
- Latest input date in both runs: 2026-06-30
- Batch A v2 experimental columns: 12
- Batch B experimental columns: 8
- Hypothesis tests run: no
- Production dashboard logic modified: no

## Accepted For Hypothesis Design

These are still research-only. Acceptance here means suitable for future hypothesis candidate design, not production promotion.

- FREQ_008 regime-shift volatility disagreement:
  - Accepted columns: `freq_008_vol_disagreement_score`, `freq_008_vol_disagreement_score_pct`, `freq_008_vol_disagreement_rank_change_20d`, `freq_008_vol_disagreement_flag`
  - Evidence: score latest `0.8938492063492064`, score percentile latest `0.9523809523809523`, first valid score date `2002-01-25`, score coverage `0.8947`.
  - Formula note: unchanged from Batch A and still uses rolling percentile-normalized components before averaging.

- FREQ_007 volatility term-structure stress persistence:
  - Accepted columns: `freq_007_vol_term_daily_stress_count`, `freq_007_vol_term_stress_persistence_5d`, `freq_007_vol_term_stress_persistence_20d`
  - Evidence: latest daily stress count `1.0`, 5-day persistence `0.2`, 20-day persistence `0.35`; post-VIX9D coverage `1.0000`, pre-VIX9D coverage `0.0000`.
  - QA note: `vol_term_inversion_flag` is included in availability, safe boolean conversion is used, and early missing term-structure history remains missing.

- FREQ_003 false-calm internal deterioration count:
  - Accepted columns: `freq_003_false_calm_internal_deterioration_count`, `freq_003_false_calm_internal_deterioration_flag`
  - Required companion diagnostic: `freq_003_false_calm_missing_component_count`
  - Evidence: quiet-state days `4,739`, deterioration flag true days `770`, flag coverage `0.4354`, latest count `1.0`, latest missing component count `1.0`.
  - Missingness note: the count is an observed true-component count; missing components are tracked separately. The flag remains missing when count is below 3 and missing inputs could change the result.

## Context-Only

- FREQ_010 safe-haven rotation confirmation:
  - Context-only columns: `freq_010_safe_haven_confirmation_score`, `freq_010_rates_led_stress_flag`, `freq_010_riskoff_confirmation_flag`, `freq_010_safe_haven_rotation_state`
  - Evidence: latest state `treasury_only_safe_haven`, latest true riskoff flag `0.0`, output coverage `0.8674`.
  - State distribution: `treasury_and_defensive_bid` 2,717; `treasury_only_safe_haven` 1,500; `unconfirmed` 536; `rates_led_stress` 490; `mixed_defensive_rates_stress` 362; `defensive_only_rotation` 353; missing 911.
  - Promotion note: state is not alert-ready. True riskoff confirmation requires both treasury bid and defensive bid.

- FREQ_004 repair episode quality score:
  - Context-only diagnostics: `freq_004_repair_episode_active`, `freq_004_repair_failure_pressure_count`, `freq_004_repair_episode_quality_score`, `freq_004_repair_relapse_flag`
  - Evidence: active repair days `1,104`, relapse flag true days `857`, episode-active coverage `0.9914`, quality-score coverage `0.1607`.
  - Promotion note: this is episode diagnostics only. It should not be used as a hypothesis trigger until the episode framing is reviewed.

- FREQ_007 descriptive persistent flag:
  - `freq_007_vol_term_persistent_stress_flag` remains descriptive only, even though the continuous persistence scores are accepted for hypothesis design.

- FREQ_003 diagnostics:
  - `freq_003_false_calm_quiet_state` and `freq_003_false_calm_missing_component_count` are diagnostic companions, not standalone alert features.

## Requires More Design

- FREQ_004 requires more design before hypothesis-trigger use because the quality score is active-episode-only and the current framing is explicitly diagnostic.
- FREQ_010 requires more design before alert use because the state labels are context-only and rates-led versus riskoff precedence should be reviewed by a human before any dashboard or trigger promotion.
- FREQ_003 binary flag requires an explicit missingness policy in any future hypothesis plan because latest flag is missing and full-sample flag coverage is `0.4354`; the count plus missing-component diagnostic is the safer design surface.

## Protected-File Check

Current `git status --short` showed untracked research and lab paths only, including `feature_lab/`, `feature_research/`, `feature_specs/`, `feature_backlog/`, `prompts/`, and `research_loop/`.

No protected production files appeared as modified:

- `qqq_autoresearch/features.py`
- `qqq_autoresearch/data_sources.py`
- `qqq_autoresearch/config.py`
- `qqq_autoresearch/pipeline.py`
- `qqq_autoresearch/render.py`
- `run_dashboard.py`

No files under `outputs/` were written by the Batch A v2 or Batch B scripts.
