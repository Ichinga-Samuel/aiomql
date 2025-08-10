# -*- coding: utf-8 -*-
from numpy import isnan, zeros
from pandas import DataFrame, Series

from pandas_ta._typing import DictLike, Int
from pandas_ta.ma import ma
from pandas_ta.utils import (
    sum_signed_rolling_deltas,
    v_bool,
    v_mamode,
    v_offset,
    v_pos_default,
    v_series
)


def tmo(
    open_: Series, close: Series,
    tmo_length: Int = None, calc_length: Int = None, smooth_length: Int = None,
    momentum: bool = None, normalize: bool = None, exclusive: bool = None,
    mamode: str = None, offset: Int = None, **kwargs: DictLike,
) -> DataFrame:
    """True Momentum Oscillator

    This indicator attempts to quantify momentum.

    Sources:
        * [tradingview A](https://www.tradingview.com/script/VRwDppqd-True-Momentum-Oscillator/)
        * [tradingview B](https://www.tradingview.com/script/65vpO7T5-True-Momentum-Oscillator-Universal-Edition/)

    Parameters:
        open_ (pd.Series): ```open``` Series
        close (pd.Series): ```close``` Series
        tmo_length (int): TMO period. Default: ```14```
        calc_length (int): Initial MA period. Default: ```5```
        smooth_length (int): Main and smooth signal MA period. Default: ```3```
        mamode (str): See ```help(ta.ma)```. Default: ```"ema"```
        momentum (bool): Compute main and smooth momentum. Default: ```False```
        normalize (bool): Normalize. Default: ```False```
        exclusive (bool): Exclusive period over ```n``` bars, or inclusively
            over ```n-1``` bars. Default: ```True```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): DataFrame.fillna(value)

    Returns:
        (pd.DataFrame): 4 columns
    """
    # Validate
    tmo_length = v_pos_default(tmo_length, 14)
    calc_length = v_pos_default(calc_length, 5)
    smooth_length = v_pos_default(smooth_length, 3)
    _length = max(tmo_length, calc_length, smooth_length)

    open_ = v_series(open_, _length)
    close = v_series(close, _length)
    offset = v_offset(offset)

    if "length" in kwargs:
        kwargs.pop("length")

    if open_ is None or close is None:
        return None

    mamode = v_mamode(mamode, "ema")
    compute_momentum = v_bool(momentum, False)
    normalize_signal = v_bool(normalize, False)
    exclusive = v_bool(exclusive, True)

    signed_diff_sum = sum_signed_rolling_deltas(
        open_, close, tmo_length, exclusive=exclusive
    )
    if all(isnan(signed_diff_sum)):
        return None  # Emergency Break

    initial_ma = ma(mamode, signed_diff_sum, length=calc_length)
    if all(isnan(initial_ma)):
        return None  # Emergency Break

    main = ma(mamode, initial_ma, length=smooth_length)
    if all(isnan(main)):
        return None  # Emergency Break

    smooth = ma(mamode, main, length=smooth_length)
    if all(isnan(smooth)):
        return None  # Emergency Break

    if compute_momentum:
        mom_main = main - main.shift(tmo_length)
        mom_smooth = smooth - smooth.shift(tmo_length)
    else:
        zero_array = zeros(main.size)
        mom_main = Series(zero_array, index=main.index)
        mom_smooth = Series(zero_array, index=smooth.index)

    # Offset
    if offset != 0:
        main = main.shift(offset)
        smooth = smooth.shift(offset)
        mom_main = mom_main.shift(offset)
        mom_smooth = mom_smooth.shift(offset)

    # Fill
    if "fillna" in kwargs:
        main.fillna(kwargs["fillna"], inplace=True)
        smooth.fillna(kwargs["fillna"], inplace=True)
        mom_main.fillna(kwargs["fillna"], inplace=True)
        mom_smooth.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{tmo_length}_{calc_length}_{smooth_length}"
    main.name = f"TMO{_props}"
    smooth.name = f"TMOs{_props}"
    mom_main.name = f"TMOM{_props}"
    mom_smooth.name = f"TMOMs{_props}"
    main.category = smooth.category = "momentum"
    mom_main.category = mom_smooth.category = main.category

    data = {
        main.name: main,
        smooth.name: smooth,
        mom_main.name: mom_main,
        mom_smooth.name: mom_smooth,
    }
    df = DataFrame(data, index=close.index)
    df.name = f"TMO{_props}"
    df.category = main.category

    return df
