# Research Iterations

Each research iteration is a self-contained evidence package. Do not overwrite prior iterations. Failed hypotheses and weak results must remain visible.

## Required Folder Name

Use zero-padded iteration folders:

```text
research_iterations/iteration_001/
research_iterations/iteration_002/
research_iterations/iteration_003/
```

## Required Files

Every iteration that generates and tests hypotheses should contain:

```text
research_iterations/iteration_00N/
├── prior_results_summary.md
├── hypotheses.yaml
├── HYPOTHESES.md
├── tests/
│   ├── iteration_00N_hypothesis_test_summary.csv
│   ├── iteration_00N_hypothesis_test_folds.csv
│   ├── iteration_00N_hypothesis_test_daily_signals.csv
│   ├── iteration_00N_hypothesis_test_events.csv
│   ├── iteration_00N_hypothesis_test_summary.json
│   └── iteration_00N_hypothesis_test_report.html
├── analysis.md
└── next_iteration_plan.md
```

If an iteration does not include testing, explain why in `analysis.md` and record the missing evidence explicitly.

## Required Evidence

At minimum, analysis must report:

- alert burden
- base hit rate
- alert hit rate
- base-rate lift
- event coverage
- false calm
- yearly fold stability
- lead time if available

## Guardrails

- Do not use invented features.
- Do not use unavailable future data.
- Do not use live sentiment for historical testing without point-in-time archives.
- Do not optimize thresholds unless explicitly approved.
- Do not modify production dashboard logic.
- Preserve failed hypotheses and lessons learned.
