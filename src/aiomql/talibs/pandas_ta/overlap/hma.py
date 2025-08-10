# -*- coding: utf-8 -*-
from sys import modules as module_
from numpy import sqrt
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_mamode, v_offset, v_pos_default, v_series
from .ema import ema
from .sma import sma
from .wma import wma



def hma(
    close: Series, length: Int = None, mamode: str = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Hull Moving Average

    This indicator, by Alan Hull, attempts to reduce lag compared to
    classical moving averages.

    Sources:
        * [Alan Hull](https://alanhull.com/hull-moving-average)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        mamode (str): One of: 'ema', 'sma', or 'wma'. Default: ```"wma"```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, length + 2)

    if close is None:
        return

    mamode = v_mamode(mamode, "wma")
    offset = v_offset(offset)

    if mamode not in ["ema", "sma", "wma"]:
        return

    _ma = getattr(module_[__name__], mamode)

    # Calculate
    half_length = int(length / 2)
    sqrt_length = int(sqrt(length))

    maf = _ma(close, length=half_length)
    mas = _ma(close, length=length)
    hma = _ma(close=2 * maf - mas, length=sqrt_length)

    # Offset
    if offset != 0:
        hma = hma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        hma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    hma.name = f"HMA{"" if mamode == "wma" else mamode[0]}_{length}"
    hma.category = "overlap"

    return hma
