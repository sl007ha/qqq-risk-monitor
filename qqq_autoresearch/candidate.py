"""Frozen candidate logic for QQQ Risk Monitor v1.3.1.

In future autoresearch iterations, this is the only file that an agent should be
allowed to modify. For the initial local-port phase, it preserves the Colab v1.3.1
R2 x MMDI logic exactly.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .utils import (
    active_run_length,
    classify_mmdi_zone,
    combined_interpretation,
    combined_signal_label,
    combined_state_from_row,
    rolling_percentile_of_last,
    stress_count_intensity,
)

R2_COMPONENTS = [
    "r2_price_below_200dma",
    "r2_6m_momentum_negative",
    "r2_drawdown_active",
    "r2_short_momentum_shock",
    "r2_vol_stress",
    "r2_credit_stress",
]

MMDI_COMPONENTS = [
    "mmdi_vix_stress",
    "mmdi_vxn_stress",
    "mmdi_drawdown_stress",
    "mmdi_trend_damage",
    "mmdi_realized_vol_stress",
    "mmdi_leadership_narrowing_stress",
]


def apply_signals(features: pd.DataFrame, config: dict) -> pd.DataFrame:
    work = features.copy()

    work["r2_price_below_200dma"] = work["dist_200dma"] < config["r2_price_below_200dma_threshold"]
    work["r2_6m_momentum_negative"] = work["ret_126d"] < config["r2_6m_momentum_threshold"]
    work["r2_drawdown_active"] = (
        (work["dd_from_126d_high"] < config["r2_126d_drawdown_threshold"])
        | (work["dd_from_252d_high"] < config["r2_252d_drawdown_threshold"])
    )
    work["r2_short_momentum_shock"] = work["ret_21d"] < config["r2_21d_shock_threshold"]
    work["r2_vol_stress"] = (
        (work["vix"] > config["r2_vix_level_threshold"])
        | (work["vix_pctile_3y"] > config["r2_vix_pctile_threshold"])
        | (work["realized_vol_21d_pctile_3y"] > config["r2_vix_pctile_threshold"])
    )
    if bool(work["credit_data_available"].iloc[-1]) and work["credit_spread"].notna().sum() >= 252:
        work["r2_credit_stress"] = (
            (work["credit_spread_level_pctile"] > config["r2_credit_pctile_threshold"])
            | (work["credit_spread_20d_change"] > config["r2_credit_20d_change_threshold"])
        )
    else:
        work["r2_credit_stress"] = False

    work["R2_STRESS_COUNT"] = work[R2_COMPONENTS].sum(axis=1)
    work["R2_ACTIVE"] = work["R2_STRESS_COUNT"] >= config["r2_active_stress_count_threshold"]
    work["R2_ACTIVE_RUN_LENGTH"] = active_run_length(work["R2_ACTIVE"])
    work["R2_STRESS_INTENSITY"] = work["R2_STRESS_COUNT"].apply(stress_count_intensity)

    work["mmdi_vix_stress"] = work["vix_pctile_3y"] * 100
    work["mmdi_vxn_stress"] = work["vxn_pctile_3y"] * 100
    work["mmdi_drawdown_stress"] = rolling_percentile_of_last(work["dd_from_252d_high"].abs(), window=756, min_periods=252) * 100
    work["mmdi_trend_damage"] = rolling_percentile_of_last(-work["dist_200dma"], window=756, min_periods=252) * 100
    work["mmdi_realized_vol_stress"] = work["realized_vol_21d_pctile_3y"] * 100
    work["qqqe_qqq_ratio"] = work["qqqe_close"] / work["qqq_close"]
    work["qqqe_qqq_ratio_252d_high"] = work["qqqe_qqq_ratio"].rolling(252).max()
    work["qqqe_qqq_ratio_dd"] = work["qqqe_qqq_ratio"] / work["qqqe_qqq_ratio_252d_high"] - 1
    work["mmdi_leadership_narrowing_stress"] = (
        rolling_percentile_of_last(work["qqqe_qqq_ratio_dd"].abs(), window=756, min_periods=252) * 100
    )

    work["MMDI_COMPONENT_COUNT"] = work[MMDI_COMPONENTS].notna().sum(axis=1)
    work["MMDI"] = work[MMDI_COMPONENTS].mean(axis=1)
    work.loc[work["MMDI_COMPONENT_COUNT"] < 3, "MMDI"] = np.nan
    work["MMDI_10D_CHANGE"] = work["MMDI"] - work["MMDI"].shift(10)
    work["MMDI_ZONE"] = work["MMDI"].apply(lambda x: classify_mmdi_zone(x, config))
    work["MMDI_HIGH"] = work["MMDI"] >= config["mmdi_high_threshold"]
    work["MMDI_EXTREME"] = work["MMDI"] >= config["mmdi_extreme_threshold"]

    work["COMBINED_STATE"] = [
        combined_state_from_row(r2, mmdi, config) for r2, mmdi in zip(work["R2_ACTIVE"], work["MMDI"])
    ]
    work["COMBINED_SIGNAL"] = work["COMBINED_STATE"].apply(combined_signal_label)
    work["COMBINED_INTERPRETATION"] = work["COMBINED_STATE"].apply(combined_interpretation)

    return work
