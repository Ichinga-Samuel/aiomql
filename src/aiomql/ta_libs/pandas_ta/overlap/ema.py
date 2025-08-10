# -*- coding: utf-8 -*-
from numpy import nan
from numba import njit
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.utils import (
    v_bool,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)



def ema(
    close: Series, length: Int = None,
    talib: bool = None, presma: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Exponential Moving Average

    This Moving Average is more responsive than the Simple Moving
    Average (SMA).

    Sources:
        * [investopedia](https://www.investopedia.com/ask/answers/122314/what-exponential-moving-average-ema-formula-and-how-ema-calculated.asp)
        * [stockcharts](https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:moving_averages)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        talib (bool): If installed, use TA Lib. Default: ```True```
        presma (bool): Initialize with SMA like TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        adjust (bool): Default: ```False```
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, length)

    if close is None:
        return

    mode_tal = v_talib(talib)
    presma = v_bool(presma, True)
    offset = v_offset(offset)
    adjust = kwargs.setdefault("adjust", False)

    # Calculate
    if Imports["talib"] and mode_tal and length > 1:
        from talib import EMA
        ema = EMA(close, length)
    else:
        if presma:  # TA Lib implementation
            close = close.copy()
            sma_nth = close.iloc[0:length].mean()
            close.iloc[:length - 1] = nan
            close.iloc[length - 1] = sma_nth
        ema = close.ewm(span=length, adjust=adjust).mean()

    # Offset
    if offset != 0:
        ema = ema.shift(offset)

    # Fill
    if "fillna" in kwargs:
        ema.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    ema.name = f"EMA_{length}"
    ema.category = "overlap"

    return ema
