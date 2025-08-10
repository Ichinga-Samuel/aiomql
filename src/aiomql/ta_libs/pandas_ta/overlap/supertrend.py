# -*- coding: utf-8 -*-
from numpy import nan
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.overlap import hl2
from pandas_ta.utils import v_mamode, v_offset, v_pos_default, v_series
from pandas_ta.volatility import atr



def supertrend(
    high: Series, low: Series, close: Series,
    length: Int = None, atr_length: Int = None,
    multiplier: IntFloat = None,
    atr_mamode : str = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Supertrend

    This indicator attempts to identify trend direction as well as support and
    resistance levels.

    Sources:
        * [freebsensetips](http://www.freebsensetips.com/blog/detail/7/What-is-supertrend-indicator-its-calculation)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```7```
        atr_length (int): ATR period. Default: ```length```
        multiplier (float): Coefficient for upper and lower band distance to
            midrange. Default: ```3.0```
        atr_mamode (str) : MA type to be used for ATR calculation.
            See ```help(ta.ma)```. Default: ```"rma"```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 4 columns
    """
    # Validate
    length = v_pos_default(length, 7)
    atr_length = v_pos_default(atr_length, length)
    high = v_series(high, length + 1)
    low = v_series(low, length + 1)
    close = v_series(close, length + 1)

    if high is None or low is None or close is None:
        return

    multiplier = v_pos_default(multiplier, 3.0)
    atr_mamode = v_mamode(atr_mamode, "rma")
    offset = v_offset(offset)

    # Calculate
    m = close.size
    dir_, trend = [1] * m, [0] * m
    long, short = [nan] * m, [nan] * m

    hl2_ = hl2(high, low)
    matr = multiplier * atr(high, low, close, atr_length, mamode=atr_mamode)
    lb = hl2_ - matr
    ub = hl2_ + matr

    for i in range(1, m):
        if close.iat[i] > ub.iat[i - 1]:
            dir_[i] = 1
        elif close.iat[i] < lb.iat[i - 1]:
            dir_[i] = -1
        else:
            dir_[i] = dir_[i - 1]
            if dir_[i] > 0 and lb.iat[i] < lb.iat[i - 1]:
                lb.iat[i] = lb.iat[i - 1]
            if dir_[i] < 0 and ub.iat[i] > ub.iat[i - 1]:
                ub.iat[i] = ub.iat[i - 1]

        if dir_[i] > 0:
            trend[i] = long[i] = lb.iat[i]
        else:
            trend[i] = short[i] = ub.iat[i]

    trend[0] = nan
    dir_[:length] = [nan] * length

    _props = f"_{length}_{multiplier}"
    data = {
        f"SUPERT{_props}": trend,
        f"SUPERTd{_props}": dir_,
        f"SUPERTl{_props}": long,
        f"SUPERTs{_props}": short
    }
    df = DataFrame(data, index=close.index)

    df.name = f"SUPERT{_props}"
    df.category = "overlap"

    # Offset
    if offset != 0:
        df = df.shift(offset)

    # Fill
    if "fillna" in kwargs:
        df.fillna(kwargs["fillna"], inplace=True)

    return df
