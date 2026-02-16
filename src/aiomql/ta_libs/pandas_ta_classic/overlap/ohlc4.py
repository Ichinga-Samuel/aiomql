# -*- coding: utf-8 -*-
# OHLC4 (OHLC4)
from ..utils import get_offset, verify_series


def ohlc4(open_, high, low, close, offset=None, **kwargs):
    """Indicator: OHLC4"""
    # Validate Arguments
    open_ = verify_series(open_)
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
    offset = get_offset(offset)

    # Calculate Result
    ohlc4 = 0.25 * (open_ + high + low + close)

    # Offset
    if offset != 0:
        ohlc4 = ohlc4.shift(offset)

    # Name & Category
    ohlc4.name = "OHLC4"
    ohlc4.category = "overlap"

    return ohlc4


ohlc4.__doc__ = """OHLC4 (Average of Open, High, Low, Close)

OHLC4 calculates the average of the Open, High, Low, and Close prices for 
each period. This simple average provides a balanced representation of price 
action across the entire period, giving equal weight to all four OHLC values.
It's commonly used as a smoother alternative to close prices alone.

Sources:
    https://www.tradingview.com/support/solutions/43000502001-ohlc4/
    https://www.investopedia.com/terms/o/ohlc-chart.asp

Calculation:
    Default Inputs:
        None (uses raw OHLC prices)
    
    OHLC4 = (Open + High + Low + Close) / 4

Args:
    open_ (pd.Series): Series of 'open' prices
    high (pd.Series): Series of 'high' prices
    low (pd.Series): Series of 'low' prices
    close (pd.Series): Series of 'close' prices
    offset (int): How many periods to offset the result. Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated.
"""
