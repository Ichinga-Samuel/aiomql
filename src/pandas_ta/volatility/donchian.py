# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_offset, v_pos_default, v_series



def donchian(
    high: Series, low: Series,
    lower_length: Int = None, upper_length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Donchian Channels

    This indicator attempt to quantify volatility similarily to
    Bollinger Bands and Keltner Channels.

    Sources:
        * [tradingview](https://www.tradingview.com/wiki/Donchian_Channels_(DC))

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        lower_length (int): Lower period. Default: ```20```
        upper_length (int): Upper period. Default: ```20```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 3 columns
    """
    # Validate
    lower_length = v_pos_default(lower_length, 20)
    upper_length = v_pos_default(upper_length, 20)
    lmin_periods = int(kwargs.pop("lmin_periods", lower_length))
    umin_periods = int(kwargs.pop("umin_periods", upper_length))

    _length = max(lower_length, lmin_periods, upper_length, umin_periods)
    high = v_series(high, _length)
    low = v_series(low, _length)

    if high is None or low is None:
        return

    offset = v_offset(offset)

    # Calculate
    lower = low.rolling(lower_length, min_periods=lmin_periods).min()
    upper = high.rolling(upper_length, min_periods=umin_periods).max()
    mid = 0.5 * (lower + upper)

    # Fill
    if "fillna" in kwargs:
        lower.fillna(kwargs["fillna"], inplace=True)
        mid.fillna(kwargs["fillna"], inplace=True)
        upper.fillna(kwargs["fillna"], inplace=True)

    # Offset
    if offset != 0:
        lower = lower.shift(offset)
        mid = mid.shift(offset)
        upper = upper.shift(offset)

    # Name and Category
    lower.name = f"DCL_{lower_length}_{upper_length}"
    mid.name = f"DCM_{lower_length}_{upper_length}"
    upper.name = f"DCU_{lower_length}_{upper_length}"
    mid.category = upper.category = lower.category = "volatility"

    data = {lower.name: lower, mid.name: mid, upper.name: upper}
    df = DataFrame(data, index=high.index)
    df.name = f"DC_{lower_length}_{upper_length}"
    df.category = mid.category

    return df
