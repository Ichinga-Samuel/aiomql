# -*- coding: utf-8 -*-
from numpy import isnan
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.overlap.ema import ema
from pandas_ta.utils import (
    v_drift,
    v_offset,
    v_pos_default,
    v_scalar,
    v_series
)



def trix(
    close: Series, length: Int = None, signal: Int = None,
    scalar: IntFloat = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Trix

    This indicator attempts to identify divergences as an oscillator.

    Sources:
        * [tradingview](https://www.tradingview.com/wiki/TRIX)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```18```
        signal (int): Signal period. Default: ```9```
        scalar (float): Scalar. Default: ```100```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 30)
    signal = v_pos_default(signal, 9)
    if length < signal:
        length, signal = signal, length
    _length = 3 * length - 1
    close = v_series(close, _length)

    if close is None:
        return

    scalar = v_scalar(scalar, 100)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    ema1 = ema(close=close, length=length, **kwargs)
    if all(isnan(ema1)):
        return  # Emergency Break

    ema2 = ema(close=ema1, length=length, **kwargs)
    if all(isnan(ema2)):
        return  # Emergency Break

    ema3 = ema(close=ema2, length=length, **kwargs)
    if all(isnan(ema3)):
        return  # Emergency Break

    trix = scalar * ema3.pct_change(drift)
    trix_signal = trix.rolling(signal).mean()

    # Offset
    if offset != 0:
        trix = trix.shift(offset)
        trix_signal = trix_signal.shift(offset)

    # Fill
    if "fillna" in kwargs:
        trix.fillna(kwargs["fillna"], inplace=True)
        trix_signal.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    trix.name = f"TRIX_{length}_{signal}"
    trix_signal.name = f"TRIXs_{length}_{signal}"
    trix.category = trix_signal.category = "momentum"

    data = {trix.name: trix, trix_signal.name: trix_signal}
    df = DataFrame(data, index=close.index)
    df.name = f"TRIX_{length}_{signal}"
    df.category = "momentum"

    return df
