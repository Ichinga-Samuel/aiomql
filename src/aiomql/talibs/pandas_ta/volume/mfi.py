# -*- coding: utf-8 -*-
from sys import float_info as sflt
from numpy import convolve, maximum, nan, ones, roll, where
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.overlap import hlc3
from pandas_ta.utils import (
    nb_nonzero_range,
    v_drift,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)



def mfi(
    high: Series, low: Series, close: Series, volume: Series,
    length: Int = None, talib: bool = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Money Flow Index

    This indicator is an oscillator that attempts to quantify buying and
    selling pressure.

    Sources:
        * [tradingview](https://www.tradingview.com/wiki/Money_Flow_(MFI))

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        volume (pd.Series): ```volume``` Series
        length (int): The period. Default: ```14```
        talib (bool): If installed, use TA Lib. Default: ```True```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Warning:
        TA-Lib Correlation: ```np.float64(0.9959302104966524)```

    Tip:
        Corrective contributions welcome!
    """
    # Validate
    length = v_pos_default(length, 14)
    _length = length + 1
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)
    volume = v_series(volume, _length)

    if high is None or low is None or close is None or volume is None:
        return

    mode_tal = v_talib(talib)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import MFI
        mfi = MFI(high, low, close, volume, length)
    else:
        m, _ones = close.size, ones(length)

        tp = (high.to_numpy() + low.to_numpy() + close.to_numpy()) / 3.0
        smf = tp * volume.to_numpy() * where(tp > roll(tp, shift=drift), 1, -1)

        pos, neg = maximum(smf, 0), maximum(-smf, 0)
        avg_gain, avg_loss = convolve(pos, _ones)[:m], convolve(neg, _ones)[:m]

        _mfi = (100.0 * avg_gain) / (avg_gain + avg_loss + sflt.epsilon)
        _mfi[:length] = nan

        mfi = Series(_mfi, index=close.index)

    # Offset
    if offset != 0:
        mfi = mfi.shift(offset)

    # Fill
    if "fillna" in kwargs:
        mfi.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    mfi.name = f"MFI_{length}"
    mfi.category = "volume"

    return mfi
