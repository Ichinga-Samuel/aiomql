# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.utils import v_lowerbound, v_offset, v_series, v_talib



def variance(
    close: Series, length: Int = None,
    ddof: Int = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Rolling Variance

    Calculates a rolling Variance.

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
    length = v_lowerbound(length, 1, 30)
    if "min_periods" in kwargs and kwargs["min_periods"] is not None:
        min_periods = int(kwargs["min_periods"])
    else:
        min_periods = length
    close = v_series(close, max(length, min_periods))

    if close is None:
        return

    ddof = int(ddof) if isinstance(ddof, int) and 0 <= ddof < length else 1
    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import VAR
        variance = VAR(close, length)
    else:
        variance = close.rolling(length, min_periods=min_periods).var(ddof)

    # Offset
    if offset != 0:
        variance = variance.shift(offset)

    # Fill
    if "fillna" in kwargs:
        variance.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    variance.name = f"VAR_{length}"
    variance.category = "statistics"

    return variance
