# -*- coding: utf-8 -*-
from numpy import nan
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.utils import (
    v_drift,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)



def vidya(
    close: Series, length: Int = None,
    talib: bool = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Variable Index Dynamic Average

    This indicator, by Tushar Chande, is similar to an EMA but it has a
    dynamically adjusted lookback period dependent based on CMO.

    Sources:
        * [perfecttrendsystem](https://www.perfecttrendsystem.com/blog_mt4_2/en/vidya-indicator-for-mt4)
        * [tradingview](https://www.tradingview.com/script/hdrf0fXV-Variable-Index-Dynamic-Average-VIDYA/)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```14```
        talib (bool): If installed, use TA Lib. Default: ```True```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Note:
        Sometimes used as a moving average or a trend identifier.
    """
    # Validate
    length = v_pos_default(length, 14)
    close = v_series(close, length + 1)

    if close is None:
        return

    mode_tal = v_talib(talib)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    m = close.size
    alpha = 2 / (length + 1)

    if Imports["talib"] and mode_tal:
        from talib import CMO
        cmo_ = 0.01 * CMO(close, length)
    else:
        cmo_ = _cmo(close, length, drift)
    abs_cmo = cmo_.abs().astype(float)

    vidya = Series(0.0, index=close.index)
    for i in range(length, m):
        vidya.iloc[i] = alpha * abs_cmo.iloc[i] * close.iloc[i] + \
            vidya.iloc[i - 1] * (1 - alpha * abs_cmo.iloc[i])
    vidya.replace({0: nan}, inplace=True)

    # Offset
    if offset != 0:
        vidya = vidya.shift(offset)

    # Fill
    if "fillna" in kwargs:
        vidya.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    vidya.name = f"VIDYA_{length}"
    vidya.category = "overlap"

    return vidya


def _cmo(x: Series, length: Int, drift: Int):
    """Chande Momentum Oscillator Patch

    Unguarded CMO Patch

    Parameters:
        x (pd.Series): ```x``` Series
        length (int): The period.
        drift (int): Difference amount.

    Returns:
        (pd.Series): 1 column

    Info: Weird Circular TypeError!?
        For some reason: from pandas_ta.momentum import cmo causes
        pandas_ta.momentum.coppock to not be able to import it's _wma_ like
        from pandas_ta.overlap import wma?
    """
    mom = x.diff(drift)
    positive = mom.copy().clip(lower=0)
    negative = mom.copy().clip(upper=0).abs()
    pos_sum = positive.rolling(length).sum()
    neg_sum = negative.rolling(length).sum()

    return (pos_sum - neg_sum) / (pos_sum + neg_sum)
