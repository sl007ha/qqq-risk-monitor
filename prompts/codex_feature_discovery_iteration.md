# Codex Prompt: Feature Discovery Iteration

Use Superpowers and evidence-over-claims.

Work in `qqq-risk-monitor`.

Goal: run a controlled feature discovery iteration using latest research, prior failures, and the current feature inventory. Do not run new hypothesis tests. Do not modify production dashboard logic. Do not modify `qqq_autoresearch/data_sources.py`, `qqq_autoresearch/features.py`, or `qqq_autoresearch/config.py`.

Read:

- `AGENTS.md`
- `README.md`
- `FEATURE_UNIVERSE.md`
- `research_loop/program_research_loop.md`
- `research_loop/program_feature_discovery.md`
- `research_loop/feature_promotion_gates.yaml`
- `research_loop/research_state.yaml`
- `feature_backlog/feature_ideas.yaml`
- `feature_backlog/feature_lineage.yaml`
- latest prior iteration analysis, decision log, and next iteration plan
- `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv`
- `outputs/qqq_r2_mmdi_v1_3_1_feature_catalog.csv`
- `outputs/qqq_r2_mmdi_v1_3_1_feature_snapshot_latest.csv`

Tasks:

1. Summarize the latest research failures, active baselines, and unresolved blind spots.
2. Extract feature ideas only from prior iteration failures, dashboard blind spots, research sources, or market mechanisms.
3. For each proposed feature, include economic mechanism, raw inputs, formula, data source, point-in-time risk, expected direction, and candidate hypothesis use.
4. Check each proposed feature against the current feature inventory for redundancy.
5. Mark unavailable inputs as future data requirements.
6. Mark live sentiment or headline-derived ideas as current-context-only unless a historical point-in-time archive exists.
7. Update or create an iteration-local feature discovery report.
8. Do not implement features unless the human explicitly asks for experimental implementation.
9. Do not generate hypotheses unless the human explicitly asks for hypothesis generation.

Required output fields for each proposed feature:

- feature_id
- title
- source_type
- source_references
- economic_mechanism
- raw_inputs
- formula
- data_source
- point_in_time_risk
- expected_direction
- candidate_hypothesis_use
- leakage_risks
- redundancy_check
- future_data_requirement
- proposed_gate_status

Hard rules:

- Codex may propose features, but cannot add them to production `features.py` without human approval.
- Do not modify production dashboard logic.
- Do not run hypothesis tests.
- Do not optimize thresholds.
- Do not use live sentiment or headline features for historical backtests unless point-in-time archives exist.
- Every proposed feature must have a source.

Final response must cite file evidence and state whether any feature remains blocked by feasibility, leakage, redundancy, or missing data.
