# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta.overlap import sma
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.utils import high_low_range, v_percent
from pandas_ta.utils import real_body, v_offset, v_pos_default
from pandas_ta.utils import v_bool, v_scalar, v_series



def cdl_doji(
    open_: Series, high: Series, low: Series, close: Series,
    length: Int = None, factor: IntFloat = None,
    scalar: IntFloat = None, asint: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Doji

    Attempts to identify a "Doji" candle which is shorter than 10% of
    the average of the 10 previous bars High-Low range.

    Sources:
        * [TA Lib](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_CDLDOJI.c)

    Parameters:
        open_ (pd.Series): ```open``` Series
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```10```
        factor (float): Doji value. Default: ```100```
        scalar (float): Scalar. Default: ```100```
        asint (bool): Returns as ```Int```. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        naive (bool): Prefills potential Doji; bodies that are less
            than a percentage, ```factor```, of it's High-Low range.
            Default: ```False```
        fillna (value): Replaces ```na```'s with ```value```.

    Returns:
        (pd.Series): 1 column

    Warning:
        TA-Lib Correlation: ```np.float64(0.9434563530497265)```

    Tip:
        Corrective contributions welcome!
    """
    # Validate
    length = v_pos_default(length, 10)
    open_ = v_series(open_, length)
    high = v_series(high, length)
    low = v_series(low, length)
    close = v_series(close, length)

    if open_ is None or high is None or low is None or close is None:
        return

    factor = v_scalar(factor, 10) if v_percent(factor) else 10
    scalar = v_scalar(scalar, 100)
    asint = v_bool(asint, True)
    offset = v_offset(offset)
    naive = kwargs.pop("naive", False)

    # Calculate
    body = real_body(open_, close).abs()
    hl_range = high_low_range(high, low).abs()
    hl_range_avg = sma(hl_range, length)
    doji = body < 0.01 * factor * hl_range_avg

    if naive:
        doji.iat[:length] = body < 0.01 * factor * hl_range
    if asint:
        doji = scalar * doji.astype(int)

    # Offset
    if offset != 0:
        doji = doji.shift(offset)

    # Fill
    if "fillna" in kwargs:
        doji.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    doji.name = f"CDL_DOJI_{length}_{0.01 * factor}"
    doji.category = "candle"

    return doji
