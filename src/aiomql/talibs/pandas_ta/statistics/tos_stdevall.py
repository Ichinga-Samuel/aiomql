# -*- coding: utf-8 -*-
from numpy import arange, array, polyfit, std
from pandas import DataFrame, DatetimeIndex, Series
from pandas_ta._typing import DictLike, Int, List
from pandas_ta.utils import v_list, v_lowerbound, v_offset, v_series



def tos_stdevall(
    close: Series, length: Int = None,
    stds: List = None, ddof: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """TD Ameritrade's Think or Swim Standard Deviation All

    This indicator returns the standard deviation(s) over all the bars or the
    last ```n``` (length) bars.

    Sources:
        * [thinkorswim](https://tlc.thinkorswim.com/center/reference/thinkScript/Functions/Statistical/StDevAll)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): Bars since current/last bar, Series[-1]. Default: ```None```
        stds (list): List of standard deviations in increasing order from the
            central Linear Regression line. Default: ```[1,2,3]```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 7+ columns

    Note:
        * TA Lib does not have a ```ddof``` parameter.
        * The divisor used in calculations is: ```N - ddof```, where ```N```
            is the number of elements. To use ```ddof```, set ```talib=False```.

    Danger:
        Possible Data Leak
    """
    # Validate
    _props = f"TOS_STDEVALL"
    if length is None:
        length = close.size
    else:
        length = v_lowerbound(length, 2, 30)
        close = close.iloc[-length:]
        _props = f"{_props}_{length}"

    close = v_series(close, 2)

    if close is None:
        return

    stds = v_list(stds, [1, 2, 3])
    if min(stds) <= 0:
        return

    if not all(i < j for i, j in zip(stds, stds[1:])):
        stds = stds[::-1]

    ddof = int(ddof) if isinstance(ddof, int) and 0 <= ddof < length else 1
    offset = v_offset(offset)

    # Calculate
    X = src_index = close.index
    if isinstance(close.index, DatetimeIndex):
        X = arange(length)
        close = array(close)

    m, b = polyfit(X, close, 1)
    lr = Series(m * X + b, index=src_index)
    stdev = std(close, ddof=ddof)

    # Name and Category
    df = DataFrame({f"{_props}_LR": lr}, index=src_index)
    for i in stds:
        df[f"{_props}_L_{i}"] = lr - i * stdev
        df[f"{_props}_U_{i}"] = lr + i * stdev
        df[f"{_props}_L_{i}"].name = df[f"{_props}_U_{i}"].name = f"{_props}"
        df[f"{_props}_L_{i}"].category = df[f"{_props}_U_{i}"].category = "statistics"

    # Offset
    if offset != 0:
        df = df.shift(offset)

    # Fill
    if "fillna" in kwargs:
        df.fillna(kwargs["fillna"], inplace=True)

    df.name = f"{_props}"
    df.category = "statistics"

    return df
