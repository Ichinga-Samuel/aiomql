# -*- coding: utf-8 -*-
from numpy import copy, cos, exp, zeros_like
from numba import njit
from pandas import Series
from pandas_ta._typing import Array, DictLike, Int, IntFloat
from pandas_ta.utils import v_offset, v_pos_default, v_series



# John F. Ehler's Super Smoother Filter by Everget (3 poles), Tradingview
# https://www.tradingview.com/script/VdJy0yBJ-Ehlers-Super-Smoother-Filter/
@njit(cache=True)
def nb_ssf3(x, n, pi, sqrt3):
    m, result = x.size, copy(x)
    a = exp(-pi / n)
    b = 2 * a * cos(-pi * sqrt3 / n)
    c = a * a

    d4 = c * c
    d3 = -c * (1 + b)
    d2 = b + c
    d1 = 1 - d2 - d3 - d4

    # result[:3] = x[:3]
    for i in range(3, m):
        result[i] = d1 * x[i] + d2 * result[i - 1] \
            + d3 * result[i - 2] + d4 * result[i - 3]

    return result


def ssf3(
    close: Series, length: Int = None,
    pi: IntFloat = None, sqrt3: IntFloat = None,
    offset: Int = None, **kwargs: DictLike
):
    """Ehlers's 3 Pole Super Smoother Filter

    This indicator, by John F. Ehlers's © 2013, is a (Recursive) Digital
    Filter that attempts to reduce lag and remove aliases. This version
    has two poles.

    Sources:
        * [mql5](https://www.mql5.com/en/code/589)
        * [tradingview](https://www.tradingview.com/script/VdJy0yBJ-Ehlers-Super-Smoother-Filter/)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```20```
        pi (float): The value of ```PI```. The default is Ehler's truncated
            value: ```3.14159```. Default: ```3.14159```
        sqrt3 (float): The value of ```sqrt(3)``` to use. The default is
            Ehler's truncated value: ```1.732```. Default: ```1.732```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Note:
        * Everget's calculation on TradingView:
            ```pi=np.pi```, ```sqrt2=np.sqrt(2)```
    """
    # Validate
    length = v_pos_default(length, 20)
    close = v_series(close, length)

    if close is None:
        return

    pi = v_pos_default(pi, 3.14159)
    sqrt3 = v_pos_default(sqrt3, 1.732)
    offset = v_offset(offset)

    # Calculate
    np_close = close.to_numpy()
    ssf = nb_ssf3(np_close, length, pi, sqrt3)
    ssf = Series(ssf, index=close.index)

    # Offset
    if offset != 0:
        ssf = ssf.shift(offset)

    # Fill
    if "fillna" in kwargs:
        ssf.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    ssf.name = f"SSF3_{length}"
    ssf.category = "overlap"

    return ssf
