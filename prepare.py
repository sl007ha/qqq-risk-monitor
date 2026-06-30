#!/usr/bin/env python
"""Autoresearch-style prepare step.

For this initial local-port phase, this step freezes the market/macro data and
feature table but does not optimize or iterate.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from qqq_autoresearch.config import get_config
from qqq_autoresearch.data_sources import download_market_data
from qqq_autoresearch.features import build_features


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", default="artifacts", help="Directory for prepared CSV artifacts.")
    args = parser.parse_args()
    artifact_dir = Path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    config = get_config()
    bundle = download_market_data(config)
    features = build_features(bundle.data, config)

    bundle.data.to_csv(artifact_dir / "raw_market_data.csv")
    features.to_csv(artifact_dir / "features_daily.csv")
    bundle.availability.to_csv(artifact_dir / "data_availability.csv", index=False)

    print(f"Prepared raw data and features in: {artifact_dir}")
    print(f"Rows: {len(features):,}; date range: {features.index.min().date()} to {features.index.max().date()}")


if __name__ == "__main__":
    main()
