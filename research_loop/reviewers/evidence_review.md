# Evidence Review Checklist

Use this checklist after hypothesis tests produce evidence artifacts and before updating the registry or proposing dashboard candidates.

## Aggregate Performance

- What is the aggregate lift versus base rate?
- Is the result economically meaningful after considering alert burden?
- Does the signal improve on the relevant active baseline, not only on a weak rejected variant?

## Alert Burden

- What percentage of days are alerted?
- Is alert burden lower than the baseline when burden reduction is the goal?
- Are high-burden signals explicitly marked as context-only or rejected?

## Event Coverage

- What fraction of target events receive at least one timely alert?
- Which events are missed, and are misses clustered in one market regime?
- Does coverage improve without simply alerting most days?

## False Calm

- Does the signal reduce false calm periods before material drawdowns?
- Does it identify deterioration inside quiet dashboard states?
- Are missing-data cases separated from true calm cases?

## Fold And Year Stability

- How many walk-forward folds have positive lift?
- Are results concentrated in one period, crisis, or volatility regime?
- Are yearly hit rates and alert burdens stable enough to justify another iteration?

## Lead Time

- What is the median lead time in business days?
- Are alerts early enough to be useful?
- Are zero-day or same-day alerts clearly identified?

## Sample Size

- How many alert days, target events, folds, and event-level hits support the result?
- Are sparse signals labeled as exploratory rather than reliable?
- Are null or zero-hit cases preserved as failed evidence?

## Regime Concentration

- Does the result depend mainly on 2000-2002, 2008-2009, 2020, 2022, or another single regime?
- Does the result generalize across low-volatility and high-volatility periods?
- Is any conclusion downgraded if the evidence is regime-concentrated?

## Decision Discipline

- Are accepted, rejected, and needs-redesign conclusions recorded separately?
- Are thresholds pre-declared and not optimized after seeing outcomes?
- Are production dashboard claims avoided unless a human-approved production proposal exists?
