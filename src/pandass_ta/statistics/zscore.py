# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.overlap import sma
from pandas_ta.statistics import stdev
from pandas_ta.utils import v_lowerbound, v_offset, v_series



def zscore(
    close: Series, length: Int = None, std: IntFloat = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Rolling Z Score

    Calculates a rolling Z Score.

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```30```
        std (float): Number of deviation standards. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_lowerbound(length, 1, 30)
    close = v_series(close, length)

    if close is None:
        return

    std = v_lowerbound(std, 1, 1.0)
    offset = v_offset(offset)

    # Calculate
    std *= stdev(close=close, length=length, **kwargs)
    mean = sma(close=close, length=length, **kwargs)
    zscore = (close - mean) / std

    # Offset
    if offset != 0:
        zscore = zscore.shift(offset)

    # Fill
    if "fillna" in kwargs:
        zscore.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    zscore.name = f"ZS_{length}"
    zscore.category = "statistics"

    return zscore
