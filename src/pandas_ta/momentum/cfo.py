# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.overlap import linreg
from pandas_ta.utils import (
    v_drift,
    v_offset,
    v_pos_default,
    v_scalar,
    v_series
)



def cfo(
    close: Series, length: Int = None,
    scalar: IntFloat = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Chande Forcast Oscillator

    This indicator attempts to calculate the percentage difference between
    the actual price and the Time Series Forecast (the endpoint of a
    linear regression line).

    Sources:
        * [fmlabs](https://www.fmlabs.com/reference/default.htm?url=ForecastOscillator.htm)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```9```
        scalar (float): Scalar. Default: ```100```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 9)
    close = v_series(close, length)

    if close is None:
        return

    scalar = v_scalar(scalar, 100)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    # Finding linear regression of Series
    cfo = scalar * (close - linreg(close, length=length, tsf=True)) / close

    # Offset
    if offset != 0:
        cfo = cfo.shift(offset)

    # Fill
    if "fillna" in kwargs:
        cfo.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    cfo.name = f"CFO_{length}"
    cfo.category = "momentum"

    return cfo
