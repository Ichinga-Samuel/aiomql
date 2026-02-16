# -*- coding: utf-8 -*-
# Short Run (SHORT_RUN)
from .decreasing import decreasing
from .increasing import increasing
from ..utils import get_offset, verify_series


def short_run(fast, slow, length=None, offset=None, **kwargs):
    """Indicator: Short Run"""
    # Validate Arguments
    length = int(length) if length and length > 0 else 2
    fast = verify_series(fast, length)
    slow = verify_series(slow, length)
    offset = get_offset(offset)

    if fast is None or slow is None:
        return

    # Calculate Result
    pt = decreasing(fast, length) & increasing(slow, length)  # potential top or top
    bd = decreasing(fast, length) & decreasing(
        slow, length
    )  # fast and slow are decreasing
    short_run = pt | bd

    # Offset
    if offset != 0:
        short_run = short_run.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        short_run.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        if "fill_method" in kwargs:

            if kwargs["fill_method"] == "ffill":

                short_run.ffill(inplace=True)

            elif kwargs["fill_method"] == "bfill":

                short_run.bfill(inplace=True)

    # Name and Categorize it
    short_run.name = f"SR_{length}"
    short_run.category = "trend"

    return short_run


short_run.__doc__ = """Short Run

Identifies potential short (bearish) trend conditions by detecting when the fast 
moving average is decreasing while the slow moving average is either increasing 
(potential top) or also decreasing (confirmed downtrend).

Sources:
    Used in AMAT (Archer Moving Averages Trends) indicator

Calculation:
    Default Inputs:
        length=2
    
    PT = DECREASING(fast, length) AND INCREASING(slow, length)  # Potential top
    BD = DECREASING(fast, length) AND DECREASING(slow, length)  # Both decreasing
    SHORT_RUN = PT OR BD

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
