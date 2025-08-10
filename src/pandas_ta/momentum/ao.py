# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.overlap import sma
from pandas_ta.utils import v_offset, v_pos_default, v_series



def ao(
    high: Series, low: Series, fast: Int = None, slow: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Awesome Oscillator

    This indicator attempts to identify momentum with the intention to
    affirm trends or anticipate possible reversals.

    Sources:
        * [ifcm](https://www.ifcm.co.uk/ntx-indicators/awesome-oscillator)
        * [tradingview](https://www.tradingview.com/wiki/Awesome_Oscillator_(AO))

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        fast (int): Fast period. Default: ```5```
        slow (int): Slow period. Default: ```34```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    fast = v_pos_default(fast, 5)
    slow = v_pos_default(slow, 34)
    if slow < fast:
        fast, slow = slow, fast
    _length = max(fast, slow)
    high = v_series(high, _length)
    low = v_series(low, _length)

    if high is None or low is None:
        return

    offset = v_offset(offset)

    # Calculate
    median_price = 0.5 * (high + low)
    fast_sma = sma(median_price, fast)
    slow_sma = sma(median_price, slow)
    ao = fast_sma - slow_sma

    # Offset
    if offset != 0:
        ao = ao.shift(offset)

    # Fill
    if "fillna" in kwargs:
        ao.fillna(kwargs["fillna"], inplace=True)
    # Name and Category
    ao.name = f"AO_{fast}_{slow}"
    ao.category = "momentum"

    return ao
