# -*- coding: utf-8 -*-
from numpy import float64, zeros_like
from numba import njit
from pandas import Series
from pandas_ta._typing import Array, DictLike, Int
from pandas_ta.utils import v_offset, v_pos_default, v_series, v_str



# Exponential Decay - https://tulipindicators.org/edecay
@njit(cache=True)
def nb_exponential_decay(x, n):
    m, rate = x.size, 1.0 - (1.0 / n)

    result = zeros_like(x, dtype=float64)
    result[0] = x[0]

    for i in range(1, m):
        result[i] = max(0, x[i], result[i - 1] * rate)

    return result


# Linear Decay - https://tulipindicators.org/decay
@njit(cache=True)
def nb_linear_decay(x, n):
    m, rate = x.size, 1.0 / n

    result = zeros_like(x, dtype=float64)
    result[0] = x[0]

    for i in range(1, m):
        result[i] = max(0, x[i], result[i - 1] - rate)

    return result


def decay(
    close: Series, length: Int = None, mode: str = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Decay

    This function creates a decay moving forward from prior signals.

    Sources:
        * [tulipindicators](https://tulipindicators.org/decay)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```1```
        mode (str): Either ```"linear"``` or ```"exp"``` (exponetional)
            Default: ```"linear"```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    close = v_series(close, length)

    if close is None:
        return

    length = v_pos_default(length, 1)
    mode = v_str(mode, "linear")
    offset = v_offset(offset)

    # Calculate
    _mode, np_close = "L", close.to_numpy()

    if mode in ["exp", "exponential"]:
        _mode = "EXP"
        result = nb_exponential_decay(np_close, length)
    else:  # "linear"
        result = nb_linear_decay(np_close, length)

    result = Series(result, index=close.index)

    # Offset
    if offset != 0:
        result = result.shift(offset)

    # Fill
    if "fillna" in kwargs:
        result.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    result.name = f"{_mode}DECAY_{length}"
    result.category = "trend"

    return result
