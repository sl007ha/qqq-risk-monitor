# QQQ Risk Monitor Feature Discovery Program

This document defines the controlled feature discovery loop for the Codex Research OS. Feature discovery is research-only until a human explicitly approves any production dashboard or production feature-construction change.

## Loop Overview

```text
research intake
-> feature idea extraction
-> feature spec
-> data feasibility
-> leakage/redundancy audit
-> experimental implementation
-> feature validation
-> accepted feature snapshot
-> hypothesis generation
```

The loop exists to turn prior research failures, dashboard blind spots, research sources, and market mechanisms into auditable feature candidates before those candidates are used in hypotheses.

## Global Hard Rules

- Codex may propose features, but may not add them to production feature construction without explicit human approval.
- Do not modify production dashboard logic from this loop.
- Do not modify `qqq_autoresearch/data_sources.py`, `qqq_autoresearch/features.py`, or `qqq_autoresearch/config.py` from this loop.
- Do not add features directly to production feature construction.
- Do not run hypothesis tests during a feature discovery iteration unless the human explicitly asks for tests in that same task.
- Every proposed feature must have a source: prior iteration failure, dashboard blind spot, research source, or market mechanism.
- Every proposed feature must include economic mechanism, raw inputs, formula, data source, point-in-time risk, expected direction, and candidate hypothesis use.
- Every feature must be checked against the current feature inventory for redundancy before implementation.
- Live sentiment or headline-derived features are current-context-only unless historical point-in-time archives exist.

## 1. Research Intake

Read the current research state and evidence trail before proposing new features:

- `AGENTS.md`
- `research_loop/program_research_loop.md`
- `research_loop/research_state.yaml`
- `research_loop/promotion_gates.yaml`
- `feature_backlog/feature_ideas.yaml`
- `feature_backlog/feature_lineage.yaml`
- latest iteration analysis, decision log, and next iteration plan
- current exported feature inventory when available

Intake should summarize:

- active hypotheses and unresolved failure modes
- rejected hypotheses and preserved lessons
- dashboard blind spots
- missing data or unavailable feature requests
- current feature families and known current-context-only fields

## 2. Feature Idea Extraction

Extract feature ideas from evidence, not from wishful naming. Each idea must identify:

- feature idea ID
- source type
- source files or hypotheses
- market mechanism
- failure mode or blind spot addressed
- expected direction
- candidate hypothesis use
- status under `research_loop/feature_promotion_gates.yaml`

Idea extraction output belongs in `feature_backlog/feature_ideas.yaml` or an iteration-specific review file. Do not place unavailable desired features in `exact_feature_columns_used`; that field is reserved for hypothesis specs and must only use inventory columns copied verbatim.

## 3. Feature Spec

A feature spec is the first durable contract for a proposed feature. Specs belong under `feature_specs/` and must follow `feature_specs/README.md`.

At minimum, each spec must define:

- feature ID and title
- source and lineage
- economic mechanism
- raw inputs
- formula or deterministic construction
- data source and point-in-time availability
- leakage risk
- redundancy audit against current inventory
- coverage requirement
- expected direction
- candidate hypothesis use
- validation plan
- production promotion status

If a feature cannot be specified without inventing unavailable data, mark it as a future data requirement instead of implementing it.

## 4. Data Feasibility

Before implementation, audit data availability:

- Is each raw input already in exported dashboard outputs, in a stable public source, or in a documented future data source?
- Is the input available point-in-time for historical dates?
- Are release lags, restatements, survivorship, or current-only snapshots present?
- Does the expected coverage span enough folds or events to support later validation?
- Is the source allowed under repository rules?

Feasibility findings should be stored with the feature spec or in a feasibility audit under the current iteration folder.

## 5. Leakage And Redundancy Audit

A proposed feature must pass both checks before experimental implementation:

- Leakage audit: no future return, future drawdown, future event membership, revised-after-the-fact data, or current-only headline/sentiment data may be used as a historical predictor.
- Redundancy audit: compare the proposed feature against `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv` and related feature catalog outputs. Document exact existing columns that may overlap.

If redundancy is high, the feature may still proceed only if it adds a distinct mechanism, episode framing, timing transform, or interaction that the existing inventory does not provide.

## 6. Experimental Implementation

Experimental feature implementation belongs under `feature_lab/` or an iteration-specific research folder. It must not modify production feature construction.

Allowed inputs:

- exported dashboard CSVs under `outputs/`
- iteration-local input snapshots
- documented public data pulled by research-only scripts

Disallowed without human approval:

- editing `qqq_autoresearch/features.py`
- editing `qqq_autoresearch/data_sources.py`
- editing `qqq_autoresearch/config.py`
- wiring experimental columns into `run_dashboard.py`
- adding experimental features to production dashboard HTML or CSV exports

## 7. Feature Validation

Feature validation checks the feature itself before it becomes eligible for hypothesis generation. It is not a hypothesis backtest.

Minimum checks:

- deterministic construction from declared raw inputs
- no leakage flags unresolved
- coverage, first valid date, latest valid date, and missingness documented
- redundancy comparison documented
- expected direction and interpretation documented
- historical usability classified as safe-for-backtest, research-only, or current-context-only
- experimental output snapshot written if implementation exists

## 8. Accepted Feature Snapshot

Accepted research features should be captured in an accepted feature snapshot before hypothesis generation. The snapshot should include:

- feature ID
- spec path
- implementation path if any
- validation artifact path
- exact experimental column names
- coverage summary
- leakage classification
- redundancy finding
- status gate reached
- human approval status for any production use

Acceptance into a research inventory does not mean production dashboard approval.

## 9. Hypothesis Generation

Only features at `eligible_for_hypothesis` may be used to generate new hypothesis candidates. Hypothesis generation must still obey the research-loop rules:

- use exact columns only when they exist in the relevant inventory or accepted experimental snapshot
- put unavailable desired inputs under `future_data_requirement`
- keep thresholds deterministic and pre-declared
- do not optimize thresholds without explicit human approval
- do not use live sentiment or headline data in historical tests unless point-in-time archives exist
- do not modify production dashboard logic

## Human Approval Boundary

Codex can propose feature ideas, write specs, run feasibility audits, implement experimental research-only features, and validate feature snapshots. A human must explicitly approve:

- production feature construction changes
- edits to protected source files
- dashboard promotion
- threshold optimization tasks
- using new external data sources in production
