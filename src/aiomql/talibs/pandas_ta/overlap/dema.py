# -*- coding: utf-8 -*-
from numpy import isnan
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.utils import v_offset, v_pos_default, v_series, v_talib
from .ema import ema



def dema(
    close: Series, length: Int = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Double Exponential Moving Average

    This indicator attempts to create a smoother average with less lag than
    the EMA.

    Sources:
        * [tradingtechnologies](https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/double-exponential-moving-average-dema/)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Warning:
        TA-Lib Correlation: ```np.float64(0.9999894518202522)```

    Tip:
        Corrective contributions welcome!
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, length)

    if close is None:
        return

    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import DEMA
        dema = DEMA(close, length)
    else:
        ema1 = ema(close=close, length=length, talib=mode_tal)
        ema2 = ema(close=ema1, length=length, talib=mode_tal)
        dema = 2 * ema1 - ema2

    if all(isnan(dema.to_numpy())):
        return  # Emergency Break

    # Offset
    if offset != 0:
        dema = dema.shift(offset)

    # Fill
    if "fillna" in kwargs:
        dema.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    dema.name = f"DEMA_{length}"
    dema.category = "overlap"

    return dema
