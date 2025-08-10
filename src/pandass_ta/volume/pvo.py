# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.overlap import ema
from pandas_ta.utils import v_offset, v_pos_default, v_scalar, v_series



def pvo(
    volume: Series, fast: Int = None, slow: Int = None,
    signal: Int = None, scalar: IntFloat = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Percentage Volume Oscillator

    This indicator is a volume momentum oscillator.

    Sources:
        * [fmlabs](https://www.fmlabs.com/reference/default.htm?url=PVO.htm)

    Parameters:
        volume (pd.Series): ```volume``` Series
        fast (int): Fast MA period. Default: ```12```
        slow (int): Slow MA period. Default: ```26```
        signal (int): Signal period. Default: ```9```
        scalar (float): Scalar. Default: ```100```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 3 columns
    """
    # Validate
    fast = v_pos_default(fast, 12)
    slow = v_pos_default(slow, 26)
    signal = v_pos_default(signal, 9)
    if slow < fast:
        fast, slow = slow, fast
    volume = v_series(volume, max(fast, slow, signal))

    if volume is None:
        return

    scalar = v_scalar(scalar, 100)
    offset = v_offset(offset)

    # Calculate
    fastma = ema(volume, length=fast)
    slowma = ema(volume, length=slow)
    pvo = scalar * (fastma - slowma) / slowma

    signalma = ema(pvo, length=signal)
    histogram = pvo - signalma

    # Offset
    if offset != 0:
        pvo = pvo.shift(offset)
        histogram = histogram.shift(offset)
        signalma = signalma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        pvo.fillna(kwargs["fillna"], inplace=True)
        histogram.fillna(kwargs["fillna"], inplace=True)
        signalma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{fast}_{slow}_{signal}"
    pvo.name = f"PVO{_props}"
    histogram.name = f"PVOh{_props}"
    signalma.name = f"PVOs{_props}"
    pvo.category = histogram.category = signalma.category = "momentum"

    data = {pvo.name: pvo, histogram.name: histogram, signalma.name: signalma}
    df = DataFrame(data, index=volume.index)
    df.name = pvo.name
    df.category = pvo.category

    return df
