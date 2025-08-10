# -*- coding: utf-8 -*-
from functools import partial

from numpy import nan
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, IntFloat, Union
from pandas_ta.utils._math import zero
from pandas_ta.utils._validate import (
    v_bool,
    v_drift,
    v_float,
    v_int,
    v_offset,
    v_series
)



__all__ = [
    "above",
    "above_value",
    "below",
    "below_value",
    "cross",
    "cross_value",
    "signals",
    "tsignals",
    "xsignals"
]



def above(
    x: Series, y: Series, asint: bool = True, offset: Int = None, **kwargs
) -> Series:
    """Above

    Determines if each ```x``` value is above (or ```>=```) each ```y``` value.

    Parameters:
        x (Series): ```x```
        y (Series): ```y```
        asint (bool): Returns as ```Int```.
        offset (Int): Post shift. Default: ```0```

    Returns:
        (Series): State where ```x >=  y```.

    Example:
        ```py
        x = Series([4, 2, 0, -1, 1])
        y = Series([1, 1, 1, 1, 1])

        x_above_y = ta.above(x, y)
        # x_above_y = Series([1, 1, 0, 0, 1])
        ```
    """
    return partial(_above_below, above=True)(x, y, asint=asint, offset=offset, **kwargs)


def above_value(
    x: Series, value: IntFloat, asint: bool = True,
    offset: Int = None, **kwargs
) -> Series:
    """Above Value

    Determines if each ```x``` value is above (or ```>=```) a
    constant ```value```.

    Parameters:
        x (Series): ```x```
        value (IntFloat): Value to compare with ```x```.
        asint (bool): Returns as ```Int```.

    Returns:
        (Series): State where ```x >= y```.

    Example:
        ```py
        x = Series([4, 2, 0, -1, 1])
        x_above_1 = ta.above_value(x, 1)
        # x_above_1 = Series([1, 1, 0, 0, 1])
        ```
    """
    if not isinstance(value, (int, float)):
        print("[X] value is not a number")
        return
    y = Series(value, index=x.index, name=f"{value}".replace(".", "_"))
    return partial(_above_below, above=True)(x, y, asint=asint, offset=offset, **kwargs)


def below(
    x: Series, y: Series, asint: bool = True, offset: Int = None, **kwargs
) -> Series:
    """Below

    Determines if each ```x``` value is below (or ```<=```) each ```y``` value.

    Parameters:
        x (Series): ```x```
        y (Series): ```y```
        asint (bool): Returns as ```Int```.
        offset (Int): Post shift. Default: ```0```

    Returns:
        (Series): State where ```x <= y```.

    Example:
        ```py
        x = Series([4, 2, 0, -1, 1])
        y = Series([1, 1, 1, 1, 1])

        x_below_y = ta.below(x, y)
        # x_below_y = Series([0, 0, 1, 1, 1])
        ```
    """
    return partial(_above_below, above=False)(x, y, asint=asint, offset=offset, **kwargs)


def below_value(
    x: Series, value: IntFloat, asint: bool = True,
    offset: Int = None, **kwargs
) -> Series:
    """Below Value

    Determines if each ```x``` value is below (or ```<=```) a
    constant ```value```.

    Parameters:
        x (Series): ```x```
        value (IntFloat): Value to compare with ```x```.
        asint (bool): Returns as ```Int```.
        offset (Int): Post shift. Default: ```0```

    Returns:
        (Series): State where ```x <= y```.

    Example:
        ```py
        x = Series([4, 2, 0, -1, 1])
        x_below_1 = ta.below_value(x, 1)
        # x_below_1 = Series([0, 0, 1, 1, 1])
        ```
    """
    if not isinstance(value, (int, float)):
        print("[X] value is not a number")
        return
    y = Series(value, index=x.index, name=f"{value}".replace(".", "_"))
    return partial(_above_below, above=False)(x, y, asint=asint, offset=offset, **kwargs)


def cross(
    x: Series, y: Series,
    above: bool = True, equal: bool = True,
    asint: bool = True, offset: Int = None,
    **kwargs: DictLike
) -> Series:
    """Cross

    Determines where ```x``` crosses ```y```, either _above_ or _below_,
    strictly (_equal_) or not.

    Parameters:
        x (Series): ```x```
        y (Series): ```y```
        above (bool): Check above. Check below, set ```above=False```
        equal (bool): At least/most, ```=```, check.
        asint (bool): Returns as ```Int```.
        offset (Int): Post shift. Default: ```0```

    Returns:
        (Series): Values where ```x``` crosses ```y```.

    Example:
        ```py
        x = Series([4, 2, 0, -1, 1])
        y = Series([1, 1, 1, 1, 1])

        # Cross Above Examples
        x_xae_y = ta.cross(x, y, above=True, equal=True)
        # x_xae_y = Series([0, 0, 0, 0, 1])

        x_xa_y = ta.cross(x, y, above=True, equal=False)
        # x_xa_y = Series([0, 0, 0, 0, 0])

        # Cross Below Examples
        x_xbe_y = ta.cross(x, y, above=False, equal=True)
        # x_xbe_y = Series([0, 0, 1, 0, 1])

        x_xb_y = ta.cross(x, y, above=False, equal=False)
        # x_xb_y = Series([0, 0, 1, 0, 0])
        ```
    """
    # Validate
    x = v_series(x)
    y = v_series(y)
    offset = v_offset(offset)

    x.apply(zero)
    y.apply(zero)

    # Calculate
    if above:
        current = x >= y if equal else x > y
        previous = x.shift(1) < y.shift(1)
    else:
        current = x <= y if equal else x < y
        previous = x.shift(1) > y.shift(1)

    cross = current & previous
    # ensure there is no cross on the first entry
    cross.iloc[0] = False

    if asint:
        cross = cross.astype(int)

    # Offset
    if offset != 0:
        cross = cross.shift(offset)

    # Name and Category
    cross.name = f"{x.name}_{'XA' if above else 'XB'}_{y.name}"
    cross.category = "signal"

    return cross


def cross_value(
    x: Series, value: IntFloat,
    above: bool = True, equal: bool = True,
    asint: bool = True, offset: Int = None,
    **kwargs
) -> Series:
    """Cross Value

    Determines where ```x``` crosses a constant ```value```, either _above_
    or _below_, strictly (_equal_) or not.

    Parameters:
        x (Series): ```x```
        value (IntFloat): Value to compare with ```x```.
        above (bool): Check above. Check below, set ```above=False```
        equal (bool): At least/most, ```=```, check.
        asint (bool): Returns as ```Int```.
        offset (Int): Post shift. Default: ```0```

    Returns:
        (Series): Values where ```x``` crosses ```y```.

    Example:
        ```py
        x = Series([4, 2, 0, -1, 1])

        # Cross Above Examples
        x_xae_y = ta.cross_value(x, 1, above=True, equal=True)
        # x_xae_y = Series([0, 0, 0, 0, 1])

        x_xa_y = ta.cross_value(x, 1, above=True, equal=False)
        # x_xa_y = Series([0, 0, 0, 0, 0])

        # Cross Below Examples
        x_xbe_y = ta.cross_value(x, 1, above=False, equal=True)
        # x_xbe_y = Series([0, 0, 1, 0, 1])

        x_xb_y = ta.cross_value(x, 1, above=False, equal=False)
        # x_xb_y = Series([0, 0, 1, 0, 0])
        ```
    """
    y = Series(value, index=x.index, name=f"{value}".replace(".", "_"))
    return cross(x, y, above, equal, asint, offset, **kwargs)



def signals(
    indicator: Series, xa: IntFloat = None, xb: IntFloat = None,
    cross_values: bool = None, xseries: Series = None,
    xseries_a: Series = None, xseries_b: Series = None,
    cross_series: bool = None, offset: Int = None
) -> DataFrame:
    """Signals

    Mulitfuncational signal checker that determines whether an
    indicator crosses above/below value or Series.

    Parameters:
        indicator (Series): Indicator to check for signal crossings.
        cross_values (bool): Check if crossed value.
        xseries (Series): Cross Series
        xseries_a (Series): Cross Above Series
        xseries_b (Series): Cross Below Series
        cross_series (bool): Check if crossed ```xseries```.

    Other Parameters:
        xa (IntFloat): Crossing above value.
        xb (IntFloat): Crossing below value.
        offset (Int): Post shift. Default: ```0```

    Returns:
        (DataFrame): 2 columns

    Note:
        See sources of: ```er```, ```macd```, ```rsi```, and ```rsx```
        for examples of use.
    """
    df = DataFrame()

    if xa is not None and isinstance(xa, (int, float)):
        if cross_values:
            xa_start = cross_value(indicator, xa, above=True, offset=offset)
            xa_end = cross_value(indicator, xa, above=False, offset=offset)

            df[xa_start.name] = xa_start
            df[xa_end.name] = xa_end
        else:
            xd_above = above_value(indicator, xa, offset=offset)
            df[xd_above.name] = xd_above

    if xb is not None and isinstance(xb, (int, float)):
        if cross_values:
            xb_start = cross_value(indicator, xb, above=True, offset=offset)
            xb_end = cross_value(indicator, xb, above=False, offset=offset)

            df[xb_start.name] = xb_start
            df[xb_end.name] = xb_end
        else:
            xd_below = below_value(indicator, xb, offset=offset)
            df[xd_below.name] = xd_below

    # xseries is the default value for both xseries_a and xseries_b
    if xseries_a is None:
        xseries_a = xseries
    if xseries_b is None:
        xseries_b = xseries

    if xseries_a is not None and v_series(xseries_a):
        if cross_series:
            xsa = cross(indicator, xseries_a, above=True, offset=offset)
        else:
            xsa = above(indicator, xseries_a, offset=offset)

        df[xsa.name] = xsa

    if xseries_b is not None and v_series(xseries_b):
        if cross_series:
            xsb = cross(indicator, xseries_b, above=False, offset=offset)
        else:
            xsb = below(indicator, xseries_b, offset=offset)

        df[xsb.name] = xsb

    return df


def _above_below(
    x: Series, y: Series,
    above: bool = True, asint: bool = True,
    offset: Int = None, **kwargs
) -> Series:
    """Above / Below

    Determines if ```x``` is above or below ```y```.

    Parameters:
        x (Series): ```x```
        y (Series): ```y```
        above (bool): Above check. Below: ```above=False```
        equal (bool): At least/most, ```=```, check.
        asint (bool): Returns as ```Int```.
        offset (Int): Post shift. Default: ```0```

    Returns:
        (Series): Values where ```x``` values are above/below ```y``` values.
    """
    # Verify
    x = v_series(x)
    y = v_series(y)
    offset = v_offset(offset)

    x.apply(zero)
    y.apply(zero)

    # Calculate
    if above:
        current = x >= y
    else:
        current = x <= y

    if asint:
        current = current.astype(int)

    # Offset
    if offset != 0:
        current = current.shift(offset)

    # Name and Category
    current.name = f"{x.name}_{'A' if above else 'B'}_{y.name}"
    current.category = "signal"

    return current



def tsignals(
    trend: Series, asbool: bool = None,
    trade_offset: Int = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Trend Signals

    This function creates Trend, Trades, Entries and Exit values per bar when
    given a trend condition e.g. ```trend = close > sma(close, 50)```.

    Source:
        * Kevin Johnson

    Parameters:
        trend (pd.Series): ```trend``` Series. Boolean or integer values of
            ```0``` and ```1```
        asbool (bool): Return booleans. Default: ```False```
        trade_offset (value): Shift trade entries/exits with live: ```0``` and
            backesting: ```1```. Default: ```0```
        drift (int): Difference amount. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 4 columns

    Note: Column Detail
        * Trends (trend: 1, no trend: 0)
        * Trades (Enter: 1, Exit: -1, Otherwise: 0)
        * Entries (entry: 1, nothing: 0)
        * Exits (exit: 1, nothing: 0)

    Note: Details
        A ```trend``` is a state or condition, that is as simple
        as ```Close > MA``` or something more complex that has boolean
        or integer (trend: 1, no trend: 0) values.

    Tip: VectorBT
        * For backtesting, set ```trade_offset=1```.
        * Setting ```asbool=True``` is useful for backtesting with vectorbt's
          ```Portfolio.from_signal(close, entries, exits)``` method.

    Example:
        These are two different outcomes for each (long/short) position and
        depends on the source and it's behavior.

        Signals when ```Close > SMA50(Close)```

            ta.tsignals(close > ta.sma(close, 50), asbool=False)

        Signals when ```EMA(Close, 8) > EMA(Close, 21)```

            ta.tsignals(ta.ema(close, 8) > ta.ema(close, 21), asbool=True)

    Warning:
        Check ALL outcomes BEFORE making an Issue
    """
    # Validate
    trend = v_series(trend)
    if trend is None:
        return

    asbool = v_bool(asbool, False)
    trade_offset = v_int(trade_offset, 0)
    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    trends = trend.astype(int)
    trades = trends.diff(drift).shift(trade_offset).fillna(0).astype(int)
    entries = (trades > 0).astype(int)
    exits = (trades < 0).abs().astype(int)

    if asbool:
        trends = trends.astype(bool)
        entries = entries.astype(bool)
        exits = exits.astype(bool)

    data = {
        f"TS_Trends": trends,
        f"TS_Trades": trades,
        f"TS_Entries": entries,
        f"TS_Exits": exits,
    }
    df = DataFrame(data, index=trends.index)

    # Offset
    if offset != 0:
        df = df.shift(offset)

    # Fill
    if "fillna" in kwargs:
        df.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    df.name = f"TS"
    df.category = "trend"

    return df



def xsignals(
    source: Series,
    xa: Union[IntFloat, Series],
    xb: Union[IntFloat, Series],
    above: bool = True, long: bool = True,
    asbool: bool = None, trade_offset: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Cross Signals

    This function creates Trend, Trades, Entries and Exits values per bar
    for crossing events.

    Sources:
        * Kevin Johnson

    Parameters:
        source (pd.Series): ```source``` Signal
        xa (pd.Series): Series the Signal crosses above if ```above=True```
        xb (pd.Series): Series the Signal crosses below if ```above=True```
        above (bool): The ```source``` crossing; below is ```False```.
            Default: ```True```
        long (bool): The ```source``` position; short is ```False```.
            Default: ```True```
        offset (int): Post shift. Default: ```0```
        asbool (bool): Return booleans. Default: ```False```
        trade_offset (value): Shift trade entries/exits with live: ```0``` and
            backesting: ```1```. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 4 columns

    Note: Column Detail
        * Trends  (trend: 1, no trend: 0)
        * Trades  (Enter: 1, Exit: -1, Otherwise: 0)
        * Entries (entry: 1, nothing: 0)
        * Exits   (exit: 1, nothing: 0)

    Tip: VectorBT
        * For backtesting, set ```trade_offset=1```.
        * Setting ```asbool=True``` is useful for backtesting with vectorbt's
          ```Portfolio.from_signal(close, entries, exits)``` method.

    Example:
        These are two different outcomes for each (long/short) position and
        depends on the source and it's behavior.

            rsi = df.ta.rsi()

        When RSI crosses above 20 and then below 80 in a long position:

            ta.xsignals(source=rsi, xa=20, xb=80, above=True, long=True)
            # Simpler
            # ta.xsignals(rsi, 20, 80, True, True)

        When RSI crosses below 20 and then above 80 in a long position:

            ta.xsignals(source=rsi, xa=20, xb=80, above=False, long=True)
            # Simpler
            # ta.xsignals(rsi, 20, 80, False, True)

        * Similarly, short positions (```long=False```) also differ depending
          on ```above``` state.

    Warning:
        Check ALL parameter combination outcomes BEFORE making an Issue.
    """
    # Validate
    source = v_series(source)
    if source is None:
        return

    offset = v_offset(offset)

    # Calculate
    if above:
        entries = cross_value(source, xa)
        exits = -cross_value(source, xb, above=False)
    else:
        entries = cross_value(source, xa, above=False)
        exits = -cross_value(source, xb)
    trades = entries + exits

    # Modify trades to fill gaps for trends
    trades.replace({0: nan}, inplace=True)
    trades.ffill(limit_area="inside", inplace=True) # or trades.bfill(limit_area="inside", inplace=True)
    trades.fillna(0, inplace=True)

    trends = (trades > 0).astype(int)
    if not long:
        trends = 1 - trends

    tskwargs = {
        "asbool": asbool,
        "trade_offset": trade_offset,
        "offset": offset
    }
    df = tsignals(trends, **tskwargs)

    # Offset handled by tsignals
    DataFrame({
        f"XS_LONG": df.TS_Trends,
        f"XS_SHORT": 1 - df.TS_Trends
    })

    # Fill
    if "fillna" in kwargs:
        df.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    df.name = f"XS"
    df.category = "trend"

    return df
