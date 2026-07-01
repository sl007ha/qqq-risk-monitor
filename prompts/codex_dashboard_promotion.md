# Codex Prompt: Dashboard Promotion Review

Use Superpowers and evidence-over-claims.

Work in `qqq-risk-monitor`.

Goal: prepare a human-reviewed dashboard promotion proposal from existing research evidence. Do not modify production dashboard logic unless the human explicitly approves implementation in a separate step.

Read:

- `AGENTS.md`
- `research_loop/promotion_gates.yaml`
- `research_loop/research_state.yaml`
- source iteration analysis
- source iteration test outputs
- source hypothesis specs

Tasks:

1. Evaluate whether the candidate satisfies `dashboard_candidate` gates.
2. Create a shadow dashboard candidate folder under `dashboard_candidates/YYYY-MM-DD_candidate_name/`.
3. Write:

```text
candidate_memo.md
source_hypotheses.yaml
evidence_summary.csv
shadow_signal_daily.csv
risk_review.md
approval_status.yaml
```

4. Set `approval_status.yaml` to `status: proposed`.
5. Explain exactly what human approval would authorize and what remains out of scope.

Hard rules:

- Do not modify production dashboard logic in this task.
- Do not modify `data_sources.py`, `features.py`, or `config.py`.
- Do not claim dashboard readiness unless gates are satisfied by evidence.
- Human approval is required before production implementation.

Final response must link the candidate folder and summarize the evidence gate status.
