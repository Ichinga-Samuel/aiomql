# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.utils import v_offset, v_series, v_talib



def wcp(
    high: Series, low: Series, close: Series, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Weighted Closing Price

    This indicator is a weighted value of: high, low and twice the close.

    Sources:
        * [fmlabs](https://www.fmlabs.com/reference/default.htm?url=WeightedCloses.htm)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    _length = 1
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import WCLPRICE
        wcp = WCLPRICE(high, low, close)
    else:
        weight = high.to_numpy() + low.to_numpy() + 2 * close.to_numpy()
        wcp = Series(weight, index=close.index)

    # Offset
    if offset != 0:
        wcp = wcp.shift(offset)

    # Fill
    if "fillna" in kwargs:
        wcp.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    wcp.name = "WCP"
    wcp.category = "overlap"

    return wcp
