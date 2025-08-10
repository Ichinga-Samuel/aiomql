# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.utils import v_offset, v_pos_default, v_series



def quantile(
    close: Series, length: Int = None, q: IntFloat = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Rolling Quantile

    Calculates a rolling Quantile.

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```30```
        q (float): The quantile. Default: ```0.5```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 30)
    if "min_periods" in kwargs and kwargs["min_periods"] is not None:
        min_periods = int(kwargs["min_periods"])
    else:
        min_periods = length
    close = v_series(close, max(length, min_periods))

    if close is None:
        return

    q = float(q) if isinstance(q, float) and 0 < q < 1 else 0.5
    offset = v_offset(offset)

    # Calculate
    quantile = close.rolling(length, min_periods=min_periods).quantile(q)

    # Offset
    if offset != 0:
        quantile = quantile.shift(offset)

    # Fill
    if "fillna" in kwargs:
        quantile.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    quantile.name = f"QTL_{length}_{q}"
    quantile.category = "statistics"

    return quantile
