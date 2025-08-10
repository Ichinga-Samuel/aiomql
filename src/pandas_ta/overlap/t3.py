# -*- coding: utf-8 -*-
from numpy import isnan
from pandas import Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.maps import Imports
from pandas_ta.utils import v_offset, v_pos_default, v_series, v_talib
from .ema import ema



def t3(
    close: Series, length: Int = None, a: IntFloat = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """T3

    This indicator, by Tim Tillson, attempts to be smoother and more
    responsive relative to other moving averages.

    Sources:
        * [binarytribune](http://www.binarytribune.com/forex-trading-indicators/t3-moving-average-indicator/)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        a (float): The a factor, 0 < a < 1. Default: ```0.7```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        adjust (bool): Default: True
        presma (bool): If True, uses SMA for initial value.
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Warning:
        TA-Lib Correlation: ```np.float64(0.9999994265973177)```

    Tip:
        Corrective contributions welcome!
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, 5 * (length + 1))

    if close is None:
        return

    a = float(a) if isinstance(a, float) and 0 < a < 1 else 0.7
    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import T3
        t3 = T3(close, length, a)
    else:
        c1 = -a * a**2
        c2 = 3 * a**2 + 3 * a**3
        c3 = -6 * a**2 - 3 * a - 3 * a**3
        c4 = a**3 + 3 * a**2 + 3 * a + 1

        e1 = ema(close=close, length=length, talib=mode_tal, **kwargs)
        e2 = ema(close=e1, length=length, talib=mode_tal, **kwargs)
        e3 = ema(close=e2, length=length, talib=mode_tal, **kwargs)
        e4 = ema(close=e3, length=length, talib=mode_tal, **kwargs)
        e5 = ema(close=e4, length=length, talib=mode_tal, **kwargs)
        e6 = ema(close=e5, length=length, talib=mode_tal, **kwargs)
        t3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3

    # Offset
    if offset != 0:
        t3 = t3.shift(offset)

    # Fill
    if "fillna" in kwargs:
        t3.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    t3.name = f"T3_{length}_{a}"
    t3.category = "overlap"

    return t3
