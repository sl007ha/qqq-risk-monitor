# QQQ Risk Monitor v2 Feature Universe

This repository now includes an additive v2 feature-universe layer for future Autoresearch / Codex experiments.

The current v1.3.1 R2 × MMDI dashboard signal is **not changed**. The new layer only adds extra public data, computes additional research features, and exports feature/sentiment tables.

## New feature families

```text
A. Price / Trend Structure
B. Drawdown / Distance from High
C. Volatility / Range / Path Risk
D. Momentum / Reversal
E. Breadth / Market Internals
F. Leadership / Relative Strength
G. Semiconductor / AI / Tech Confirmation
H. Rates / Yield Curve
I. Credit / Funding Stress
J. Vol / Options / Tail Stress
K. Macro / Regime Context
L. Liquidity / Volume / Flow
M. Mainstream Narrative / Semantic
```

## New outputs

After running:

```bash
python run_dashboard.py --output-dir outputs
```

you will still get the main dashboard HTML. You will also get:

```text
outputs/qqq_r2_mmdi_v1_3_1_feature_catalog.csv
outputs/qqq_r2_mmdi_v1_3_1_feature_snapshot_latest.csv
outputs/qqq_r2_mmdi_v1_3_1_sentiment_summary.csv
outputs/qqq_r2_mmdi_v1_3_1_sentiment_headlines.csv
```

The dashboard HTML also appends feature-universe and mainstream narrative / semantic sections near the bottom.

## Important caveat on sentiment

The mainstream narrative / semantic panel uses live Google News RSS headline snapshots and transparent keyword scoring. It is useful for current dashboard context, but it is **not historical/backtest-ready** unless headline snapshots are archived point-in-time.

Do not use the live RSS sentiment score in historical model optimization until a point-in-time headline archive exists.
