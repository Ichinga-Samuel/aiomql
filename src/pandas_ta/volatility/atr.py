# -*- coding: utf-8 -*-
from numpy import isnan, nan
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.ma import ma
from pandas_ta.maps import Imports
from pandas_ta.utils import (
    v_bool,
    v_drift,
    v_mamode,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)
from .true_range import true_range



def atr(
    high: Series, low: Series, close: Series, length: Int = None,
    mamode: str = None, talib: bool = None,
    prenan: bool = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Average True Range

    This indicator attempts to quantify volatility with a focus on gaps or
    limit moves.

    Sources:
        * [tradingview](https://www.tradingview.com/wiki/Average_True_Range_(ATR))

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```14```
        mamode (str): See ```help(ta.ma)```. Default: ```"rma"```
        talib (bool): If installed, use TA Lib. Default: ```True```
        prenan (bool): Sets initial values to ```np.nan``` based
            on ```drift```. Default: ```False```
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
    _length = length + 1
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    mamode = v_mamode(mamode, "rma")
    mode_tal = v_talib(talib)
    prenan = v_bool(prenan, False)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import ATR
        atr = ATR(high, low, close, length)
    else:
        tr = true_range(
            high=high, low=low, close=close,
            talib=mode_tal, prenan=prenan, drift=drift
        )
        if all(isnan(tr)):
            return  # Emergency Break

        presma = kwargs.pop("presma", True)
        if presma:
            sma_nth = tr[0:length].mean()
            tr[:length - 1] = nan
            tr.iloc[length - 1] = sma_nth
        atr = ma(mamode, tr, length=length, talib=mode_tal)

    if all(isnan(atr)):
        return  # Emergency Break

    percent = kwargs.pop("percent", False)
    if percent:
        atr *= 100 / close

    # Offset
    if offset != 0:
        atr = atr.shift(offset)

    # Fill
    if "fillna" in kwargs:
        atr.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    atr.name = f"ATR{mamode[0]}{'p' if percent else ''}_{length}"
    atr.category = "volatility"

    return atr
