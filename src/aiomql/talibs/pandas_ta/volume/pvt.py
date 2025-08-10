# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.momentum import roc
from pandas_ta.utils import v_drift, v_offset, v_series



def pvt(
    close: Series, volume: Series, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Price-Volume Trend

    This indicator attempts to quantify money flow.

    Sources:
        * [tradingview](https://www.tradingview.com/wiki/Price_Volume_Trend_(PVT))

    Parameters:
        close (pd.Series): ```close``` Series
        volume (pd.Series): ```volume``` Series
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    drift = v_drift(drift)
    _drift = drift + 1
    close = v_series(close, _drift)
    volume = v_series(volume, _drift)

    if close is None or volume is None:
        return

    offset = v_offset(offset)

    # Calculate
    pv = roc(close=close, length=drift) * volume
    pvt = pv.cumsum()

    # Offset
    if offset != 0:
        pvt = pvt.shift(offset)

    # Fill
    if "fillna" in kwargs:
        pvt.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    pvt.name = f"PVT"
    pvt.category = "volume"

    return pvt
