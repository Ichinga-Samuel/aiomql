# -*- coding: utf-8 -*-
from warnings import simplefilter
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, List
from pandas_ta.overlap import hlc3
from pandas_ta.utils import v_datetime_ordered, v_list, v_offset, v_series



def vwap(
    high: Series, low: Series, close: Series, volume: Series,
    anchor: str = None, bands: List = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Volume Weighted Average Price

    This indicator computes the Volume Weighted Average Price.

    Sources:
        * [tradingview](https://www.tradingview.com/wiki/Volume_Weighted_Average_Price_(VWAP))
        * [Trading Technologies](https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/volume-weighted-average-price-vwap/)
        * [Stockcharts](https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:vwap_intraday)
        * [Sierra Chart](https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=108&Name=Volume_Weighted_Average_Price_-_VWAP_-_with_Standard_Deviation_Lines)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        volume (pd.Series): ```volume``` Series
        anchor (str): VWAP Anchor. Default: ```"D"```.
        bands (list): List of positive ```IntFloat``` deviations.
            Default: ```[]```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series | pd.DataFrame): ```DataFrame``` when ```bands``` is set.
            Default: ```Series```

    Note:
        * Commonly used with intraday charts to identify general direction.
        * Depending on the index values, it will implement various
          [Timeseries Offset Aliases](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases)

    Tip:
        * Negative bands are computed automatically.
    """
    # Validate
    _length = 1
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)
    volume = v_series(volume, _length)

    if high is None or low is None or close is None or volume is None:
        return

    bands = v_list(bands)
    offset = v_offset(offset)

    if anchor and isinstance(anchor, str) and len(anchor) >= 1:
        anchor = anchor.upper()
    else:
        anchor = "D"

    typical_price = hlc3(high=high, low=low, close=close)
    if not v_datetime_ordered(volume) or \
        not v_datetime_ordered(typical_price):
        print("[!] VWAP requires an ordered DatetimeIndex.")
        return

    # Calculate
    _props = f"VWAP_{anchor}"
    wp = typical_price * volume
    simplefilter(action="ignore", category=UserWarning)
    vwap = wp.groupby(wp.index.to_period(anchor)).cumsum() \
        / volume.groupby(volume.index.to_period(anchor)).cumsum()

    if bands and len(bands):
        # Calculate vwap stdev bands
        vwap_var = volume * (typical_price - vwap) ** 2
        vwap_var_sum = vwap_var \
            .groupby(vwap_var.index.to_period(anchor)).cumsum()
        vwap_volume_sum = volume \
            .groupby(volume.index.to_period(anchor)).cumsum()
        std_volume_weighted = (vwap_var_sum / vwap_volume_sum) ** 0.5

    # Name and Category
    vwap.name = _props
    vwap.category = "overlap"

    if bands:
        df = DataFrame({vwap.name: vwap}, index=close.index)
        for i in bands:
            df[f"{_props}_L_{i}"] = vwap - i * std_volume_weighted
            df[f"{_props}_U_{i}"] = vwap + i * std_volume_weighted
            df[f"{_props}_L_{i}"].name = df[f"{_props}_U_{i}"].name = _props
            df[f"{_props}_L_{i}"].category = "overlap"
            df[f"{_props}_U_{i}"].category = "overlap"
        df.name = _props
        df.category = "overlap"

    # Offset
    if offset != 0:
        if bands and not df.empty:
            df = df.shift(offset)
        vwap = vwap.shift(offset)

    # Fill
    if "fillna" in kwargs:
        if bands and not df.empty:
            df.fillna(kwargs["fillna"], inplace=True)
        else:
            vwap.fillna(kwargs["fillna"], inplace=True)

    if bands and not df.empty:
        return df
    return vwap
