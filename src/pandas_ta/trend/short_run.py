# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_offset, v_pos_default, v_series
from .decreasing import decreasing
from .increasing import increasing



def short_run(
    fast: Series, slow: Series, length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Short Run

    This indicator, by Kevin Johnson, attempts to identify short runs.

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
    dec = decreasing(fast, length)

    # potential top or top
    pt = dec & increasing(slow, length)
    # fast and slow are decreasing
    bd = dec & decreasing(slow, length)
    short_run = pt | bd

    # Offset
    if offset != 0:
        short_run = short_run.shift(offset)

    # Fill
    if "fillna" in kwargs:
        short_run.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    short_run.name = f"SR_{length}"
    short_run.category = "trend"

    return short_run
