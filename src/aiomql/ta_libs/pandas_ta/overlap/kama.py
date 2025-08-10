# -*- coding: utf-8 -*-
from numpy import nan
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.ma import ma
from pandas_ta.utils import (
    non_zero_range,
    v_drift,
    v_mamode,
    v_offset,
    v_pos_default,
    v_series
)



def kama(
    close: Series, length: Int = None, fast: Int = None, slow: Int = None,
    mamode: str = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Kaufman's Adaptive Moving Average

    This indicator, by Perry Kaufman, attempts to find the overall trend by
    adapting to volatility.

    Sources:
        * [stockcharts](https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:kaufman_s_adaptive_moving_average)
        * [tradingview](https://www.tradingview.com/script/wZGOIz9r-REPOST-Indicators-3-Different-Adaptive-Moving-Averages/)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        fast (int): Fast MA period. Default: ```2```
        slow (int): Slow MA period. Default: ```30```
        mamode (str): See ```help(ta.ma)```. Default: ```"sma"```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 10)
    fast = v_pos_default(fast, 2)
    slow = v_pos_default(slow, 30)
    close = v_series(close, max(fast, slow, length))

    if close is None:
        return

    mamode = v_mamode(mamode, "sma")
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    def weight(length: int) -> float:
        return 2 / (length + 1)

    fr = weight(fast)
    sr = weight(slow)

    abs_diff = non_zero_range(close, close.shift(length)).abs()
    peer_diff = non_zero_range(close, close.shift(drift)).abs()
    peer_diff_sum = peer_diff.rolling(length).sum()
    er = abs_diff / peer_diff_sum
    x = er * (fr - sr) + sr
    sc = x * x

    m = close.size
    ma0 = ma(mamode, close.iloc[:length], length=length, **kwargs).iloc[-1]
    result = [nan for _ in range(0, length - 1)] + [ma0]
    for i in range(length, m):
        result.append(sc.iat[i] * close.iat[i] \
            + (1 - sc.iat[i]) * result[i - 1])

    kama = Series(result, index=close.index)

    # Offset
    if offset != 0:
        kama = kama.shift(offset)

    # Fill
    if "fillna" in kwargs:
        kama.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    kama.name = f"KAMA_{length}_{fast}_{slow}"
    kama.category = "overlap"

    return kama
