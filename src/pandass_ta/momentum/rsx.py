# -*- coding: utf-8 -*-
from numpy import nan
from pandas_ta._typing import DictLike, Int
from pandas import concat, DataFrame, Series
from pandas_ta.utils import (
    signals,
    v_drift,
    v_offset,
    v_pos_default,
    v_series
)
from shutil import which



def rsx(
    close: Series, length: Int = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Relative Strength Xtra

    This indicator, by Jurik Research, is an enhanced version of the RSI which
    attemps to reduce noise and provide a clearer, though slightly
    delayed, signal.

    Sources:
        * [jurikres](http://www.jurikres.com/catalog1/ms_rsx.htm)
        * [prorealcode](https://www.prorealcode.com/prorealtime-indicators/jurik-rsx/)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```14```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 14)
    close = v_series(close, length)

    if close is None:
        return

    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    m = close.size
    vC, v1C = 0, 0
    v4, v8, v10, v14, v18, v20 = 0, 0, 0, 0, 0, 0

    f0, f8, f10, f18, f20, f28, f30, f38 = 0, 0, 0, 0, 0, 0, 0, 0
    f40, f48, f50, f58, f60, f68, f70, f78 = 0, 0, 0, 0, 0, 0, 0, 0
    f80, f88, f90 = 0, 0, 0

    result = [nan for _ in range(0, length - 1)] + [50]
    for i in range(length, m):
        if f90 == 0:
            f90 = 1.0
            f0 = 0.0
            if length - 1.0 >= 5:
                f88 = length - 1.0
            else:
                f88 = 5.0
            f8 = 100.0 * close.iat[i]
            f18 = 3.0 / (length + 2.0)
            f20 = 1.0 - f18
        else:
            if f88 <= f90:
                f90 = f88 + 1
            else:
                f90 = f90 + 1
            f10 = f8
            f8 = 100 * close.iat[i]
            v8 = f8 - f10
            f28 = f20 * f28 + f18 * v8
            f30 = f18 * f28 + f20 * f30
            vC = 1.5 * f28 - 0.5 * f30
            f38 = f20 * f38 + f18 * vC
            f40 = f18 * f38 + f20 * f40
            v10 = 1.5 * f38 - 0.5 * f40
            f48 = f20 * f48 + f18 * v10
            f50 = f18 * f48 + f20 * f50
            v14 = 1.5 * f48 - 0.5 * f50
            f58 = f20 * f58 + f18 * abs(v8)
            f60 = f18 * f58 + f20 * f60
            v18 = 1.5 * f58 - 0.5 * f60
            f68 = f20 * f68 + f18 * v18
            f70 = f18 * f68 + f20 * f70
            v1C = 1.5 * f68 - 0.5 * f70
            f78 = f20 * f78 + f18 * v1C
            f80 = f18 * f78 + f20 * f80
            v20 = 1.5 * f78 - 0.5 * f80

            if f88 >= f90 and f8 != f10:
                f0 = 1.0
            if f88 == f90 and f0 == 0.0:
                f90 = 0.0

        if f88 < f90 and v20 > 0.0000000001:
            v4 = (v14 / v20 + 1.0) * 50.0
            if v4 > 100.0:
                v4 = 100.0
            if v4 < 0.0:
                v4 = 0.0
        else:
            v4 = 50.0
        result.append(v4)
    rsx = Series(result, index=close.index)

    # Offset
    if offset != 0:
        rsx = rsx.shift(offset)

    # Fill
    if "fillna" in kwargs:
        rsx.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    rsx.name = f"RSX_{length}"
    rsx.category = "momentum"

    signal_indicators = kwargs.pop("signal_indicators", False)
    if not signal_indicators:
        return rsx
    else:
        signalsdf = concat(
            [
                DataFrame({rsx.name: rsx}),
                signals(
                    indicator=rsx,
                    xa=kwargs.pop("xa", 80),
                    xb=kwargs.pop("xb", 20),
                    xseries=kwargs.pop("xseries", None),
                    xseries_a=kwargs.pop("xseries_a", None),
                    xseries_b=kwargs.pop("xseries_b", None),
                    cross_values=kwargs.pop("cross_values", False),
                    cross_series=kwargs.pop("cross_series", True),
                    offset=offset,
                ),
            ],
            axis=1
        )
        return signalsdf
