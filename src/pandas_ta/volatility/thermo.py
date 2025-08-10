# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.ma import ma
from pandas_ta.utils import (
    v_bool,
    v_drift,
    v_mamode,
    v_offset,
    v_pos_default,
    v_series
)



def thermo(
    high: Series, low: Series, length: Int = None,
    long: Int = None, short: Int = None,
    mamode: str = None, asint: bool = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Elders Thermometer

    This indicator, by Dr Alexander Elder, attempts to quantify volatility.

    Sources:
        * [motivewave](https://www.motivewave.com/studies/elders_thermometer.htm)
        * [tradingview](https://www.tradingview.com/script/HqvTuEMW-Elder-s-Market-Thermometer-LazyBear/)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        length (int): The period. Default: ```20```
        long (int): Buy factor. Default: ```2```
        short (float): Sell factor. Default: ```0.5```
        mamode (str): See ```help(ta.ma)```. Default: ```"ema"```
        asint (int): Returns as int. Default: ```True```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 4 columns
    """
    # Validate
    length = v_pos_default(length, 20)
    high = v_series(high, length + 1)
    low = v_series(low, length + 1)

    if high is None or low is None:
        return

    long = v_pos_default(long, 2)
    short = v_pos_default(short, 0.5)
    mamode = v_mamode(mamode, "ema")
    asint = v_bool(asint, True)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    thermoL = (low.shift(drift) - low).abs()
    thermoH = (high - high.shift(drift)).abs()

    thermo = thermoL
    thermo = thermo.where(thermoH < thermoL, thermoH)
    thermo.index = high.index

    thermo_ma = ma(mamode, thermo, length=length)
    thermo_long = thermo < (thermo_ma * long)
    thermo_short = thermo > (thermo_ma * short)

    if asint:
        thermo_long = thermo_long.astype(int)
        thermo_short = thermo_short.astype(int)

    # Offset
    if offset != 0:
        thermo = thermo.shift(offset)
        thermo_ma = thermo_ma.shift(offset)
        thermo_long = thermo_long.shift(offset)
        thermo_short = thermo_short.shift(offset)

    # Fill
    if "fillna" in kwargs:
        thermo.fillna(kwargs["fillna"], inplace=True)
        thermo_ma.fillna(kwargs["fillna"], inplace=True)
        thermo_long.fillna(kwargs["fillna"], inplace=True)
        thermo_short.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{length}_{long}_{short}"
    thermo.name = f"THERMO{_props}"
    thermo_ma.name = f"THERMOma{_props}"
    thermo_long.name = f"THERMOl{_props}"
    thermo_short.name = f"THERMOs{_props}"
    thermo.category = thermo_ma.category = "volatility"
    thermo_long.category = thermo_short.category = thermo.category

    data = {
        thermo.name: thermo,
        thermo_ma.name: thermo_ma,
        thermo_long.name: thermo_long,
        thermo_short.name: thermo_short
    }
    df = DataFrame(data, index=high.index)
    df.name = f"THERMO{_props}"
    df.category = thermo.category

    return df
