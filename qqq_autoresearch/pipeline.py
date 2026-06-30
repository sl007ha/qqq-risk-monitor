"""End-to-end local dashboard pipeline."""
from __future__ import annotations

from pathlib import Path

from .candidate import apply_signals
from .config import get_config
from .data_sources import download_market_data
from .features import build_features
from .render import build_all_dashboard_artifacts, write_csv_outputs, write_dashboard_html


def run_pipeline(output_dir: str | Path = "outputs", config_overrides: dict | None = None) -> dict:
    config = get_config(config_overrides)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    bundle = download_market_data(config)
    features = build_features(bundle.data, config)
    work = apply_signals(features, config)
    artifacts = build_all_dashboard_artifacts(work, bundle.availability, config)

    html_path = output_dir / f"{config['export_prefix']}_dashboard.html"
    write_csv_outputs(work, artifacts, output_dir, config)
    write_dashboard_html(work, artifacts, html_path, config)

    latest = work.dropna(subset=["qqq_close"]).iloc[-1]
    summary = {
        "dashboard_html": str(html_path),
        "latest_date": str(latest.name.date()),
        "current_state": str(latest["COMBINED_STATE"]),
        "combined_signal": str(latest["COMBINED_SIGNAL"]),
        "r2_active": bool(latest["R2_ACTIVE"]),
        "r2_stress_count": int(latest["R2_STRESS_COUNT"]),
        "mmdi": None if latest["MMDI"] != latest["MMDI"] else float(latest["MMDI"]),
        "credit_source": str(latest["credit_source"]),
        "us10y_source": str(latest["us10y_source"]),
    }
    return summary
