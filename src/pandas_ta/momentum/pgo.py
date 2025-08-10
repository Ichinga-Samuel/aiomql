# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.overlap import ema, sma
from pandas_ta.utils import v_offset, v_pos_default, v_series
from pandas_ta.volatility import atr



def pgo(
    high: Series, low: Series, close: Series, length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Pretty Good Oscillator

    This indicator, by Mark Johnson, attempts to identify breakouts for longer
    time periods based on the distance of the current bar to its N-day
    SMA, expressed in terms of an ATR over a similar length.

    Sources:
        * [tradingtechnologies](https://library.tradingtechnologies.com/trade/chrt-ti-pretty-good-oscillator.html)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```14```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Note: Entry
        * Long when greater than 3.
        * Short when less than -3.
    """
    # Validate
    length = v_pos_default(length, 14)
    _length = 2 * length
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    offset = v_offset(offset)

    # Calculate
    pgo = (close - sma(close, length)) \
        / ema(atr(high, low, close, length), length)

    # Offset
    if offset != 0:
        pgo = pgo.shift(offset)

    # Fill
    if "fillna" in kwargs:
        pgo.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    pgo.name = f"PGO_{length}"
    pgo.category = "momentum"

    return pgo
