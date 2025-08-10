# -*- coding: utf-8 -*-
from numpy import nan
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.overlap import ema
from pandas_ta.utils import (
    non_zero_range,
    v_offset,
    v_pos_default,
    v_series
)



def schaff_tc(close: Series, seed: Series, tc_length: int, factor: IntFloat):
    lowest_xmacd = seed.rolling(tc_length).min()
    xmacd_range = non_zero_range(seed.rolling(tc_length).max(), lowest_xmacd)
    m = len(seed)

    # Initialize lists
    stoch1, pf = [0] * m, [0] * m
    stoch2, pff = [0] * m, [0] * m

    for i in range(1, m):
        # %Fast K of MACD
        if lowest_xmacd.iloc[i] > 0:
            stoch1[i] = 100 * ((seed.iloc[i] - lowest_xmacd.iloc[i]) / xmacd_range.iloc[i])
        else:
            stoch1[i] = stoch1[i - 1]
        # Smoothed Calculation for % Fast D of MACD
        pf[i] = round(pf[i - 1] + (factor * (stoch1[i] - pf[i - 1])), 8)

        # find min and max so far
        if i < tc_length:
            # If there are not enough elements for a full tclength window,
            # use what is available
            lowest_pf = min(pf[:i+1])
            highest_pf = max(pf[:i+1])
        else:
            lowest_pf = min(pf[i - tc_length + 1:i + 1])
            highest_pf = max(pf[i - tc_length + 1:i + 1])

        # Ensure non-zero range
        pf_range = highest_pf - lowest_pf if highest_pf - lowest_pf > 0 else 1

        # % of Fast K of PF
        if pf_range > 0:
            stoch2[i] = 100 * ((pf[i] - lowest_pf) / pf_range)
        else:
            stoch2[i] = stoch2[i - 1]
        pff[i] = round(pff[i - 1] + (factor * (stoch2[i] - pff[i - 1])), 8)

    pf_series = Series(pf, index=close.index)
    pff_series = Series(pff, index=close.index)

    return pff_series, pf_series


def stc(
    close: Series, tc_length: Int = None,
    fast: Int = None, slow: Int = None, factor: IntFloat = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Schaff Trend Cycle

    This indicator is an evolved MACD with additional smoothing.

    Sources:
        * [rengel8](https://github.com/rengel8)
        * [prorealcode](https://www.prorealcode.com/prorealtime-indicators/schaff-trend-cycle2/)

    Parameters:
        close (pd.Series): ```close``` Series
        tc_length (int): TC period. (Adjust to the half of cycle)
            Default: ```10```
        fast (int): Fast MA period. Default: ```12```
        slow (int): Slow MA period. Default: ```26```
        factor (float): Smoothing factor for last stoch. calculation.
            Default: ```0.5```
        offset (int): How many bars to shift the results. Default: ```0``

    Other Parameters:
        ma1 (Series): User chosen MA. Default: ```False```
        ma2 (Series): User chosen MA. Default: ```False```
        osc (Series): User chosen oscillator. Default: ```False```
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 3 columns

    Note:
        Can also seed STC with two MAs, ```ma1``` and ```ma2```, or an oscillator ```osc```.

        * ```ma1``` and ```ma2``` are **both** required if this option is used.
    """
    # Validate
    fast = v_pos_default(fast, 12)
    slow = v_pos_default(slow, 26)
    tc_length = v_pos_default(tc_length, 10)
    if slow < fast:
        fast, slow = slow, fast
    _length = max(tc_length, fast, slow)
    close = v_series(close, _length)

    if close is None:
        return

    factor = v_pos_default(factor, 0.5)
    offset = v_offset(offset)

    # Calculate
    # kwargs allows for three more series (ma1, ma2 and osc) which can be passed
    # here ma1 and ma2 input negate internal ema calculations, osc substitutes
    # both ma's.
    ma1 = kwargs.pop("ma1", False)
    ma2 = kwargs.pop("ma2", False)
    osc = kwargs.pop("osc", False)

    if isinstance(ma1, Series) and isinstance(ma2, Series) and not osc:
        ma1 = v_series(ma1, _length)
        ma2 = v_series(ma2, _length)

        if ma1 is None or ma2 is None:
            return
        seed = ma1 - ma2

    elif isinstance(osc, Series):
        osc = v_series(osc, _length)
        if osc is None:
            return
        seed = osc

    else:
        fastma = ema(close, length=fast)
        slowma = ema(close, length=slow)
        seed = fastma - slowma

    pff, pf = schaff_tc(close, seed, tc_length, factor)
    pf[:_length - 1] = nan

    stc = Series(pff, index=close.index)
    macd = Series(seed, index=close.index)
    stoch = Series(pf, index=close.index)

    stc.iloc[:_length - 1] = nan

    # Offset
    if offset != 0:
        stc = stc.shift(offset)
        macd = macd.shift(offset)
        stoch = stoch.shift(offset)

    # Fill
    if "fillna" in kwargs:
        stc.fillna(kwargs["fillna"], inplace=True)
        macd.fillna(kwargs["fillna"], inplace=True)
        stoch.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{tc_length}_{fast}_{slow}_{factor}"
    stc.name = f"STC{_props}"
    macd.name = f"STCmacd{_props}"
    stoch.name = f"STCstoch{_props}"
    stc.category = macd.category = stoch.category = "momentum"

    data = {
        stc.name: stc,
        macd.name: macd,
        stoch.name: stoch
    }
    df = DataFrame(data, index=close.index)
    df.name = f"STC{_props}"
    df.category = stc.category

    return df
