# -*- coding: utf-8 -*-
from numpy import inf, fabs, nan
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import (
    non_zero_range,
    v_drift,
    v_offset,
    v_pos_default,
    v_series
)



def vhf(
    close: Series, length: Int = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Vertical Horizontal Filter

    This indicator, by Adam White, attempts to identify trending and
    ranging markets.

    Sources:
        * [incrediblecharts](https://www.incrediblecharts.com/indicators/vertical_horizontal_filter.php)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```28```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 28)
    close = v_series(close, length)

    if close is None:
        return

    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    hcp = close.rolling(length).max()
    lcp = close.rolling(length).min()
    diff = fabs(close.diff(drift))
    vhf = fabs(non_zero_range(hcp, lcp)) / diff.rolling(length).sum()
    vhf.replace([inf, -inf], nan, inplace=True)
    # np_vhf = where(np_vhf == inf, nan, np_vhf)

    # Offset
    if offset != 0:
        vhf = vhf.shift(offset)

    # Fill
    if "fillna" in kwargs:
        vhf.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    vhf.name = f"VHF_{length}"
    vhf.category = "trend"

    return vhf
