# -*- coding: utf-8 -*-
from numpy import isnan
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.overlap import swma
from pandas_ta.utils import non_zero_range, v_offset, v_pos_default, v_series



def rvgi(
    open_: Series, high: Series, low: Series, close: Series,
    length: Int = None, swma_length: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Relative Vigor Index

    This indicator attempts to quantify the strength of a trend relative to
    its trading range.

    Sources:
        * [investopedia](https://www.investopedia.com/terms/r/relative_vigor_index.asp)

    Parameters:
        open_ (pd.Series): ```open``` Series
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```14```
        swma_length (int): SWMA period. Default: ```4```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    length = v_pos_default(length, 14)
    swma_length = v_pos_default(swma_length, 4)
    _length = length + swma_length - 1
    open_ = v_series(open_, _length)
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if open_ is None or high is None or low is None or close is None:
        return

    offset = v_offset(offset)

    # Calculate
    high_low_range = non_zero_range(high, low)
    close_open_range = non_zero_range(close, open_)

    numerator = swma(close_open_range, length=swma_length) \
        .rolling(length).sum()
    denominator = swma(high_low_range, length=swma_length) \
        .rolling(length).sum()

    rvgi = numerator / denominator
    signal = swma(rvgi, length=swma_length)

    if all(isnan(signal.to_numpy())):
        return  # Emergency Break

    # Offset
    if offset != 0:
        rvgi = rvgi.shift(offset)
        signal = signal.shift(offset)

    # Fill
    if "fillna" in kwargs:
        rvgi.fillna(kwargs["fillna"], inplace=True)
        signal.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    rvgi.name = f"RVGI_{length}_{swma_length}"
    signal.name = f"RVGIs_{length}_{swma_length}"
    rvgi.category = signal.category = "momentum"

    data = {rvgi.name: rvgi, signal.name: signal}
    df = DataFrame(data, index=close.index)
    df.name = f"RVGI_{length}_{swma_length}"
    df.category = rvgi.category

    return df
