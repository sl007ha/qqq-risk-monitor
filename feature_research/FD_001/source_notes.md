# FD_001 Source Notes

FD_001 combines the local iteration_003 evidence trail with recent market-risk, volatility, cross-asset stress, finance-agent, and leakage-safe evaluation research. The external sources are used for feature ideation and audit discipline only. No external data source is approved for production use by this file.

## Local Evidence

`research_loop/research_state.yaml` and `hypothesis_registry/rewrite_queue.yaml` point to three active research needs:

- Reduce false-calm alert burden while preserving I003_H005 coverage and lead time.
- Compare downside-volatility variants at event level rather than optimizing daily lift.
- Use leadership as context for false-calm or downside-volatility alerts, not as a broad standalone warning.

`feature_backlog/feature_requests_from_hypotheses.yaml` adds two preserved failure needs:

- Earlier cross-asset lead-time features because I003_H002 did not improve 0BD median lead versus I002_H002.
- Event-based repair features because I002_H004 and I003_H004 failed with zero event coverage.

`research_iterations/iteration_003/analysis.md` and `research_iterations/iteration_003/decision_log.md` provide the evidence basis:

- I003_H001: strong lift but worse than I002_H001 on burden, lift, and median lead.
- I003_H002: lower burden but worse lift, coverage, stability, and unchanged 0BD lead.
- I003_H003: very high coverage but too broad as a standalone alert.
- I003_H004: failed false-repair formulation, 0.00% event coverage.
- I003_H005: best new learning, but still too broad for dashboard promotion.

The current inventory has 342 columns. Relevant existing groups include credit spreads and credit changes, Treasury and curve fields, VIX/VXN/VVIX and volatility term structure, realized and downside volatility, R2 and MMDI components, leadership relative-strength columns, Mag7 breadth, liquidity proxies, and live headline/sentiment outputs. The feature universe documentation marks live RSS headline semantics as current-context-only unless point-in-time snapshots are archived.

## External Research Readout

### Market Stress And Cross-Asset Spillovers

BIS Working Paper 1250 develops market condition indicators for Treasury, FX, and money markets and finds value in modeling future tail stress with cross-market spillovers and drivers such as funding liquidity, investor overextension, and the global financial cycle. FD_001 translates this into cross-asset sequence, funding-pressure, and safe-haven rotation features rather than a single same-day stress trigger.

The OFR Financial Stress Index is useful as a category template: credit, equity valuation, funding, safe assets, and volatility. It also states that its daily monitor publishes with a two-business-day data lag, which is a reminder that external stress indices need release-lag handling before historical use.

### Volatility Forecasting

The Federal Reserve volatility comparison reports that regime-switching HAR-style models can outperform more complex ML alternatives in realized volatility and risk forecasting. FD_001 therefore favors interpretable regime and persistence features over black-box model outputs.

Recent volatility preprints emphasize regime shifts, heavy tails, model degradation across turbulent periods, and limited-data instability. This supports downside-volatility persistence, volatility-term persistence, and regime-disagreement ideas.

### Text, LLMs, And Agentic Quant Research

TradingAgents, FinRobot, FinGPT, the finance LLM agent survey, and the 2026 agentic trading survey are useful for process design: multi-role decomposition, source provenance, DataOps discipline, risk management roles, and auditability. They do not justify using live LLM or news outputs in historical backtests unless those outputs are archived point-in-time.

News and narrative volatility papers support the idea that text can matter more during high-volatility regimes. FD_001 keeps those ideas as current-context-only or future-data requirements because this repo currently has live RSS snapshots, not historical point-in-time archives.

### Leakage-Safe Evaluation

The backtest-overfitting literature reinforces that feature acceptance should not be confused with hypothesis validation. FD_001 does not run tests. Later hypotheses should use purged or otherwise leakage-aware evaluation, especially when labels overlap across forward drawdown horizons.

## Implications For FD_001

- Promote features that can be constructed from current exported columns or clearly auditable public daily series.
- Defer options-surface, intraday, news, and LLM-agent features until point-in-time archives exist.
- Prefer episode, persistence, duration, and sequence transforms that may add timing information beyond current daily levels.
- Keep every promoted feature research-only until validated and explicitly approved for production.
