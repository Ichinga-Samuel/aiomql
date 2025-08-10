# -*- coding: utf-8 -*-
from numpy import isnan, log, nan
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.overlap import hl2
from pandas_ta.utils import high_low_range, v_offset, v_pos_default, v_series



def fisher(
    high: Series, low: Series, length: Int = None, signal: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Fisher Transform

    This indicator attempts to identify significant reversals through
    normalization.

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        length (int): The period. Default: ```9```
        signal (int): Signal period. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 2 columns

    Tip: Reversal Signal
        When the two lines cross.
    """
    # Validate
    length = v_pos_default(length, 9)
    signal = v_pos_default(signal, 1)
    _length = max(length, signal)
    high = v_series(high, _length)
    low = v_series(low, _length)

    if high is None or low is None:
        return

    offset = v_offset(offset)

    # Calculate
    hl2_ = hl2(high, low)
    highest_hl2 = hl2_.rolling(length).max()
    lowest_hl2 = hl2_.rolling(length).min()

    hlr = high_low_range(highest_hl2, lowest_hl2)
    hlr[hlr < 0.001] = 0.001

    position = ((hl2_ - lowest_hl2) / hlr) - 0.5

    v = 0
    m = high.size
    result = [nan for _ in range(0, length - 1)] + [0]
    for i in range(length, m):
        v = 0.66 * position.iat[i] + 0.67 * v
        if v < -0.99:
            v = -0.999
        if v > 0.99:
            v = 0.999
        result.append(0.5 * (log((1 + v) / (1 - v)) + result[i - 1]))

    fisher = Series(result, index=high.index)
    if all(isnan(fisher)):
        return  # Emergency Break

    signalma = fisher.shift(signal)

    # Offset
    if offset != 0:
        fisher = fisher.shift(offset)
        signalma = signalma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        fisher.fillna(kwargs["fillna"], inplace=True)
        signalma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{length}_{signal}"
    fisher.name = f"FISHERT{_props}"
    signalma.name = f"FISHERTs{_props}"
    fisher.category = signalma.category = "momentum"

    data = {fisher.name: fisher, signalma.name: signalma}
    df = DataFrame(data, index=high.index)
    df.name = f"FISHERT{_props}"
    df.category = fisher.category

    return df
