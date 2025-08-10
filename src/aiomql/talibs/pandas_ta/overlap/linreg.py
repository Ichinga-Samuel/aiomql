# -*- coding: utf-8 -*-
from sys import float_info as sflt
from numpy import arctan, nan, pi, zeros_like
from numpy.version import version as np_version
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.utils import (
    strided_window,
    v_offset,
    v_pos_default,
    v_series,
    v_talib,
    zero
)



def linreg(
    close: Series, length: Int = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Linear Regression Moving Average

    This indicator is a simplified version of Standard Linear Regression. It is
    one variable rolling regression whereas a Standard Linear Regression is
    between two or more variables.

    Sources:
        * [TA Lib](https://ta-lib.org)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        angle (bool): Returns the slope angle in radians.
            Default: ```False```
        degrees (bool): Return the slope angle in degrees.
            Default: ```False```
        intercept (bool): Return the intercept. Default: ```False```
        r (bool): Return the 'r' correlation. Default: ```False```
        slope (bool): Return the slope. Default: ```False```
        tsf (bool): Return the Time Series Forecast value.
            Default: ```False```
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Warning:
        TA-Lib Correlation: ```np.float64(0.9985638477660118)```

    Tip:
        Corrective contributions welcome!
    """
    # Validate
    length = v_pos_default(length, 14)
    close = v_series(close, length)

    if close is None:
        return

    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    angle = kwargs.pop("angle", False)
    intercept = kwargs.pop("intercept", False)
    degrees = kwargs.pop("degrees", False)
    r = kwargs.pop("r", False)
    slope = kwargs.pop("slope", False)
    tsf = kwargs.pop("tsf", False)

    # Calculate
    np_close = close.to_numpy()

    if Imports["talib"] and mode_tal and not r:
        from talib import LINEARREG, LINEARREG_ANGLE, LINEARREG_INTERCEPT, LINEARREG_SLOPE, TSF
        if tsf:
            linreg = TSF(close, timeperiod=length)
        elif slope:
            linreg = LINEARREG_SLOPE(close, timeperiod=length)
        elif intercept:
            linreg = LINEARREG_INTERCEPT(close, timeperiod=length)
        elif angle:
            linreg = LINEARREG_ANGLE(close, timeperiod=length)
        else:
            linreg = LINEARREG(close, timeperiod=length)
    else:
        linreg_ = zeros_like(np_close)
        # [1, 2, ..., n] from 1 to n keeps Sum(xy) low
        x = range(1, length + 1)
        x_sum = 0.5 * length * (length + 1)
        x2_sum = x_sum * (2 * length + 1) / 3
        divisor = length * x2_sum - x_sum * x_sum

        # Needs to be reworked outside the method
        def linear_regression(series):
            y_sum = series.sum()
            xy_sum = (x * series).sum()

            m = (length * xy_sum - x_sum * y_sum) / divisor
            if slope:
                return m
            b = (y_sum * x2_sum - x_sum * xy_sum) / divisor
            if intercept:
                return b

            if angle:
                theta = arctan(m)
                if degrees:
                    theta *= 180 / pi
                return theta

            if r:
                y2_sum = (series * series).sum()
                rn = length * xy_sum - x_sum * y_sum
                rd = (divisor * (length * y2_sum - y_sum * y_sum)) ** 0.5
                if zero(rd) == 0:
                    rd = sflt.epsilon
                return rn / rd

            return m * length + b if not tsf else m * (length - 1) + b

        if np_version >= "1.20.0":
            from numpy.lib.stride_tricks import sliding_window_view
            linreg_ = [
                linear_regression(_) for _ in sliding_window_view(
                    np_close, length)
            ]

        else:
            linreg_ = [
                linear_regression(_) for _ in strided_window(
                    np_close, length)
            ]

        linreg = Series([nan] * (length - 1) + linreg_, index=close.index)

    # Offset
    if offset != 0:
        linreg = linreg.shift(offset)

    # Fill
    if "fillna" in kwargs:
        linreg.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    linreg.name = f"LINREG"
    if slope:
        linreg.name += "m"
    if intercept:
        linreg.name += "b"
    if angle:
        linreg.name += "a"
    if r:
        linreg.name += "r"

    linreg.name += f"_{length}"
    linreg.category = "overlap"

    return linreg
