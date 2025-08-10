# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.overlap import sma
from pandas_ta.utils import v_offset, v_pos_default, v_series



def vwma(
    close: Series, volume: Series, length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Volume Weighted Moving Average

    Computes a weighted average using price and volume.

    Sources:
        * [motivewave](https://www.motivewave.com/studies/volume_weighted_moving_average.htm)

    Parameters:
        close (pd.Series): ```close``` Series
        volume (pd.Series): ```volume``` Series
        length (int): The period. Default: ```10```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, length)
    volume = v_series(volume, length)

    if close is None or volume is None:
        return

    offset = v_offset(offset)

    # Calculate
    pv = close * volume
    vwma = sma(close=pv, length=length) / sma(close=volume, length=length)

    # Offset
    if offset != 0:
        vwma = vwma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        vwma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    vwma.name = f"VWMA_{length}"
    vwma.category = "overlap"

    return vwma
