# -*- coding: utf-8 -*-
from numpy import nan
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_drift, v_series



def pvr(
    close: Series, volume: Series,
    drift: Int = None, **kwargs: DictLike
) -> Series:
    """Price Volume Rank

    This indicator, by Anthony J. Macek, is a simple rank computation with
    close and volume values.

    Sources:
        * Anthony J. Macek, June, 1994 issue of Technical Analysis of
          Stocks & Commodities (TASC) Magazine
        * [fmlabs](https://www.fmlabs.com/reference/default.htm?url=PVrank.htm)

    Parameters:
        close (pd.Series): ```close``` Series
        volume (pd.Series): ```volume``` Series
        drift (int): Difference amount. Default: ```1```

    Returns:
        (pd.Series): 1 column

    Note: Signals
        - Buy < 2.5
        - Sell > 2.5
    """
    # Validate
    drift = v_drift(drift)
    close = v_series(close, drift)
    volume = v_series(volume, drift)

    if close is None or volume is None:
        return

    # Calculate
    close_diff = close.diff(drift).fillna(0)
    volume_diff = volume.diff(drift).fillna(0)

    pvr = Series(nan, index=close.index)

    pvr.loc[(close_diff >= 0) & (volume_diff >= 0)] = 1
    pvr.loc[(close_diff >= 0) & (volume_diff < 0)] = 2
    pvr.loc[(close_diff < 0) & (volume_diff >= 0)] = 3
    pvr.loc[(close_diff < 0) & (volume_diff < 0)] = 4

    # Name and Category
    pvr.name = f"PVR"
    pvr.category = "volume"

    return pvr
