# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.ma import ma
from pandas_ta.maps import Imports
from pandas_ta.utils import (
    v_drift,
    v_mamode,
    v_offset,
    v_pos_default,
    v_series,
    v_talib,
    zero
)



def dm(
    high: Series, low: Series, length: Int = None,
    mamode: str = None, talib: bool = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Directional Movement

    This indicator, by J. Welles Wilder in 1978, attempts to
    determine direction.

    Sources:
        * [sierrachart](https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=24&Name=Directional_Movement_Index)
        * [tradingview](https://www.tradingview.com/pine-script-reference/#fun_dmi)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        mamode (str): See ```help(ta.ma)```. Default: ```"rma"```
        talib (bool): If installed, use TA Lib. Default: ```True```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 2 columns
    """
    # Validate
    length = v_pos_default(length, 14)
    high = v_series(high, length)
    low = v_series(low, length)

    if high is None or low is None:
        return

    mamode = v_mamode(mamode, "rma")
    mode_tal = v_talib(talib)
    drift = v_drift(drift)
    offset = v_offset(offset)

    if Imports["talib"] and mode_tal and high.size and low.size:
        from talib import MINUS_DM, PLUS_DM
        pos = PLUS_DM(high, low, length)
        neg = MINUS_DM(high, low, length)
    else:
        up = high - high.shift(drift)
        dn = low.shift(drift) - low

        pos_ = ((up > dn) & (up > 0)) * up
        neg_ = ((dn > up) & (dn > 0)) * dn

        pos_ = pos_.apply(zero)
        neg_ = neg_.apply(zero)

        # Not the same values as TA Lib's -+DM (Good First Issue)
        pos = ma(mamode, pos_, length=length, talib=mode_tal)
        neg = ma(mamode, neg_, length=length, talib=mode_tal)

    # Offset
    if offset != 0:
        pos = pos.shift(offset)
        neg = neg.shift(offset)

    # Fill
    if "fillna" in kwargs:
        pos.fillna(kwargs["fillna"], inplace=True)
        neg.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{length}"
    data = {f"DMP{_props}": pos, f"DMN{_props}": neg}
    df = DataFrame(data, index=high.index)
    df.name = f"DM{_props}"
    df.category = "momentum"

    return df
