# -*- coding: utf-8 -*-
from numpy import nan, roll
from pandas import Series
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_bool, v_offset, v_pos_default, v_series



def percent_return(
    close: Series, length: Int = None, cumulative: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Percent Return

    Calculates the percent return.

    Sources:
        * [stackoverflow](https://stackoverflow.com/questions/31287552/logarithmic-returns-in-pandas-dataframe)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```1```
        cumulative (bool): If True, returns the cumulative returns.
            Default: ```False```
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

    cumulative = v_bool(cumulative, False)
    offset = v_offset(offset)

    # Calculate
    np_close = close.to_numpy()
    if cumulative:
        pr = (np_close / np_close[0]) - 1
    else:
        pr = (np_close / roll(np_close, length)) - 1
        pr[:length] = nan
    pct_return = Series(pr, index=close.index)

    # Offset
    if offset != 0:
        pct_return = pct_return.shift(offset)

    # Fill
    if "fillna" in kwargs:
        pct_return.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    pct_return.name = f"{'CUM' if cumulative else ''}PCTRET_{length}"
    pct_return.category = "performance"

    return pct_return
