# -*- coding: utf-8 -*-
from pandas import concat, DataFrame, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.maps import Imports
from pandas_ta.overlap import ema
from pandas_ta.utils import (
    signals,
    v_offset,
    v_pos_default,
    v_series,
    v_talib
)



def macd(
    close: Series, fast: Int = None, slow: Int = None,
    signal: Int = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Moving Average Convergence Divergence

    This indicator attempts to identify trends.

    Sources:
        * [tradingview](https://www.tradingview.com/wiki/MACD_(Moving_Average_Convergence/Divergence))
        * [tradingview (AS Mode)](https://tr.tradingview.com/script/YFlKXHnP/)

    Parameters:
        close (pd.Series): ```close``` Series
        fast (int): Fast MA period. Default: ```12```
        slow (int): Slow MA period. Default: ```26```
        signal (int): Signal period. Default: ```9```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        asmode (value): Enable AS version of MACD. Default: ```False```
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 3 columns
    """
    # Validate
    fast = v_pos_default(fast, 12)
    slow = v_pos_default(slow, 26)
    signal = v_pos_default(signal, 9)
    if slow < fast:
        fast, slow = slow, fast
    _length = slow + signal - 1
    close = v_series(close, _length)

    if close is None:
        return

    mode_tal = v_talib(talib)
    offset = v_offset(offset)
    as_mode = kwargs.setdefault("asmode", False)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import MACD
        macd, signalma, histogram = MACD(close, fast, slow, signal)
    else:
        fastma = ema(close, length=fast, talib=mode_tal)
        slowma = ema(close, length=slow, talib=mode_tal)

        macd = fastma - slowma
        macd_fvi = macd.loc[macd.first_valid_index():, ]
        signalma = ema(close=macd_fvi, length=signal, talib=mode_tal)
        histogram = macd - signalma

    if as_mode:
        macd = macd - signalma
        macd_fvi = macd.loc[macd.first_valid_index():, ]
        signalma = ema(close=macd_fvi, length=signal, talib=mode_tal)
        histogram = macd - signalma

    # Offset
    if offset != 0:
        macd = macd.shift(offset)
        histogram = histogram.shift(offset)
        signalma = signalma.shift(offset)

    # Fill
    if "fillna" in kwargs:
        macd.fillna(kwargs["fillna"], inplace=True)
        histogram.fillna(kwargs["fillna"], inplace=True)
        signalma.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _asmode = "AS" if as_mode else ""
    _props = f"_{fast}_{slow}_{signal}"
    macd.name = f"MACD{_asmode}{_props}"
    histogram.name = f"MACD{_asmode}h{_props}"
    signalma.name = f"MACD{_asmode}s{_props}"
    macd.category = histogram.category = signalma.category = "momentum"

    data = {
        macd.name: macd,
        histogram.name: histogram,
        signalma.name: signalma
    }
    df = DataFrame(data, index=close.index)
    df.name = f"MACD{_asmode}{_props}"
    df.category = macd.category

    signal_indicators = kwargs.pop("signal_indicators", False)
    if not signal_indicators:
        return df
    else:
        signalsdf = concat(
            [
                df,
                signals(
                    indicator=histogram,
                    xa=kwargs.pop("xa", 0),
                    xb=kwargs.pop("xb", None),
                    xseries=kwargs.pop("xseries", None),
                    xseries_a=kwargs.pop("xseries_a", None),
                    xseries_b=kwargs.pop("xseries_b", None),
                    cross_values=kwargs.pop("cross_values", True),
                    cross_series=kwargs.pop("cross_series", True),
                    offset=offset,
                ),
                signals(
                    indicator=macd,
                    xa=kwargs.pop("xa", 0),
                    xb=kwargs.pop("xb", None),
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
