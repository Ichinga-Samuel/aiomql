# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.utils import v_offset, v_pos_default, v_series, v_talib



def willr(
    high: Series, low: Series, close: Series,
    length: Int = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """William's Percent R

    This indicator attempts to identify "overbought" and "oversold"
    conditions similar to the RSI.

    Sources:
        * [tradingview](https://www.tradingview.com/wiki/Williams_%25R_(%25R))

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```14```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 14)
    if "min_periods" in kwargs and kwargs["min_periods"] is not None:
        min_periods = int(kwargs["min_periods"])
    else:
        min_periods = length
    _length = max(length, min_periods)
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import WILLR
        willr = WILLR(high, low, close, length)
    else:
        lowest_low = low.rolling(length, min_periods=min_periods).min()
        highest_high = high.rolling(length, min_periods=min_periods).max()

        willr = 100 * ((close - lowest_low) / (highest_high - lowest_low) - 1)

    # Offset
    if offset != 0:
        willr = willr.shift(offset)

    # Fill
    if "fillna" in kwargs:
        willr.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    willr.name = f"WILLR_{length}"
    willr.category = "momentum"

    return willr
