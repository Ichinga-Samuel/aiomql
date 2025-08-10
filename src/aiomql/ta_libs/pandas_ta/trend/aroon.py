# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.maps import Imports
from pandas_ta.utils import (
    recent_maximum_index,
    recent_minimum_index,
    v_offset,
    v_pos_default,
    v_scalar,
    v_series,
    v_talib
)



def aroon(
    high: Series, low: Series,
    length: Int = None, scalar: IntFloat = None, talib: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Aroon & Aroon Oscillator

    This indicator attempts to identify trends and their magnitude.

    Sources:
        * [tradingtechnologies](https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/aroon-ar/)
        * [tradingview](https://www.tradingview.com/wiki/Aroon)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        length (int): The period. Default: ```14```
        scalar (float): Scalar. Default: ```100```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 3 columns
    """
    # Validate
    length = v_pos_default(length, 14)
    high = v_series(high, length + 1)
    low = v_series(low, length + 1)

    if high is None or low is None:
        return

    scalar = v_scalar(scalar, 100)
    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    if Imports["talib"] and mode_tal:
        from talib import AROON, AROONOSC
        aroon_down, aroon_up = AROON(high, low, length)
        aroon_osc = AROONOSC(high, low, length)
    else:
        periods_from_hh = high.rolling(length + 1) \
            .apply(recent_maximum_index,raw=True)
        periods_from_ll = low.rolling(length + 1) \
            .apply(recent_minimum_index,raw=True)

        aroon_up = aroon_down = scalar
        aroon_up *= 1 - (periods_from_hh / length)
        aroon_down *= 1 - (periods_from_ll / length)
        aroon_osc = aroon_up - aroon_down

    # Offset
    if offset != 0:
        aroon_up = aroon_up.shift(offset)
        aroon_down = aroon_down.shift(offset)
        aroon_osc = aroon_osc.shift(offset)

    # Fill
    if "fillna" in kwargs:
        aroon_up.fillna(kwargs["fillna"], inplace=True)
        aroon_down.fillna(kwargs["fillna"], inplace=True)
        aroon_osc.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    aroon_up.name = f"AROONU_{length}"
    aroon_down.name = f"AROOND_{length}"
    aroon_osc.name = f"AROONOSC_{length}"

    aroon_down.category = aroon_up.category = aroon_osc.category = "trend"

    data = {
        aroon_down.name: aroon_down,
        aroon_up.name: aroon_up,
        aroon_osc.name: aroon_osc
    }
    df = DataFrame(data, index=high.index)
    df.name = f"AROON_{length}"
    df.category = aroon_down.category

    return df
