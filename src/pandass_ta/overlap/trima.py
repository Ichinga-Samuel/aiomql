# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.utils import v_offset, v_pos_default, v_series, v_talib
from .sma import sma



def trima(
    close: Series, length: Int = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Triangular Moving Average

    This indicator is a weighted moving average where the shape of the
    weights are triangular with the greatest weight is in the middle
    of the period.

    Sources:
        * [tradingtechnologies](https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/triangular-moving-average-trima/)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        adjust (bool): Default: True
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Note:
        tma = sma(sma(src, ceil(length / 2)), floor(length / 2) + 1)  # Tradingview
        trima = sma(sma(x, n), n)  # Tradingview

    Warning:
        TA-Lib Correlation: ```np.float64(0.9991752493891967)```

    Tip:
        Corrective contributions welcome!
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, length)

    if close is None:
        return

    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import TRIMA
        trima = TRIMA(close, length)
    else:
        half_length = round(0.5 * (length + 1))
        sma1 = sma(close, length=half_length, talib=mode_tal)
        trima = sma(sma1, length=half_length, talib=mode_tal)

    # Offset
    if offset != 0:
        trima = trima.shift(offset)

    # Fill
    if "fillna" in kwargs:
        trima.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    trima.name = f"TRIMA_{length}"
    trima.category = "overlap"

    return trima
