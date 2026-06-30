"""Point-in-time market and macro data download helpers.

The local runner keeps external data loading outside candidate.py so that later
autoresearch iterations cannot silently change the data source or alignment.
"""
from __future__ import annotations

import io
import os
import time
from dataclasses import dataclass

import pandas as pd
import requests
import yfinance as yf


@dataclass
class DownloadBundle:
    data: pd.DataFrame
    availability: pd.DataFrame
    credit_source: str
    credit_data_available: bool
    us10y_source: str


def load_yf_close(ticker: str, start: str) -> pd.Series:
    data = yf.download(
        ticker,
        start=start,
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    if data is None or data.empty:
        print(f"WARNING: No Yahoo data for {ticker}")
        return pd.Series(dtype=float, name=ticker)
    close = data["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close.index = pd.to_datetime(close.index).tz_localize(None)
    close = close.sort_index().dropna()
    close.name = ticker
    return close


def get_fred_api_key() -> str | None:
    key = os.environ.get("FRED_API_KEY")
    if key:
        key = str(key).strip()
    return key or None


def load_fred_series_official_api(
    series_id: str,
    start: str = "1998-01-01",
    end: str | None = None,
    api_key: str | None = None,
    timeout: int = 30,
    retries: int = 3,
    sleep_seconds: int = 2,
) -> pd.Series:
    api_key = api_key or get_fred_api_key()
    if not api_key:
        raise ValueError("No FRED_API_KEY found.")

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "asc",
        "observation_start": start,
        "limit": 100000,
    }
    if end:
        params["observation_end"] = end

    headers = {"User-Agent": "Mozilla/5.0 qqq-risk-monitor-local"}
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
            resp.raise_for_status()
            payload = resp.json()
            if "error_code" in payload:
                raise RuntimeError(
                    f"FRED API error {payload.get('error_code')}: {payload.get('error_message')}"
                )
            obs = payload.get("observations", [])
            if not obs:
                raise RuntimeError(f"FRED returned no observations for {series_id}")
            fred_df = pd.DataFrame(obs)
            fred_df["date"] = pd.to_datetime(fred_df["date"])
            fred_df["value"] = pd.to_numeric(
                fred_df["value"].replace(".", pd.NA), errors="coerce"
            )
            s = fred_df.set_index("date")["value"].sort_index().dropna()
            s.name = series_id
            if s.empty:
                raise RuntimeError(f"FRED series {series_id} parsed but empty")
            print(
                f"FRED official API OK: {series_id}, "
                f"{s.index.min().date()} to {s.index.max().date()}, {len(s):,} observations"
            )
            return s
        except Exception as e:
            last_error = e
            print(f"WARNING: FRED official API {series_id} attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                time.sleep(sleep_seconds)

    raise last_error


def load_fred_series_graph_csv_fallback(
    series_id: str,
    timeout: int = 30,
    retries: int = 3,
    sleep_seconds: int = 2,
) -> pd.Series:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    headers = {"User-Agent": "Mozilla/5.0 qqq-risk-monitor-local"}
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            fred_df = pd.read_csv(io.StringIO(resp.text))
            date_col = "observation_date" if "observation_date" in fred_df.columns else fred_df.columns[0]
            value_col = series_id if series_id in fred_df.columns else fred_df.columns[-1]
            fred_df[date_col] = pd.to_datetime(fred_df[date_col])
            s = pd.to_numeric(fred_df[value_col].replace(".", pd.NA), errors="coerce")
            s.index = fred_df[date_col]
            s = s.sort_index().dropna()
            s.name = series_id
            if s.empty:
                raise RuntimeError(f"FRED graph CSV {series_id} parsed but empty")
            print(
                f"FRED graph CSV fallback OK: {series_id}, "
                f"{s.index.min().date()} to {s.index.max().date()}, {len(s):,} observations"
            )
            return s
        except Exception as e:
            last_error = e
            print(f"WARNING: FRED graph CSV {series_id} attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                time.sleep(sleep_seconds)
    raise last_error


def load_fred_series(series_id: str, start: str = "1998-01-01", end: str | None = None) -> pd.Series:
    api_key = get_fred_api_key()
    if api_key:
        try:
            return load_fred_series_official_api(series_id=series_id, start=start, end=end, api_key=api_key)
        except Exception as e:
            print(f"WARNING: official FRED API failed for {series_id}; falling back to graph CSV. Error: {e}")
    else:
        print(f"INFO: No FRED_API_KEY found. Using graph CSV fallback for {series_id}.")
    return load_fred_series_graph_csv_fallback(series_id)


def _safe_index_min(s: pd.Series):
    return s.dropna().index.min() if isinstance(s, pd.Series) and not s.dropna().empty else pd.NaT


def _safe_index_max(s: pd.Series):
    return s.dropna().index.max() if isinstance(s, pd.Series) and not s.dropna().empty else pd.NaT


def download_market_data(config: dict) -> DownloadBundle:
    start = config["start_date"]
    print("Downloading market data from Yahoo Finance...")

    qqq = load_yf_close("QQQ", start)
    spy = load_yf_close("SPY", start)
    vix = load_yf_close("^VIX", start)
    vxn = load_yf_close("^VXN", start)
    qqqe = load_yf_close("QQQE", start)
    ndx = load_yf_close("^NDX", start)
    tnx = load_yf_close("^TNX", start)

    if qqq.empty:
        raise ValueError("QQQ data download failed. Cannot continue.")

    df = pd.DataFrame(index=qqq.index)
    df.index.name = "date"
    df["qqq_close"] = qqq
    df["spy_close"] = spy.reindex(df.index).ffill()
    df["vix"] = vix.reindex(df.index).ffill()
    df["vxn"] = vxn.reindex(df.index).ffill()
    df["qqqe_close"] = qqqe.reindex(df.index).ffill()
    df["ndx_close"] = ndx.reindex(df.index).ffill()

    print("Downloading FRED data...")
    try:
        primary_credit = load_fred_series(config["primary_credit_series"], start=start)
    except Exception as e:
        print(f"WARNING: primary credit series failed after retries: {e}")
        primary_credit = pd.Series(dtype=float, name=config["primary_credit_series"])

    try:
        fallback_credit = load_fred_series(config["fallback_credit_series"], start=start)
    except Exception as e:
        print(f"WARNING: fallback credit series failed after retries: {e}")
        fallback_credit = pd.Series(dtype=float, name=config["fallback_credit_series"])

    try:
        dgs10 = load_fred_series("DGS10", start=start)
    except Exception as e:
        print(f"WARNING: FRED DGS10 failed after retries, using Yahoo ^TNX fallback if available: {e}")
        dgs10 = pd.Series(dtype=float, name="DGS10")

    use_primary = False
    if not primary_credit.empty and primary_credit.index.min() <= pd.Timestamp(config["primary_min_start_date"]):
        use_primary = True

    if use_primary:
        credit = primary_credit
        credit_source = config["primary_credit_series"]
        credit_data_available = True
    elif not fallback_credit.empty:
        credit = fallback_credit
        credit_source = config["fallback_credit_series"]
        credit_data_available = True
    else:
        print("WARNING: Both FRED credit series failed. Continuing with credit component disabled.")
        credit = pd.Series(pd.NA, index=df.index, name="CREDIT_UNAVAILABLE")
        credit_source = "CREDIT_UNAVAILABLE_FRED_5XX_OR_TIMEOUT"
        credit_data_available = False

    df["credit_spread"] = credit.reindex(df.index).ffill()
    df["credit_source"] = credit_source
    df["credit_data_available"] = credit_data_available

    df["us10y_yield"] = dgs10.reindex(df.index).ffill()
    if df["us10y_yield"].dropna().empty and not tnx.empty:
        df["us10y_yield"] = (tnx / 10.0).reindex(df.index).ffill()
    us10y_source = "FRED_DGS10" if not dgs10.empty else ("Yahoo_^TNX_fallback" if not tnx.empty else "US10Y_UNAVAILABLE")
    df["us10y_source"] = us10y_source

    availability = pd.DataFrame([
        {"series": "QQQ", "start": _safe_index_min(qqq), "end": _safe_index_max(qqq), "count": int(qqq.count())},
        {"series": "SPY", "start": _safe_index_min(spy), "end": _safe_index_max(spy), "count": int(spy.count())},
        {"series": "^VIX", "start": _safe_index_min(vix), "end": _safe_index_max(vix), "count": int(vix.count())},
        {"series": "^VXN", "start": _safe_index_min(vxn), "end": _safe_index_max(vxn), "count": int(vxn.count())},
        {"series": "QQQE", "start": _safe_index_min(qqqe), "end": _safe_index_max(qqqe), "count": int(qqqe.count())},
        {"series": "^NDX", "start": _safe_index_min(ndx), "end": _safe_index_max(ndx), "count": int(ndx.count())},
        {"series": credit_source, "start": _safe_index_min(df["credit_spread"]), "end": _safe_index_max(df["credit_spread"]), "count": int(df["credit_spread"].count())},
        {"series": us10y_source, "start": _safe_index_min(df["us10y_yield"]), "end": _safe_index_max(df["us10y_yield"]), "count": int(df["us10y_yield"].count())},
    ])

    return DownloadBundle(
        data=df,
        availability=availability,
        credit_source=credit_source,
        credit_data_available=credit_data_available,
        us10y_source=us10y_source,
    )
