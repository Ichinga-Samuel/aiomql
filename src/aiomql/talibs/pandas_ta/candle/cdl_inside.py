# -*- coding: utf-8 -*-
from numpy import roll, where
from numba import njit
from pandas import Series
from pandas_ta._typing import Array, DictLike, Int, IntFloat
from pandas_ta.utils import v_bool, v_offset, v_offset, v_scalar, v_series



@njit(cache=True)
def np_cdl_inside(high, low):
    hdiff = where(high - roll(high, 1) < 0, 1, 0)
    ldiff = where(low - roll(low, 1) > 0, 1, 0)
    return hdiff & ldiff


def cdl_inside(
    open_: Series, high: Series, low: Series, close: Series,
    asbool: bool = None, scalar: IntFloat = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Inside Bar

    Attempts to identify an "Inside" candle which is smaller than it's
    previous candle.

    Sources:
        * [TA Lib](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_CDL3INSIDE.c)
        * [tradingview](https://www.tradingview.com/script/IyIGN1WO-Inside-Bar/)

    Parameters:
        open_ (pd.Series): ```open``` Series
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        asbool (bool): Return booleans. Default: ```False```
        scalar (float): Scalar. Default: ```100```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): Replaces ```na```'s with ```value```.

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    open_ = v_series(open_)
    high = v_series(high)
    low = v_series(low)
    close = v_series(close)

    if open_ is None or high is None or low is None or close is None:
        return

    asbool = v_bool(asbool, False)
    scalar = v_scalar(scalar, 100)
    offset = v_offset(offset)

    # Calculate
    np_high, np_low = high.to_numpy(), low.to_numpy()
    np_inside = np_cdl_inside(np_high, np_low)
    inside = Series(np_inside, index=close.index, dtype=bool)

    if not asbool:
        inside = scalar * inside.astype(int)

    # Offset
    if offset != 0:
        inside = inside.shift(offset)

    # Fill
    if "fillna" in kwargs:
        inside.fillna(kwargs["fillna"], inplace=True)
    # Name and Category
    inside.name = f"CDL_INSIDE"
    inside.category = "candle"

    return inside
