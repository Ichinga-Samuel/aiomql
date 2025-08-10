# -*- coding: utf-8 -*-
from numpy import pi, sin
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_offset, v_pos_default, v_series, weights



def sinwma(
    close: Series, length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Sine Weighted Moving Average

    This indicator is a weighted average using sine cycles where the central
    values have greater weight.

    Source:
        * [Everget](https://www.tradingview.com/u/everget/)
        * [tradingview](https://www.tradingview.com/script/6MWFvnPO-Sine-Weighted-Moving-Average/)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 14)
    close = v_series(close, length)

    if close is None:
        return

    offset = v_offset(offset)

    # Calculate
    sines = Series(
        [sin((i + 1) * pi / (length + 1)) for i in range(0, length)]
    )
    w = sines / sines.sum()

    sinwma = close.rolling(length, min_periods=length) \
        .apply(weights(w), raw=True)

    # Offset
    if offset != 0:
        sinwma = sinwma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        sinwma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    sinwma.name = f"SINWMA_{length}"
    sinwma.category = "overlap"

    return sinwma
