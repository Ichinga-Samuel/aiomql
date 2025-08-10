# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.overlap import linreg
from pandas_ta.utils import v_offset, v_pos_default, v_series



def cti(
    close: Series, length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Correlation Trend Indicator

    This oscillator, by John Ehlers' in 2020, attempts to identify the
    magnitude and direction of a trend using linear regession.

    Note:
        This is a wrapper for ```ta.linreg(close, r=True)```.

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```12```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 12)
    close = v_series(close, length)

    if close is None:
        return

    offset = v_offset(offset)

    # Calculate
    cti = linreg(close, length=length, r=True)

    # Offset
    if offset != 0:
        cti = cti.shift(offset)

    # Fill
    if "fillna" in kwargs:
        cti.fillna(method=kwargs["fillna"], inplace=True)

    # Name and Category
    cti.name = f"CTI_{length}"
    cti.category = "momentum"

    return cti
