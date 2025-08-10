# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_offset, v_pos_default, v_series
from .decreasing import decreasing
from .increasing import increasing



def long_run(
    fast: Series, slow: Series, length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Long Run

    This indicator, by Kevin Johnson, attempts to identify long runs.

    Sources:
        * Kevin Johnson
        * [tradingview](https://www.tradingview.com/script/Z2mq63fE-Trade-Archer-Moving-Averages-v1-4F/)

    Parameters:
        fast (pd.Series): ```fast``` Series.
        slow (pd.Series): ```slow``` Series.
        length (int): The ```decreasing``` and ```increasing``` period.
            Default: ```2```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 2)
    fast = v_series(fast, length)
    slow = v_series(slow, length)

    if fast is None or slow is None:
        return

    offset = v_offset(offset)

    # Calculate
    inc = increasing(fast, length)

    # potential bottom or bottom
    pb = inc & decreasing(slow, length)
    # fast and slow are increasing
    bi = inc & increasing(slow, length)
    long_run = pb | bi

    # Offset
    if offset != 0:
        long_run = long_run.shift(offset)

    # Fill
    if "fillna" in kwargs:
        long_run.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    long_run.name = f"LR_{length}"
    long_run.category = "trend"

    return long_run
