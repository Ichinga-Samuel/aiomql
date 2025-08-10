# -*- coding: utf-8 -*-
from numpy import sqrt
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.utils import v_offset, v_pos_default, v_series, v_talib
from .variance import variance



def stdev(
    close: Series, length: Int = None,
    ddof: Int = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Rolling Standard Deviation

    Calculates a rolling Standard Deviation.

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```30```
        ddof (int): Delta Degrees of Freedom. Default: ```1```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Note:
        * TA Lib does not have a ```ddof``` parameter.
        * The divisor used in calculations is: ```N - ddof```, where ```N```
          is the number of elements. To use ```ddof```, set ```talib=False```.
    """
    # Validate
    length = v_pos_default(length, 30)
    close = v_series(close, length)

    if close is None:
        return

    ddof = int(ddof) if isinstance(ddof, int) and 0 <= ddof < length else 1
    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import STDDEV
        stdev = STDDEV(close, length)
    else:
        stdev = variance(
            close=close, length=length, ddof=ddof, talib=mode_tal
        ).apply(sqrt)

    # Offset
    if offset != 0:
        stdev = stdev.shift(offset)

    # Fill
    if "fillna" in kwargs:
        stdev.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    stdev.name = f"STDEV_{length}"
    stdev.category = "statistics"

    return stdev
