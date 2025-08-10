# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.utils import (
    v_percent,
    v_bool,
    v_drift,
    v_offset,
    v_pos_default,
    v_series
)



def increasing(
    close: Series, length: Int = None, strict: bool = None,
    asint: bool = None, percent: IntFloat = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Increasing

    This indicator, by Kevin Johnson, attempts to identify increasing periods.

    Sources:
        * Kevin Johnson

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```1```
        strict (bool): Check if continuously increasing. Default: ```False```
        percent (float): Percent, i.e. ```5.0```. Default: ```None```
        asint (bool): Returns as ```Int```. Default: ```True```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 1)
    close = v_series(close, length)

    if close is None:
        return

    strict = v_bool(strict, False)
    asint = v_bool(asint, True)
    percent = float(percent) if v_percent(percent) else False
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    close_ = (1 + 0.01 * percent) * close if percent else close
    if strict:
        # Returns value as float64? Have to cast to bool
        increasing = close > close_.shift(drift)
        for x in range(3, length + 1):
            increasing &= (close.shift(x - (drift + 1)) > close_.shift(x - drift))

        increasing.fillna(0, inplace=True)
        increasing = increasing.astype(bool)
    else:
        increasing = close_.diff(length) > 0

    if asint:
        increasing = increasing.astype(int)

    # Offset
    if offset != 0:
        increasing = increasing.shift(offset)

    # Fill
    if "fillna" in kwargs:
        increasing.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _percent = f"_{0.01 * percent}" if percent else ''
    _props = f"{'S' if strict else ''}INC{'p' if percent else ''}"
    increasing.name = f"{_props}_{length}{_percent}"
    increasing.category = "trend"

    return increasing
