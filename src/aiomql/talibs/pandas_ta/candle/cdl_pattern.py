# -*- coding: utf-8 -*-
from pandas import Series, DataFrame
from pandas_ta._typing import DictLike, Int, IntFloat, List, Union
from pandas_ta.maps import Imports
from pandas_ta.utils import v_offset, v_scalar, v_series
from pandas_ta.candle import cdl_doji, cdl_inside



ALL_PATTERNS = [
    "2crows", "3blackcrows", "3inside", "3linestrike", "3outside",
    "3starsinsouth", "3whitesoldiers", "abandonedbaby", "advanceblock",
    "belthold", "breakaway", "closingmarubozu", "concealbabyswall",
    "counterattack", "darkcloudcover", "doji", "dojistar", "dragonflydoji",
    "engulfing", "eveningdojistar", "eveningstar", "gapsidesidewhite",
    "gravestonedoji", "hammer", "hangingman", "harami", "haramicross",
    "highwave", "hikkake", "hikkakemod", "homingpigeon", "identical3crows",
    "inneck", "inside", "invertedhammer", "kicking", "kickingbylength",
    "ladderbottom", "longleggeddoji", "longline", "marubozu", "matchinglow",
    "mathold", "morningdojistar", "morningstar", "onneck", "piercing",
    "rickshawman", "risefall3methods", "separatinglines", "shootingstar",
    "shortline", "spinningtop", "stalledpattern", "sticksandwich", "takuri",
    "tasukigap", "thrusting", "tristar", "unique3river", "upsidegap2crows",
    "xsidegap3methods"
]


def cdl_pattern(
    open_: Series, high: Series, low: Series, close: Series,
    name: Union[str, List[str]] = "all", scalar: IntFloat = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Candle Pattern

    This function wraps TA Lib candle patterns.

    Sources:
        * [TA Lib](https://ta-lib.org)

    Parameters:
        open_ (pd.Series): ```open``` Series
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        name (Union[str, List[str]]): Pattern name or a list of pattern names.
            Default: ```"all"```
        scalar (float): Scalar. Default: ```100```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): Replaces ```na```'s with ```value```.

    Returns:
        (pd.DataFrame): Pattern Column(s)

    Warning: TA Lib
        TA Lib must be installed
    """
    # Validate Arguments
    open_ = v_series(open_, 1)
    high = v_series(high, 1)
    low = v_series(low, 1)
    close = v_series(close, 1)

    if open_ is None or high is None or low is None or close is None:
        return

    offset = v_offset(offset)
    scalar = v_scalar(scalar, 100)

    pta_patterns = {"doji": cdl_doji, "inside": cdl_inside}

    if name == "all":
        name = ALL_PATTERNS

    if isinstance(name, str):
        name = [name]

    if Imports["talib"]:
        import talib.abstract as tala

    result = {}
    for n in name:
        if n not in ALL_PATTERNS:
            print(f"[X] There is no candle pattern named {n} available!")
            continue

        if n in pta_patterns:
            pattern_result = pta_patterns[n](
                open_, high, low, close, offset=offset, scalar=scalar, **kwargs
            )
            if not isinstance(pattern_result, Series):
                continue
            result[pattern_result.name] = pattern_result

        else:
            if not Imports["talib"]:
                print(f"[i] Requires TA-Lib to use {n}. (pip install TA-Lib)")
                continue

            pf = tala.Function(f"CDL{n.upper()}")
            pattern_result = Series(
                0.01 * scalar * pf(open_, high, low, close, **kwargs)
            )
            pattern_result.index = close.index

            # Offset
            if offset != 0:
                pattern_result = pattern_result.shift(offset)

            # Fill
            if "fillna" in kwargs:
                pattern_result.fillna(kwargs["fillna"], inplace=True)
            result[f"CDL_{n.upper()}"] = pattern_result

    if len(result) == 0:
        return

    # Name and Category
    df = DataFrame(result)
    df.name = "CDL_PATTERN"
    df.category = "candle"
    return df

cdl = cdl_pattern  # Alias
