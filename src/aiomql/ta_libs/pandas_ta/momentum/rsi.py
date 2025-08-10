# -*- coding: utf-8 -*-
from pandas import DataFrame, concat, Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.maps import Imports
from pandas_ta.ma import ma
from pandas_ta.utils import (
    signals,
    v_drift,
    v_mamode,
    v_offset,
    v_pos_default,
    v_scalar,
    v_series,
    v_talib
)



def rsi(
    close: Series, length: Int = None, scalar: IntFloat = None,
    mamode: str = None, talib: bool = None,
    drift: Int = None, offset: Int = None,
    **kwargs: DictLike
) -> Series:
    """Relative Strength Index

    This oscillator used to attempts to quantify "velocity" and "magnitude".

    Sources:
        * [tradingview](https://www.tradingview.com/wiki/Relative_Strength_Index_(RSI))

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```14```
        scalar (float): Scalar. Default: ```100```
        mamode (str): See ```help(ta.ma)```. Default: ```"rma"```
        talib (bool): If installed, use TA Lib. Default: ```True```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Warning:
        TA-Lib Correlation: ```np.float64(0.9289853267851295)```

    Tip:
        Corrective contributions welcome!
    """
    # Validate
    length = v_pos_default(length, 14)
    close = v_series(close, length + 1)

    if close is None:
        return

    scalar = v_scalar(scalar, 100)
    mamode = v_mamode(mamode, "rma")
    mode_tal = v_talib(talib)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import RSI
        rsi = RSI(close, length)
    else:
        negative = close.diff(drift)
        positive = negative.copy()

        positive[positive < 0] = 0  # Make negatives 0 for the positive series
        negative[negative > 0] = 0  # Make positives 0 for the negative series

        positive_avg = ma(mamode, positive, length=length, talib=mode_tal)
        negative_avg = ma(mamode, negative, length=length, talib=mode_tal)

        rsi = scalar * positive_avg / (positive_avg + negative_avg.abs())

    # Offset
    if offset != 0:
        rsi = rsi.shift(offset)

    # Fill
    if "fillna" in kwargs:
        rsi.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    rsi.name = f"RSI_{length}"
    rsi.category = "momentum"

    signal_indicators = kwargs.pop("signal_indicators", False)
    if not signal_indicators:
        return rsi
    else:
        signalsdf = concat(
            [
                DataFrame({rsi.name: rsi}),
                signals(
                    indicator=rsi,
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
            axis=1,
        )
        return signalsdf
