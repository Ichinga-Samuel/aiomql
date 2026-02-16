# -*- coding: utf-8 -*-
# Long Run (LONG_RUN)
from .decreasing import decreasing
from .increasing import increasing
from ..utils import get_offset, verify_series


def long_run(fast, slow, length=None, offset=None, **kwargs):
    """Indicator: Long Run"""
    # Validate Arguments
    length = int(length) if length and length > 0 else 2
    fast = verify_series(fast, length)
    slow = verify_series(slow, length)
    offset = get_offset(offset)

    if fast is None or slow is None:
        return

    # Calculate Result
    pb = increasing(fast, length) & decreasing(
        slow, length
    )  # potential bottom or bottom
    bi = increasing(fast, length) & increasing(
        slow, length
    )  # fast and slow are increasing
    long_run = pb | bi

    # Offset
    if offset != 0:
        long_run = long_run.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        long_run.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        if "fill_method" in kwargs:

            if kwargs["fill_method"] == "ffill":

                long_run.ffill(inplace=True)

            elif kwargs["fill_method"] == "bfill":

                long_run.bfill(inplace=True)

    # Name and Categorize it
    long_run.name = f"LR_{length}"
    long_run.category = "trend"

    return long_run


long_run.__doc__ = """Long Run

Identifies potential long (bullish) trend conditions by detecting when the fast 
moving average is increasing while the slow moving average is either decreasing 
(potential bottom) or also increasing (confirmed uptrend).

Sources:
    Used in AMAT (Archer Moving Averages Trends) indicator

Calculation:
    Default Inputs:
        length=2
    
    PB = INCREASING(fast, length) AND DECREASING(slow, length)  # Potential bottom
    BI = INCREASING(fast, length) AND INCREASING(slow, length)  # Both increasing
    LONG_RUN = PB OR BI

Args:
    fast (pd.Series): Fast moving average series
    slow (pd.Series): Slow moving average series
    length (int): Lookback period. Default: 2
    offset (int): How many periods to offset the result. Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated (boolean).
"""
