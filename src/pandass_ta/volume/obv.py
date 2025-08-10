# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.utils import signed_series, v_offset, v_series, v_talib



def obv(
    close: Series, volume: Series, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """On Balance Volume

    This indicator attempts to quantify buying and selling pressure.

    Sources:
        * [motivewave](https://www.motivewave.com/studies/on_balance_volume.htm)
        * [tradingtechnologies](https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/on-balance-volume-obv/)
        * [tradingview](https://www.tradingview.com/wiki/On_Balance_Volume_(OBV))

    Parameters:
        close (pd.Series): ```close``` Series
        volume (pd.Series): ```volume``` Series
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    _length = 1
    close = v_series(close, _length)
    volume = v_series(volume, _length)

    if close is None or volume is None:
        return

    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import OBV
        obv = OBV(close, volume)
    else:
        sv = signed_series(close, initial=1) * volume
        obv = sv.cumsum()

    # Offset
    if offset != 0:
        obv = obv.shift(offset)

    # Fill
    if "fillna" in kwargs:
        obv.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    obv.name = f"OBV"
    obv.category = "volume"

    return obv
