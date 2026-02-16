# -*- coding: utf-8 -*-
# Volume Weighted Moving Average Convergence Divergence (Volume Weighted MACD)
from pandas import DataFrame
from ..overlap.vwma import vwma
from ..utils import get_offset, verify_series


def vwmacd(close, volume, fast=None, slow=None, signal=None, offset=None, **kwargs):
    """Indicator: Volume Weighted MACD (VWMACD)"""
    # Validate arguments
    fast = int(fast) if fast and fast > 0 else 12
    slow = int(slow) if slow and slow > 0 else 26
    signal = int(signal) if signal and signal > 0 else 9
    if slow < fast:
        fast, slow = slow, fast
    close = verify_series(close, max(fast, slow, signal))
    volume = verify_series(volume, max(fast, slow, signal))
    offset = get_offset(offset)

    if close is None or volume is None:
        return

    # Calculate Result
    # Volume weighted moving averages
    fast_vwma = vwma(close, volume, length=fast)
    slow_vwma = vwma(close, volume, length=slow)

    # VWMACD line
    vwmacd = fast_vwma - slow_vwma

    # Signal line
    signal_line = vwma(vwmacd, volume, length=signal)

    # Histogram
    histogram = vwmacd - signal_line

    # Offset
    if offset != 0:
        vwmacd = vwmacd.shift(offset)
        signal_line = signal_line.shift(offset)
        histogram = histogram.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        vwmacd.fillna(kwargs["fillna"], inplace=True)
        signal_line.fillna(kwargs["fillna"], inplace=True)
        histogram.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        if kwargs["fill_method"] == "ffill":
            vwmacd.ffill(inplace=True)
            signal_line.ffill(inplace=True)
            histogram.ffill(inplace=True)
        elif kwargs["fill_method"] == "bfill":
            vwmacd.bfill(inplace=True)
            signal_line.bfill(inplace=True)
            histogram.bfill(inplace=True)

    # Name and Categorize it
    _props = f"_{fast}_{slow}_{signal}"
    vwmacd.name = f"VWMACD{_props}"
    signal_line.name = f"VWMACDs{_props}"
    histogram.name = f"VWMACDh{_props}"
    vwmacd.category = signal_line.category = histogram.category = "momentum"

    # Prepare DataFrame to return
    data = {
        vwmacd.name: vwmacd,
        histogram.name: histogram,
        signal_line.name: signal_line,
    }
    df = DataFrame(data)
    df.name = f"VWMACD{_props}"
    df.category = "momentum"

    return df


vwmacd.__doc__ = """Volume Weighted MACD (VWMACD)

Volume Weighted MACD is a variation of the traditional MACD that incorporates
volume into the calculation. It uses Volume Weighted Moving Averages (VWMA)
instead of EMAs to give more weight to periods with higher volume.

Sources:
    https://www.tradingview.com/script/NUs1Y5V7-Volume-Weighted-MACD/
    Technical Analysis Using Multiple Timeframes by Brian Shannon

Calculation:
    Default Inputs:
        fast=12, slow=26, signal=9

    FastVWMA = VWMA(close, volume, fast)
    SlowVWMA = VWMA(close, volume, slow)

    VWMACD = FastVWMA - SlowVWMA
    Signal = VWMA(VWMACD, volume, signal)
    Histogram = VWMACD - Signal

Args:
    close (pd.Series): Series of 'close's
    volume (pd.Series): Series of 'volume's
    fast (int): The fast period. Default: 12
    slow (int): The slow period. Default: 26
    signal (int): The signal period. Default: 9
    offset (int): How many periods to offset the result. Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.DataFrame: VWMACD, Signal, and Histogram columns.
"""
