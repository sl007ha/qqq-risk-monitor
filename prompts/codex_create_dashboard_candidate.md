# Codex Prompt: Create Shadow Dashboard Candidate

Use Superpowers and evidence-over-claims.

Work in `qqq-risk-monitor`.

Goal:
Create a shadow dashboard candidate package from promoted research hypotheses. Do not modify production dashboard logic.

Start from:

- `AGENTS.md`
- `research_loop/research_state.yaml`
- `research_loop/promotion_gates.yaml`
- `dashboard_candidates/README.md`
- `dashboard_candidates/candidate_template/`
- source iteration analysis and test outputs

Hard rules:

- Do not modify `qqq_autoresearch/data_sources.py`.
- Do not modify `qqq_autoresearch/features.py`.
- Do not modify `qqq_autoresearch/config.py`.
- Do not modify production dashboard logic.
- Do not create a production implementation.
- Do not optimize thresholds.
- Do not use live sentiment or headline features for historical tests unless point-in-time archives exist.
- Do not invent features.
- Human approval is required before production work.

Candidate workflow:

1. Confirm the source hypothesis satisfies `promote_to_shadow_dashboard` in `research_loop/promotion_gates.yaml`, or document the missing gate and why a shadow proposal is still useful.
2. Create a new folder under `dashboard_candidates/YYYY-MM-DD_candidate_name/`.
3. Copy and fill:
   - `dashboard_logic_proposal.md`
   - `candidate_rules.yaml`
   - `approval_checklist.md`
4. Add source evidence:
   - source hypotheses
   - exact feature columns
   - alert days
   - alert burden
   - base-rate lift
   - event coverage
   - positive-lift folds
   - median lead
   - false calm analysis
   - failure modes
5. Add comparison versus current dashboard.
6. Leave production approval status as not requested unless the human explicitly approves production implementation.

Final response must include:

- candidate folder path
- source hypotheses
- gate evidence
- missing gates or risks
- explicit statement that production dashboard logic was not modified
