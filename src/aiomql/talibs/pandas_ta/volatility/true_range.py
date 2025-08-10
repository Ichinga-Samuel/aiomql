# -*- coding: utf-8 -*-
from numpy import isnan, nan
from pandas import concat, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.utils import (
    non_zero_range,
    v_bool,
    v_drift,
    v_offset,
    v_series,
    v_talib
)



def true_range(
    high: Series, low: Series, close: Series,
    talib: bool = None, prenan: bool = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """True Range

    This indicator attempts to quantify a High-Low range including potential
    gap scenarios.

    Sources:
        * [macroption](https://www.macroption.com/true-range/)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        talib (bool): If installed, use TA Lib. Default: ```True```
        prenan (bool): Sets initial values to ```nan``` based
            on ```drift```. Default: ```False```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Warning:
        TA-Lib Correlation: ```np.float64(0.9999999999999999)```

    Tip:
        Corrective contributions welcome!
    """
    # Validate
    _length = 1
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    mode_tal = v_talib(talib)
    prenan = v_bool(prenan, False)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import TRANGE
        true_range = TRANGE(high, low, close)
    else:
        hl_range = non_zero_range(high, low)
        pc = close.shift(drift)
        ranges = [hl_range, high - pc, pc - low]
        true_range = concat(ranges, axis=1)
        true_range = true_range.abs().max(axis=1)
        if prenan:
            true_range.iloc[:drift] = nan

    if all(isnan(true_range)):
        return  # Emergency Break

    # Offset
    if offset != 0:
        true_range = true_range.shift(offset)

    # Fill
    if "fillna" in kwargs:
        true_range.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    true_range.name = f"TRUERANGE_{drift}"
    true_range.category = "volatility"

    return true_range
