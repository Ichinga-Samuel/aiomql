# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.maps import Imports
from pandas_ta.utils import (
    non_zero_range,
    v_offset,
    v_scalar,
    v_series,
    v_talib
)



def bop(
    open_: Series, high: Series, low: Series, close: Series,
    scalar: IntFloat = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Balance of Power

    This indicator attempts to quantify the market strength of buyers
    versus sellers.

    Sources:
        * [worden](http://www.worden.com/TeleChartHelp/Content/Indicators/Balance_of_Power.htm)

    Parameters:
        open_ (pd.Series): ```open``` Series
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        scalar (float): Scalar. Default: ```1```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    open_ = v_series(open_)
    high = v_series(high)
    low = v_series(low)
    close = v_series(close)
    scalar = v_scalar(scalar, 1)
    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal and close.size:
        from talib import BOP
        bop = BOP(open_, high, low, close)
    else:
        high_low_range = non_zero_range(high, low)
        close_open_range = non_zero_range(close, open_)
        bop = scalar * close_open_range / high_low_range

    # Offset
    if offset != 0:
        bop = bop.shift(offset)

    # Fill
    if "fillna" in kwargs:
        bop.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    bop.name = f"BOP"
    bop.category = "momentum"

    return bop
