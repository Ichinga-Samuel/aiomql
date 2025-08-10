# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_drift, v_offset, v_pos_default, v_series
from pandas_ta.volatility import true_range



def vortex(
    high: Series, low: Series, close: Series,
    length: Int = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Vortex

    This indicator attempts to capture positive and negative trend movement
    using two oscillators.

    Sources:
        * [stockcharts](https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:vortex_indicator)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```14```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 2 columns
    """
    # Validate
    length = v_pos_default(length, 14)
    if "min_periods" in kwargs and kwargs["min_periods"] is not None:
        min_periods = int(kwargs["min_periods"])
    else:
        min_periods = length
    _length = max(length, min_periods)
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    tr = true_range(high=high, low=low, close=close)
    tr_sum = tr.rolling(length, min_periods=min_periods).sum()

    vmp = (high - low.shift(drift)).abs()
    vmm = (low - high.shift(drift)).abs()

    vip = vmp.rolling(length, min_periods=min_periods).sum() / tr_sum
    vim = vmm.rolling(length, min_periods=min_periods).sum() / tr_sum

    # Offset
    if offset != 0:
        vip = vip.shift(offset)
        vim = vim.shift(offset)

    # Fill
    if "fillna" in kwargs:
        vip.fillna(kwargs["fillna"], inplace=True)
        vim.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    vip.name = f"VTXP_{length}"
    vim.name = f"VTXM_{length}"
    vip.category = vim.category = "trend"

    data = {vip.name: vip, vim.name: vim}
    df = DataFrame(data, index=close.index)
    df.name = f"VTX_{length}"
    df.category = "trend"

    return df
