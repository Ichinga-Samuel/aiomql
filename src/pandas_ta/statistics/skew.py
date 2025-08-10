# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_offset, v_pos_default, v_series



def skew(
    close: Series, length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Rolling Skew

    Calculates a rolling Skew.

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```30```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Danger:
        Possible Data Leak
    """
    # Validate
    length = v_pos_default(length, 30)
    if "min_periods" in kwargs and kwargs["min_periods"] is not None:
        min_periods = int(kwargs["min_periods"])
    else:
        min_periods = length
    close = v_series(close, max(length, min_periods))

    if close is None:
        return

    offset = v_offset(offset)

    # Calculate
    skew = close.rolling(length, min_periods=min_periods).skew()

    # Offset
    if offset != 0:
        skew = skew.shift(offset)

    # Fill
    if "fillna" in kwargs:
        skew.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    skew.name = f"SKEW_{length}"
    skew.category = "statistics"

    return skew
