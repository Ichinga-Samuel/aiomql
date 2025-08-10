# -*- coding: utf-8 -*-
from statistics import pstdev
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.ma import ma
from pandas_ta.utils import (
    v_mamode,
    v_offset,
    v_pos_default,
    v_series
)



def vhm(
        volume: Series, length: Int = None, std_length = None,
        mamode: str = None, offset: Int = None, **kwargs: DictLike
    ) -> Series:
    """Volume Heatmap

    This indicator attempts to quantify volume trend strength of
    specified length.

    Sources:
        * [tradingview](https://www.tradingview.com/script/unWex8N4-Heatmap-Volume-xdecow/)

    Parameters:
        volume (pd.Series): ```volume``` Series
        length (int): The period. Default: ```610```
        std_length (int): Standard devation. Default: ```610```
        mamode (str): Mean MA. See ```help(ta.ma)```. Default: ```"sma"```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Note: Signals
        - Extremely Cold: ```vhm <= -0.5```
        -           Cold: ```-0.5 < vhm <= 1.0```
        -         Medium: ```1.0 < vhm <= 2.5```
        -            Hot: ```2.5 < vhm <= 4.0```
        -  Extremely Hot: ```vhm >= 4```
    """
    # Validate
    length = v_pos_default(length, 610)
    std_length = v_pos_default(std_length, length)
    _length = max(length, std_length)
    volume = v_series(volume, _length)

    if volume is None:
        return

    mamode = v_mamode(mamode, "sma")
    offset = v_offset(offset)

    # Calculate
    mu = ma(mamode, volume, length=length)
    vhm = (volume - mu) / pstdev(volume, std_length)

    # Offset
    if offset != 0:
        vhm = vhm.shift(offset)

    # Fill
    if "fillna" in kwargs:
        vhm.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"VHM_{length}"
    vhm.name = _props if length == std_length else f"{_props}_{std_length}"
    vhm.category = "volume"

    return vhm
