# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.ma import ma
from pandas_ta.utils import v_mamode, v_offset, v_pos_default, v_series



def bias(
    close: Series, length: Int = None, mamode: str = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Bias

    This indicator computes the Rate of Change between the source and a
    moving average.

    Sources:
        * Few internet resources on definitive definition.

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```26```
        mamode (str): See ```help(ta.ma)```. Default: ```"sma"```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 26)
    close = v_series(close, length)

    if close is None:
        return

    mamode = v_mamode(mamode, "sma")
    offset = v_offset(offset)

    # Calculate
    bma = ma(mamode, close, length=length, **kwargs)
    bias = (close / bma) - 1

    # Offset
    if offset != 0:
        bias = bias.shift(offset)

    # Fill
    if "fillna" in kwargs:
        bias.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    bias.name = f"BIAS_{bma.name}"
    bias.category = "momentum"

    return bias
