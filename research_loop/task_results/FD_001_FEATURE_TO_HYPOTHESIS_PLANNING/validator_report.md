# Validator Report: FD_001_FEATURE_TO_HYPOTHESIS_PLANNING

- Base ref: `origin/main`
- Started UTC: 2026-07-01T09:24:22+00:00
- Finished UTC: 2026-07-01T09:24:27+00:00
- Validator count: 4
- All passed: true

## 1. `research_loop/validators/validate_no_protected_pr_diff.py`

- Return code: 0
- Passed: true

### stdout

```text
PROTECTED_PR_DIFF_CHECK_PASSED
base_ref origin/main
protected_hits 0
```

### stderr

```text

```

## 2. `research_loop/validators/validate_feature_snapshot.py --snapshot-dir feature_lab/FD_001_combined`

- Return code: 0
- Passed: true

### stdout

```text
FEATURE_SNAPSHOT_CHECK_PASSED
snapshot_dir feature_lab\FD_001_combined
rows 6869
feature_columns 22
role_column classification
role_counts {'candidate_hypothesis_design': 10, 'descriptive_only': 4, 'context_only': 4, 'episode_diagnostics_only': 4}
latest_date 2026-06-30
```

### stderr

```text

```

## 3. `research_loop/validators/validate_hypothesis_plan.py --plan-yaml hypothesis_registry/fd_001_feature_to_hypothesis_plan.yaml --snapshot-dir feature_lab/FD_001_combined`

- Return code: 0
- Passed: true

### stdout

```text
HYPOTHESIS_PLAN_CHECK_PASSED
candidate_count 4
hypothesis_ids FD001_H001_FALSE_CALM_CONFIRMED_DOWNSIDE, FD001_H002_VOL_TERM_PERSISTENT_ACUTE_STRESS, FD001_H003_VOL_DISAGREEMENT_REGIME_SHIFT, FD001_H004_FALSE_CALM_VOL_DISAGREEMENT_CONFIRMATION
```

### stderr

```text

```

## 4. `declared task output check for FD_001_FEATURE_TO_HYPOTHESIS_PLANNING`

- Return code: 0
- Passed: true

### stdout

```text
TASK_OUTPUT_CHECK_PASSED
task_id FD_001_FEATURE_TO_HYPOTHESIS_PLANNING
output_count 2
```

### stderr

```text

```
