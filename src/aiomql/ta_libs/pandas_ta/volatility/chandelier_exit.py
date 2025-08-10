# -*- coding: utf-8 -*-
from numpy import isnan, nan
from pandas import Series, DataFrame
from pandas_ta.volatility import atr
from pandas_ta._typing import Int, IntFloat, DictLike
from pandas_ta.utils import (
    v_bool,
    v_drift,
    v_mamode,
    v_pos_default,
    v_offset,
    v_series,
    v_talib
)



def chandelier_exit(
    high: Series, low: Series, close: Series,
    high_length: Int = None, low_length: Int = None,
    atr_length: Int = None, multiplier: IntFloat = None,
    mamode: str = None, talib: bool = None, use_close: bool = None,
    drift: Int = None, offset: Int = None, **kwargs: DictLike
):
    """Chandelier Exit

    This indicator attempts to identify trailing stop-losses based on ATR.

    Sources:
        * [stockcharts](https://school.stockcharts.com/doku.php?id=technical_indicators:chandelier_exit)
        * [tradingview](https://in.tradingview.com/scripts/chandelier/)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        high_length (int): Highest high period. Default: ```22```
        low_length (int): Lowest low period. Default: ```22```
        atr_length (int) : ATR length. Default: ```14```
        multiplier (float): Lower & Upper Bands scalar. Default: ```2.0```
        mamode (str): See ```help(ta.ma)```. Default: ```"rma"```
        talib (bool): If installed, use TA Lib. Default: ```True```
        use_close (bool): Use  ```max(high_length, low_length)``` for
            the ```close```. Default: ```False```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 3 columns
    """
    # Validate
    atr_length = v_pos_default(atr_length, 14)
    high_length = v_pos_default(high_length, 22)
    low_length = v_pos_default(low_length, 22)
    roll_length = max(high_length, low_length)
    _length = max(atr_length, roll_length) + 1

    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    multiplier = v_pos_default(multiplier, 2.0)
    mamode = v_mamode(mamode, "rma")
    mode_tal = v_talib(talib)
    use_close = v_bool(use_close, False)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    atr_ = atr(
        high=high, low=low, close=close, length=atr_length,
        mamode=mamode, talib=mode_tal, drift=drift, offset=offset
    )
    if atr_ is None or all(isnan(atr_)):
        return

    atr_mult = atr_ * multiplier

    if use_close:
        long = close.rolling(roll_length, min_periods=1).max() - atr_mult
        short = close.rolling(roll_length, min_periods=1).min() + atr_mult
    else:
        long = high.rolling(high_length, min_periods=1).max() - atr_mult
        short = low.rolling(low_length, min_periods=1).min() + atr_mult

    uptrend = (close > long.shift(drift)).astype(int)
    downtrend = -(close < short.shift(drift)).astype(int)

    direction = uptrend + downtrend
    if direction.iloc[0] == 0:
        direction.iloc[0] = 1
    direction = direction.replace(0, nan).ffill()

    # Offset
    if offset != 0:
        long = long.shift(offset)
        short = short.shift(offset)
        direction = direction.shift(offset)

    # Fill
    if "fillna" in kwargs:
        long.fillna(kwargs["fillna"], inplace=True)
        short.fillna(kwargs["fillna"], inplace=True)
        direction.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _name = "CHDLREXT"
    _props = f"_{high_length}_{low_length}_{atr_length}_{multiplier}"
    if use_close:
        _props = f"_CLOSE_{_props}"

    data = {
        f"{_name}l{_props}": long,
        f"{_name}s{_props}": short,
        f"{_name}d{_props}": direction
    }
    df = DataFrame(data, index=close.index)
    df.name = f"{_name}{_props}"
    df.category = "volatility"

    return df
