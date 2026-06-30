"""Broad v2 feature-universe extension for QQQ Risk Monitor.

This module is additive: it appends extra public data, computes a wide feature
library, and exports feature/sentiment tables. It does not change the current
v1.3.1 R2 x MMDI signal rule.
"""
from __future__ import annotations

import html
import re
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import yfinance as yf

from .data_sources import load_fred_series, load_yf_close
from .utils import active_run_length, rolling_percentile_of_last

EXTRA_YF_TICKERS = {
    "dia":"DIA", "iwm":"IWM", "rsp":"RSP", "xlk":"XLK", "xly":"XLY", "xlp":"XLP", "xlf":"XLF", "xli":"XLI", "xlv":"XLV", "xlu":"XLU",
    "mtum":"MTUM", "qual":"QUAL", "soxx":"SOXX", "smh":"SMH", "nvda":"NVDA", "msft":"MSFT", "aapl":"AAPL", "amzn":"AMZN", "googl":"GOOGL", "meta":"META", "tsla":"TSLA",
    "hyg":"HYG", "lqd":"LQD", "tlt":"TLT", "ief":"IEF", "arkk":"ARKK", "dxy":"DX-Y.NYB", "vix9d":"^VIX9D", "vix3m":"^VIX3M", "vvix":"^VVIX", "skew":"^SKEW", "move":"^MOVE",
}
EXTRA_FRED_SERIES = {
    "dgs2":"DGS2", "dgs3mo":"DGS3MO", "dfii10":"DFII10", "ig_oas":"BAMLC0A0CM", "cpi":"CPIAUCSL", "unrate":"UNRATE", "claims":"ICSA",
    "fedfunds":"FEDFUNDS", "nfci":"NFCI", "walcl":"WALCL", "sofr":"SOFR", "tedrate":"TEDRATE",
}
FEATURE_FAMILIES = {
    "A. Price / Trend Structure": ["price_vs_ma20","price_vs_ma50","price_vs_ma100","price_vs_ma200","ma20_vs_ma50","ma50_vs_ma200","ma200_slope_20d","ma200_slope_60d","price_cross_ma50_10d","price_cross_ma200_20d","days_above_ma50","days_below_ma200","failed_reclaim_ma50","failed_reclaim_ma200"],
    "B. Drawdown / Distance from High": ["qqq_dd_20d","qqq_dd_60d","qqq_dd_126d","qqq_dd_252d","dist_52w_high","dist_52w_low","underwater_days_52w","drawdown_speed_20d","rebound_from_trough_20d","lower_high_flag","lower_low_flag"],
    "C. Volatility / Range / Path Risk": ["range_5d_vs_252d","range_20d_vs_252d","high_low_range_1d","atr_pct_14","qqq_vol_10d","qqq_vol_20d","qqq_vol_60d","vol_20d_vs_60d","vol_20d_vs_252d","downside_vol_20d","upside_vol_20d","downside_upside_vol_ratio","gap_down_count_20d","large_red_day_count_20d","realized_skew_20d","realized_kurt_20d"],
    "D. Momentum / Reversal": ["qqq_ret_1w","qqq_ret_2w","qqq_ret_1m","qqq_ret_3m","qqq_ret_6m","qqq_ret_12m","tsmom_1m_sign","tsmom_3m_sign","tsmom_6m_sign","tsmom_12m_sign","vol_adj_mom_60d","vol_adj_mom_126d","mom_1m_minus_6m","reversal_5d_after_60d_runup","rsi_14","rsi_25","macd_signal","macd_hist_change"],
    "E. Breadth / Market Internals": ["mmdi_level","mmdi_5d_change","mmdi_10d_change","mmdi_20d_change","mmdi_percentile_252d","mmdi_falling_from_high","mmdi_low_after_high","advance_decline_line_20d","pct_above_20dma","pct_above_50dma","pct_above_200dma","new_highs_lows_20d","nasdaq_adv_dec_ratio","qqq_equal_weight_rel","qqq_vs_qqqe_3m","qqq_vs_qqqe_6m","qqq_vs_rsp_3m","qqq_vs_iwm_3m","qqq_vs_iwm_6m"],
    "F. Leadership / Relative Strength": ["qqq_vs_spy_1m","qqq_vs_spy_3m","qqq_vs_dia_3m","qqq_vs_iwm_3m","qqq_vs_rsp_3m","qqq_vs_qqqe_3m","xlk_vs_spy_3m","xly_vs_xlp_3m","xlf_vs_spy_3m","xli_vs_spy_3m","xlv_vs_spy_3m","xlp_vs_spy_3m","xlu_vs_spy_3m","mtum_vs_qual_3m","growth_vs_value_3m","large_vs_small_3m"],
    "G. Semiconductor / AI / Tech Confirmation": ["soxx_ret_1m","soxx_ret_3m","soxx_ret_6m","qqq_vs_soxx_1m","qqq_vs_soxx_3m","qqq_vs_soxx_6m","soxx_vs_spy_3m","smh_vs_qqq_3m","nvda_vs_qqq_3m","msft_vs_qqq_3m","aapl_vs_qqq_3m","mag7_equal_weight_vs_qqq","mag7_breadth","semis_failure_flag","qqq_up_soxx_down_20d"],
    "H. Rates / Yield Curve": ["ust2y_change_20d","ust10y_change_20d","real_yield_10y_change_20d","tlt_ret_20d","ief_ret_20d","tlt_ief_rel_3m","yield_curve_10y2y","yield_curve_10y3m","curve_steepening_20d","rate_vol_proxy","dxy_change_20d","usd_yield_shock"],
    "I. Credit / Funding Stress": ["hy_oas_level","hy_oas_change_20d","ig_oas_level","ig_oas_change_20d","hy_ig_spread","hyg_ret_20d","lqd_ret_20d","hyg_vs_lqd_20d","credit_spread_accel_20d","ted_spread_proxy","sofr_spread_proxy","credit_not_confirming_equity","credit_worsening_equity_up"],
    "J. Vol / Options / Tail Stress": ["vix_level","vix_change_5d","vix_change_20d","vix_percentile_252d","vix9d_vs_vix","vix3m_vs_vix","vol_term_inversion_flag","vvix_level","skew_index","put_call_ratio","qqq_iv_rv_spread","tail_hedge_demand_flag","panic_vol_flag","vol_crush_after_spike"],
    "K. Macro / Regime Context": ["inflation_regime","inflation_surprise","growth_regime","unemployment_trend","claims_trend","fed_policy_regime","fed_surprise_30d","real_rate_regime","liquidity_regime","financial_conditions_index","earnings_revision_trend","valuation_regime","ai_capex_risk_proxy","macro_uncertainty_proxy"],
    "L. Liquidity / Volume / Flow": ["qqq_volume_z_20d","dollar_volume_z_20d","obv_20d_chg","obv_60d_chg","up_down_volume_ratio_20d","volume_on_down_days","volume_on_up_days","etf_flow_qqq_20d","arkk_vs_qqq_3m","margin_debt_change","liquidity_drain_proxy","market_depth_proxy","amihud_illiquidity_proxy"],
    "M. Mainstream Narrative / Semantic": ["headline_sentiment_score","headline_risk_score","headline_euphoria_score","headline_ai_score","headline_recession_score","headline_count","headline_negative_share","headline_positive_share"],
}

def _safe_index_min(s):
    return s.dropna().index.min() if isinstance(s, pd.Series) and not s.dropna().empty else pd.NaT

def _safe_index_max(s):
    return s.dropna().index.max() if isinstance(s, pd.Series) and not s.dropna().empty else pd.NaT

def _availability_row(name, s):
    return {"series": name, "start": _safe_index_min(s), "end": _safe_index_max(s), "count": int(s.count()) if isinstance(s, pd.Series) else 0}

def _load_yf_ohlcv(ticker, start):
    data = yf.download(ticker, start=start, auto_adjust=True, progress=False, threads=False)
    if data is None or data.empty:
        print(f"WARNING: No Yahoo OHLCV data for {ticker}")
        return pd.DataFrame()
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [c[0] if isinstance(c, tuple) else c for c in data.columns]
    data.index = pd.to_datetime(data.index).tz_localize(None)
    return data[[c for c in ["Open","High","Low","Close","Volume"] if c in data.columns]].sort_index()

def add_feature_universe_data(raw, availability, config):
    start = config.get("start_date", "1998-01-01")
    df, rows = raw.copy(), []
    qqq_ohlcv = _load_yf_ohlcv("QQQ", start)
    if not qqq_ohlcv.empty:
        df["qqq_open"] = qqq_ohlcv["Open"].reindex(df.index)
        df["qqq_high"] = qqq_ohlcv["High"].reindex(df.index)
        df["qqq_low"] = qqq_ohlcv["Low"].reindex(df.index)
        df["qqq_volume"] = qqq_ohlcv.get("Volume", pd.Series(index=df.index, dtype=float)).reindex(df.index)
        rows.append(_availability_row("QQQ_OHLCV", qqq_ohlcv["Close"]))
    for prefix, ticker in EXTRA_YF_TICKERS.items():
        if prefix == "qqqe" and "qqqe_close" in df.columns:
            continue
        s = load_yf_close(ticker, start)
        df[f"{prefix}_close"] = s.reindex(df.index).ffill()
        rows.append(_availability_row(ticker, s))
    for prefix, series_id in EXTRA_FRED_SERIES.items():
        try:
            s = load_fred_series(series_id, start=start)
        except Exception as e:
            print(f"WARNING: FRED extra series {series_id} failed: {e}")
            s = pd.Series(dtype=float, name=series_id)
        df[prefix] = s.reindex(df.index).ffill()
        rows.append(_availability_row(series_id, s))
    extra = pd.DataFrame(rows)
    availability = pd.concat([availability, extra], ignore_index=True) if availability is not None and not availability.empty else extra
    return df, availability

def _ret(s, n): return s / s.shift(n) - 1

def _rel(a, b, n): return _ret(a, n) - _ret(b, n)

def _z(s, window=252, min_periods=60):
    return (s - s.rolling(window, min_periods=min_periods).mean()) / s.rolling(window, min_periods=min_periods).std().replace(0, np.nan)

def _rsi(close, window):
    d = close.diff(); gain = d.clip(lower=0).rolling(window).mean(); loss = (-d.clip(upper=0)).rolling(window).mean(); rs = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)

def _ensure(work, cols):
    for c in cols:
        if c not in work.columns: work[c] = np.nan

def add_feature_universe_features(work, config):
    work = work.copy(); close = work["qqq_close"]; high = work.get("qqq_high", close); low = work.get("qqq_low", close); open_ = work.get("qqq_open", close)
    volume = work.get("qqq_volume", pd.Series(index=work.index, dtype=float)); simple_ret = close.pct_change(); log_ret = np.log(close / close.shift(1)); prev_close = close.shift(1)
    work["ma_20d"] = close.rolling(20).mean(); work["ma_100d"] = close.rolling(100).mean(); work["price_vs_ma20"] = close/work["ma_20d"]-1; work["price_vs_ma50"] = work["dist_50dma"]; work["price_vs_ma100"] = close/work["ma_100d"]-1; work["price_vs_ma200"] = work["dist_200dma"]
    work["ma20_vs_ma50"] = work["ma_20d"]/work["ma_50d"]-1; work["ma50_vs_ma200"] = work["ma_50d"]/work["ma_200d"]-1; work["ma200_slope_20d"] = work["ma_200d"]/work["ma_200d"].shift(20)-1; work["ma200_slope_60d"] = work["ma_200d"]/work["ma_200d"].shift(60)-1
    work["price_cross_ma50_10d"] = (((work["price_vs_ma50"]<0)&(work["price_vs_ma50"].shift(1)>=0))|((work["price_vs_ma50"]>0)&(work["price_vs_ma50"].shift(1)<=0))).rolling(10,min_periods=1).max().fillna(0).astype(bool)
    work["price_cross_ma200_20d"] = (((work["price_vs_ma200"]<0)&(work["price_vs_ma200"].shift(1)>=0))|((work["price_vs_ma200"]>0)&(work["price_vs_ma200"].shift(1)<=0))).rolling(20,min_periods=1).max().fillna(0).astype(bool)
    work["days_above_ma50"] = active_run_length(work["price_vs_ma50"]>0); work["days_below_ma200"] = active_run_length(work["price_vs_ma200"]<0); work["failed_reclaim_ma50"] = (high.rolling(10).max()>work["ma_50d"].rolling(10).max())&(close<work["ma_50d"]); work["failed_reclaim_ma200"] = (high.rolling(20).max()>work["ma_200d"].rolling(20).max())&(close<work["ma_200d"])
    work["qqq_dd_20d"] = close/close.rolling(20).max()-1; work["qqq_dd_60d"] = close/close.rolling(60).max()-1; work["qqq_dd_126d"] = work["dd_from_126d_high"]; work["qqq_dd_252d"] = work["dd_from_252d_high"]; work["dist_52w_high"] = work["dd_from_252d_high"]; work["dist_52w_low"] = close/close.rolling(252).min()-1; work["underwater_days_52w"] = active_run_length(work["dist_52w_high"] < -1e-10); work["drawdown_speed_20d"] = work["dist_52w_high"]-work["dist_52w_high"].shift(20); work["rebound_from_trough_20d"] = close/close.rolling(20).min()-1; work["lower_high_flag"] = close.rolling(20).max()<close.rolling(20).max().shift(20); work["lower_low_flag"] = close.rolling(20).min()<close.rolling(20).min().shift(20)
    r5 = high.rolling(5).max()/low.rolling(5).min()-1; r20 = high.rolling(20).max()/low.rolling(20).min()-1; r252 = high.rolling(252).max()/low.rolling(252).min()-1; work["range_5d_vs_252d"] = r5/r252.replace(0,np.nan); work["range_20d_vs_252d"] = r20/r252.replace(0,np.nan); work["high_low_range_1d"] = high/low-1
    tr = pd.concat([(high-low),(high-prev_close).abs(),(low-prev_close).abs()],axis=1).max(axis=1); work["atr_pct_14"] = tr.rolling(14).mean()/close; work["qqq_vol_10d"] = log_ret.rolling(10).std()*np.sqrt(252); work["qqq_vol_20d"] = log_ret.rolling(20).std()*np.sqrt(252); work["qqq_vol_60d"] = log_ret.rolling(60).std()*np.sqrt(252); work["vol_20d_vs_60d"] = work["qqq_vol_20d"]/work["qqq_vol_60d"].replace(0,np.nan); work["vol_20d_vs_252d"] = work["qqq_vol_20d"]/work["realized_vol_252d"].replace(0,np.nan)
    work["downside_vol_20d"] = log_ret.where(log_ret<0).rolling(20,min_periods=10).std()*np.sqrt(252); work["upside_vol_20d"] = log_ret.where(log_ret>0).rolling(20,min_periods=10).std()*np.sqrt(252); work["downside_upside_vol_ratio"] = work["downside_vol_20d"]/work["upside_vol_20d"].replace(0,np.nan); work["gap_down_count_20d"] = ((open_/prev_close-1)<-0.01).rolling(20).sum(); work["large_red_day_count_20d"] = ((close/open_-1)<-0.02).rolling(20).sum(); work["realized_skew_20d"] = simple_ret.rolling(20).skew(); work["realized_kurt_20d"] = simple_ret.rolling(20).kurt()
    for label,n in {"1w":5,"2w":10,"1m":20,"3m":60,"6m":126,"12m":252}.items(): work[f"qqq_ret_{label}"] = _ret(close,n)
    work["tsmom_1m_sign"] = np.sign(work["qqq_ret_1m"]); work["tsmom_3m_sign"] = np.sign(work["qqq_ret_3m"]); work["tsmom_6m_sign"] = np.sign(work["qqq_ret_6m"]); work["tsmom_12m_sign"] = np.sign(work["qqq_ret_12m"]); work["vol_adj_mom_60d"] = work["qqq_ret_3m"]/work["qqq_vol_60d"].replace(0,np.nan); work["vol_adj_mom_126d"] = work["qqq_ret_6m"]/work["realized_vol_63d"].replace(0,np.nan); work["mom_1m_minus_6m"] = work["qqq_ret_1m"]-work["qqq_ret_6m"]; work["reversal_5d_after_60d_runup"] = (work["qqq_ret_3m"].shift(5)>0.10)&(work["qqq_ret_1w"]<-0.03); work["rsi_14"] = _rsi(close,14); work["rsi_25"] = _rsi(close,25)
    ema12 = close.ewm(span=12, adjust=False).mean(); ema26 = close.ewm(span=26, adjust=False).mean(); macd = ema12-ema26; sig = macd.ewm(span=9, adjust=False).mean(); hist = macd-sig; work["macd_line"] = macd; work["macd_signal"] = sig; work["macd_hist"] = hist; work["macd_hist_change"] = hist.diff(5)
    work["qqq_equal_weight_rel"] = work["qqqe_close"]/work["qqq_close"]
    for label,n in [("1m",20),("3m",60),("6m",126)]:
        for out,b in [("spy","spy_close"),("qqqe","qqqe_close"),("rsp","rsp_close"),("iwm","iwm_close"),("soxx","soxx_close")]:
            if b in work: work[f"qqq_vs_{out}_{label}"] = _rel(work["qqq_close"], work[b], n)
    for prefix in ["dia","xlk","xlf","xli","xlv","xlp","xlu","xly","mtum","qual","soxx","smh","nvda","msft","aapl","arkk"]:
        col=f"{prefix}_close"
        if col in work:
            work[f"{prefix}_ret_1m"]=_ret(work[col],20); work[f"{prefix}_ret_3m"]=_ret(work[col],60); work[f"{prefix}_ret_6m"]=_ret(work[col],126)
    for out,a,b,n in [("qqq_vs_dia_3m","qqq_close","dia_close",60),("xlk_vs_spy_3m","xlk_close","spy_close",60),("xly_vs_xlp_3m","xly_close","xlp_close",60),("xlf_vs_spy_3m","xlf_close","spy_close",60),("xli_vs_spy_3m","xli_close","spy_close",60),("xlv_vs_spy_3m","xlv_close","spy_close",60),("xlp_vs_spy_3m","xlp_close","spy_close",60),("xlu_vs_spy_3m","xlu_close","spy_close",60),("mtum_vs_qual_3m","mtum_close","qual_close",60),("growth_vs_value_3m","qqq_close","rsp_close",60),("large_vs_small_3m","spy_close","iwm_close",60),("soxx_vs_spy_3m","soxx_close","spy_close",60),("smh_vs_qqq_3m","smh_close","qqq_close",60),("nvda_vs_qqq_3m","nvda_close","qqq_close",60),("msft_vs_qqq_3m","msft_close","qqq_close",60),("aapl_vs_qqq_3m","aapl_close","qqq_close",60)]:
        if a in work and b in work: work[out] = _rel(work[a], work[b], n)
    mag_cols=[f"{t}_close" for t in ["aapl","msft","nvda","amzn","googl","meta","tsla"] if f"{t}_close" in work]
    if mag_cols:
        norm=[work[c]/work[c].dropna().iloc[0] for c in mag_cols if not work[c].dropna().empty]
        if norm:
            mag7_eq=pd.concat(norm,axis=1).mean(axis=1); qqq_norm=work["qqq_close"]/work["qqq_close"].dropna().iloc[0]; work["mag7_equal_weight_vs_qqq"]=_rel(mag7_eq,qqq_norm,60); work["mag7_breadth"]=pd.concat([_ret(work[c],60)>0 for c in mag_cols],axis=1).mean(axis=1)
    work["semis_failure_flag"]=(work.get("soxx_ret_3m",np.nan)<0)&(work.get("qqq_ret_3m",np.nan)>0); work["qqq_up_soxx_down_20d"]=(work["qqq_ret_1m"]>0)&(work.get("soxx_ret_1m",np.nan)<0)
    _ensure(work,["advance_decline_line_20d","pct_above_20dma","pct_above_50dma","pct_above_200dma","new_highs_lows_20d","nasdaq_adv_dec_ratio"])
    dgs2=work.get("dgs2",pd.Series(index=work.index,dtype=float)); dfii10=work.get("dfii10",pd.Series(index=work.index,dtype=float)); work["ust2y_change_20d"]=dgs2-dgs2.shift(20); work["ust10y_change_20d"]=work["us10y_20d_change"]; work["real_yield_10y_change_20d"]=dfii10-dfii10.shift(20)
    if "tlt_close" in work: work["tlt_ret_20d"]=_ret(work["tlt_close"],20)
    if "ief_close" in work: work["ief_ret_20d"]=_ret(work["ief_close"],20)
    if "tlt_close" in work and "ief_close" in work: work["tlt_ief_rel_3m"]=_rel(work["tlt_close"],work["ief_close"],60)
    work["yield_curve_10y2y"]=work["us10y_yield"]-work.get("dgs2",np.nan); work["yield_curve_10y3m"]=work["us10y_yield"]-work.get("dgs3mo",np.nan); work["curve_steepening_20d"]=work["yield_curve_10y2y"]-work["yield_curve_10y2y"].shift(20); work["rate_vol_proxy"]=work.get("move_close",np.nan)
    if "dxy_close" in work: work["dxy_change_20d"]=_ret(work["dxy_close"],20)
    work["usd_yield_shock"]=(work.get("dxy_change_20d",np.nan)>0.02)&(work["ust10y_change_20d"]>0.25)
    work["hy_oas_level"]=work["credit_spread"]; work["hy_oas_change_20d"]=work["credit_spread_20d_change"]; work["ig_oas_level"]=work.get("ig_oas",np.nan); work["ig_oas_change_20d"]=work["ig_oas_level"]-work["ig_oas_level"].shift(20); work["hy_ig_spread"]=work["hy_oas_level"]-work["ig_oas_level"]
    if "hyg_close" in work: work["hyg_ret_20d"]=_ret(work["hyg_close"],20)
    if "lqd_close" in work: work["lqd_ret_20d"]=_ret(work["lqd_close"],20)
    if "hyg_close" in work and "lqd_close" in work: work["hyg_vs_lqd_20d"]=_rel(work["hyg_close"],work["lqd_close"],20)
    work["credit_spread_accel_20d"]=work["credit_spread_20d_change"]-work["credit_spread_20d_change"].shift(20); work["ted_spread_proxy"]=work.get("tedrate",np.nan); work["sofr_spread_proxy"]=work.get("sofr",np.nan)-work.get("fedfunds",np.nan); work["credit_not_confirming_equity"]=(work["qqq_ret_1m"]>0)&(work["credit_spread_20d_change"]>0); work["credit_worsening_equity_up"]=work["credit_not_confirming_equity"]
    work["vix_level"]=work["vix"]; work["vix_change_5d"]=work["vix"]-work["vix"].shift(5); work["vix_change_20d"]=work["vix"]-work["vix"].shift(20); work["vix_percentile_252d"]=rolling_percentile_of_last(work["vix"],window=252,min_periods=126); work["vix9d_vs_vix"]=work.get("vix9d_close",np.nan)-work["vix"]; work["vix3m_vs_vix"]=work.get("vix3m_close",np.nan)-work["vix"]; work["vol_term_inversion_flag"]=(work.get("vix9d_close",np.nan)>work["vix"])|(work["vix"]>work.get("vix3m_close",np.nan)); work["vvix_level"]=work.get("vvix_close",np.nan); work["skew_index"]=work.get("skew_close",np.nan); work["put_call_ratio"]=np.nan; work["qqq_iv_rv_spread"]=(work["vxn"]/100.0)-work["qqq_vol_20d"]; skew_pct=rolling_percentile_of_last(pd.to_numeric(work.get("skew_index",pd.Series(index=work.index,dtype=float)),errors="coerce"),window=252,min_periods=126); work["tail_hedge_demand_flag"]=skew_pct>0.80; work["panic_vol_flag"]=(work["vix"]>30)|(work["vix_percentile_252d"]>0.90); work["vol_crush_after_spike"]=(work["vix"].shift(10)>30)&(work["vix_change_5d"]<-5)
    cpi=work.get("cpi",pd.Series(index=work.index,dtype=float)); work["cpi_yoy"]=cpi/cpi.shift(252)-1; work["inflation_regime"]=np.where(work["cpi_yoy"]>0.03,1,np.where(work["cpi_yoy"].notna(),0,np.nan)); work["inflation_surprise"]=work["cpi_yoy"]-work["cpi_yoy"].shift(21); work["growth_regime"]=np.nan; work["unemployment_trend"]=work.get("unrate",np.nan)-work.get("unrate",np.nan).shift(63); work["claims_trend"]=work.get("claims",np.nan)/work.get("claims",np.nan).shift(63)-1; fed_chg_63=work.get("fedfunds",np.nan)-work.get("fedfunds",np.nan).shift(63); work["fed_policy_regime"]=np.select([fed_chg_63>0.25,fed_chg_63<-0.25],[1,-1],default=0); work["fed_surprise_30d"]=work.get("fedfunds",np.nan)-work.get("fedfunds",np.nan).shift(30); work["real_rate_regime"]=work.get("dfii10",np.nan); work["liquidity_regime"]=work.get("walcl",np.nan)/work.get("walcl",np.nan).shift(63)-1; work["financial_conditions_index"]=work.get("nfci",np.nan); work["earnings_revision_trend"]=np.nan; work["valuation_regime"]=np.nan; work["ai_capex_risk_proxy"]=np.nan; dxy_mom=work.get("dxy_close",pd.Series(index=work.index,dtype=float)).pct_change(20); work["macro_uncertainty_proxy"]=_z(work["vix"],252,126)+_z(dxy_mom,252,126)
    work["qqq_volume_z_20d"]=_z(volume,20,10); dollar_volume=volume*close; work["dollar_volume_z_20d"]=_z(dollar_volume,20,10); direction=np.sign(close.diff()).fillna(0); work["obv"]=(direction*volume.fillna(0)).cumsum(); work["obv_20d_chg"]=work["obv"]-work["obv"].shift(20); work["obv_60d_chg"]=work["obv"]-work["obv"].shift(60); up_vol=volume.where(simple_ret>0).rolling(20).sum(); down_vol=volume.where(simple_ret<0).rolling(20).sum(); work["up_down_volume_ratio_20d"]=up_vol/down_vol.replace(0,np.nan); work["volume_on_down_days"]=down_vol/volume.rolling(20).sum().replace(0,np.nan); work["volume_on_up_days"]=up_vol/volume.rolling(20).sum().replace(0,np.nan); work["etf_flow_qqq_20d"]=np.nan
    if "arkk_close" in work: work["arkk_vs_qqq_3m"]=_rel(work["arkk_close"],work["qqq_close"],60)
    work["margin_debt_change"]=np.nan; work["liquidity_drain_proxy"]=-(work.get("walcl",np.nan)/work.get("walcl",np.nan).shift(63)-1); work["market_depth_proxy"]=np.nan; work["amihud_illiquidity_proxy"]=(simple_ret.abs()/dollar_volume.replace(0,np.nan)).rolling(20).mean()
    return work

def add_feature_universe_post_signal_features(work, config):
    work=work.copy()
    if "MMDI" in work:
        work["mmdi_level"]=work["MMDI"]; work["mmdi_5d_change"]=work["MMDI"]-work["MMDI"].shift(5); work["mmdi_10d_change"]=work.get("MMDI_10D_CHANGE",work["MMDI"]-work["MMDI"].shift(10)); work["mmdi_20d_change"]=work["MMDI"]-work["MMDI"].shift(20); work["mmdi_percentile_252d"]=rolling_percentile_of_last(work["MMDI"],window=252,min_periods=126); work["mmdi_252d_high"]=work["MMDI"].rolling(252).max(); work["mmdi_falling_from_high"]=work["MMDI"]-work["mmdi_252d_high"]; work["mmdi_low_after_high"]=(work["mmdi_252d_high"]>=config["mmdi_high_threshold"])&(work["MMDI"]<config["mmdi_high_threshold"])
    return work

POS={"rally","surge","record","breakout","strong","optimism","beat","upbeat","growth","boom","rebound","recovery","bullish","soft landing","easing"}
NEG={"selloff","crash","plunge","drop","slump","fear","risk","warning","bubble","recession","default","stress","panic","hawkish","tightening","correction"}
RISK={"crash","selloff","correction","recession","default","credit","spread","funding","volatility","risk","liquidity","bubble","overvalued","geopolitical","tariff"}
EUP={"ai","record","mania","boom","surge","melt-up","euphoria","fomo"}; AI={"ai","artificial intelligence","chip","chips","semiconductor","gpu","nvidia","data center"}; REC={"recession","slowdown","unemployment","claims","layoffs","hard landing"}
FEEDS=["QQQ OR Nasdaq 100 stocks","Nasdaq AI stocks market","Federal Reserve rates stock market","credit spreads funding stress stock market","semiconductor stocks AI chips Nasdaq"]

def _count(text, terms):
    low=text.lower(); n=0
    for t in terms: n += low.count(t) if " " in t else len(re.findall(rf"\b{re.escape(t)}\b",low))
    return n

def _score(text):
    clean=html.unescape(re.sub(r"<[^>]+>"," ",text or "")); pos=_count(clean,POS); neg=_count(clean,NEG); denom=max(1,pos+neg)
    return {"positive_terms":pos,"negative_terms":neg,"risk_terms":_count(clean,RISK),"euphoria_terms":_count(clean,EUP),"ai_terms":_count(clean,AI),"recession_terms":_count(clean,REC),"headline_sentiment_score":(pos-neg)/denom,"headline_risk_score":_count(clean,RISK),"headline_euphoria_score":_count(clean,EUP),"headline_ai_score":_count(clean,AI),"headline_recession_score":_count(clean,REC)}

def _rss_url(q): return "https://news.google.com/rss/search?q="+urllib.parse.quote_plus(q)+"&hl=en-US&gl=US&ceid=US:en"

def fetch_sentiment_headlines(timeout=10):
    rows=[]; headers={"User-Agent":"Mozilla/5.0 qqq-risk-monitor-local"}
    for q in FEEDS:
        url=_rss_url(q)
        try:
            resp=requests.get(url,headers=headers,timeout=timeout); resp.raise_for_status(); root=ET.fromstring(resp.content)
            for item in root.findall(".//item")[:20]:
                title=item.findtext("title") or ""; desc=item.findtext("description") or ""; rows.append({"source":"Google News","query":q,"published":item.findtext("pubDate") or "","title":html.unescape(re.sub(r"<[^>]+>"," ",title)).strip(),"link":item.findtext("link") or "",**_score(title+" "+desc)})
        except Exception as e:
            rows.append({"source":"Google News","query":q,"published":"","title":f"RSS fetch failed: {e}","link":url,"headline_sentiment_score":np.nan,"headline_risk_score":np.nan,"headline_euphoria_score":np.nan,"headline_ai_score":np.nan,"headline_recession_score":np.nan})
    return pd.DataFrame(rows)

def sentiment_summary(items):
    valid=items.dropna(subset=["headline_sentiment_score"]) if items is not None and not items.empty and "headline_sentiment_score" in items else pd.DataFrame(); n=len(valid)
    return pd.DataFrame([{"as_of_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"headline_count":n,"headline_sentiment_score":valid["headline_sentiment_score"].mean() if n else np.nan,"headline_risk_score":valid["headline_risk_score"].mean() if n else np.nan,"headline_euphoria_score":valid["headline_euphoria_score"].mean() if n else np.nan,"headline_ai_score":valid["headline_ai_score"].mean() if n else np.nan,"headline_recession_score":valid["headline_recession_score"].mean() if n else np.nan,"headline_negative_share":(valid["headline_sentiment_score"]<0).mean() if n else np.nan,"headline_positive_share":(valid["headline_sentiment_score"]>0).mean() if n else np.nan,"important_caveat":"Live RSS headline semantics only; not historical/backtest-ready unless snapshots are archived point-in-time."}])

def build_feature_catalog(work=None):
    rows=[]
    for fam, cols in FEATURE_FAMILIES.items():
        for f in cols:
            cnt=int(work[f].notna().sum()) if work is not None and f in work.columns else 0; status="available" if cnt else ("placeholder" if work is not None and f in getattr(work,'columns',[]) else "missing")
            rows.append({"family":fam,"feature":f,"status":status,"latest_available":bool(cnt),"non_null_count":cnt,"source_note":"Live RSS headline snapshot; not historical/backtest-ready unless archived point-in-time." if fam.startswith("M.") else ("Placeholder: requires additional point-in-time data source." if status!="available" else "Public market/FRED/Yahoo-derived feature.")})
    return pd.DataFrame(rows)

def latest_feature_snapshot(work, max_rows=180):
    latest=work.dropna(subset=["qqq_close"]).iloc[-1]; cat=build_feature_catalog(work); rows=[]
    for _,r in cat.iterrows(): rows.append({"family":r["family"],"feature":r["feature"],"latest_value":latest.get(r["feature"],pd.NA),"status":r["status"],"source_note":r["source_note"]})
    return pd.DataFrame(rows).head(max_rows)

def _style(df): return df.to_html(index=False,border=0,classes="dataframe dashboard-table",na_rep="N/A",escape=True)

def write_feature_universe_outputs(work, output_dir, config, html_path=None):
    output_dir=Path(output_dir); output_dir.mkdir(parents=True,exist_ok=True); prefix=config["export_prefix"]
    items=fetch_sentiment_headlines(); artifacts={"feature_catalog":build_feature_catalog(work),"feature_snapshot":latest_feature_snapshot(work, config.get("feature_snapshot_top_n",180)),"sentiment_summary":sentiment_summary(items),"sentiment_headlines":items}
    for key,fn in {"feature_catalog":f"{prefix}_feature_catalog.csv","feature_snapshot":f"{prefix}_feature_snapshot_latest.csv","sentiment_summary":f"{prefix}_sentiment_summary.csv","sentiment_headlines":f"{prefix}_sentiment_headlines.csv"}.items(): artifacts[key].to_csv(output_dir/fn,index=False)
    if html_path is not None and Path(html_path).exists():
        doc=Path(html_path).read_text(encoding="utf-8"); sections=[("Feature Universe Catalog",artifacts["feature_catalog"]),("Latest Feature Snapshot",artifacts["feature_snapshot"]),("Mainstream Narrative / Semantic Summary",artifacts["sentiment_summary"]),("Mainstream Narrative / Semantic Headlines",artifacts["sentiment_headlines"].head(50))]
        block="<section><h2>v2 Feature Universe Notes</h2><p class='note'>The expanded feature universe is exported for future research and Autoresearch/Codex experiments. It does not change the current v1.3.1 R2 × MMDI dashboard signal yet.</p><p class='note'>Mainstream narrative / semantic features are a live RSS headline snapshot. They are not historical/backtest-ready unless snapshots are archived point-in-time.</p></section>"+"\n".join([f"<section><h2>{html.escape(n)}</h2>{_style(df)}</section>" for n,df in sections])
        doc=doc.replace("</body>",block+"\n</body>") if "</body>" in doc else doc+block; Path(html_path).write_text(doc,encoding="utf-8")
    return artifacts
