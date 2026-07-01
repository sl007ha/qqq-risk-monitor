# Codex Prompt: Run Full Research Iteration

Use Superpowers and evidence-over-claims.

Work in `qqq-risk-monitor`.

Goal:
Run the next Codex-driven QQQ Risk Monitor research iteration as a controlled closed loop.

Start from:

- `AGENTS.md`
- `research_loop/program_research_loop.md`
- `research_loop/research_state.yaml`
- `research_loop/promotion_gates.yaml`
- `hypothesis_registry/active_hypotheses.yaml`
- `hypothesis_registry/rejected_hypotheses.yaml`
- `hypothesis_registry/rewrite_queue.yaml`
- latest completed iteration folder

Hard rules:

- Do not modify `qqq_autoresearch/data_sources.py`.
- Do not modify `qqq_autoresearch/features.py`.
- Do not modify `qqq_autoresearch/config.py`.
- Do not modify production dashboard logic.
- Do not optimize thresholds unless explicitly approved in this prompt.
- Do not use live sentiment or headline features for historical tests unless point-in-time archives exist.
- Do not invent features.
- Every `exact_feature_columns_used` value must exist verbatim in `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv`.
- Preserve failed hypotheses and lessons learned.

Required loop:

1. Read the current state, gates, registries, rewrite queue, and prior iteration evidence.
2. Run the dashboard feature pull only if the iteration explicitly requires refreshed feature outputs.
3. Validate feature availability before writing hypotheses.
4. Generate only the number of hypotheses requested by the human.
5. Pre-register hypothesis files in `research_iterations/iteration_00N/`.
6. Implement deterministic research-only trigger logic in a new iteration-specific module.
7. Run purged walk-forward tests.
8. Write analysis, decision log, next iteration plan, and update registries/state.
9. Run `python research_loop/validate_iteration_artifacts.py research_iterations/iteration_00N`.
10. Report terminal/file evidence before claiming success.

Required artifacts:

- `prior_results_summary.md`
- `HYPOTHESES.md`
- `hypotheses.yaml`
- research-only trigger module if tests are run
- research-only CLI if tests are run
- tests summary CSV
- tests daily signal CSV
- tests events CSV
- `analysis.md`
- `decision_log.md`
- `next_iteration_plan.md`

Final response must include:

- commands run
- validation output
- top-line metrics
- files changed
- protected-file check result
