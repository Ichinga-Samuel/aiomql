# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_offset, v_series



def hl2(
    high: Series, low: Series,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """HL2

    HL2 is the midpoint/average of high and low.

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```.
            Only works when offset.

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    high = v_series(high)
    low = v_series(low)
    offset = v_offset(offset)

    if high is None or low is None:
        return

    # Calculate
    avg = 0.5 * (high.to_numpy() + low.to_numpy())
    hl2 = Series(avg, index=high.index)

    # Offset
    if offset != 0:
        hl2 = hl2.shift(offset)

        # Fill
        if "fillna" in kwargs:
            hl2.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    hl2.name = "HL2"
    hl2.category = "overlap"

    return hl2
