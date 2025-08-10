# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.overlap import ema
from pandas_ta.utils import v_offset, v_pos_default, v_series



def eri(
    high: Series, low: Series, close: Series, length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Elder Ray Index

    This indicator, by Dr Alexander Elder, attempts to identify market
    strength.

    Sources:
        * [admiralmarkets](https://admiralmarkets.com/education/articles/forex-indicators/bears-and-bulls-power-indicator)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```14```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 2 columns

    Note:
        * Possible entry signals when used in combination with a trend,
        * Bear Power attempts to quantify lower value appeal.
        * Bull Power attempts the to quantify higher value appeal.
    """
    # Validate
    length = v_pos_default(length, 13)
    high = v_series(high, length)
    low = v_series(low, length)
    close = v_series(close, length)

    if high is None or low is None or close is None:
        return

    offset = v_offset(offset)

    # Calculate
    ema_ = ema(close, length)
    bull = high - ema_
    bear = low - ema_

    # Offset
    if offset != 0:
        bull = bull.shift(offset)
        bear = bear.shift(offset)

    # Fill
    if "fillna" in kwargs:
        bull.fillna(kwargs["fillna"], inplace=True)
        bear.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    bull.name = f"BULLP_{length}"
    bear.name = f"BEARP_{length}"
    bull.category = bear.category = "momentum"

    data = {bull.name: bull, bear.name: bear}
    df = DataFrame(data, index=close.index)
    df.name = f"ERI_{length}"
    df.category = bull.category

    return df
