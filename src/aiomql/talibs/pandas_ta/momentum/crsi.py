# -*- coding: utf-8 -*-
from pandas import Series
from pandas_ta._typing import Array, DictLike, Int, IntFloat
from pandas_ta.maps import Imports
from pandas_ta.momentum.rsi import rsi
from pandas_ta.utils import (
    consecutive_streak,
    percent_rank,
    v_drift,
    v_offset,
    v_pos_default,
    v_scalar,
    v_series,
    v_talib,
)



def crsi(
    close: Series, rsi_length: Int = None, streak_length: Int = None,
    rank_length: Int = None, scalar: IntFloat = None, talib: bool = None,
    drift: Int = None, offset: Int = None, **kwargs: DictLike,
) -> Series:
    """Connors Relative Strength Index

    This indicator attempts to identify momentum and potential reversals at
    "overbought" or "oversold" conditions.

    Sources:
        * [alvarezquanttrading](https://alvarezquanttrading.com/blog/connorsrsi-analysis/)
        * [tradingview](https://www.tradingview.com/support/solutions/43000502017-connors-rsi-crsi/)
        * An Introduction to ConnorsRSI. Connors Research Trading Strategy Series.
          Connors, L., Alvarez, C., & Radtke, M. (2012). ISBN 978-0-9853072-9-5.

    Parameters:
        close (pd.Series): ```close``` Series
        rsi_length (int): The RSI period. Default: ```3```
        streak_length (int): Streak RSI period. Default: ```2```
        rank_length (int): Percent Rank length. Default: ```100```
        scalar (float): Scalar. Default: ```100```
        talib (bool): If installed, use TA Lib. Default: ```True```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    rsi_length = v_pos_default(rsi_length, 3)
    streak_length = v_pos_default(streak_length, 2)
    rank_length = v_pos_default(rank_length, 100)
    _length = max(rsi_length, streak_length, rank_length)
    close = v_series(close, _length)

    if "length" in kwargs:
        kwargs.pop("length")

    if close is None:
        return None

    scalar = v_scalar(scalar, 100)
    mode_tal = v_talib(talib)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    np_close = close.to_numpy()
    streak = Series(consecutive_streak(np_close), index=close.index)

    if Imports["talib"] and mode_tal:
        from talib import RSI
        _rsi = RSI(close, rsi_length)
        _streak_rsi = RSI(streak, streak_length)
    else:
        # Both TA-lib and Pandas-TA use the Wilder's RSI
        # and its smoothing function
        _rsi = rsi(
            close, length=rsi_length, scalar=scalar, talib=talib,
            drift=drift, offset=offset, **kwargs
        )

        _streak_rsi = rsi(
            streak, length=streak_length, scalar=scalar, talib=talib,
            drift=drift, offset=offset, **kwargs
        )

    _crsi = (_rsi + _streak_rsi + percent_rank(close, rank_length)) / 3.0
    crsi = Series(_crsi, index=close.index)

    # Offset
    if offset != 0:
        crsi = crsi.shift(offset)

    # Fill
    if "fillna" in kwargs:
        crsi.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    crsi.name = f"CRSI_{rsi_length}_{streak_length}_{rank_length}"
    crsi.category = "momentum"

    return crsi
