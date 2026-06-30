"""Feature preparation layer.

This corresponds to autoresearch's `prepare.py` responsibility: freeze data,
time alignment, and feature construction before any candidate logic runs.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .utils import expanding_percentile_of_last, rolling_percentile_of_last


def build_features(raw: pd.DataFrame, config: dict) -> pd.DataFrame:
    work = raw.copy()
    close = work["qqq_close"]
    log_ret = np.log(close / close.shift(1))

    work["ret_21d"] = close / close.shift(21) - 1
    work["ret_63d"] = close / close.shift(63) - 1
    work["ret_126d"] = close / close.shift(126) - 1
    work["ret_252d"] = close / close.shift(252) - 1

    work["ma_50d"] = close.rolling(50).mean()
    work["ma_200d"] = close.rolling(200).mean()
    work["dist_50dma"] = close / work["ma_50d"] - 1
    work["dist_200dma"] = close / work["ma_200d"] - 1

    work["high_63d"] = close.rolling(63).max()
    work["high_126d"] = close.rolling(126).max()
    work["high_252d"] = close.rolling(252).max()
    work["dd_from_63d_high"] = close / work["high_63d"] - 1
    work["dd_from_126d_high"] = close / work["high_126d"] - 1
    work["dd_from_252d_high"] = close / work["high_252d"] - 1
    work["r2_drawdown_worst"] = work[["dd_from_126d_high", "dd_from_252d_high"]].min(axis=1)

    work["realized_vol_21d"] = log_ret.rolling(21).std() * np.sqrt(252)
    work["realized_vol_63d"] = log_ret.rolling(63).std() * np.sqrt(252)
    work["realized_vol_252d"] = log_ret.rolling(252).std() * np.sqrt(252)
    work["vol_ratio_21d_252d"] = work["realized_vol_21d"] / work["realized_vol_252d"]

    work["credit_spread_level_pctile"] = expanding_percentile_of_last(work["credit_spread"], min_periods=252)
    work["credit_spread_20d_change"] = work["credit_spread"] - work["credit_spread"].shift(20)
    work["us10y_20d_change"] = work["us10y_yield"] - work["us10y_yield"].shift(20)
    work["us10y_63d_change"] = work["us10y_yield"] - work["us10y_yield"].shift(63)

    work["vix_pctile_3y"] = rolling_percentile_of_last(work["vix"], window=756, min_periods=252)
    work["vxn_pctile_3y"] = rolling_percentile_of_last(work["vxn"], window=756, min_periods=252)
    work["realized_vol_21d_pctile_3y"] = rolling_percentile_of_last(work["realized_vol_21d"], window=756, min_periods=252)

    return work
