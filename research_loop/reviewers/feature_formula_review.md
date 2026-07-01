# Feature Formula Review Checklist

Use this checklist before accepting an experimental feature snapshot or using a feature in hypothesis planning.

## Missingness

- Does any formula treat missing input data as a market signal?
- Are missing components counted separately when missingness could change the result?
- Are early-history missing inputs left missing rather than silently treated as non-stress?
- Are current-context-only inputs excluded from historical tests unless point-in-time archives exist?

## Scale And Aggregation

- Are raw components on compatible scales before averaging or summing?
- If scales differ, are components normalized with trailing-only ranks, percentiles, z-scores, or fixed economic units?
- Are binary flags, counts, and continuous scores documented as distinct output types?

## Rolling Windows

- Are rolling means, medians, quantiles, percentiles, and ranks trailing-only?
- Does the current row use only current-or-past information?
- Are minimum periods documented, and do early windows remain missing when insufficient history exists?

## Leakage

- Does the formula avoid future returns, future drawdowns, future troughs, future labels, and event outcomes?
- Does it avoid target-aware tuning or threshold optimization?
- Are macro/FRED inputs release-lagged before any historical use?
- Are hypothesis outputs excluded from feature construction?

## Categorical State Logic

- Are state categories mutually exclusive when they are intended to be mutually exclusive?
- Is state precedence explicit and economically justified?
- Are context-only states prevented from being used as alert-ready trigger columns?

## Promotion Boundary

- Is the feature implemented only under `feature_lab/` or another research-only path?
- Are `qqq_autoresearch/features.py`, `data_sources.py`, `config.py`, `pipeline.py`, `render.py`, and `run_dashboard.py` untouched?
- Is every output column classified as `candidate_hypothesis_design`, `context_only`, `descriptive_only`, or `episode_diagnostics_only`?
