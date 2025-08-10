# -*- coding: utf-8 -*-
from numpy import full, nan, zeros
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.utils import v_offset, v_pos_default, v_series, zero



def psar(
    high: Series, low: Series, close: Series = None,
    af0: IntFloat = None, af: IntFloat = None, max_af: IntFloat = None, tv=False,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Parabolic Stop and Reverse

    This indicator, by J. Wells Wilder, attempts to identify trend direction
    and potential reversals.

    Sources:
        * [sierrachart](https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=66&Name=Parabolic)
        * [tradingview](https://www.tradingview.com/pine-script-reference/#fun_sar)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): Optional ```close``` Series
        af0 (float): Initial Acceleration Factor. Default: ```0.02```
        af (float): Acceleration Factor. Default: ```0.02```
        max_af (float): Maximum Acceleration Factor. Default: ```0.2```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 4 columns

    Warning:
        TA-Lib Correlation: ```np.float64(0.9837617513753181)```

    Tip:
        Corrective contributions welcome!
    """
    # Validate
    _length = 1
    high = v_series(high, _length)
    low = v_series(low, _length)

    if high is None or low is None:
        return

    orig_high = high.copy()
    orig_low = low.copy()
    # Numpy arrays offer some performance improvements
    high, low = high.to_numpy(), low.to_numpy()

    paf = v_pos_default(af, 0.02) # paf is used to keep af from parameters
    af0 = v_pos_default(af0, paf)
    af = af0

    max_af = v_pos_default(max_af, 0.2)
    offset = v_offset(offset)

    # Set up
    m = high.size
    sar = zeros(m)
    long = full(m, nan)
    short = full(m, nan)
    reversal = zeros(m, dtype=int)
    _af = zeros(m)
    _af[:2] = af0
    falling = _falling(orig_high.iloc[:2], orig_low.iloc[:2])
    ep = low[0] if falling else high[0]
    if close is not None:
        close = v_series(close)
        sar[0] = close.iloc[0]
    else:
        sar[0] = high[0] if falling else low[0]

    # Calculate
    for i in range(1, m):
        sar[i] = sar[i - 1] + af * (ep - sar[i - 1])

        if falling:
            reverse = high[i] > sar[i]
            if low[i] < ep:
                ep = low[i]
                af = min(af + af0, max_af)
            sar[i] = max(high[i - 1], sar[i])
        else:
            reverse = low[i] < sar[i]
            if high[i] > ep:
                ep = high[i]
                af = min(af + af0, max_af)
            sar[i] = min(low[i - 1], sar[i])

        if reverse:
            sar[i] = ep
            af = af0
            falling = not falling
            ep = low[i] if falling else high[i]

        # Separate long/short SAR based on falling
        if falling:
            short[i] = sar[i]
        else:
            long[i] = sar[i]

        _af[i] = af
        reversal[i] = int(reverse)

    _af = Series(_af, index=orig_high.index)
    long = Series(long, index=orig_high.index)
    short = Series(short, index=orig_high.index)
    reversal = Series(reversal, index=orig_high.index)

    # Offset
    if offset != 0:
        _af = _af.shift(offset)
        long = long.shift(offset)
        short = short.shift(offset)
        reversal = reversal.shift(offset)

    # Fill
    if "fillna" in kwargs:
        _af.fillna(kwargs["fillna"], inplace=True)
        long.fillna(kwargs["fillna"], inplace=True)
        short.fillna(kwargs["fillna"], inplace=True)
        reversal.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _name = f"PSAR"
    _props = f"_{af0}_{max_af}"

    data = {
        f"{_name}l{_props}": long,
        f"{_name}s{_props}": short,
        f"{_name}af{_props}": _af,
        f"{_name}r{_props}": reversal
    }
    df = DataFrame(data, index=orig_high.index)
    df.name = f"{_name}{_props}"
    df.category = long.category = short.category = "trend"

    return df


def _falling(high, low, drift: int = 1):
    """Returns the last -DM value"""
    # Not to be confused with ta.falling()
    up = high - high.shift(drift)
    dn = low.shift(drift) - low
    _dmn = (((dn > up) & (dn > 0)) * dn).apply(zero).iloc[-1]
    return _dmn > 0
