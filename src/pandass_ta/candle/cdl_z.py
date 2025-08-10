# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.statistics import zscore
from pandas_ta.utils import v_bool, v_offset, v_pos_default, v_series



def cdl_z(
    open_: Series, high: Series, low: Series, close: Series,
    length: Int = None, full: bool = None, ddof: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Z Candles

    Creates candlesticks using a rolling Z Score.

    Sources:
        * Kevin Johnson

    Parameters:
        open_ (pd.Series): ```open``` Series
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        full (bool): Apply ```length``` to whole DataFrame.
            Default: ```False```
        ddof (int): By default, uses Pandas ```ddof=1```.
            For Numpy calculation, use ```0```. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        naive (bool): If ```True```, prefills potential Doji less
            than the length if it less than a percentage of it's
            High-Low range. Default: ```False```
        fillna (value): Replaces ```na```'s with ```value```.

    Returns:
        (pd.DataFrame): 4 columns

    Note:
        * Numpy ```std()``` [ddof](https://numpy.org/doc/stable/reference/generated/numpy.std.html) explanation.
    """
    # Validate
    length = v_pos_default(length, 30)
    open_ = v_series(open_, length)
    high = v_series(high, length)
    low = v_series(low, length)
    close = v_series(close, length)

    if open_ is None or high is None or low is None or close is None:
        return

    full = v_bool(full, False)
    ddof = int(ddof) if isinstance(ddof, int) and 0 <= ddof < length else 1
    offset = v_offset(offset)

    # Calculate
    if full:
        length = close.size

    z_open = zscore(open_, length=length, ddof=ddof)
    z_high = zscore(high, length=length, ddof=ddof)
    z_low = zscore(low, length=length, ddof=ddof)
    z_close = zscore(close, length=length, ddof=ddof)

    _full = "a" if full else ""
    _props = _full if full else f"_{length}_{ddof}"
    data = {
        f"open_Z{_props}": z_open,
        f"high_Z{_props}": z_high,
        f"low_Z{_props}": z_low,
        f"close_Z{_props}": z_close,
    }
    df = DataFrame(data, index=close.index)

    if full:
        df.fillna(method="backfill", axis=0, inplace=True)

    # Offset
    if offset != 0:
        df = df.shift(offset)

    # Fill
    if "fillna" in kwargs:
        df.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    df.name = f"CDL_Z{_props}"
    df.category = "candle"

    return df
