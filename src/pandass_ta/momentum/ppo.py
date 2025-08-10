# -*- coding: utf-8 -*-
from numpy import isnan
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.ma import ma
from pandas_ta.maps import Imports
from pandas_ta.utils import (
    tal_ma,
    v_mamode,
    v_offset,
    v_pos_default,
    v_scalar,
    v_series,
    v_talib
)



def ppo(
    close: Series, fast: Int = None, slow: Int = None, signal: Int = None,
    scalar: IntFloat = None, mamode: str = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Percentage Price Oscillator

    Similar to MACD.

    Sources:
        * [investopedia](https://www.investopedia.com/terms/p/ppo.asp)

    Parameters:
        close (pd.Series): ```close``` Series
        fast (int): Fast MA period. Default: ```12```
        slow (int): Slow MA period. Default: ```26```
        signal (int): Signal period. Default: ```9```
        scalar (float): Scalar. Default: ```100```
        mamode (str): See ```help(ta.ma)```. Default: ```"sma"```
        talib (bool): If installed, use TA Lib. Default: ```True```
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
    _length = max(fast, slow, signal)
    close = v_series(close, _length)

    if close is None:
        return

    scalar = v_scalar(scalar, 100)
    mamode = v_mamode(mamode, "sma")
    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import PPO
        ppo = PPO(close, fast, slow, tal_ma(mamode))
    else:
        fastma = ma(mamode, close, length=fast, talib=mode_tal)
        slowma = ma(mamode, close, length=slow, talib=mode_tal)
        ppo = scalar * (fastma - slowma) / slowma

    if all(isnan(ppo)):
        return  # Emergency Break

    signalma = ma("ema", ppo, length=signal, talib=mode_tal)
    histogram = ppo - signalma

    # Offset
    if offset != 0:
        ppo = ppo.shift(offset)
        histogram = histogram.shift(offset)
        signalma = signalma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        ppo.fillna(kwargs["fillna"], inplace=True)
        histogram.fillna(kwargs["fillna"], inplace=True)
        signalma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{fast}_{slow}_{signal}"
    ppo.name = f"PPO{_props}"
    histogram.name = f"PPOh{_props}"
    signalma.name = f"PPOs{_props}"
    ppo.category = histogram.category = signalma.category = "momentum"

    data = {
        ppo.name: ppo,
        histogram.name: histogram,
        signalma.name: signalma
    }
    df = DataFrame(data, index=close.index)
    df.name = f"PPO{_props}"
    df.category = ppo.category

    return df
