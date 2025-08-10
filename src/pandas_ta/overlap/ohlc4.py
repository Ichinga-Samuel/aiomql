# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_offset, v_series



def ohlc4(
    open_: Series, high: Series, low: Series, close: Series,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """OHLC4

    OHLC4 is the average of open, high, low and close.

    Parameters:
        open_ (pd.Series): ```open``` Series
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```.
            Only works when offset.

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    open_ = v_series(open_)
    high = v_series(high)
    low = v_series(low)
    close = v_series(close)
    offset = v_offset(offset)

    # Calculate
    avg = 0.25 * (open_.to_numpy() + high.to_numpy() + low.to_numpy() + close.to_numpy())
    ohlc4 = Series(avg, index=close.index)

    # Offset
    if offset != 0:
        ohlc4 = ohlc4.shift(offset)

        # Fill
        if "fillna" in kwargs:
            ohlc4.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    ohlc4.name = "OHLC4"
    ohlc4.category = "overlap"

    return ohlc4
