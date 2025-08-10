# -*- coding: utf-8 -*-
from sys import float_info as sflt
from numpy import sqrt
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.utils import v_bool, v_offset, v_pos_default, v_series



def hwc(
    close: Series, scalar: IntFloat = None, channels: bool = None,
    na: IntFloat = None, nb: IntFloat = None,
    nc: IntFloat = None, nd: IntFloat = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Holt-Winter Channel

    This indicator creates a three-parameter moving average using the
    "Holt-Winters" method.

    Sources:
        * [rengel8](https://github.com/rengel8) (2021-08-11) based on the
          implementation from "MetaTrader 5"
        * [mql5](https://www.mql5.com/en/code/20857)

    Parameters:
        close (pd.Series): ```close``` Series
        scalar (float): Channel scalar. Default: ```1```
        channels (bool): Return width and percentage columns.
            Default: ```True```
        na (float): Smoothed series in range ```[0, 1]```. Default: ```0.2```
        nb (float): Trend value in range ```[0, 1]```. Default: ```0.1```
        nc (float): Seasonality value in range ```[0, 1]```. Default: ```0.1```
        nd (float): Channel value in range ```[0, 1]```. Default: ```0.1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 3 columns
    """
    # Validate
    close = v_series(close, 1)
    scalar = v_pos_default(scalar, 1)
    channels = v_bool(channels, True)
    na = v_pos_default(na, 0.2)
    nb = v_pos_default(nb, 0.1)
    nc = v_pos_default(nc, 0.1)
    nd = v_pos_default(nd, 0.1)
    offset = v_offset(offset)

    if close is None:
        return

    # Calculate Result
    last_a = last_v = last_var = 0
    last_f = last_price = last_result = close.iloc[0]
    lower, result, upper = [], [], []
    chan_pct_width, chan_width = [], []

    m = close.size
    for i in range(m):
        F = (1.0 - na) * (last_f + last_v + 0.5 * last_a) + na * close.iloc[i]
        V = (1.0 - nb) * (last_v + last_a) + nb * (F - last_f)
        A = (1.0 - nc) * last_a + nc * (V - last_v)
        result.append((F + V + 0.5 * A))

        var = (1.0 - nd) * last_var + \
            nd * (last_price - last_result) * (last_price - last_result)
        stddev = sqrt(last_var)
        upper.append(result[i] + scalar * stddev)
        lower.append(result[i] - scalar * stddev)

        if channels:
            # channel width
            chan_width.append(upper[i] - lower[i])
            # channel percentage price position
            chan_pct_width.append(
                (close.iloc[i] - lower[i]) / (upper[i] - lower[i] + sflt.epsilon)
            )

        # update values
        last_price = close.iloc[i]
        last_a = A
        last_f = F
        last_v = V
        last_var = var
        last_result = result[i]

    # Aggregate
    hwc = Series(result, index=close.index)
    hwc_upper = Series(upper, index=close.index)
    hwc_lower = Series(lower, index=close.index)
    if channels:
        hwc_width = Series(chan_width, index=close.index)
        hwc_pctwidth = Series(chan_pct_width, index=close.index)

    # Offset
    if offset != 0:
        hwc = hwc.shift(offset)
        hwc_upper = hwc_upper.shift(offset)
        hwc_lower = hwc_lower.shift(offset)
        if channels:
            hwc_width = hwc_width.shift(offset)
            hwc_pctwidth = hwc_pctwidth.shift(offset)

    # Fill
    if "fillna" in kwargs:
        hwc.fillna(kwargs["fillna"], inplace=True)
        hwc_upper.fillna(kwargs["fillna"], inplace=True)
        hwc_lower.fillna(kwargs["fillna"], inplace=True)
        if channels:
            hwc_width.fillna(kwargs["fillna"], inplace=True)
            hwc_pctwidth.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{scalar}"
    hwc.name = f"HWM{_props}"
    hwc_upper.name = f"HWU{_props}"
    hwc_lower.name = f"HWL{_props}"
    hwc.category = hwc_upper.category = hwc_lower.category = "volatility"

    if channels:
        data = {
            hwc.name: hwc,
            hwc_lower.name: hwc_lower,
            hwc_upper.name: hwc_upper,
            f"HWW{_props}": hwc_width,
            f"HWPCT{_props}": hwc_pctwidth
        }
    else:
        data = {
            hwc.name: hwc,
            hwc_lower.name: hwc_lower,
            hwc_upper.name: hwc_upper
        }
    df = DataFrame(data, index=close.index)
    df.name = f"HWC_{scalar}"
    df.category = hwc.category

    return df
