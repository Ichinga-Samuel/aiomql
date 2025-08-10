# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.utils import v_offset, v_pos_default, v_series



def _mcgd(x, n, k):
    d = (k * n * (x[1] / x[0]) ** 4)
    x[1] = (x[0] + ((x[1] - x[0]) / d))
    return x[1]


def mcgd(
    close: Series, length: Int = None, c: IntFloat = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """McGinley Dynamic Indicator

    This indicator, by John R. McGinley, is not a moving average but a
    differential smoothing technique.

    Sources:
        * John R. McGinley, a Certified Market Technician (CMT) and former
          editor of the Market Technicians Association's Journal of
          Technical Analysis.
        * [investopedia](https://www.investopedia.com/articles/forex/09/mcginley-dynamic-indicator.asp)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        c (float): Denominator multiplier. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Note:
        Sometimes ```c``` is set to ```0.6```.
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, length)

    if close is None:
        return

    c = float(c) if isinstance(c, float) and 0 < c <= 1 else 1
    offset = v_offset(offset)

    # Calculate
    close = close.copy()

    mcg_ds = close[0:].rolling(2, min_periods=2) \
        .apply(_mcgd, kwargs={"n": length, "k": c}, raw=True)

    # Offset
    if offset != 0:
        mcg_ds = mcg_ds.shift(offset)

    # Fill
    if "fillna" in kwargs:
        mcg_ds.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    mcg_ds.name = f"MCGD_{length}"
    mcg_ds.category = "overlap"

    return mcg_ds
