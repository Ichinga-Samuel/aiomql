# -*- coding: utf-8 -*-
# Rainbow Charts
from pandas import DataFrame
from ..overlap.sma import sma
from ..utils import get_offset, verify_series


def rainbow(close, length=None, offset=None, **kwargs):
    """Indicator: Rainbow Charts"""
    # Validate arguments
    length = int(length) if length and length > 0 else 2
    num_ribbons = int(kwargs.pop("num_ribbons", 10)) if "num_ribbons" in kwargs else 10
    close = verify_series(close, length * num_ribbons)
    offset = get_offset(offset)

    if close is None:
        return

    # Calculate Result
    # Create rainbow of SMAs
    # Each SMA is calculated on the previous SMA
    ribbons = {}
    prev_sma = close

    for i in range(1, num_ribbons + 1):
        current_sma = sma(prev_sma, length=length)
        ribbons[f"RAINBOW_{i}"] = current_sma
        prev_sma = current_sma

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
    df.name = f"RAINBOW_{length}_{num_ribbons}"
    df.category = "overlap"

    return df


rainbow.__doc__ = """Rainbow Charts

Rainbow Charts use multiple moving averages calculated sequentially, where each
MA is calculated on the previous MA rather than the price. This creates a
"rainbow" effect that helps visualize trend strength and potential reversals.

Sources:
    https://www.investopedia.com/articles/trading/06/rainbow.asp
    https://www.prorealcode.com/prorealtime-indicators/rainbow-oscillator/

Calculation:
    Default Inputs:
        length=2, num_ribbons=10

    MA1 = SMA(close, length)
    MA2 = SMA(MA1, length)
    MA3 = SMA(MA2, length)
    ...
    MA[n] = SMA(MA[n-1], length)

Args:
    close (pd.Series): Series of 'close's
    length (int): SMA period. Default: 2
    offset (int): How many periods to offset the result. Default: 0

Kwargs:
    num_ribbons (int): Number of rainbow bands. Default: 10
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.DataFrame: New features generated.
"""
