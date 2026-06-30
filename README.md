# QQQ Risk Monitor — R2 × MMDI Dashboard v1.3.1

Autoresearch-style local port of the original Colab dashboard.

The original Colab version had two cells:
1. install/download data/construct signals;
2. render dashboard tables/charts and export files.

This local version separates those responsibilities so the project can later be used with an autoresearch workflow.

## Structure

```text
.
├── prepare.py                     # freeze/download raw data and feature table
├── run_dashboard.py               # main local dashboard runner
├── run_experiment.py              # autoresearch-compatible runner, no optimization yet
├── program.md                     # research / agent governance instructions
├── requirements.txt
└── qqq_autoresearch/
    ├── config.py                  # frozen config and thresholds
    ├── data_sources.py            # Yahoo/FRED loaders
    ├── features.py                # deterministic feature construction
    ├── candidate.py               # R2 × MMDI signal logic; future AI-editable file
    ├── render.py                  # tables, charts, single HTML renderer
    └── pipeline.py                # orchestration
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

## Run

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
```

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
