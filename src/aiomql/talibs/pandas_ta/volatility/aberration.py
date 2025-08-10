# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.overlap import hlc3, sma
from pandas_ta.utils import v_offset, v_pos_default, v_series
from .atr import atr



def aberration(
    high: Series, low: Series, close: Series,
    length: Int = None, atr_length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Aberration

    Similar to Keltner Channels.

    Sources:
        * [Request #46](https://github.com/twopirllc/pandas-ta/issues/46)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```5```
        atr_length (int): ATR period. Default: ```15```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 4 columns
    """
    # Validate
    length = v_pos_default(length, 5)
    atr_length = v_pos_default(atr_length, 15)
    _length = max(atr_length, length) + 1
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    offset = v_offset(offset)

    # Calculate
    atr_ = atr(high=high, low=low, close=close, length=atr_length)
    jg = hlc3(high=high, low=low, close=close)

    zg = sma(jg, length)
    sg = zg + atr_
    xg = zg - atr_

    # Offset
    if offset != 0:
        zg = zg.shift(offset)
        sg = sg.shift(offset)
        xg = xg.shift(offset)
        atr_ = atr_.shift(offset)

    # Fill
    if "fillna" in kwargs:
        zg.fillna(kwargs["fillna"], inplace=True)
        sg.fillna(kwargs["fillna"], inplace=True)
        xg.fillna(kwargs["fillna"], inplace=True)
        atr_.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{length}_{atr_length}"
    zg.name = f"ABER_ZG{_props}"
    sg.name = f"ABER_SG{_props}"
    xg.name = f"ABER_XG{_props}"
    atr_.name = f"ABER_ATR{_props}"
    zg.category = sg.category = "volatility"
    xg.category = atr_.category = zg.category

    data = {zg.name: zg, sg.name: sg, xg.name: xg, atr_.name: atr_}
    df = DataFrame(data, index=close.index)
    df.name = f"ABER{_props}"
    df.category = zg.category

    return df
