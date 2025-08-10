# -*- coding: utf-8 -*-
from numba import njit
from pandas import Series
from pandas_ta._typing import Array, DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.utils import (
    nb_idiff,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)



@njit(cache=True)
def nb_mom(x, n):
    return nb_idiff(x, n)


def mom(
    close: Series, length: Int = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Momentum

    This indicator attempts to quantify speed by using the differences over
    a bar length.

    Sources:
        * [onlinetradingconcepts](http://www.onlinetradingconcepts.com/TechnicalAnalysis/Momentum.html)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```1```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, length + 1)

    if close is None:
        return

    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import MOM
        mom = MOM(close, length)
    else:
        np_close = close.to_numpy()
        _mom = nb_mom(np_close, length)
        mom = Series(_mom, index=close.index)

    # Offset
    if offset != 0:
        mom = mom.shift(offset)

    # Fill
    if "fillna" in kwargs:
        mom.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    mom.name = f"MOM_{length}"
    mom.category = "momentum"

    return mom
