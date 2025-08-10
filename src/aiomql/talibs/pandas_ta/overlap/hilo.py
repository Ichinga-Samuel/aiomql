# -*- coding: utf-8 -*-
from numpy import nan
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.ma import ma
from pandas_ta.utils import v_mamode, v_offset, v_pos_default, v_series



def hilo(
    high: Series, low: Series, close: Series,
    high_length: Int = None, low_length: Int = None, mamode: str = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Gann HiLo Activator

    This indicator, by Robert Krausz, uses two different Moving Averages to
    identify trends.

    Sources:
        * Gann HiLo Activator, , Stocks & Commodities Magazine, 1998
        * [sierrachart](https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=447&Name=Gann_HiLo_Activator)
        * [tradingview](https://www.tradingview.com/script/XNQSLIYb-Gann-High-Low/)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        high_length (int): High period. Default: ```13```
        low_length (int): Low period. Default: ```21```
        mamode (str): See ```help(ta.ma)```. Default: ```"sma"```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 3 columns

    Note:
        Increasing ```high_length``` and decreasing ```low_length``` is
        better for short trades and vice versa for long trades.
    """
    # Validate
    high_length = v_pos_default(high_length, 13)
    low_length = v_pos_default(low_length, 21)
    _length = max(high_length, low_length) + 1
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    mamode = v_mamode(mamode, "sma")
    offset = v_offset(offset)

    # Calculate
    m = close.size
    hilo = Series(nan, index=close.index)
    long = Series(nan, index=close.index)
    short = Series(nan, index=close.index)

    high_ma = ma(mamode, high, length=high_length)
    low_ma = ma(mamode, low, length=low_length)

    for i in range(1, m):
        if close.iat[i] > high_ma.iat[i - 1]:
            hilo.iat[i] = long.iat[i] = low_ma.iat[i]
        elif close.iat[i] < low_ma.iat[i - 1]:
            hilo.iat[i] = short.iat[i] = high_ma.iat[i]
        else:
            hilo.iat[i] = hilo.iat[i - 1]
            long.iat[i] = short.iat[i] = hilo.iat[i - 1]

    # Offset
    if offset != 0:
        hilo = hilo.shift(offset)
        long = long.shift(offset)
        short = short.shift(offset)

    # Fill
    if "fillna" in kwargs:
        hilo.fillna(kwargs["fillna"], inplace=True)
        long.fillna(kwargs["fillna"], inplace=True)
        short.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{high_length}_{low_length}"
    data = {
        f"HILO{_props}": hilo,
        f"HILOl{_props}": long,
        f"HILOs{_props}": short
    }
    df = DataFrame(data, index=close.index)

    df.name = f"HILO{_props}"
    df.category = "overlap"

    return df
