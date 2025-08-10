# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import (
    fibonacci,
    v_ascending,
    v_offset,
    v_pos_default,
    v_series,
    weights
)



def fwma(
    close: Series, length: Int = None, asc: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Fibonacci's Weighted Moving Average

    This indicator, by Kevin Johnson, is similar to a Weighted Moving Average
    (WMA) where the weights are based on the Fibonacci Sequence.

    Sources:
        * Kevin Johnson

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        asc (bool): Recent values weigh more. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, length)

    if close is None:
        return

    asc = v_ascending(asc)
    offset = v_offset(offset)

    # Calculate
    fibs = fibonacci(n=length, weighted=True)
    fwma = close.rolling(length, min_periods=length) \
        .apply(weights(fibs), raw=True)

    # Offset
    if offset != 0:
        fwma = fwma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        fwma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    fwma.name = f"FWMA_{length}"
    fwma.category = "overlap"

    return fwma
