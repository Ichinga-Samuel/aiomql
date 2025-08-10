# -*- coding: utf-8 -*-
from numpy import cos, exp, mean, nan, pi, roll, sin, sqrt, zeros
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_bool, v_offset, v_pos_default, v_series



def ebsw(
    close: Series, length: Int = None, bars: Int = None,
    initial_version: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Even Better SineWave

    This indicator attempts to quantify market cycles using a low pass filter.

    Sources:
        * [rengel8](https://github.com/rengel8)
        * J.F.Ehlers 'Cycle Analytics for Traders', 2014
        * [Pandas TA Issue #350](https://github.com/twopirllc/pandas-ta/issues/350)
        * [Proreal Code](https://www.prorealcode.com/prorealtime-indicators/even-better-sinewave/)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): Max cycle/trend period. Values between ```40-48``` work
            as expected with minimum value: ```39```. Default: ```40```
        bars (int): Period of low pass filtering. Default: ```10```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): Replaces ```na```'s with ```value```.

    Returns:
        (pd.Series): 1 column

    Note:
        The _default_ is more cycle oriented and seems to be less
        whipsaw-prune. The older version might offer earlier signals at medium
        and stronger reversals. Compared to TradingView, returns very close
        results but appears to be one bar earlier.
    """
    # Validate
    length = v_pos_default(length, 40)
    close = v_series(close, length)

    if close is None:
        return

    initial_version = v_bool(initial_version, False)
    bars = v_pos_default(bars, 10)
    offset = v_offset(offset)

    # Calculate
    # allow initial version to be used (more responsive/caution!)
    m = close.size
    if isinstance(initial_version, bool) and initial_version:
        # not the default version that is active
        alpha1 = hp = 0  # alpha and HighPass
        a1 = b1 = c1 = c2 = c3 = 0
        filter_ = power_ = wave = 0
        lastClose = lastHP = 0
        filtHist = [0, 0]   # Filter history

        result = [nan for _ in range(0, length - 1)] + [0]
        for i in range(length, m):
            # HighPass filter cyclic components whose periods are shorter than
            # Duration input
            alpha1 = (1 - sin(360 / length)) / cos(360 / length)
            hp = 0.5 * (1 + alpha1) * (close.iloc[i] - lastClose) + alpha1 * lastHP

            # Smooth with a Super Smoother Filter from equation 3-3
            a1 = exp(-sqrt(2) * pi / bars)
            b1 = 2 * a1 * cos(sqrt(2) * 180 / bars)
            c2 = b1
            c3 = -1 * a1 * a1
            c1 = 1 - c2 - c3
            filter_ = 0.5 * c1 * (hp + lastHP) + c2 * \
                filtHist[1] + c3 * filtHist[0]
            # filter_ = float("{:.8f}".format(float(filter_))) # to fix for
            # small scientific notations, the big ones fail

            # 3 Bar average of wave amplitude and power
            wave = (filter_ + filtHist[1] + filtHist[0]) / 3
            power_ = (filter_ * filter_ + filtHist[1] * filtHist[1] \
                + filtHist[0] * filtHist[0]) / 3
            # Normalize the Average Wave to Square Root of the Average Power
            wave = wave / sqrt(power_)

            # update storage, result
            filtHist.append(filter_)  # append new filter_ value
            # remove first element of list (left) -> updating/trim
            filtHist.pop(0)
            lastHP = hp
            lastClose = close.iloc[i]
            result.append(wave)

    else:  # Default
        lastHP = lastClose = 0
        filtHist = zeros(3)
        result = [nan] * (length - 1) + [0]

        angle = 2 * pi / length
        alpha1 = (1 - sin(angle)) / cos(angle)
        ang = 2 ** .5 * pi / bars
        a1 = exp(-ang)
        c2 = 2 * a1 * cos(ang)
        c3 = -a1 ** 2
        c1 = 1 - c2 - c3

        for i in range(length, m):
            hp = 0.5 * (1 + alpha1) * (close.iloc[i] - lastClose) + alpha1 * lastHP

            # Rotate filters to overwrite oldest value
            filtHist = roll(filtHist, -1)
            filtHist[-1] = 0.5 * c1 * \
                (hp + lastHP) + c2 * filtHist[1] + c3 * filtHist[0]

            # Wave calculation
            wave = mean(filtHist)
            rms = sqrt(mean(filtHist ** 2))
            wave = wave / rms

            # Update past values
            lastHP = hp
            lastClose = close.iloc[i]
            result.append(wave)

    ebsw = Series(result, index=close.index)

    # Offset
    if offset != 0:
        ebsw = ebsw.shift(offset)

    # Fill
    if "fillna" in kwargs:
        ebsw.fillna(kwargs["fillna"], inplace=True)
    # Name and Category
    ebsw.name = f"EBSW_{length}_{bars}"
    ebsw.category = "cycle"

    return ebsw
