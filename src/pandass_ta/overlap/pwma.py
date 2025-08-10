# -*- coding: utf-8 -*-
# from numpy.version import version as np_version
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import (
    pascals_triangle,
    v_offset,
    v_ascending,
    v_pos_default,
    v_series,
    weights
)



def pwma(
    close: Series, length: Int = None, asc: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Pascal's Weighted Moving Average

    This indicator, by Kevin Johnson, creates a weighted moving average using
    Pascal's Triangle.

    Sources:
        * Kevin Johnson

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        asc (bool): Ascending. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 1 column
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, length)

    if close is None:
        return

    asc = v_ascending(asc)
    offset = v_offset(offset)

    # Calculate
    triangle = pascals_triangle(n=length - 1, weighted=True)
    pwma = close.rolling(length, min_periods=length) \
        .apply(weights(triangle), raw=True)

    # Offset
    if offset != 0:
        pwma = pwma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        pwma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    pwma.name = f"PWMA_{length}"
    pwma.category = "overlap"

    return pwma
