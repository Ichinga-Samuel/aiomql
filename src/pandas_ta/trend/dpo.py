# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.overlap import sma
from pandas_ta.utils import v_bool, v_offset, v_pos_default, v_series



def dpo(
    close: Series, length: Int = None, centered: bool = True,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Detrend Price Oscillator

    This indicator attempts to detrend (remove the trend) and identify cycles.

    Sources:
        * [fidelity](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/dpo)
        * [stockcharts](http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:detrended_price_osci)
        * [tradingview](https://www.tradingview.com/scripts/detrendedpriceoscillator/)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```20```
        centered (bool): Shift the dpo back by ```int(0.5 * length) + 1```.
            Set to ```False``` to remove data leakage. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Danger: Possible Data Leak
        Set ```centered=False``` to remove data leakage. See [Issue #60]( https://github.com/twopirllc/pandas-ta/issues/60#).
    """
    # Validate
    length = v_pos_default(length, 20)
    close = v_series(close, length + 1)

    if close is None:
        return

    centered = v_bool(centered, True)
    offset = v_offset(offset)

    # Calculate
    t = int(0.5 * length) + 1
    ma = sma(close, length)

    if centered:
        dpo = (close.shift(t) - ma).shift(-t)
    else:
        dpo = close - ma.shift(t)

    # Offset
    if offset != 0:
        dpo = dpo.shift(offset)

    # Fill
    if "fillna" in kwargs:
        dpo.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    dpo.name = f"DPO_{length}"
    dpo.category = "trend"

    return dpo
