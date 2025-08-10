# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.ma import ma
from pandas_ta.maps import Imports
from pandas_ta.utils import tal_ma, v_mamode, v_offset
from pandas_ta.utils import v_pos_default, v_series, v_talib



def apo(
    close: Series, fast: Int = None, slow: Int = None,
    mamode: str = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Absolute Price Oscillator

    This indicator attempts to quantify momentum.

    Sources:
        * [tradingtechnologies](https://www.tradingtechnologies.com/xtrader-help/x-study/technical-indicator-definitions/absolute-price-oscillator-apo/)

    Parameters:
        close (pd.Series): ```close``` Series
        fast (int): Fast period. Default: ```12```
        slow (int): Slow period. Default: ```26```
        mamode (str): See ```help(ta.ma)```. Default: ```"sma"```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Note:
        * Simply the difference of two different EMAs.
        * APO and MACD lines are equivalent.
    """
    # Validate
    fast = v_pos_default(fast, 12)
    slow = v_pos_default(slow, 26)
    if slow < fast:
        fast, slow = slow, fast
    close = v_series(close, max(fast, slow))

    if close is None:
        return

    mamode = v_mamode(mamode, "sma")
    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import APO
        apo = APO(close, fast, slow, tal_ma(mamode))
    else:
        fastma = ma(mamode, close, length=fast, talib=mode_tal)
        slowma = ma(mamode, close, length=slow, talib=mode_tal)
        apo = fastma - slowma

    # Offset
    if offset != 0:
        apo = apo.shift(offset)

    # Fill
    if "fillna" in kwargs:
        apo.fillna(kwargs["fillna"], inplace=True)
    # Name and Category
    apo.name = f"APO_{fast}_{slow}"
    apo.category = "momentum"

    return apo
