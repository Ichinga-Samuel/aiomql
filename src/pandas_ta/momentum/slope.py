# -*- coding: utf-8 -*-
from numpy import arctan, pi, rad2deg
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import (
    nb_idiff,
    v_bool,
    v_offset,
    v_pos_default,
    v_series
)



def slope(
    close: Series, length: Int = None,
    as_angle: bool = None, to_degrees: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Slope

    Calculates a rolling slope.

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```1```
        as_angle (bool): Converts slope to an angle in radians
            per ```np.arctan()```. Default: ```False```
        to_degrees (value): If ```as_angle=True```, converts radians to
            degrees. Default: ```False```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 1)
    close = v_series(close, length + 1)

    if close is None:
        return

    as_angle = v_bool(as_angle, False)
    to_degrees = v_bool(to_degrees, False)
    offset = v_offset(offset)

    # Calculate
    np_close = close.to_numpy()
    _slope = nb_idiff(np_close, length) / length
    if as_angle:
        _slope = arctan(_slope)
        if to_degrees:
            _slope = rad2deg(_slope)
    slope = Series(_slope, index=close.index)

    # Offset
    if offset != 0:
        slope = slope.shift(offset)

    # Fill
    if "fillna" in kwargs:
        slope.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    slope.name = f"SLOPE_{length}" if not as_angle else f"ANGLE{'d' if to_degrees else 'r'}_{length}"
    slope.category = "momentum"

    return slope
