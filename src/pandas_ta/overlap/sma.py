# -*- coding: utf-8 -*-
from numpy import convolve, ones
from numba import njit
from pandas import Series
from pandas_ta._typing import Array, DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.utils import (
    nb_prepend,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)



# Fast SMA Options: https://github.com/numba/numba/issues/4119
@njit(cache=True)
def nb_sma(x, n):
    result = convolve(ones(n) / n, x)[n - 1:1 - n]
    return nb_prepend(result, n - 1)


def sma(
    close: Series, length: Int = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Simple Moving Average

    This indicator is the the textbook moving average, a rolling sum of
    values divided by the window period (or length).

    Sources:
        * [tradingtechnologies](https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/simple-moving-average-sma/)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        adjust (bool): Adjust the values. Default: ```True```
        presma (bool): If True, uses SMA for initial value.
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 10)
    if "min_periods" in kwargs and kwargs["min_periods"] is not None:
        min_periods = int(kwargs["min_periods"])
    else:
        min_periods = length
    close = v_series(close, max(length, min_periods))

    if close is None:
        return

    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal and length > 1:
        from talib import SMA
        sma = SMA(close, length)
    else:
        np_close = close.to_numpy()
        sma = nb_sma(np_close, length)
        sma = Series(sma, index=close.index)

    # Offset
    if offset != 0:
        sma = sma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        sma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    sma.name = f"SMA_{length}"
    sma.category = "overlap"

    return sma
