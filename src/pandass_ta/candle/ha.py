# -*- coding: utf-8 -*-
from numpy import empty_like, maximum, minimum
from numba import njit
from pandas import DataFrame, Series
from pandas_ta._typing import Array, DictLike, Int
from pandas_ta.utils import v_offset, v_series



@njit(cache=True)
def np_ha(np_open, np_high, np_low, np_close):
    ha_close = 0.25 * (np_open + np_high + np_low + np_close)
    ha_open = empty_like(ha_close)
    ha_open[0] = 0.5 * (np_open[0] + np_close[0])

    m = np_close.size
    for i in range(1, m):
        ha_open[i] = 0.5 * (ha_open[i - 1] + ha_close[i - 1])

    ha_high = maximum(maximum(ha_open, ha_close), np_high)
    ha_low = minimum(minimum(ha_open, ha_close), np_low)

    return ha_open, ha_high, ha_low, ha_close


def ha(
    open_: Series, high: Series, low: Series, close: Series,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Heikin Ashi Candles

    Creates Japanese _ohlc_ candlesticks that attempts to filter out market
    noise. Developed by Munehisa Homma in the 1700s, Heikin Ashi Candles share
    some characteristics with standard candlestick charts but creates a
    smoother candlestick appearance.

    Sources:
        * [Investopedia](https://www.investopedia.com/terms/h/heikinashi.asp)

    Parameters:
        open_ (pd.Series): ```open``` Series
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): Replaces ```na```'s with ```value```.

    Returns:
        (pd.DataFrame): 4 columns
    """
    # Validate
    open_ = v_series(open_, 1)
    high = v_series(high, 1)
    low = v_series(low, 1)
    close = v_series(close, 1)
    offset = v_offset(offset)

    if open_ is None or high is None or low is None or close is None:
        return

    # Calculate
    np_open, np_high = open_.to_numpy(), high.to_numpy()
    np_low, np_close = low.to_numpy(), close.to_numpy()
    ha_open, ha_high, ha_low, ha_close = np_ha(np_open, np_high, np_low, np_close)
    df = DataFrame({
        "HA_open": ha_open,
        "HA_high": ha_high,
        "HA_low": ha_low,
        "HA_close": ha_close,
    }, index=close.index)

    # Offset
    if offset != 0:
        df = df.shift(offset)

    # Fill
    if "fillna" in kwargs:
        df.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    df.name = "Heikin-Ashi"
    df.category = "candle"

    return df
