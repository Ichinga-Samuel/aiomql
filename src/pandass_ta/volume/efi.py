# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.ma import ma
from pandas_ta.utils import (
    v_drift,
    v_mamode,
    v_offset,
    v_pos_default,
    v_series
)



def efi(
    close: Series, volume: Series, length: Int = None,
    mamode: str = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Elder's Force Index

    This indicator attempts to quantify movement magnitude as well as
    potential reversals and price corrections.

    Sources:
        * [motivewave](https://www.motivewave.com/studies/elders_force_index.htm)
        * [tradingview](https://www.tradingview.com/wiki/Elder%27s_Force_Index_(EFI))

    Parameters:
        close (pd.Series): ```close``` Series
        volume (pd.Series): ```volume``` Series
        length (int): The period. Default: ```13```
        mamode (str): See ```help(ta.ma)```. Default: ```"ema"```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 13)
    close = v_series(close, length)
    volume = v_series(volume, length)

    if close is None or volume is None:
        return

    mamode = v_mamode(mamode, "ema")
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    pv_diff = close.diff(drift) * volume
    efi = ma(mamode, pv_diff, length=length)

    # Offset
    if offset != 0:
        efi = efi.shift(offset)

    # Fill
    if "fillna" in kwargs:
        efi.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    efi.name = f"EFI_{length}"
    efi.category = "volume"

    return efi
