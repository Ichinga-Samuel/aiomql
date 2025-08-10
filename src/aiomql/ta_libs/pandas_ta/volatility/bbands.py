# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.ma import ma
from pandas_ta.maps import Imports
from pandas_ta.statistics import stdev
from pandas_ta.utils import (
    non_zero_range,
    tal_ma,
    v_mamode,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)



def bbands(
    close: Series, length: Int = None,
    lower_std: IntFloat = None, upper_std: IntFloat = None,
    ddof: Int = None, mamode: str = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Bollinger Bands

    This indicator, by John Bollinger, attempts to quantify volatility by
    creating lower and upper bands centered around a moving average.

    Sources:
        * [tradingview](https://www.tradingview.com/wiki/Bollinger_Bands_(BB))

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```5```
        lower_std (IntFloat): Lower standard deviation. Default: ```2.0```
        upper_std (IntFloat): Upper standard deviation. Default: ```2.0```
        ddof (int): Degrees of Freedom to use. Default: ```0```
        mamode (str): See ```help(ta.ma)```. Default: ```"sma"```
        talib (bool): If installed, use TA Lib. Default: ```True```
        ddof (int): By default, uses Pandas ```ddof=1```.
            For Numpy calculation, use ```0```. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 5 columns

    Note:
        * TA Lib does not have a ```ddof``` parameter.
        * The divisor used in calculations is: ```N - ddof```, where ```N```
          is the number of elements. To use ```ddof```, set ```talib=False```.
    """
    # Validate
    length = v_pos_default(length, 5)
    close = v_series(close, length)

    if close is None:
        return

    lower_std = v_pos_default(lower_std, 2.0)
    upper_std = v_pos_default(upper_std, 2.0)
    ddof = int(ddof) if isinstance(ddof, int) and 0 <= ddof < length else 1
    mamode = v_mamode(mamode, "sma")
    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import BBANDS
        upper, mid, lower = BBANDS(close, length, upper_std, lower_std, tal_ma(mamode))
    else:
        std_dev = stdev(close=close, length=length, ddof=ddof, talib=mode_tal)
        lower_deviations = lower_std * std_dev
        upper_deviations = upper_std * std_dev

        mid = ma(mamode, close, length=length, talib=mode_tal, **kwargs)
        lower = mid - lower_deviations
        upper = mid + upper_deviations

    ulr = non_zero_range(upper, lower)
    bandwidth = 100 * ulr / mid
    percent = non_zero_range(close, lower) / ulr

    # Offset
    if offset != 0:
        lower = lower.shift(offset)
        mid = mid.shift(offset)
        upper = upper.shift(offset)
        bandwidth = bandwidth.shift(offset)
        percent = percent.shift(offset)

    # Fill
    if "fillna" in kwargs:
        lower.fillna(kwargs["fillna"], inplace=True)
        mid.fillna(kwargs["fillna"], inplace=True)
        upper.fillna(kwargs["fillna"], inplace=True)
        bandwidth.fillna(kwargs["fillna"], inplace=True)
        percent.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{length}_{lower_std}_{upper_std}"
    lower.name = f"BBL{_props}"
    mid.name = f"BBM{_props}"
    upper.name = f"BBU{_props}"
    bandwidth.name = f"BBB{_props}"
    percent.name = f"BBP{_props}"
    upper.category = lower.category = "volatility"
    mid.category = bandwidth.category = upper.category

    data = {
        lower.name: lower,
        mid.name: mid,
        upper.name: upper,
        bandwidth.name: bandwidth,
        percent.name: percent
    }
    df = DataFrame(data, index=close.index)
    df.name = f"BBANDS{_props}"
    df.category = mid.category

    return df
