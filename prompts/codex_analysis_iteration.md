# Codex Prompt: Analysis Iteration

Use Superpowers and evidence-over-claims.

Work in `qqq-risk-monitor`.

Goal: analyze a completed research iteration and update the research decision trail. Do not generate new hypotheses unless explicitly asked. Do not modify production dashboard logic.

Read:

- `AGENTS.md`
- `research_loop/promotion_gates.yaml`
- target iteration `hypotheses.yaml`
- target iteration test summary CSV
- target iteration fold CSV
- target iteration event or lead-time CSV if present
- prior iteration analysis if present

Tasks:

1. Summarize results by hypothesis.
2. Compare against promotion, rewrite, drop, and dashboard-candidate gates.
3. Identify strongest candidates, weak candidates, failed ideas, and ambiguous results.
4. Preserve failure lessons.
5. Write:

```text
research_iterations/iteration_00N/analysis.md
research_iterations/iteration_00N/next_iteration_plan.md
```

6. Update `research_loop/research_state.yaml` only if asked or if the task explicitly includes state update.

Required metrics:

- alert burden
- base hit rate
- alert hit rate
- base-rate lift
- event coverage
- false calm
- yearly fold stability
- lead-time if available

Hard rules:

- No production dashboard changes.
- No threshold optimization.
- Claims must cite generated evidence.

Final response must identify which hypotheses are keep, rewrite, drop, or dashboard-candidate proposals.
