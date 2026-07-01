# Codex Repository Rules

This repository is a research and dashboard project for QQQ drawdown-risk monitoring. Codex may propose and test research ideas, but production dashboard changes require explicit human approval.

## Non-Negotiable Research Rules

- Do not invent features.
- Every `exact_feature_columns_used` entry must be copied verbatim from `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv`.
- If a desired feature is unavailable, list it under `future_data_requirement`; do not place it in `exact_feature_columns_used`.
- Do not use live sentiment or headline features for historical backtests unless point-in-time archives exist.
- Do not optimize thresholds unless the human explicitly approves a threshold-optimization task.
- Research trigger thresholds must be deterministic, pre-declared, and based on training-window quantiles or fixed economic constants.
- Do not modify production dashboard logic without human approval.
- Do not modify `qqq_autoresearch/data_sources.py`, `qqq_autoresearch/features.py`, or `qqq_autoresearch/config.py` unless the human explicitly approves that exact file scope.
- Do not change existing successful scripts except by adding clearly separated research-iteration scripts.

## Evidence Requirements

Every research iteration must produce evidence files. At minimum:

- hypothesis registry for the iteration
- deterministic trigger implementation if tests are run
- test summary CSV
- fold-level CSV
- daily signal CSV
- event-level coverage or lead-time evidence when available
- analysis document
- next-iteration plan
- decision log or state update

Do not claim success, validity, or improvement unless current terminal output or generated file evidence supports the claim.

## Human-In-The-Loop Promotion

Codex may:

- inspect features and prior results
- propose hypotheses
- write research-only trigger code
- run walk-forward tests
- analyze results
- propose dashboard candidates

Codex may not:

- promote a candidate into the production dashboard
- alter R2 or MMDI definitions
- alter data-source or core feature construction logic
- treat a research result as production-ready

Only a human can approve promotion from research output to production dashboard work.

## Failed Hypotheses

Preserve failed hypotheses and lessons learned. Do not delete failed research solely because it performed poorly. Failed ideas are part of the evidence trail and should be recorded in iteration analysis, the hypothesis registry, or `research_loop/research_state.yaml`.
