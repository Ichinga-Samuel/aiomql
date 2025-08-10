# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import signed_series, v_bool, v_offset, v_series



def pvol(
    close: Series, volume: Series, signed: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Price-Volume

    This indicator returns the product of Price & Volume (Price * Volume).

    Parameters:
        close (pd.Series): ```close``` Series
        volume (pd.Series): ```volume``` Series
        signed (bool): Return with signs. Default: ```False```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    close = v_series(close)
    volume = v_series(volume)
    signed = v_bool(signed, False)
    offset = v_offset(offset)

    # Calculate
    pvol = close * volume
    if signed:
        pvol *= signed_series(close, 1)

    # Offset
    if offset != 0:
        pvol = pvol.shift(offset)

    # Fill
    if "fillna" in kwargs:
        pvol.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    pvol.name = f"PVOL"
    pvol.category = "volume"

    return pvol
