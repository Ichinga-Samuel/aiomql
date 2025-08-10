# -*- coding: utf-8 -*-
from numpy import isnan
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.utils import (
    v_mamode,
    v_offset,
    v_pos_default,
    v_series,
    v_tradingview
)
from pandas_ta.volatility import atr



def cksp(
    high: Series, low: Series, close: Series,
    p: Int = None, x: IntFloat = None, q: Int = None,
    tvmode: bool = None, mamode: str = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Chande Kroll Stop

    This indicator, by Tushar Chande and Stanley Kroll, attempts to identify
    trends with long and short stops.

    Sources:
        * "The New Technical Trader", Wiley 1st ed. ISBN 9780471597803, page 95
        * [multicharts](https://www.multicharts.com/discussion/viewtopic.php?t=48914)

    Parameters:
        close (pd.Series): ```close``` Series
        p (int): ATR and first stop period; see Note.
            Default: ```10``` for both modes
        x (float): ATR scalar; see Note. Default: ```1``` or ```3```
        q (int): Second stop period; see Note. Default: ```9``` or ```20```
        tvmode (bool): Trading View mode. Default: ```True```
        mamode (str): See ```help(ta.ma)```. Default: ```None```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 2 columns

    Note: Book vs TradingView Defaults
        * Book: ```p=10, x=3, q=20, ma="sma"```
        * Trading View: ```p=10, x=1, q=9,  ma="rma"```
    """
    # Validate
    mode_tv = v_tradingview(tvmode)
    p = v_pos_default(p, 10)
    # TODO: clean up x and q
    x = float(x) if isinstance(x, float) and x > 0 else 1 if tvmode is True else 3
    q = int(q) if isinstance(q, float) and q > 0 else 9 if tvmode is True else 20
    _length = p + q

    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    mamode = v_mamode(mamode, "rma") if mode_tv else v_mamode(mamode, "sma")
    offset = v_offset(offset)

    # Calculate
    atr_ = atr(high=high, low=low, close=close, length=p, mamode=mamode)
    if atr_ is None or all(isnan(atr_)):
        return

    long_stop_ = high.rolling(p).max() - x * atr_
    long_stop = long_stop_.rolling(q).max()

    short_stop_ = low.rolling(p).min() + x * atr_
    short_stop = short_stop_.rolling(q).min()

    # Offset
    if offset != 0:
        long_stop = long_stop.shift(offset)
        short_stop = short_stop.shift(offset)

    # Fill
    if "fillna" in kwargs:
        long_stop.fillna(kwargs["fillna"], inplace=True)
        short_stop.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{p}_{x}_{q}"
    long_stop.name = f"CKSPl{_props}"
    short_stop.name = f"CKSPs{_props}"
    long_stop.category = short_stop.category = "trend"

    data = {long_stop.name: long_stop, short_stop.name: short_stop}
    df = DataFrame(data, index=close.index)
    df.name = f"CKSP{_props}"
    df.category = long_stop.category

    return df
