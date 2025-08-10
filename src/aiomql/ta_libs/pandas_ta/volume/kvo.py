# -*- coding: utf-8 -*-
from numpy import isnan
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.ma import ma
from pandas_ta.overlap import hlc3
from pandas_ta.utils import (
    signed_series,
    v_drift,
    v_mamode,
    v_offset,
    v_pos_default,
    v_series
)



def kvo(
    high: Series, low: Series, close: Series, volume: Series,
    fast: Int = None, slow: Int = None, signal: Int = None,
    mamode: str = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Klinger Volume Oscillator

    This indicator, by Stephen J. Klinger., attempts to predict
    price reversals.

    Sources:
        * [daytrading](https://www.daytrading.com/klinger-volume-oscillator)
        * [investopedia](https://www.investopedia.com/terms/k/klingeroscillator.asp)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        volume (pd.Series): ```volume``` Series
        fast (int): Fast MA period. Default: ```34```
        slow (int): Slow MA period. Default: ```55```
        signal (int): Signal period. Default: ```13```
        mamode (str): See ```help(ta.ma)```. Default: ```"ema"```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 2 columns
    """
    # Validate
    fast = v_pos_default(fast, 34)
    slow = v_pos_default(slow, 55)
    signal = v_pos_default(signal, 13)
    _length = max(fast, slow) + signal
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)
    volume = v_series(volume, _length)

    if high is None or low is None or close is None or volume is None:
        return

    mamode = v_mamode(mamode, "ema")
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    signed_volume = volume * signed_series(hlc3(high, low, close), -1)
    sv = signed_volume.loc[signed_volume.first_valid_index():, ]

    kvo = ma(mamode, sv, length=fast) - ma(mamode, sv, length=slow)
    if kvo is None or all(isnan(kvo.to_numpy())):
        return  # Emergency Break

    kvo_signal = ma(mamode, kvo.loc[kvo.first_valid_index():, ], length=signal)
    if kvo_signal is None or all(isnan(kvo_signal.to_numpy())):
        return  # Emergency Break

    # Offset
    if offset != 0:
        kvo = kvo.shift(offset)
        kvo_signal = kvo_signal.shift(offset)

    # Fill
    if "fillna" in kwargs:
        kvo.fillna(kwargs["fillna"], inplace=True)
        kvo_signal.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{fast}_{slow}_{signal}"
    kvo.name = f"KVO{_props}"
    kvo_signal.name = f"KVOs{_props}"
    kvo.category = kvo_signal.category = "volume"

    data = {kvo.name: kvo, kvo_signal.name: kvo_signal}
    df = DataFrame(data, index=close.index)
    df.name = f"KVO{_props}"
    df.category = kvo.category

    return df
