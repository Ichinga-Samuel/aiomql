# -*- coding: utf-8 -*-
# Madrid Moving Average Ribbon (MMAR)
from pandas import DataFrame
from ..overlap.ema import ema
from ..utils import get_offset, verify_series


def mmar(close, length=None, offset=None, **kwargs):
    """Indicator: Madrid Moving Average Ribbon (MMAR)"""
    # Validate arguments
    length = int(length) if length and length > 0 else 10
    close = verify_series(close, length)
    offset = get_offset(offset)

    if close is None:
        return

    # Calculate Result
    # Create ribbon of EMAs with incremental periods
    step = kwargs.pop("step", 5)
    num_ribbons = kwargs.pop("num_ribbons", 6)

    ribbons = {}
    for i in range(num_ribbons):
        period = length + (i * step)
        ema_value = ema(close, length=period)
        ribbons[f"MMAR_{period}"] = ema_value

    # Create DataFrame
    df = DataFrame(ribbons)

    # Offset
    if offset != 0:
        df = df.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        df.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        if kwargs["fill_method"] == "ffill":
            df.ffill(inplace=True)
        elif kwargs["fill_method"] == "bfill":
            df.bfill(inplace=True)

    # Name and Categorize it
    df.name = f"MMAR_{length}_{step}_{num_ribbons}"
    df.category = "overlap"

    return df


mmar.__doc__ = """Madrid Moving Average Ribbon (MMAR)

The Madrid Moving Average Ribbon is a visual trend indicator that consists of
multiple EMAs with incrementally increasing periods. It helps identify trend
strength and direction through the spacing and alignment of the moving averages.

Sources:
    https://www.tradingview.com/script/a87v7d4L-Madrid-Moving-Average-Ribbon/
    https://www.forexstrategiesresources.com/trend-following-forex-strategies/

Calculation:
    Default Inputs:
        length=10, step=5, num_ribbons=6

    For i in range(num_ribbons):
        period = length + (i * step)
        MMAR[i] = EMA(close, period)

    Returns DataFrame with columns:
    MMAR_10, MMAR_15, MMAR_20, MMAR_25, MMAR_30, MMAR_35

Args:
    close (pd.Series): Series of 'close's
    length (int): Initial EMA period. Default: 10
    offset (int): How many periods to offset the result. Default: 0

Kwargs:
    step (int): Period increment between ribbons. Default: 5
    num_ribbons (int): Number of EMA ribbons. Default: 6
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.DataFrame: New features generated.
"""
