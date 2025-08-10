# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.utils import v_offset, v_series, v_talib



def hlc3(
    high: Series, low: Series, close: Series, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """HLC3

    HLC3 is the average of high, low and close.

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```.
            Only works when offset.

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    high = v_series(high)
    low = v_series(low)
    close = v_series(close)
    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    if high is None or low is None or close is None:
        return

    # Calculate
    if Imports["talib"] and mode_tal and close.size:
        from talib import TYPPRICE
        hlc3 = TYPPRICE(high, low, close)
    else:
        avg = (high.to_numpy() + low.to_numpy() + close.to_numpy()) / 3.0
        hlc3 = Series(avg, index=close.index)

    # Offset
    if offset != 0:
        hlc3 = hlc3.shift(offset)

        # Fill
        if "fillna" in kwargs:
            hlc3.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    hlc3.name = "HLC3"
    hlc3.category = "overlap"

    return hlc3
