# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.maps import Imports
from pandas_ta.utils import (
    v_bool,
    v_drift,
    v_mamode,
    v_offset,
    v_pos_default,
    v_scalar,
    v_series,
    v_talib
)
from pandas_ta.volatility import atr



def natr(
    high: Series, low: Series, close: Series,
    length: Int = None, scalar: IntFloat = None, mamode: str = None,
    talib: bool = None, prenan: bool = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Normalized Average True Range

    This indicator applies a normalizer to Average True Range.

    Sources:
        * [tradingtechnologies](https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/normalized-average-true-range-natr/)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```20```
        scalar (float): Scalar. Default: ```100```
        mamode (str): See ```help(ta.ma)```. Default: ```"ema"```
        talib (bool): If installed, use TA Lib. Default: ```True```
        prenan (bool): Sets initial values to ```np.nan``` based
            on ```drift```. Default: ```False```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Warning:
        TA-Lib Correlation: ```np.float64(0.9506743353852364)```

    Tip:
        Corrective contributions welcome!
    """
    # Validate
    length = v_pos_default(length, 14)
    _length = length + 1
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    scalar = v_scalar(scalar, 100)
    mamode = v_mamode(mamode, "ema")
    mode_tal = v_talib(talib)
    prenan = v_bool(prenan, False)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import NATR
        natr = NATR(high, low, close, length)
    else:
        natr = (scalar / close) * \
        atr(
            high=high, low=low, close=close, length=length,
            mamode=mamode, drift=drift, talib=mode_tal,
            prenan=prenan, offset=offset, **kwargs
        )

    # Offset
    if offset != 0:
        natr = natr.shift(offset)

    # Fill
    if "fillna" in kwargs:
        natr.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    natr.name = f"NATR_{length}"
    natr.category = "volatility"

    return natr
