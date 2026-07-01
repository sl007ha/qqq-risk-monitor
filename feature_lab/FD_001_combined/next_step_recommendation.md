# FD_001 Combined Next-Step Recommendation

## Recommendation

Freeze the FD_001 combined experimental snapshot for FD_001-derived feature-to-hypothesis planning.

This is a research freeze only. It does not approve production dashboard promotion, production feature construction, or changes to R2/MMDI logic.

## Ready For Feature-To-Hypothesis Planning

Use these columns as candidate hypothesis inputs:

- `freq_003_false_calm_internal_deterioration_count`
- `freq_003_false_calm_confirmed_flag`
- `freq_003_false_calm_possible_flag`
- `freq_007_vol_term_daily_stress_count`
- `freq_007_vol_term_stress_persistence_5d`
- `freq_007_vol_term_stress_persistence_20d`
- `freq_008_vol_disagreement_score`
- `freq_008_vol_disagreement_score_pct`
- `freq_008_vol_disagreement_rank_change_20d`
- `freq_008_vol_disagreement_flag`

Evidence:

- Combined snapshot rows: 6,869
- Combined latest date: 2026-06-30
- Candidate hypothesis design columns: 10
- FREQ_003 confirmed false-calm days: 770
- FREQ_003 possible false-calm days: 1,583
- FREQ_007 post-VIX9D coverage is current through 2026-06-30
- FREQ_008 latest score percentile: `0.9523809523809524`

## Context-Only

Use these columns only as context in hypothesis design, not as standalone alert triggers:

- `freq_010_safe_haven_confirmation_score`
- `freq_010_rates_led_stress_flag`
- `freq_010_riskoff_confirmation_flag`
- `freq_010_safe_haven_rotation_state`

Evidence:

- Latest FREQ_010 state: `treasury_only_safe_haven`
- Latest FREQ_010 true riskoff confirmation flag: `0.0`
- FREQ_010 output coverage: `0.8674`
- FREQ_010 remains context-only and not alert-ready.

## Diagnostics-Only

Use these columns as diagnostics and design aids, not as direct hypothesis triggers:

- `freq_004_repair_episode_active`
- `freq_004_repair_failure_pressure_count`
- `freq_004_repair_episode_quality_score`
- `freq_004_repair_relapse_flag`

Evidence:

- Active repair days: 1,104
- Repair relapse flag true days: 857
- Repair quality score coverage: `0.1607`
- FREQ_004 remains episode diagnostics only because repair-trigger design still needs review.

## Descriptive-Only Companions

Keep these columns attached to candidate features for interpretation and missingness control:

- `freq_003_quiet_state`
- `freq_003_false_calm_missing_component_count`
- `freq_003_false_calm_unknown_due_to_missing_flag`
- `freq_007_vol_term_persistent_stress_flag`

Evidence:

- FREQ_003 missing component count latest value: `1.0`
- FREQ_003 unknown-due-to-missing days: 813
- FREQ_007 persistent stress flag is descriptive only; continuous persistence scores are the candidate-design surface.

## FREQ_003 Missing Uncertainty

FREQ_003 missing uncertainty was handled correctly for feature discovery:

- Observed deterioration count uses only non-missing stress components.
- Missing components are counted separately in `freq_003_false_calm_missing_component_count`.
- `freq_003_false_calm_confirmed_flag` is true only when observed count is at least 3.
- `freq_003_false_calm_confirmed_flag` is missing for 813 quiet rows where observed count is below 3 but missing components could lift the total to 3 or more.
- `freq_003_false_calm_possible_flag` is true for confirmed plus uncertainty-possible rows.
- `freq_003_false_calm_unknown_due_to_missing_flag` marks the 813 ambiguous rows directly.

This preserves missingness as uncertainty rather than treating missing data as either calm or stress.

## Freeze Decision

The combined snapshot is ready to freeze for FD_001-derived hypothesis generation because:

- it includes all Batch A v2 experimental columns and all Batch B v2 experimental columns;
- it has one row per source daily-wide input date;
- every output column is classified as candidate, context-only, descriptive-only, or episode-diagnostics-only;
- validation summaries record latest values, first valid dates, coverage, state distributions, count distributions, and missing-uncertainty distributions;
- no hypothesis tests were run;
- no protected production files or production output files were modified.

Next action: run feature-to-hypothesis planning using only `candidate_hypothesis_design` columns as trigger candidates, while carrying context, descriptive, and diagnostics-only columns as explanatory companions.
