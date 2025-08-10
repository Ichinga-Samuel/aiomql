# -*- coding: utf-8 -*-
from numpy import log
from pandas import Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.utils import v_offset, v_pos_default, v_series



def entropy(
    close: Series, length: Int = None, base: IntFloat = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Entropy

    This indicator attempts to quantify the unpredictability of the data,
    or equivalently, its average information. It is a rolling entropy
    calculation.

    Sources:
        * [wikipedia](https://en.wikipedia.org/wiki/Entropy_(information_theory))

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        base (float): Logarithmic Base. Default: ```2```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, 2 * length - 1)

    if close is None:
        return

    base = v_pos_default(base, 2.0)
    offset = v_offset(offset)

    # Calculate
    p = close / close.rolling(length).sum()
    entropy = (-p * log(p) / log(base)).rolling(length).sum()

    # Offset
    if offset != 0:
        entropy = entropy.shift(offset)

    # Fill
    if "fillna" in kwargs:
        entropy.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    entropy.name = f"ENTP_{length}"
    entropy.category = "statistics"

    return entropy
