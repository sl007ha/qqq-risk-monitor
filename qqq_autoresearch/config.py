"""Frozen dashboard configuration for QQQ Risk Monitor v1.3.1."""
from __future__ import annotations

from copy import deepcopy

DEFAULT_CONFIG = {
    "module": "QQQ Risk Monitor — R2 × MMDI Dashboard v1.3.1",
    "start_date": "1998-01-01",
    "primary_credit_series": "BAMLH0A0HYM2",
    "fallback_credit_series": "BAA10Y",
    "primary_min_start_date": "1999-01-01",
    "mmdi_high_threshold": 50.0,
    "mmdi_extreme_threshold": 80.0,
    "r2_price_below_200dma_threshold": -0.03,
    "r2_6m_momentum_threshold": -0.05,
    "r2_126d_drawdown_threshold": -0.10,
    "r2_252d_drawdown_threshold": -0.12,
    "r2_21d_shock_threshold": -0.05,
    "r2_vix_level_threshold": 25.0,
    "r2_vix_pctile_threshold": 0.80,
    "r2_credit_pctile_threshold": 0.80,
    "r2_credit_20d_change_threshold": 0.25,
    "r2_active_stress_count_threshold": 3,
    "component_chart_days": 252,
    "mag7_tickers": ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA"],
    "ndx_cape_manual_value": None,
    "ndx_cape_manual_asof": None,
    "compute_ndx_cape_proxy": False,
    "ndx_cape_proxy_top_n": 40,
    "export_prefix": "qqq_r2_mmdi_v1_3_1",
}


def get_config(overrides: dict | None = None) -> dict:
    cfg = deepcopy(DEFAULT_CONFIG)
    if overrides:
        cfg.update(overrides)
    return cfg
