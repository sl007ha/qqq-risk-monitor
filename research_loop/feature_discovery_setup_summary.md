# Feature Discovery Setup Summary

This setup adds a controlled feature discovery loop to the existing Codex Research OS. It does not add production features, change dashboard logic, or authorize protected file edits.

## How Feature Discovery Fits Into The Research Loop

The existing research loop moves from feature pull to hypothesis generation, validation, testing, analysis, decision logging, and dashboard candidate review. The new feature discovery loop sits before hypothesis generation when prior results show that the current inventory is not enough.

The controlled sequence is:

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

Feature discovery should be triggered when an iteration failure points to a missing construct, such as lead time, episode quality, confirmation strength, context filtering, or fold stability. This preserves failed hypotheses as useful evidence while preventing Codex from inventing unavailable columns or silently changing production feature construction.

## How Codex Should Propose New Features

Codex should start from evidence:

- prior iteration failures
- dashboard blind spots
- research sources
- market mechanisms

Every proposed feature must include:

- economic mechanism
- raw inputs
- formula
- data source
- point-in-time risk
- expected direction
- candidate hypothesis use
- source and lineage
- redundancy check against the current feature inventory

The initial backlog is stored in `feature_backlog/feature_ideas.yaml`, with source lineage in `feature_backlog/feature_lineage.yaml`. The first seeded themes are:

- earlier cross-asset lead-time features
- event-based repair quality features
- leadership-as-context features
- false-calm confirmation features
- downside-volatility stability features

Feature specs belong in `feature_specs/`. Experimental feature work belongs in `feature_lab/` or an iteration-specific research folder. Accepted experimental features must be captured in a research-only accepted feature snapshot before they become eligible for hypothesis generation.

## What Still Requires Human Approval

Human approval is still required before:

- adding any feature to production feature construction
- modifying `qqq_autoresearch/data_sources.py`
- modifying `qqq_autoresearch/features.py`
- modifying `qqq_autoresearch/config.py`
- modifying production dashboard logic
- promoting a research feature or hypothesis into the production dashboard
- optimizing thresholds
- using live sentiment or headline-derived features in historical backtests without point-in-time archives

Codex may propose features, write specs, audit feasibility, implement research-only experimental features, validate feature snapshots, and draft hypothesis candidates from accepted feature snapshots. None of those steps grants production approval.

## Files Added

- `research_loop/program_feature_discovery.md`
- `research_loop/feature_promotion_gates.yaml`
- `feature_backlog/feature_ideas.yaml`
- `feature_backlog/feature_lineage.yaml`
- `feature_specs/README.md`
- `feature_lab/README.md`
- `prompts/codex_feature_discovery_iteration.md`
- `prompts/codex_feature_feasibility_audit.md`
- `prompts/codex_feature_to_hypothesis_plan.md`
- `research_loop/feature_discovery_setup_summary.md`
