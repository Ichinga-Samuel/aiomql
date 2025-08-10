# -*- coding: utf-8 -*-
from numpy import isnan, nan, uintc, zeros_like
from numba import njit
from pandas import Series
from pandas_ta._typing import Array, DictLike, Int, IntFloat
from pandas_ta.ma import ma as _ma
from pandas_ta.maps import Imports
from pandas_ta.utils import (
    v_drift,
    v_mamode,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)
from pandas_ta.volatility import atr



@njit(cache=True)
def nb_atrts(x, ma, atr_, length, ma_length):
    m = x.size
    k = max(length, ma_length)

    result = x.copy()
    up = zeros_like(x, dtype=uintc)
    dn = zeros_like(x, dtype=uintc)

    expn = x > ma
    up[expn], dn[~expn] = 1, 1
    up[:k], dn[:k] = 0, 0
    result[:k] = nan

    for i in range(k, m):
        pr = result[i - 1]
        if up[i]:
            result[i] = x[i] - atr_[i]
            if result[i] < pr:
                result[i] = pr
        if dn[i]:
            result[i] = x[i] + atr_[i]
            if result[i] > pr:
                result[i] = pr

    long, short = result * up, result * dn
    long[long == 0], short[short == 0] = nan, nan

    return result, long, short


def atrts(
    high: Series, low: Series, close: Series, length: Int = None,
    ma_length: Int = None, k: IntFloat = None,
    mamode: str = None, talib: bool = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """ATR Trailing Stop

    This indicator attempts to identify exits for long and short positions.
    To determine trend, it uses a moving average with a scalable ATR.

    Sources:
        * [motivewave](https://www.motivewave.com/studies/atr_trailing_stops.htm)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```14```
        ma_length (int): MA Length. Default: ```20```
        k (int): ATR multiplier. Default: ```3```
        mamode (str): See ```help(ta.ma)```. Default: ```"ema"```
        talib (bool): If installed, use TA Lib. Default: ```True```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        percent (bool): Return as percent. Default: ```False```
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 14)
    ma_length = v_pos_default(ma_length, 20)
    _length = length + ma_length
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    k = v_pos_default(k, 3.0)
    mamode = v_mamode(mamode, "ema")
    mode_tal = v_talib(talib)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import ATR
        atr_ = ATR(high, low, close, length)
    else:
        atr_ = atr(
            high=high, low=low, close=close, length=length,
            mamode=mamode, drift=drift, talib=mode_tal,
            offset=offset, **kwargs
        )

    if all(isnan(atr_)):
        return  # Emergency Break

    atr_ *= k
    ma_ = _ma(mamode, close, length=ma_length, talib=mode_tal)

    np_close, np_ma, np_atr = close.to_numpy(), ma_.to_numpy(), atr_.to_numpy()
    np_atrts_, _, _ = nb_atrts(np_close, np_ma, np_atr, length, ma_length)

    percent = kwargs.pop("percent", False)
    if percent:
        np_atrts_ *= 100 / np_close

    atrts = Series(np_atrts_, index=close.index)

    # Offset
    if offset != 0:
        atrts = atrts.shift(offset)

    # Fill
    if "fillna" in kwargs:
        atrts.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"ATRTS{mamode[0]}{'p' if percent else ''}"
    atrts.name = f"{_props}_{length}_{ma_length}_{k}"
    atrts.category = "volatility"

    return atrts
