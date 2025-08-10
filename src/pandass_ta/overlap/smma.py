# -*- coding: utf-8 -*-
from numpy import nan
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.ma import ma
from pandas_ta.utils import (
    v_mamode,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)



def smma(
    close: Series, length: Int = None,
    mamode: str = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """SMoothed Moving Average

    This indicator attempts to confirm trends and identify support and
    resistance areas. It tries to reduce noise in contrast to reducing lag.

    Sources:
        * [sierrachart](https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=173&Name=Moving_Average_-_Smoothed)
        * [tradingview](https://www.tradingview.com/scripts/smma/)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        mamode (str): See ```help(ta.ma)```. Default: ```"sma"```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Note:
        A core component of Bill Williams Alligator indicator.
    """
    # Validate
    length = v_pos_default(length, 7)
    if "min_periods" in kwargs and kwargs["min_periods"] is not None:
        min_periods = int(kwargs["min_periods"])
    else:
        min_periods = length
    close = v_series(close, max(length, min_periods))

    if close is None:
        return

    mamode = v_mamode(mamode, "sma")
    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    m = close.size
    smma = close.copy()
    smma[:length - 1] = nan
    smma.iloc[length - 1] = ma(mamode, close[0:length], length=length, talib=mode_tal).iloc[-1]

    for i in range(length, m):
        smma.iat[i] = ((length - 1) * smma.iat[i - 1] + smma.iat[i]) / length

    # Offset
    if offset != 0:
        smma = smma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        smma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    smma.name = f"SMMA_{length}"
    smma.category = "overlap"

    return smma
