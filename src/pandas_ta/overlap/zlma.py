# -*- coding: utf-8 -*-
from sys import modules as sys_modules
from numpy import isnan
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_mamode, v_offset, v_pos_default, v_series

# Available MAs for zlma
from .dema import dema
from .ema import ema
from .fwma import fwma
from .hma import hma
from .linreg import linreg
from .midpoint import midpoint
from .pwma import pwma
from .rma import rma
from .sinwma import sinwma
from .sma import sma
from .ssf import ssf
from .swma import swma
from .t3 import t3
from .tema import tema
from .trima import trima
from .vidya import vidya
from .wma import wma



def zlma(
    close: Series, length: Int = None, mamode: str = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Zero Lag Moving Average

    This indicator, by John Ehlers and Ric Way, attempts to eliminate the lag
    often introduced in other moving averages.

    Sources:
        * [wikipedia](https://en.wikipedia.org/wiki/Zero_lag_exponential_moving_average)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        mamode (str): One of: "dema", "ema", "fwma", "hma", "linreg",
            "midpoint", "pwma", "rma", "sinwma", "ssf", "swma", "t3",
            "tema", "trima", "vidya", or "wma". Default: ```"ema"```
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

    mamode = v_mamode(mamode, "ema")
    supported_mas = [
        "dema", "ema", "fwma", "hma", "linreg", "midpoint", "pwma", "rma",
        "sinwma", "sma", "ssf", "swma", "t3", "tema", "trima", "vidya", "wma"
    ]

    if mamode not in supported_mas:
        return

    offset = v_offset(offset)

    # Calculate
    lag = int(0.5 * (length - 1))
    close_ = 2 * close - close.shift(lag)

    kwargs.update({"close": close_})
    kwargs.update({"length": length})

    fn = getattr(sys_modules[__name__], mamode)
    zlma = fn(**kwargs)

    if zlma is None or all(isnan(zlma)):
        return  # Emergency Break

    # Offset
    if offset != 0:
        zlma = zlma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        zlma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    zlma.name = f"ZL_{zlma.name}"
    zlma.category = "overlap"

    return zlma
