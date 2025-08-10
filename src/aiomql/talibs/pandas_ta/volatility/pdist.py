# -*- coding: utf-8 -*-
from numpy import isnan
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import non_zero_range, v_drift, v_offset, v_series



def pdist(
    open_: Series, high: Series, low: Series, close: Series,
    drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Price Distance

    This indicator attempts to quantify the magnitude covered by
    price movements.

    Sources:
        * [prorealcode](https://www.prorealcode.com/prorealtime-indicators/pricedistance/)

    Parameters:
        open_ (pd.Series): ```open``` Series
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    drift = v_drift(drift)
    open_ = v_series(open_)
    high = v_series(high)
    low = v_series(low)
    close = v_series(close)
    offset = v_offset(offset)

    # Calculate
    pdist = 2 * non_zero_range(high, low)
    if all(isnan(pdist)):
        return  # Emergency Break

    pdist += non_zero_range(open_, close.shift(drift)).abs()
    pdist -= non_zero_range(close, open_).abs()

    if all(isnan(pdist)):
        return  # Emergency Break

    # Offset
    if offset != 0:
        pdist = pdist.shift(offset)

    # Fill
    if "fillna" in kwargs:
        pdist.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    pdist.name = "PDIST"
    pdist.category = "volatility"

    return pdist
