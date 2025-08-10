# -*- coding: utf-8 -*-
from pandas import DataFrame, concat, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import (
    signals,
    v_drift,
    v_offset,
    v_pos_default,
    v_series
)



def er(
    close: Series, length: Int = None, drift: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Efficiency Ratio

    This indicator, by Perry J. Kaufman, attempts to identify market noise
    or volatility.

    Sources:
        * "New Trading Systems and Methods", Perry J. Kaufman
        * [tc2000](https://help.tc2000.com/m/69404/l/749623-kaufman-efficiency-ratio)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column

    Note:
        It is calculated by dividing the net change in price movement over
        ```n``` periods by the sum of the absolute net changes over the
        same ```n``` periods.
    """
    # Validate
    length = v_pos_default(length, 10)
    close = v_series(close, length + 1)

    if close is None:
        return

    drift = v_drift(drift)
    offset = v_offset(offset)

    # Calculate
    abs_diff = close.diff(length).abs()
    abs_volatility = close.diff(drift).abs()
    abs_volatility_rsum = abs_volatility.rolling(window=length).sum()

    er = abs_diff / abs_volatility_rsum

    # Offset
    if offset != 0:
        er = er.shift(offset)

    # Fill
    if "fillna" in kwargs:
        er.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    er.name = f"ER_{length}"
    er.category = "momentum"

    signal_indicators = kwargs.pop("signal_indicators", False)
    if not signal_indicators:
        return er
    else:
        signalsdf = concat(
            [
                DataFrame({er.name: er}),
                signals(
                    indicator=er,
                    xa=kwargs.pop("xa", 80),
                    xb=kwargs.pop("xb", 20),
                    xseries=kwargs.pop("xseries", None),
                    xseries_a=kwargs.pop("xseries_a", None),
                    xseries_b=kwargs.pop("xseries_b", None),
                    cross_values=kwargs.pop("cross_values", False),
                    cross_series=kwargs.pop("cross_series", True),
                    offset=offset,
                ),
            ],
            axis=1,
        )
        return signalsdf
