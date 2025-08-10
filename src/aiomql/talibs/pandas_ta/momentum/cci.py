# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.maps import Imports
from pandas_ta.overlap import hlc3, sma
from pandas_ta.statistics import mad
from pandas_ta.utils import v_offset, v_pos_default, v_series, v_talib



def cci(
    high: Series, low: Series, close: Series, length: Int = None,
    c: IntFloat = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Commodity Channel Index

    This indicator attempts to identify "overbought" and "oversold" levels
    relative to a mean.

    Sources:
        * [tradingview](https://www.tradingview.com/wiki/Commodity_Channel_Index_(CCI))

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```14```
        c (float): Scaling Constant. Default: ```0.015```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 14)
    high = v_series(high, length)
    low = v_series(low, length)
    close = v_series(close, length)

    if high is None or low is None or close is None:
        return

    c = v_pos_default(c, 0.015)
    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import CCI
        cci = CCI(high, low, close, length)
    else:
        typical_price = hlc3(high=high, low=low, close=close, talib=mode_tal)
        mean_typical_price = sma(typical_price, length=length, talib=mode_tal)
        mad_typical_price = mad(typical_price, length=length)

        cci = typical_price - mean_typical_price / (c * mad_typical_price)

    # Offset
    if offset != 0:
        cci = cci.shift(offset)

    # Fill
    if "fillna" in kwargs:
        cci.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    cci.name = f"CCI_{length}_{c}"
    cci.category = "momentum"

    return cci
