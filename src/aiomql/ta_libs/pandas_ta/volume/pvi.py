# -*- coding: utf-8 -*-
from numba import njit
from numpy import empty, float64, zeros_like
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.ma import ma
from pandas_ta.utils import (
    v_bool,
    v_mamode,
    v_offset,
    v_pos_default,
    v_series
)


@njit(cache=True)
def nb_pvi(np_close, np_volume, initial):
    result = zeros_like(np_close, dtype=float64)
    result[0] = initial

    m = np_close.size
    for i in range(1, m):
        if np_volume[i] > np_volume[i - 1]:
            result[i] = result[i - i] * (np_close[i] / np_close[i - 1])
        else:
            result[i] = result[i - i]

    return result



def pvi(
    close: Series, volume: Series, length: Int = None, initial: Int = None,
    mamode: str = None, overlay: bool = None, offset: Int = None,
    **kwargs: DictLike
) -> DataFrame:
    """Positive Volume Index

    This indicator attempts to identify where smart money is active.

    Sources:
        * [investopedia](https://www.investopedia.com/terms/p/pvi.asp)
        * [sierrachart](https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=101)

    Parameters:
        close (pd.Series): ```close``` Series
        volume (pd.Series): ```volume``` Series
        length (int): The period. Default: ```255```
        initial (int): Initial value. Default: ```100```
        mamode (str): See ```help(ta.ma)```. Default: ```"ema"```
        overlay (bool): Overlay ```initial```. Default: ```False```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 2 columns

    Note:
        Commonly paired with [nvi](volume.md/#src.pandas_ta.volume.nvi.nvi)
    """
    # Validate
    length = v_pos_default(length, 255)
    close = v_series(close, length + 1)
    volume = v_series(volume, length + 1)

    if close is None or volume is None:
        return

    mamode = v_mamode(mamode, "ema")
    overlay = v_bool(overlay, False)
    if overlay:
        initial = close.iloc[0]
    initial = v_pos_default(initial, 100)
    offset = v_offset(offset)

    # Calculate
    np_close, np_volume = close.to_numpy(), volume.to_numpy()
    _pvi = nb_pvi(np_close, np_volume, initial)

    pvi = Series(_pvi, index=close.index)
    pvi_ma = ma(mamode, pvi, length=length)

    # Offset
    if offset != 0:
        pvi = pvi.shift(offset)
        pvi_ma = pvi_ma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        pvi.fillna(kwargs["fillna"], inplace=True)
        pvi_ma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _mode = mamode.lower()[0] if len(mamode) else ""
    _props = f"{_mode}_{length}"
    pvi.name = f"PVI"
    pvi_ma.name = f"PVI{_props}"
    pvi.category = pvi_ma.category = "volume"

    data = { pvi.name: pvi}
    if np_close.size > length + 1:
        data[pvi_ma.name] = pvi_ma
    df = DataFrame(data, index=close.index)

    # Name and Category
    df.name = pvi.name
    df.category = pvi.category

    return df
