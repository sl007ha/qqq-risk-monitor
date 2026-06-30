# QQQ Risk Monitor — R2 × MMDI Dashboard v1.3.1

Autoresearch-style local port of the original Colab dashboard.

The original Colab version had two cells:
1. install/download data/construct signals;
2. render dashboard tables/charts and export files.

This local version separates those responsibilities so the project can later be used with an autoresearch workflow.

## Structure

```text
.
├── prepare.py                         # freeze/download raw data and feature table
├── run_dashboard.py                   # main local dashboard runner
├── run_experiment.py                  # autoresearch-compatible runner, no optimization yet
├── run_generate_hypotheses.py         # local Ollama hypothesis generator
├── program.md                         # research / agent governance instructions
├── program_hypothesis_generation.md   # hypothesis-generation governance instructions
├── requirements.txt
└── qqq_autoresearch/
    ├── config.py                      # frozen config and thresholds
    ├── data_sources.py                # Yahoo/FRED loaders
    ├── features.py                    # deterministic feature construction
    ├── candidate.py                   # R2 × MMDI signal logic; future AI-editable file
    ├── feature_universe_extension.py  # additive v2 feature universe
    ├── feature_inventory.py           # all-column inventory export
    ├── ollama_client.py               # local Ollama HTTP client
    ├── hypothesis_agent.py            # Ollama-powered hypothesis generator
    ├── render.py                      # tables, charts, single HTML renderer
    └── pipeline.py                    # orchestration
```

## Setup

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Optional but recommended for more stable FRED access:

```bash
# Windows PowerShell
$env:FRED_API_KEY="your_fred_key"

# macOS/Linux
export FRED_API_KEY="your_fred_key"
```

Without `FRED_API_KEY`, the code falls back to FRED graph CSV.

## Run dashboard

```bash
python run_dashboard.py --output-dir outputs
```

Main output:

```text
outputs/qqq_r2_mmdi_v1_3_1_dashboard.html
```

CSV outputs are also saved to `outputs/`:

```text
qqq_r2_mmdi_v1_3_1_full_daily_data.csv
qqq_r2_mmdi_v1_3_1_current_dashboard.csv
qqq_r2_mmdi_v1_3_1_r2_component_table.csv
qqq_r2_mmdi_v1_3_1_mmdi_component_table.csv
qqq_r2_mmdi_v1_3_1_threshold_table.csv
qqq_r2_mmdi_v1_3_1_macro_table.csv
qqq_r2_mmdi_v1_3_1_ndx_cape_table.csv
qqq_r2_mmdi_v1_3_1_mag7_fundamentals_raw.csv
qqq_r2_mmdi_v1_3_1_data_availability.csv
qqq_r2_mmdi_v1_3_1_feature_catalog.csv
qqq_r2_mmdi_v1_3_1_feature_snapshot_latest.csv
qqq_r2_mmdi_v1_3_1_all_feature_inventory.csv
qqq_r2_mmdi_v1_3_1_all_feature_latest_wide.csv
qqq_r2_mmdi_v1_3_1_all_features_daily_wide.csv
qqq_r2_mmdi_v1_3_1_sentiment_summary.csv
qqq_r2_mmdi_v1_3_1_sentiment_headlines.csv
```

## Generate hypotheses with local Ollama

First run the dashboard so the `outputs/` feature files exist.

Then make sure Ollama is running locally and the model is pulled, for example:

```bash
ollama pull qwen2.5:7b
```

Generate hypotheses:

```bash
python run_generate_hypotheses.py --model qwen2.5:7b --output-dir outputs --n-hypotheses 24
```

For a stronger but slower local model, replace the model name with any model installed in Ollama, for example:

```bash
python run_generate_hypotheses.py --model qwen2.5-coder:7b --output-dir outputs --n-hypotheses 24
```

Outputs:

```text
hypotheses/HYPOTHESES.md
hypotheses/hypotheses.yaml
hypotheses/hypotheses.json
hypotheses/last_hypothesis_prompt.txt
```

To inspect the prompt without calling Ollama:

```bash
python run_generate_hypotheses.py --dry-run-prompt
```

The local Ollama step is hypothesis generation only. It should not modify dashboard logic, R2/MMDI definitions, labels, or evaluation code.

## Autoresearch mode later

For a future optimization phase, keep data and evaluation frozen and allow an AI agent to modify only:

```text
qqq_autoresearch/candidate.py
```

Do not let the agent modify:

```text
prepare.py
run_experiment.py
qqq_autoresearch/data_sources.py
qqq_autoresearch/features.py
qqq_autoresearch/config.py
```

## Notes

- This is a decision-support dashboard, not an automatic trading system.
- Yahoo/yfinance and web-scraped earnings data can change format.
- NASDAQ-100 CAPE is not computed by default; enter a trusted manual value in config if needed.
- Live RSS sentiment is current-context only and should not be used for historical backtests unless point-in-time snapshots are archived.
