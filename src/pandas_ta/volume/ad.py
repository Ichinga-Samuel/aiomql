# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.utils import non_zero_range, v_offset, v_series, v_talib



def ad(
    high: Series, low: Series, close: Series, volume: Series,
    open_: Series = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Accumulation/Distribution

    This indicator attempts to quantify accumulation/distribution from a
    relative position within it's High-Low range and volume.

    Sources:
        * [tradingtechnologies](https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/accumulationdistribution-ad/)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        volume (pd.Series): ```volume``` Series
        open_ (pd.Series): Optional ```open``` Series
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    high = v_series(high)
    low = v_series(low)
    close = v_series(close)
    volume = v_series(volume)
    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal and volume.size:
        from talib import AD
        ad = AD(high, low, close, volume)
    else:
        if open_ is not None:
            open_ = v_series(open_)
            ad = non_zero_range(close, open_)  # AD with Open
        else:
            ad = 2 * close - (high + low)  # AD with High, Low, Close

        high_low_range = non_zero_range(high, low)
        ad *= volume / high_low_range
        ad = ad.cumsum()

    # Offset
    if offset != 0:
        ad = ad.shift(offset)

    # Fill
    if "fillna" in kwargs:
        ad.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    ad.name = "AD" if open_ is None else "ADo"
    ad.category = "volume"

    return ad
