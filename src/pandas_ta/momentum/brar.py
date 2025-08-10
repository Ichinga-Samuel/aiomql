# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.utils import (
    non_zero_range,
    v_drift,
    v_offset,
    v_pos_default,
    v_scalar,
    v_series
)



def brar(
    open_: Series, high: Series, low: Series, close: Series,
    length: Int = None, scalar: IntFloat = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """BRAR

    BR and AR

    Sources:
        * No internet resources on definitive definition.

    Parameters:
        open_ (pd.Series): ```open``` Series
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```26```
        scalar (float): Scalar. Default: ```100```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 2 columns
    """
    # Validate
    length = v_pos_default(length, 26)
    open_ = v_series(open_, length)
    high = v_series(high, length)
    low = v_series(low, length)
    close = v_series(close, length)

    if open_ is None or high is None or low is None or close is None:
        return

    scalar = v_scalar(scalar, 100)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    high_open_range = non_zero_range(high, open_)
    open_low_range = non_zero_range(open_, low)
    hcy = non_zero_range(high, close.shift(drift))
    cyl = non_zero_range(close.shift(drift), low)

    hcy[hcy < 0] = 0  # Zero negative values
    cyl[cyl < 0] = 0  # ""

    ar = scalar * high_open_range.rolling(length).sum() \
        / open_low_range.rolling(length).sum()

    br = scalar * hcy.rolling(length).sum() \
        / cyl.rolling(length).sum()

    # Offset
    if offset != 0:
        ar = ar.shift(offset)
        br = ar.shift(offset)

    # Fill
    if "fillna" in kwargs:
        ar.fillna(kwargs["fillna"], inplace=True)
        br.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{length}"
    ar.name = f"AR{_props}"
    br.name = f"BR{_props}"
    ar.category = br.category = "momentum"

    data = {ar.name: ar, br.name: br}
    df = DataFrame(data, index=close.index)
    df.name = f"BRAR{_props}"
    df.category = "momentum"

    return df
