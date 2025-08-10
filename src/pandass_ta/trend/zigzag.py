# -*- coding: utf-8 -*-
from numpy import floor, isnan, nan, zeros, zeros_like, roll
from numba import njit
from pandas import Series, DataFrame
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.utils import (
    v_bool,
    v_offset,
    v_pos_default,
    v_series,
)


# Find high and low pivots using a centered rolling window.
@njit(cache=True)
def nb_rolling_hl(np_high, np_low, window_size):
    idx = zeros_like(np_high)
    swing = zeros_like(np_high) # where a high = 1 and low = -1
    value = zeros_like(np_high)

    extremes = 0
    left = int(floor(window_size / 2))
    right = left + 1
    # sample_array = [*[left-window], *[center], *[right-window]]

    m = np_high.size
    for i in range(left, m - right):
        low_center = np_low[i]
        high_center = np_high[i]
        low_window = np_low[i - left: i + right]
        high_window = np_high[i - left: i + right]

        if (low_center <= low_window).all():
            idx[extremes] = i
            swing[extremes] = -1
            value[extremes] = low_center
            extremes += 1

        if (high_center >= high_window).all():
            idx[extremes] = i
            swing[extremes] = 1
            value[extremes] = high_center
            extremes += 1

    return idx[:extremes], swing[:extremes], value[:extremes]


# Calculate zigzag points using pre-calculated unfiltered pivots.
@njit(cache=True)
def nb_zz_backtest(idx, swing, value, deviation):
    zz_idx = zeros_like(idx)
    zz_swing = zeros_like(swing)
    zz_value = zeros_like(value)
    zz_dev = zeros_like(idx)

    zigzags = 0
    changes = 0
    zz_idx[zigzags] = idx[0]
    zz_swing[zigzags] = swing[0]
    zz_value[zigzags] = value[0]
    zz_dev[zigzags] = 0

    # print(f'Starting S: {zz_swing[0]}')

    m = idx.size
    for i in range(1, m):
        last_zz_value = zz_value[zigzags]
        current_dev = (value[i] - last_zz_value) / last_zz_value

        # print(f'{i} | P {swing[i]:.0f} : {idx[i]:.0f} , {value[i]}')
        # print(f'{len(str(i))*" "} | Last: {zz_swing[zigzags-changes]:.0f} , Dev: %{(current_dev*100):.1f}')

        # Last point in zigzag is bottom
        if zz_swing[zigzags-changes] == -1:
            if swing[i] == -1:
                # If the current pivot is lower than the last ZZ bottom:
                # create a new point and log it as a change
                if value[i] < zz_value[zigzags]:
                    if zz_idx[zigzags - changes] == idx[i]:
                        continue
                    # print(f'{len(str(i))*" "} | Change -1 : {zz_value[zigzags]} to {value[i]}')
                    zigzags += 1
                    changes += 1
                    zz_idx[zigzags] = idx[i]
                    zz_swing[zigzags] = swing[i]
                    zz_value[zigzags] = value[i]
                    zz_dev[zigzags] = 100 * current_dev
            else:
                # If the deviation between pivot and the last ZZ bottom is
                # great enough create new ZZ point.
                if current_dev > 0.01 * deviation:
                    if zz_idx[zigzags - changes] == idx[i]:
                        continue
                    # print(f'{len(str(i))*" "} | new ZZ 1 {value[i]}')
                    zigzags += 1
                    zz_idx[zigzags] = idx[i]
                    zz_swing[zigzags] = swing[i]
                    zz_value[zigzags] = value[i]
                    zz_dev[zigzags] = 100 * current_dev
                    changes = 0

        # last point in zigzag is top
        else:
            if swing[i] == 1:
                # If the current pivot is higher than the last ZZ top:
                # create a new point and log it as a change
                if value[i] > zz_value[zigzags]:
                    if zz_idx[zigzags - changes] == idx[i]:
                        continue
                    # print(f'{len(str(i))*" "} | Change 1 : {zz_value[zigzags]} to {value[i]}')
                    zigzags += 1
                    changes += 1
                    zz_idx[zigzags] = idx[i]
                    zz_swing[zigzags] = swing[i]
                    zz_value[zigzags] = value[i]
                    zz_dev[zigzags] = 100 * current_dev
            else:
                # If the deviation between pivot and the last ZZ top is great
                # enough create new ZZ point.
                if current_dev < -0.01 * deviation:
                    if zz_idx[zigzags - changes] == idx[i]:
                        continue
                    # print(f'{len(str(i))*" "} | new ZZ -1 {value[i]}')
                    zigzags += 1
                    zz_idx[zigzags] = idx[i]
                    zz_swing[zigzags] = swing[i]
                    zz_value[zigzags] = value[i]
                    zz_dev[zigzags] = 100 * current_dev
                    changes = 0

    _n = zigzags + 1
    return zz_idx[:_n], zz_swing[:_n], zz_value[:_n], zz_dev[:_n]


# Calculate zigzag points using pre-calculated unfiltered pivots.
@njit(cache=True)
def nb_find_zz(idx, swing, value, deviation):
    zz_idx = zeros_like(idx)
    zz_swing = zeros_like(swing)
    zz_value = zeros_like(value)
    zz_dev = zeros_like(idx)

    zigzags = 0
    zz_idx[zigzags] = idx[-1]
    zz_swing[zigzags] = swing[-1]
    zz_value[zigzags] = value[-1]
    zz_dev[zigzags] = 0

    m = idx.size
    for i in range(m - 2, -1, -1):
        # Next point in zigzag is bottom
        if zz_swing[zigzags] == -1:
            if swing[i] == -1:
                # If the current pivot is lower than the next ZZ bottom in
                # time, move it to the pivot. As this lower value invalidates
                # the other one
                if value[i] < zz_value[zigzags] and zigzags > 1:
                    current_dev = (zz_value[zigzags - 1] - value[i]) / value[i]
                    zz_idx[zigzags] = idx[i]
                    zz_swing[zigzags] = swing[i]
                    zz_value[zigzags] = value[i]
                    zz_dev[zigzags - 1] = 100 * current_dev
            else:
                # If the deviation between pivot and the next ZZ bottom is
                # great enough create new ZZ point.
                current_dev = (value[i] - zz_value[zigzags]) / value[i]
                if current_dev > 0.01 * deviation:
                    if zz_idx[zigzags] == idx[i]:
                        continue
                    zigzags += 1
                    zz_idx[zigzags] = idx[i]
                    zz_swing[zigzags] = swing[i]
                    zz_value[zigzags] = value[i]
                    zz_dev[zigzags - 1] = 100 * current_dev

        # Next point in zigzag is top
        else:
            if swing[i] == 1:
                # If the current pivot is greater than the next ZZ top in time,
                # move it to the pivot.
                # As this higher value invalidates the other one
                if value[i] > zz_value[zigzags] and zigzags > 1:
                    current_dev = (value[i] - zz_value[zigzags - 1]) / value[i]
                    zz_idx[zigzags] = idx[i]
                    zz_swing[zigzags] = swing[i]
                    zz_value[zigzags] = value[i]
                    zz_dev[zigzags - 1] = 100 * current_dev
            else:
                # If the deviation between pivot and the next ZZ top is great
                # enough create new ZZ point.
                current_dev = (zz_value[zigzags] - value[i]) / value[i]
                if current_dev > 0.01 * deviation:
                    if zz_idx[zigzags] == idx[i]:
                        continue
                    zigzags += 1
                    zz_idx[zigzags] = idx[i]
                    zz_swing[zigzags] = swing[i]
                    zz_value[zigzags] = value[i]
                    zz_dev[zigzags - 1] = 100 * current_dev

    _n = zigzags + 1
    return zz_idx[:_n], zz_swing[:_n], zz_value[:_n], zz_dev[:_n]



# Maps nb_find_zz results back onto the original data indices.
@njit(cache=True)
def nb_map_zz(idx, swing, value, deviation, n):
    swing_map = zeros(n)
    value_map = zeros(n)
    dev_map = zeros(n)

    for j, i in enumerate(idx):
        i = int(i)
        swing_map[i] = swing[j]
        value_map[i] = value[j]
        dev_map[i] = deviation[j]

    for i in range(n):
        if swing_map[i] == 0:
            swing_map[i] = nan
            value_map[i] = nan
            dev_map[i] = nan

    return swing_map, value_map, dev_map



def zigzag(
    high: Series, low: Series, close: Series = None,
    legs: int = None, deviation: IntFloat = None, backtest: bool = None,
    offset: Int = None, **kwargs: DictLike
):
    """Zigzag

    This indicator attempts to filter out smaller movements while identifying
    trend direction. It does not predict future trends, but it does identify
    swing highs and lows.

    Sources:
        * [stockcharts](https://school.stockcharts.com/doku.php?id=technical_indicators:zigzag)
        * [tradingview](https://www.tradingview.com/support/solutions/43000591664-zig-zag/#:~:text=Definition,trader%20visual%20the%20price%20action.)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series. Default: ```None```
        legs (int): Number of legs (> 2). Default: ```10```
        deviation (float): Reversal deviation percentage. Default: ```5```
        backtest (bool): Default: ```False```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 2 columns

    Note: Deviation
        When ```deviation=10```, it shows movements greater than ```10%```.

    Note: Backtest Mode
        Ensures the DataFrame is safe for backtesting. By default, swing
        points are returned on the pivot index. Intermediate swings are
        not returned at all. This mode swing detection is placed on the bar
        that would have been detected. Furthermore, changes in swing levels
        are also included instead of only the final value.

        * Use the following formula to get the true index of a pivot:
          ```p_i = i - int(floor(legs / 2))```

    Warning:
        A Series reversal will create a new line.
    """
    # Validate
    legs = v_pos_default(legs, 10)
    _length = legs + 1
    high = v_series(high, _length)
    low = v_series(low, _length)

    if high is None or low is None:
        return

    if close is not None:
        close = v_series(close,_length)
        np_close = close.values
        if close is None:
            return

    deviation = v_pos_default(deviation, 5.0)
    offset = v_offset(offset)
    backtest = v_bool(backtest, False)

    if backtest:
        offset+=int(floor(legs/2))

    # Calculation
    np_high, np_low = high.to_numpy(), low.to_numpy()
    hli, hls, hlv = nb_rolling_hl(np_high, np_low, legs)

    if backtest:
        zzi, zzs, zzv, zzd = nb_zz_backtest(hli, hls, hlv, deviation)
    else:
        zzi, zzs, zzv, zzd = nb_find_zz(hli, hls, hlv, deviation)

    swing, value, dev = nb_map_zz(zzi, zzs, zzv, zzd, np_high.size)

    # Offset
    if offset != 0:
        swing = roll(swing, offset)
        value = roll(value, offset)
        dev = roll(dev, offset)

        swing[:offset] = nan
        value[:offset] = nan
        dev[:offset] = nan

    # Fill
    if "fillna" in kwargs:
        swing.fillna(kwargs["fillna"], inplace=True)
        value.fillna(kwargs["fillna"], inplace=True)
        dev.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{deviation}%_{legs}"
    data = {
        f"ZIGZAGs{_props}": swing,
        f"ZIGZAGv{_props}": value,
        f"ZIGZAGd{_props}": dev,
    }
    df = DataFrame(data, index=high.index)
    df.name = f"ZIGZAG{_props}"
    df.category = "trend"

    return df
