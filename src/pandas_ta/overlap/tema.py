# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.utils import v_offset, v_pos_default, v_series, v_talib
from .ema import ema



def tema(
    close: Series, length: Int = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Triple Exponential Moving Average

    This indicator attempts to be less laggy than the EMA.

    Sources:
        * [tradingtechnologies](https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/triple-exponential-moving-average-tema/)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        adjust (bool): Default: ```True```
        presma (bool): If True, uses SMA for initial value.
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Warning:
        TA-Lib Correlation: ```np.float64(0.9999355450605516)```

    Tip:
        Corrective contributions welcome!
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, 3 * length)

    if close is None:
        return

    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import TEMA
        tema = TEMA(close, length)
    else:
        ema1 = ema(close=close, length=length, talib=mode_tal, **kwargs)
        ema2 = ema(close=ema1, length=length, talib=mode_tal, **kwargs)
        ema3 = ema(close=ema2, length=length, talib=mode_tal, **kwargs)
        tema = 3 * (ema1 - ema2) + ema3

    # Offset
    if offset != 0:
        tema = tema.shift(offset)

    # Fill
    if "fillna" in kwargs:
        tema.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    tema.name = f"TEMA_{length}"
    tema.category = "overlap"

    return tema
