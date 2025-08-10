# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta.utils._core import non_zero_range

__all__ = ["candle_color", "high_low_range", "real_body"]



def candle_color(open_: Series, close: Series) -> Series:
    """Candle Change

    Checks if ```close >= open_```, if so it returns  ```1``` or ```-1```.

    Parameters:
        open_ (pd.Series): ```open``` Series
        close (pd.Series): ```close``` Series

    Returns:
        (pd.Series): 1 column
    """
    color = close.copy().astype(int)
    color[close >= open_] = 1
    color[close < open_] = -1
    return color


def high_low_range(high: Series, low: Series) -> Series:
    """High Low Range

    Calculates the difference between ```high`` and ```low```.

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series

    Returns:
        (pd.Series): 1 column
    """
    return non_zero_range(high, low)


def real_body(open_: Series, close: Series) -> Series:
    """Body Range

    Calculates the difference between ```close`` and ```open_```.

    Parameters:
        open_ (pd.Series): ```open``` Series
        close (pd.Series): ```close``` Series

    Returns:
        (pd.Series): 1 column
    """
    return non_zero_range(close, open_)
