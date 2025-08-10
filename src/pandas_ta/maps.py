# -*- coding: utf-8 -*-
from importlib.util import find_spec
from pandas_ta._typing import Dict, IntFloat, ListStr


Imports: Dict[str, bool] = {
    "talib": find_spec("talib") is not None,
    "vectorbt": find_spec("vectorbt") is not None,
    "yfinance": find_spec("yfinance") is not None,
}


# Not ideal and not dynamic but it works.
# TODO: find a dynamic solution later.
Category: Dict[str, ListStr] = {
    "candle": [
        "cdl_pattern", "cdl_z", "ha"
    ],
    "cycle": ["ebsw", "reflex"],
    "momentum": [
        "ao", "apo", "bias", "bop", "brar", "cci", "cfo", "cg", "cmo",
        "coppock", "crsi", "cti", "er", "eri", "exhc", "fisher",
        "inertia", "kdj", "kst", "macd", "mom", "pgo", "ppo", "psl", "qqe",
        "roc", "rsi", "rsx", "rvgi", "slope", "smc", "smi", "squeeze",
        "squeeze_pro", "stc", "stoch", "stochf", "stochrsi", "tmo", "trix",
        "tsi", "uo", "willr"
    ],
    "overlap": [
        "alligator", "alma", "dema", "ema", "fwma", "hilo", "hl2", "hlc3",
        "hma", "hwma", "ichimoku", "jma", "kama", "linreg", "mama",
        "mcgd", "midpoint", "midprice", "ohlc4", "pivots", "pwma", "rma",
        "sinwma", "sma", "smma", "ssf", "ssf3", "supertrend", "swma", "t3",
        "tema", "trima", "vidya", "wcp", "wma", "zlma"
    ],
    "performance": ["log_return", "percent_return"],
    "statistics": [
        "entropy", "kurtosis", "mad", "median", "quantile", "skew", "stdev",
        "tos_stdevall", "variance", "zscore"
    ],
    "trend": [
        "adx", "alphatrend", "amat", "aroon", "chop", "cksp", "decay",
        "decreasing", "dpo", "ht_trendline", "increasing",
        "long_run", "psar", "qstick", "rwi", "short_run", "trendflex",
        "vhf", "vortex", "zigzag"
    ],
    "volatility": [
        "aberration", "accbands", "atr", "atrts", "bbands", "chandelier_exit",
        "donchian", "hwc", "kc", "massi", "natr", "pdist", "rvi", "thermo",
        "true_range", "ui"
    ],
    # Note: "vp" or "Volume Profile" is excluded since it does not
    # return a Time Series
    "volume": [
        "ad", "adosc", "aobv", "cmf", "efi", "eom", "kvo", "mfi", "nvi",
        "obv", "pvi", "pvo", "pvol", "pvr", "pvt", "tsv", "vhm", "vwap",
        "vwma"
    ],
}


CANDLE_AGG: Dict[str, str] = {
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum"
}


# https://www.worldtimezone.com/markets24.php
EXCHANGE_TZ: Dict[str, IntFloat] = {
    "NZSX": 12, "ASX": 11,
    "TSE": 9, "HKE": 8, "SSE": 8, "SGX": 8,
    "NSE": 5.5, "DIFX": 4, "RTS": 3,
    "JSE": 2, "FWB": 1, "LSE": 1,
    "BMF": -2, "NYSE": -4, "TSX": -4,
    "GENR": 0 # Generated Data
}


RATE: Dict[str, IntFloat] = {
    "DAYS_PER_MONTH": 21,
    "MINUTES_PER_HOUR": 60,
    "MONTHS_PER_YEAR": 12,
    "QUARTERS_PER_YEAR": 4,
    "TRADING_DAYS_PER_YEAR": 252,  # Keep even
    "TRADING_HOURS_PER_DAY": 6.5,
    "WEEKS_PER_YEAR": 52,
    "YEARLY": 1,
}
