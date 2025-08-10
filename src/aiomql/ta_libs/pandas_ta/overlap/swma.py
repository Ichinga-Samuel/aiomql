# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import (
    symmetric_triangle,
    v_offset,
    v_pos_default,
    v_series,
    weights
)



def swma(
    close: Series, length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Symmetric Weighted Moving Average

    This indicator is based on a Symmetric Weighted Moving Average where
    weights are based on a symmetric triangle.

    Source:
        * [tradingview](https://www.tradingview.com/study-script-reference/#fun_swma)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Note:
        * ```n=3``` -> ```[1, 2, 1]```
        * ```n=4``` -> ```[1, 2, 2, 1]```
        * etc...
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, length)

    if close is None:
        return

    offset = v_offset(offset)

    # Calculate
    triangle = symmetric_triangle(length, weighted=True)
    swma = close.rolling(length, min_periods=length) \
        .apply(weights(triangle), raw=True)

    # Offset
    if offset != 0:
        swma = swma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        swma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    swma.name = f"SWMA_{length}"
    swma.category = "overlap"

    return swma
