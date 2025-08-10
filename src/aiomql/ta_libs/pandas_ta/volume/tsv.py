# -*- coding: utf-8 -*-
from numpy import isnan
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.ma import ma
from pandas_ta.utils import (
    signed_series,
    v_drift,
    v_mamode,
    v_pos_default,
    v_offset,
    v_series,
    zero
)



def tsv(
    close: Series, volume: Series,
    length: Int = None, signal: Int = None,
    mamode: str = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Time Segmented Value

    This indicator, by Worden Brothers Inc., attempts to quantify the amount
    of money flowing at various time segments of price and time; similar to
    On Balance Volume.

    Sources:
        * [tc2000](https://help.tc2000.com/m/69404/l/747088-time-segmented-volume)
        * [tradingview](https://www.tradingview.com/script/6GR4ht9X-Time-Segmented-Volume/)
        * [usethinkscript](https://usethinkscript.com/threads/time-segmented-volume-for-thinkorswim.519/)

    Parameters:
        close (pd.Series): ```close``` Series
        volume (pd.Series): ```volume``` Series
        length (int): The period. Default: ```18```
        signal (int): Signal period. Default: ```10```
        mamode (str): See ```help(ta.ma)```. Default: ```"sma"```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 3 columns

    Note:
        * The zero line is called the baseline.
        * Entries and exits signals occur when crossing the baseline.
    """
    # Validate
    length = v_pos_default(length, 18)
    signal = v_pos_default(signal, 10)
    _length = max(length, signal) + 1
    close = v_series(close, _length)

    if close is None:
        return

    mamode = v_mamode(mamode, "sma")
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    signed_volume = volume * signed_series(close, 1)     # > 0
    signed_volume[signed_volume < 0] = -signed_volume    # < 0
    signed_volume.apply(zero)                            # ~ 0
    cvd = signed_volume * close.diff(drift)

    tsv = cvd.rolling(length).sum()
    if all(isnan(tsv)):
        return  # Emergency Break

    signal_ = ma(mamode, tsv, length=signal)
    ratio = tsv / signal_

    # Offset
    if offset != 0:
        tsv = tsv.shift(offset)
        signal_ = signal.shift(offset)
        ratio = ratio.shift(offset)

    # Fill
    if "fillna" in kwargs:
        tsv.fillna(kwargs["fillna"], inplace=True)
        signal_.fillna(kwargs["fillna"], inplace=True)
        ratio.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{length}_{signal}"
    tsv.name = f"TSV{_props}"
    signal_.name = f"TSVs{_props}"
    ratio.name = f"TSVr{_props}"
    tsv.category = signal_.category = ratio.category = "volume"

    data = {tsv.name: tsv, signal_.name: signal_, ratio.name: ratio}
    df = DataFrame(data, index=close.index)
    df.name = f"TSV{_props}"
    df.category = tsv.category

    return df
