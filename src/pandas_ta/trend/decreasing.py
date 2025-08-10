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



def decreasing(
    close: Series, length: Int = None, strict: bool = None,
    asint: bool = None, percent: IntFloat = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Decreasing

    This indicator, by Kevin Johnson, attempts to identify decreasing periods.

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
    close_ = (1 - 0.01 * percent) * close if percent else close
    if strict:
        # Returns value as float64? Have to cast to bool
        decreasing = close < close_.shift(drift)
        for x in range(3, length + 1):
            decreasing &= (close.shift(x - (drift + 1)) < close_.shift(x - drift))

        decreasing.fillna(0, inplace=True)
        decreasing = decreasing.astype(bool)
    else:
        decreasing = close_.diff(length) < 0

    if asint:
        decreasing = decreasing.astype(int)

    # Offset
    if offset != 0:
        decreasing = decreasing.shift(offset)

    # Fill
    if "fillna" in kwargs:
        decreasing.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _percent = f"_{0.01 * percent}" if percent else ''
    _props = f"{'S' if strict else ''}DEC{'p' if percent else ''}"
    decreasing.name = f"{_props}_{length}{_percent}"
    decreasing.category = "trend"

    return decreasing
