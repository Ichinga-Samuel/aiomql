# -*- coding: utf-8 -*-
from numpy import isnan
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.utils import v_offset, v_pos_default, v_scalar, v_series
from .tsi import tsi



def smi(
    close: Series, fast: Int = None, slow: Int = None,
    signal: Int = None, scalar: IntFloat = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """SMI Ergodic Indicator

    This indicator, by William Blau, is the same as the TSI except the SMI
    includes a signal line. A trend is considered bullish when crossing above
    zero and bearish when crossing below zero. This implementation includes
    both the SMI Ergodic Indicator and SMI Ergodic Oscillator.

    Sources:
        * [motivewave](https://www.motivewave.com/studies/smi_ergodic_indicator.htm)
        * [tradingview A](https://www.tradingview.com/script/Xh5Q0une-SMI-Ergodic-Oscillator/)
        * [tradingview B](https://www.tradingview.com/script/cwrgy4fw-SMIIO/)

    Parameters:
        close (pd.Series): ```close``` Series
        fast (int): The short period. Default: ```5```
        slow (int): The long period. Default: ```20```
        signal (int): Signal period. Default: ```5```
        scalar (float): Scalar. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 3 columns
    """
    # Validate
    fast = v_pos_default(fast, 5)
    slow = v_pos_default(slow, 20)
    signal = v_pos_default(signal, 5)
    if slow < fast:
        fast, slow = slow, fast
    _length = slow + signal + 1
    close = v_series(close, _length)

    if close is None:
        return

    scalar = v_scalar(scalar, 1)
    offset = v_offset(offset)

    # Calculate
    tsi_df = tsi(close, fast=fast, slow=slow, signal=signal, scalar=scalar)
    if tsi_df is None:
        return  # Emergency Break

    smi = tsi_df.iloc[:, 0]
    signalma = tsi_df.iloc[:, 1]
    if all(isnan(signalma)):
        return  # Emergency Break
    osc = smi - signalma

    # Offset
    if offset != 0:
        smi = smi.shift(offset)
        signalma = signalma.shift(offset)
        osc = osc.shift(offset)

    # Fill
    if "fillna" in kwargs:
        smi.fillna(kwargs["fillna"], inplace=True)
        signalma.fillna(kwargs["fillna"], inplace=True)
        osc.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    # _scalar = f"_{scalar}" if scalar != 1 else ""
    _props = f"_{fast}_{slow}_{signal}_{scalar}"
    smi.name = f"SMI{_props}"
    signalma.name = f"SMIs{_props}"
    osc.name = f"SMIo{_props}"
    smi.category = signalma.category = osc.category = "momentum"

    data = {smi.name: smi, signalma.name: signalma, osc.name: osc}
    df = DataFrame(data, index=close.index)
    df.name = f"SMI{_props}"
    df.category = smi.category

    return df
