"""Shared formatting and signal helper functions."""
from __future__ import annotations

import math
from datetime import date

import numpy as np
import pandas as pd


def pct_fmt(x, digits: int = 1) -> str:
    if pd.isna(x):
        return "N/A"
    return f"{float(x):.{digits}%}"


def num_fmt(x, digits: int = 2) -> str:
    if pd.isna(x):
        return "N/A"
    return f"{float(x):,.{digits}f}"


def money_fmt(x, digits: int = 1) -> str:
    if pd.isna(x):
        return "N/A"
    x = float(x)
    absx = abs(x)
    if absx >= 1e12:
        return f"{x/1e12:,.{digits}f}T"
    if absx >= 1e9:
        return f"{x/1e9:,.{digits}f}B"
    if absx >= 1e6:
        return f"{x/1e6:,.{digits}f}M"
    return f"{x:,.0f}"


def bool_badge(x) -> str:
    if pd.isna(x):
        return "UNKNOWN"
    return "TRIGGERED" if bool(x) else "OK"


def safe_float(x, default=np.nan):
    try:
        if x is None:
            return default
        if isinstance(x, (list, tuple)) and len(x) == 0:
            return default
        return float(x)
    except Exception:
        return default


def active_run_length(condition: pd.Series) -> pd.Series:
    c = condition.fillna(False).astype(bool)
    group = (c != c.shift(fill_value=False)).cumsum()
    run = c.groupby(group).cumcount() + 1
    return run.where(c, 0)


def rolling_percentile_of_last(s: pd.Series, window: int = 756, min_periods: int = 252) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")

    def pct_last(x):
        x = pd.Series(x).dropna()
        if len(x) == 0:
            return np.nan
        return x.rank(pct=True).iloc[-1]

    return s.rolling(window=window, min_periods=min_periods).apply(pct_last, raw=False)


def expanding_percentile_of_last(s: pd.Series, min_periods: int = 252) -> pd.Series:
    values, out = [], []
    for x in s:
        if pd.isna(x):
            out.append(np.nan)
            continue
        values.append(float(x))
        if len(values) < min_periods:
            out.append(np.nan)
        else:
            arr = np.asarray(values)
            out.append((arr <= x).mean())
    return pd.Series(out, index=s.index)


def stress_count_intensity(x):
    if pd.isna(x):
        return "UNKNOWN"
    if x <= 1:
        return "LOW_0_1"
    if x == 2:
        return "WATCH_2"
    if x == 3:
        return "ELEVATED_3"
    return "SEVERE_4_PLUS"


def classify_mmdi_zone(mmdi, config: dict) -> str:
    if pd.isna(mmdi):
        return "UNKNOWN"
    if mmdi >= config["mmdi_extreme_threshold"]:
        return "EXTREME"
    if mmdi >= config["mmdi_high_threshold"]:
        return "HIGH"
    if mmdi >= 35:
        return "ELEVATED"
    return "LOW"


def combined_state_from_row(r2_active, mmdi, config: dict) -> str:
    if not bool(r2_active):
        return "NORMAL"
    if pd.isna(mmdi):
        return "R2_ACTIVE_UNCONFIRMED"
    if mmdi >= config["mmdi_extreme_threshold"]:
        return "EXTREME_CONFIRMED_RISK"
    if mmdi >= config["mmdi_high_threshold"]:
        return "CONFIRMED_RISK"
    return "R2_ACTIVE_UNCONFIRMED"


def combined_signal_label(state: str) -> str:
    return {
        "NORMAL": "NORMAL",
        "R2_ACTIVE_UNCONFIRMED": "EARLY_WARNING_UNCONFIRMED",
        "CONFIRMED_RISK": "CONFIRMED_WARNING",
        "EXTREME_CONFIRMED_RISK": "EXTREME_CONFIRMED_WARNING",
    }.get(state, "UNKNOWN")


def combined_interpretation(state: str) -> str:
    return {
        "NORMAL": (
            "No active R2-level fragility signal. Normal does not mean risk-free; "
            "it only means the monitor is not currently flagging elevated fragility."
        ),
        "R2_ACTIVE_UNCONFIRMED": (
            "R2 early warning is active but not confirmed by MMDI. Treat as lower-confidence "
            "but not harmless; review discretionary exposure and avoid complacency."
        ),
        "CONFIRMED_RISK": (
            "R2 early warning is confirmed by market internals. This is the dashboard-prominent risk-warning state."
        ),
        "EXTREME_CONFIRMED_RISK": (
            "R2 warning is confirmed and internal market stress is extreme. Treat as high-intensity confirmed risk, "
            "but not as a separate automatic sell trigger."
        ),
    }.get(state, "Unknown state.")
