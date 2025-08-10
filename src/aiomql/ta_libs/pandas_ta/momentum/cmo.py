# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.maps import Imports
from pandas_ta.overlap import rma
from pandas_ta.utils import (
    v_drift,
    v_offset,
    v_pos_default,
    v_scalar,
    v_series,
    v_talib
)



def cmo(
    close: Series, length: Int = None, scalar: IntFloat = None,
    talib: bool = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Chande Momentum Oscillator

    This indicator attempts to capture momentum.

    Sources:
        * [tradingtechnologies](https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/chande-momentum-oscillator-cmo/)
        * [tradingview](https://www.tradingview.com/script/hdrf0fXV-Variable-Index-Dynamic-Average-VIDYA/)

    Parameters:
        close (pd.Series): ```close``` Series
        scalar (float): Scalar. Default: ```100```
        talib (bool): If installed, use TA Lib. Uses EMA if ```False```.
            Default: ```True```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Note:
        * Overbought around 50
        * Oversold around -50.
    """
    # Validate
    length = v_pos_default(length, 14)
    close = v_series(close, length + 1)

    if close is None:
        return

    scalar = v_scalar(scalar, 100)
    mode_tal = v_talib(talib)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import CMO
        cmo = CMO(close, length)
    else:
        mom = close.diff(drift)
        positive = mom.copy().clip(lower=0)
        negative = mom.copy().clip(upper=0).abs()

        if mode_tal:
            pos_ = rma(positive, length)
            neg_ = rma(negative, length)
        else:
            pos_ = positive.rolling(length).sum()
            neg_ = negative.rolling(length).sum()

        cmo = scalar * (pos_ - neg_) / (pos_ + neg_)

    # Offset
    if offset != 0:
        cmo = cmo.shift(offset)

    # Fill
    if "fillna" in kwargs:
        cmo.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    cmo.name = f"CMO_{length}"
    cmo.category = "momentum"

    return cmo
