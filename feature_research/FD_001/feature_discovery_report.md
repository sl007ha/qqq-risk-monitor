# FD_001 Feature Discovery Report

## Scope

FD_001 is a research-only feature discovery iteration. It brainstormed 20 feature ideas and promoted 10 to feature specs. It did not implement features, run hypothesis tests, modify production dashboard logic, or edit protected production files.

## Inputs Reviewed

Local evidence:

- `research_loop/research_state.yaml`
- `hypothesis_registry/rewrite_queue.yaml`
- `feature_backlog/feature_requests_from_hypotheses.yaml`
- `research_iterations/iteration_003/analysis.md`
- `research_iterations/iteration_003/decision_log.md`
- `outputs/qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv`
- `FEATURE_UNIVERSE.md`

External research sources:

- BIS, "Predicting financial market stress with machine learning": https://www.bis.org/publ/work1250.htm
- Federal Reserve, "Linear and nonlinear econometric models against machine learning models: realized volatility prediction": https://www.federalreserve.gov/econres/feds/linear-and-nonlinear-econometric-models-against-machine-learning-models.htm
- OFR Financial Stress Index: https://www.financialresearch.gov/financial-stress-index/
- Arian, Norouzi, Seco, "Backtest Overfitting in the Machine Learning Era": https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4686376
- "Regime-aware Financial Volatility Forecasting via In-Context Learning": https://arxiv.org/html/2603.10299v1
- "Data-Efficient Realized Volatility Forecasting with Vision Transformers": https://arxiv.org/html/2511.03046v1
- "Realised Volatility Forecasting: Machine Learning via Financial Word Embedding": https://arxiv.org/html/2108.00480v6
- "Cross-Modal Temporal Fusion for Financial Market Forecasting": https://arxiv.org/html/2504.13522v2
- "TradingAgents: Multi-Agents LLM Financial Trading Framework": https://arxiv.org/abs/2412.20138
- "Agentic Trading: When LLM Agents Meet Financial Markets": https://arxiv.org/html/2605.19337v1
- "Large Language Model Agents in Finance": https://aclanthology.org/2025.findings-emnlp.972.pdf
- "FinRobot": https://arxiv.org/abs/2405.14767
- "FinGPT": https://arxiv.org/abs/2306.06031

## Local Research Interpretation

Iteration 003 leaves five clear feature-discovery needs:

1. Cross-asset lead time: I003_H002 reduced burden but worsened lift, coverage, stability, and did not improve 0BD median lead versus I002_H002.
2. False repair: I002_H004 and I003_H004 both failed, so repair needs episode-level features or a different target before retesting.
3. Leadership context: I003_H003 covered many events but was too broad as a standalone alert; I002_H003 remains the low-burden leadership baseline.
4. False calm: I003_H005 improved materially versus I002_H005 but remains too broad for dashboard promotion.
5. Downside volatility: I003_H001 improved positive-lift folds only modestly while worsening burden, lift, and lead time versus I002_H001.

The current inventory provides many raw ingredients: credit, rates, dollar, volatility, R2/MMDI, leadership relatives, Mag7 breadth, liquidity proxies, and headline snapshots. The live headline features remain current-context-only because the repo does not have historical point-in-time headline archives.

## External Research Interpretation

Recent market-stress work supports features that model cross-market spillovers, funding liquidity, investor overextension, and global-cycle pressure rather than single-market daily levels.

Recent volatility work supports regime-aware, interpretable features such as persistence, disagreement, and duration. FD_001 therefore prefers deterministic transforms over black-box forecast outputs.

Finance LLM and agentic trading research informs process design: provenance, role separation, memory, risk-agent disagreement, and auditability. It does not make live text or live LLM outputs safe for historical testing. Those ideas remain future-data or current-context-only until point-in-time archives exist.

Leakage-safe evaluation research reinforces the boundary between feature discovery and hypothesis validation. FD_001 did not run tests, and any future test should handle overlapping forward labels with purging or equivalent leakage controls.

## Feature Ideas

FD_001 extracted 20 ideas in `feature_research/FD_001/extracted_feature_ideas.yaml`.

Promoted to feature specs:

| ID | Feature | Reason promoted |
|---|---|---|
| FREQ_001 | Cross-asset stress sequence score | Directly addresses cross-asset 0BD lead-time failure using current stress columns. |
| FREQ_002 | Funding liquidity pressure bundle | Aligns with BIS/OFR stress mechanisms and current FRED-derived liquidity fields. |
| FREQ_003 | False-calm internal deterioration count | Directly targets I003_H005 burden reduction using existing R2/MMDI/vol/trend fields. |
| FREQ_004 | Repair episode quality score | Converts failed false-repair single-day logic into episode framing. |
| FREQ_005 | Downside-volatility persistence ratio | Targets I002_H001/I003_H001 stability without optimizing thresholds. |
| FREQ_006 | Leadership context gate | Keeps leadership as context, matching iteration_003 decisions. |
| FREQ_007 | Volatility term-structure stress persistence | Uses existing VIX term and tail-demand proxies as duration features. |
| FREQ_008 | Regime-shift volatility disagreement | Converts regime-aware volatility research into interpretable current-column transforms. |
| FREQ_009 | Macro liquidity drain acceleration | Uses current macro/liquidity fields while marking release-lag risk. |
| FREQ_010 | Safe-haven rotation confirmation | Adds cross-asset regime classification around Treasuries and defensive sectors. |

Not promoted:

- FREQ_011 implied-volatility surface curvature stress: needs point-in-time options surface data.
- FREQ_012 news volatility attention state: current live RSS is not historical/backtest-ready.
- FREQ_013 LLM risk-agent disagreement index: no archived agent outputs, prompts, or model versions.
- FREQ_014 agent source-provenance confidence score: governance idea, not market feature.
- FREQ_015 external financial stress index delta: promising but requires separate external data-source approval and release-lag audit.
- FREQ_016 credit-equity divergence duration: useful but mostly a narrower duration transform of existing divergence flags.
- FREQ_017 intraday realized-volatility shock signature: needs intraday data.
- FREQ_018 defensive sector rotation confirmation: likely redundant with FREQ_010.
- FREQ_019 liquidity-volume downside asymmetry: useful but largely covered by existing volume/illiquidity columns and lower priority than promoted features.
- FREQ_020 label-overlap evaluation risk marker: evaluation QA artifact, not a market feature spec.

## Promoted Feature Specs

The 10 promoted specs are:

- `feature_specs/FREQ_001_cross_asset_stress_sequence.yaml`
- `feature_specs/FREQ_002_funding_liquidity_pressure_bundle.yaml`
- `feature_specs/FREQ_003_false_calm_internal_deterioration_count.yaml`
- `feature_specs/FREQ_004_repair_episode_quality_score.yaml`
- `feature_specs/FREQ_005_downside_volatility_persistence_ratio.yaml`
- `feature_specs/FREQ_006_leadership_context_gate.yaml`
- `feature_specs/FREQ_007_vol_term_structure_stress_persistence.yaml`
- `feature_specs/FREQ_008_regime_shift_volatility_disagreement.yaml`
- `feature_specs/FREQ_009_macro_liquidity_drain_acceleration.yaml`
- `feature_specs/FREQ_010_safe_haven_rotation_confirmation.yaml`

## Redundancy And Feasibility Summary

All promoted features are at least partially redundant with current inventory inputs because FD_001 intentionally avoids adding new production data. The proposed contribution is mostly in sequence, duration, persistence, conditional context, and regime classification.

The highest feasibility ideas are FREQ_003, FREQ_005, FREQ_007, FREQ_008, and FREQ_010 because they rely mostly on market-derived columns. FREQ_001, FREQ_002, FREQ_006, and FREQ_009 have medium point-in-time or coverage risk due to FRED release timing, shorter ETF/proxy histories, or fixed-basket leadership caveats. FREQ_004 is feasible but requires careful episode construction to avoid future information.

## Guardrails For Next Step

- Do not implement any feature until an explicit experimental implementation task is approved.
- Do not run hypothesis tests from FD_001.
- Do not add these specs to production feature construction.
- Do not modify `qqq_autoresearch/data_sources.py`, `qqq_autoresearch/features.py`, or `qqq_autoresearch/config.py`.
- Treat live headline, news, and LLM-agent ideas as current-context-only unless point-in-time archives exist.
- Before any future experimental implementation, run a feasibility audit using `prompts/codex_feature_feasibility_audit.md`.

## Outputs Written

- `feature_research/FD_001/source_manifest.yaml`
- `feature_research/FD_001/source_notes.md`
- `feature_research/FD_001/extracted_feature_ideas.yaml`
- 10 `feature_specs/FREQ_xxx_*.yaml` files
- `feature_research/FD_001/feature_discovery_report.md`
