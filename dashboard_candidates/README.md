# Dashboard Candidates

Dashboard candidates are shadow proposals. They are not production dashboard changes.

## Workflow

```text
research signal
-> candidate rules
-> shadow report
-> comparison vs current dashboard
-> human approval
-> production implementation only if explicitly approved
```

## Human Approval Rule

Codex may propose and test a shadow dashboard candidate. Codex may not promote a candidate into production dashboard logic. A human must approve any production implementation and must explicitly name production files that are allowed to change.

## Candidate Creation Gates

A shadow candidate should satisfy `research_loop/promotion_gates.yaml` under `promote_to_shadow_dashboard`, or include a written exception explaining why the candidate is useful despite missing a gate.

Required evidence:

- source hypothesis IDs
- exact feature columns used
- alert burden
- base-rate lift
- event coverage
- positive-lift folds
- median lead time
- alert days
- false calm analysis
- failure mode documentation
- comparison versus the current dashboard state

## Candidate Folder Structure

Use one folder per candidate:

```text
dashboard_candidates/YYYY-MM-DD_candidate_name/
|-- dashboard_logic_proposal.md
|-- candidate_rules.yaml
|-- approval_checklist.md
|-- source_hypotheses.yaml
|-- evidence_summary.csv
|-- shadow_signal_daily.csv
|-- comparison_vs_current_dashboard.md
`-- approval_status.yaml
```

## Template

Start from:

```text
dashboard_candidates/candidate_template/
|-- dashboard_logic_proposal.md
|-- candidate_rules.yaml
`-- approval_checklist.md
```

## Production Boundary

Candidate work should stay under `dashboard_candidates/`, `research_iterations/`, `hypothesis_registry/`, or research-only scripts. Production dashboard code remains out of scope until a human approval record exists.
