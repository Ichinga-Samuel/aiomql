# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_offset, v_pos_default, v_series



def rma(
    close: Series, length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """wildeR's Moving Average

    This indicator, by Wilder, is simply an EMA where _alpha_ is
    the recipical of its _length_.

    Sources:
        * [incrediblecharts](https://www.incrediblecharts.com/indicators/wilder_moving_average.php)
        * [thinkorswim](https://tlc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/V-Z/WildersSmoothing)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, length)

    if close is None:
        return

    alpha = (1.0 / length) if length > 0 else 0.5
    offset = v_offset(offset)

    rma = close.ewm(alpha=alpha, adjust=False).mean()

    # Offset
    if offset != 0:
        rma = rma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        rma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    rma.name = f"RMA_{length}"
    rma.category = "overlap"

    return rma
