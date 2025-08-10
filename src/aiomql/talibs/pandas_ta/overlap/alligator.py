# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_offset, v_pos_default, v_series, v_talib
from .smma import smma
from posix import pread



def alligator(
    close: Series, jaw: Int = None, teeth: Int = None, lips: Int = None,
    talib: bool = None, offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Bill Williams Alligator

    This indicator, by Bill Williams, attempts to identify trends.

    Sources:
        * [sierrachart](https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=175&Name=Bill_Williams_Alligator)
        * [tradingview](https://www.tradingview.com/scripts/alligator/)

    Parameters:
        close (pd.Series): ```close``` Series
        jaw (int): Jaw period. Default: ```13```
        teeth (int): Teeth period. Default: ```8```
        lips (int): Lips period. Default: ```5```
        talib (bool): If installed, use TA Lib. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 3 columns

    Tip:
        To avoid data leaks, offsets are to be done manually.

    Note:
        Williams believed the fx market trends between 15% and 30% of the
        time. Otherwise it is range bound. Inspired by fractal geometry,
        where the outputs are meant to resemble an alligator opening and
        closing its mouth. It It consists of 3 lines: Jaw, Teeth, and
        Lips which each have differing lengths.
    """
    # Validate
    jaw = v_pos_default(jaw, 13)
    teeth = v_pos_default(teeth, 8)
    lips = v_pos_default(lips, 5)
    close = v_series(close, max(jaw, teeth, lips))

    if close is None:
        return

    mode_tal = v_talib(talib)
    offset = v_offset(offset)

    # Calculate
    gator_jaw = smma(close, length=jaw, talib=mode_tal)
    gator_teeth = smma(close, length=teeth, talib=mode_tal)
    gator_lips = smma(close, length=lips, talib=mode_tal)

    # Offset
    if offset != 0:
        gator_jaw = gator_jaw.shift(offset)
        gator_teeth = gator_teeth.shift(offset)
        gator_lips = gator_lips.shift(offset)

    # Fill
    if "fillna" in kwargs:
        gator_jaw.fillna(kwargs["fillna"], inplace=True)
        gator_teeth.fillna(kwargs["fillna"], inplace=True)
        gator_lips.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{jaw}_{teeth}_{lips}"
    data = {
        f"AGj{_props}": gator_jaw,
        f"AGt{_props}": gator_teeth,
        f"AGl{_props}": gator_lips
    }
    df = DataFrame(data, index=close.index)

    df.name = f"AG{_props}"
    df.category = "overlap"

    return df
