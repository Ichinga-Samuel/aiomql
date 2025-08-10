# -*- coding: utf-8 -*-
import re as re_
from contextlib import redirect_stdout
from io import StringIO
from sys import float_info as sflt
from webbrowser import open as webbrowser_open

from numpy import argmax, argmin, float64
from numba import njit
from pandas import DataFrame, Series

from pandas_ta._typing import Array, Int, IntFloat, ListStr, TextIO, Union
import pandas_ta.custom as custom
from pandas_ta.utils._validate import v_bool, v_pos_default, v_series, v_str
from pandas_ta.maps import Category, Imports

__all__ = [
    "camelCase2Title",
    "category_files",
    "help",
    "ms2secs",
    "non_zero_range",
    "recent_maximum_index",
    "recent_minimum_index",
    "pd_rma",
    "signed_series",
    "simplify_columns",
    "speed_test",
    "tal_ma",
    "unsigned_differences",
]



def camelCase2Title(x: str) -> str | None:
    """camelCase2Title

    Converts Camel Case to Title

    Parameters:
        x (str): Input string.

    Sources:
        * [stackoverflow](https://stackoverflow.com/questions/5020906/python-convert-camel-case-to-space-delimited-using-regex-and-taking-acronyms-in)

    Returns:
        (str | None): Title Case string or None
    """
    if isinstance(x, str) and len(x):
        return re_.sub("([a-z])([A-Z])",r"\g<1> \g<2>", x).title()
    return None


def category_files(category: str) -> list:
    """Category Files

    Helper function to return all filenames in the category directory.

    Parameters:
        category (str): String name of a Indicator Category

    Returns:
        (list): List of filenames of Category
    """
    files = [
        x.stem
        for x in list(Path(f"pandas_ta/{category}/").glob("*.py"))
        if x.stem != "__init__"
    ]
    return files


def help(s: str) -> None | TextIO:
    s = v_str(s, "")

    _categories = list(Category.keys())
    _dataframes = ["pandas", "dataframe", "extension"]
    _events = ["events", "signals"]
    _features = ["bugs", "features", "contributing"]
    _help = ["help", "support"]
    _how2 = ["how2", "how to", "usage"]
    _mp = ["custom", "multiprocessing"]
    _studies = ["study", "studies"]
    KEYWORDS = _dataframes + _events + _features + _help \
        + _how2 + _studies + _categories + _mp

    www = "https://www.pandas-ta.dev"
    if s == "":
        out = f'\nSearch words:\n\t{", ".join(sorted(KEYWORDS))}\n'
        out += '\nExample: df.ta.help("usage")'
        # print(f'\nSearch words:\n\t{", ".join(sorted(KEYWORDS))}\n\nExample: df.ta.help("usage")')
        print(out)
    elif s in _categories:
        webbrowser_open(f"{www}/api/{s.lower()}", new=1)
    elif s in _dataframes:
        webbrowser_open(f"{www}/api/ta", new=1)
    elif s in _events:
        webbrowser_open(f"{www}/api/events", new=1)
    elif s in _features:
        webbrowser_open(f"{www}/support/bugs-and-features", new=1)
    elif s in _help:
        webbrowser_open(f"{www}/support", new=1)
    elif s in _how2:
        webbrowser_open(f"{www}/support/how-to", new=1)
    elif s in _mp:
        webbrowser_open(f"{www}/getting-started/usage", new=1)
    elif s in _studies:
        webbrowser_open(f"{www}/api/studies", new=1)
    else:
        webbrowser_open(f"{www}", new=1)


def ms2secs(ms, p: Int) -> IntFloat:
    return round(0.001 * ms, p)


def non_zero_range(x: Series, y: Series) -> Series:
    """Non-Zero Range

    Calculates the difference of two Series plus epsilon to any zero values.

    Parameters:
        x (Series): Series of 'x's
        y (Series): Series of 'y's

    Returns:
        (Series): Value of ```x - y + epsilon``` per bar.
    """
    diff = x - y
    if diff.eq(0).any().any():
        diff += sflt.epsilon
    return diff


def recent_maximum_index(x) -> Int:
    """Recent Maximum Index

    Index of the largest value in ```x```

    Paramters:
        x (Series): ```x``` values

    Returns:
        (int): Index of the largest value
    """
    return int(argmax(x[::-1]))


def recent_minimum_index(x) -> Int:
    """Recent Minimum Index

    Index of the smallest value in ```x```

    Paramters:
        x (Series): ```x``` values

    Returns:
        (int): Index of the smallest value
    """
    return int(argmin(x[::-1]))


def pd_rma(x: Series, n: Int) -> Series:
    """RMA (Pandas)

    Pandas Implementation of RMA.

    Parameters:
        x (Series): ```x``` Series
        n (Int): Bars of lookback. Default: ```0.5```

    Returns:
        (Series): RMA
    """
    x = v_series(x)
    if x is None:
        return
    a = (1.0 / n) if n > 0 else 0.5
    return x.ewm(alpha=a, min_periods=n).mean()


def signed_series(x: Series, initial: Int, lag: Int = None) -> Series:
    """Signed Series

    Returns a Signed Series with or without an initial value

    Parameters:
        x (Series): Series of 'x's
        initial (int): Set inital values of the signed Series.
        lag (int): Difference between adjacent items. Default: ```1```

    Return:
        (Series): Signed Series
    """
    initial = None
    if initial is not None and not isinstance(lag, str):
        initial = initial
    x = v_series(x)
    lag = v_pos_default(lag, 1)
    sign = x.diff(lag)
    sign[sign > 0] = 1
    sign[sign < 0] = -1
    sign.iloc[0] = initial    # sign.iloc[:lag-1]
    return sign


def simplify_columns(df: DataFrame, n: Int=3) -> ListStr:
    """Simplify Columns

    Helper method for managing columns used by Squeeze and Squeeze Pro.

    Parameters:
        df (DataFrame): DataFrame with the columns
        n (int): Default:  ```3```

    Returns:
        (ListStr): List of string column
    """
    df.columns = df.columns.str.lower()
    return [c.split("_")[0][n - 1:n] for c in df.columns]


def speed_test(df: DataFrame,
        only: ListStr = None, excluded: ListStr = None,
        top: Int = None, talib: bool = False,
        ascending: bool = False, sortby: str = "secs",
        gradient: bool = False, places: Int = 5, stats: bool = False,
        verbose: bool = False, silent: bool = False
    ) -> DataFrame:
    """Speed Test

    Given a standard ohlcv DataFrame, the Speed Test calculates the
    speed of each indicator of the DataFrame Extension: df.ta.<indicator>().

    Parameters:
        df (pd.DataFrame): DataFrame with _ohlcv_ columns
        only (list): List of indicators to run. Default: ```None```
        excluded (list): List of indicators to exclude. Default: ```None```
        top (Int): Return a DataFrame the 'top' values. Default: ```None```
        talib (bool): Enable TA Lib. Default: ```False```
        ascending (bool): Ascending Order. Default: ```False```
        sortby (str): Options: "ms", "secs". Default: ```"secs"```
        gradient (bool): Returns a DataFrame the 'top' values with gradient
            styling. Default: ```False```
        places (Int): Decimal places. Default: ```5```
        stats (bool): Returns a Tuple of two DataFrames. The second tuple
            contains Stats on the performance time. Default: ```False```
        verbose (bool): Display more info. Default: ```False```
        silent (bool): Display nothing. Default: ```False```

    Returns:
        (pd.DataFrame): if ```stats=False```
        (pd.DataFrame, pd.DataFrame): if ```stats=True```
    """
    if df.empty:
        print(f"[X] No DataFrame")
        return
    talib = v_bool(talib, False)
    top = int(top) if isinstance(top, int) and top > 0 else None
    stats = v_bool(stats, False)
    verbose = v_bool(verbose, False)
    silent = v_bool(silent, False)

    _ichimoku = ["ichimoku"]
    if excluded is None and isinstance(only, list) and len(only) > 0:
        _indicators = only
    elif only is None and isinstance(excluded, list) and len(excluded) > 0:
        _indicators = df.ta.indicators(as_list=True, exclude=_ichimoku + excluded)
    else:
        _indicators = df.ta.indicators(as_list=True, exclude=_ichimoku)

    if len(_indicators) == 0: return None

    _iname = "Indicator"
    if verbose:
        print()
        data = _speed_group(df.copy(), _indicators, talib, _iname, places)
    else:
        _this = StringIO()
        with redirect_stdout(_this):
            data = _speed_group(df.copy(), _indicators, talib, _iname, places)
        _this.close()

    tdf = DataFrame.from_dict(data)
    tdf.set_index(_iname, inplace=True)
    tdf.sort_values(by=sortby, ascending=ascending, inplace=True)

    total_timedf = DataFrame(
        tdf.describe().loc[['min', '50%', 'mean', 'max']]).T
    total_timedf["total"] = tdf.sum(axis=0).T
    total_timedf = total_timedf.T

    _div = "=" * 60
    _observations = f"  Bars{'[talib]' if talib else ''}: {df.shape[0]}"
    _quick_slow = "Quickest" if ascending else "Slowest"
    _title = f"  {_quick_slow} Indicators"
    _perfstats = f"Time Stats:\n{total_timedf}"
    if top:
        _title = f"  {_quick_slow} {top} Indicators [{tdf.shape[0]}]"
        tdf = tdf.head(top)

    if not silent:
        print(f"\n{_div}\n{_title}\n{_observations}\n{_div}\n{tdf}\n\n{_div}\n{_perfstats}\n\n{_div}\n")

    if isinstance(gradient, bool) and gradient:
        return tdf.style.background_gradient("autumn_r"), total_timedf

    if stats:
        return tdf, total_timedf
    else:
        return tdf


def tal_ma(name: str) -> Int:
    """TA Lib MA

    Helper Function that returns the Enum value for TA Lib's MA Type

    Parameters:
        name (str): Abbreivated Name of the Moving Average

    Returns:
        (int): The equivalent TA Lib MA Enum value for ```name```
    """
    if Imports["talib"] and isinstance(name, str) and len(name) > 1:
        from talib import MA_Type
        name = name.lower()
        if name == "sma":
            return MA_Type.SMA   # 0
        elif name == "ema":
            return MA_Type.EMA   # 1
        elif name == "wma":
            return MA_Type.WMA   # 2
        elif name == "dema":
            return MA_Type.DEMA  # 3
        elif name == "tema":
            return MA_Type.TEMA  # 4
        elif name == "trima":
            return MA_Type.TRIMA  # 5
        elif name == "kama":
            return MA_Type.KAMA  # 6
        elif name == "mama":
            return MA_Type.MAMA  # 7
        elif name == "t3":
            return MA_Type.T3    # 8
    return 0  # Default: SMA -> 0


def unsigned_differences(
    x: Series, lag: Int = None, asint: bool = None
) -> Union[Series, Series]:
    """Unsigned Differences

    Returns two Series, an unsigned positive and unsigned negative series based
    on the differences of the original series. The positive series are only the
    increases and the negative series are only the decreases.

    Parameters:
        x (Series): Series of 'x's
        lag (int): Difference between adjacent items. Default: ```1```
        asint (bool): Returns as ```Int```. Default: ```False```

    Example:
        ta.unsigned_differences(Series([3, 2, 2, 1, 1, 5, 6, 6, 7, 5, 3]))

    Returns:
        (Union[Series, Series]): Positive Series, Negative Series
    """
    asint = v_bool(asint, False)
    lag = int(lag) if lag is not None else 1
    negative = x.diff(lag)
    negative.fillna(0, inplace=True)
    positive = negative.copy()

    positive[positive <= 0] = 0
    positive[positive > 0] = 1

    negative[negative >= 0] = 0
    negative[negative < 0] = 1

    if asint:
        positive = positive.astype(int)
        negative = negative.astype(int)

    return positive, negative


def _speed_group(
        df: DataFrame, group: ListStr = [], talib: bool = False,
        index_name: str = "Indicator", p: Int = 4
    ) -> ListStr:
    result = []
    for i in group:
        r = df.ta(i, talib=talib, timed=True)
        if r is None:
            print(f"[S] {i} skipped due to returning None")
            continue # ta.pivots() sometimes returns None
        ms = float(r.timed.split(" ")[0].split(" ")[0])
        result.append({index_name: i, "ms": ms, "secs": ms2secs(ms, p)})
    return result
