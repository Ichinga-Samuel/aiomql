# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.ma import ma
from pandas_ta.maps import Imports
from pandas_ta.utils import (
    non_zero_range,
    tal_ma,
    v_mamode,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)



def stoch(
    high: Series, low: Series, close: Series,
    k: Int = None, d: Int = None, smooth_k: Int = None,
    mamode: str = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Stochastic

    This indicator, by George Lane in the 1950's, attempts to identify and
    quantify momentum; it assumes that momentum precedes value change.

    Sources:
        * [sierrachart](https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=332&Name=KD_-_Slow)
        * [tradingview](https://www.tradingview.com/wiki/Stochastic_(STOCH))

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        k (int): The Fast %K period. Default: ```14```
        d (int): The Slow %D period. Default: ```3```
        smooth_k (int): The Slow %K period. Default: ```3```
        mamode (str): See ```help(ta.ma)```. Default: ```"sma"```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 3 columns
    """
    # Validate
    k = v_pos_default(k, 14)
    d = v_pos_default(d, 3)
    smooth_k = v_pos_default(smooth_k, 3)
    _length = k + d + smooth_k
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    mode_tal = v_talib(talib)
    mamode = v_mamode(mamode, "sma")
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal and smooth_k > 2:
        from talib import STOCH
        stoch_ = STOCH(
            high, low, close, k, d, tal_ma(mamode), d, tal_ma(mamode)
        )
        stoch_k, stoch_d = stoch_[0], stoch_[1]
    else:
        ll = low.rolling(k).min()
        hh = high.rolling(k).max()

        stoch = 100 * (close - ll) / non_zero_range(hh, ll)

        if stoch is None: return

        stoch_fvi = stoch.loc[stoch.first_valid_index():, ]
        if smooth_k == 1:
            stoch_k = stoch
        else:
            stoch_k = ma(mamode, stoch_fvi, length=smooth_k)

        stochk_fvi = stoch_k.loc[stoch_k.first_valid_index():, ]
        stoch_d = ma(mamode, stochk_fvi, length=d)

    stoch_h = stoch_k - stoch_d  # Histogram

    # Offset
    if offset != 0:
        stoch_k = stoch_k.shift(offset)
        stoch_d = stoch_d.shift(offset)
        stoch_h = stoch_h.shift(offset)

    # Fill
    if "fillna" in kwargs:
        stoch_k.fillna(kwargs["fillna"], inplace=True)
        stoch_d.fillna(kwargs["fillna"], inplace=True)
        stoch_h.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _name = "STOCH"
    _props = f"_{k}_{d}_{smooth_k}"
    stoch_k.name = f"{_name}k{_props}"
    stoch_d.name = f"{_name}d{_props}"
    stoch_h.name = f"{_name}h{_props}"
    stoch_k.category = stoch_d.category = stoch_h.category = "momentum"

    data = {
        stoch_k.name: stoch_k,
        stoch_d.name: stoch_d,
        stoch_h.name: stoch_h
    }
    df = DataFrame(data, index=close.index)
    df.name = f"{_name}{_props}"
    df.category = stoch_k.category

    return df
