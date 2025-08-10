# -*- coding: utf-8 -*-
from pandas import Series
from numpy import log, nan, roll
from pandas_ta._typing import DictLike, Int
from pandas_ta.utils import v_bool, v_offset, v_pos_default, v_series



def log_return(
    close: Series, length: Int = None, cumulative: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """Log Return

    Calculates the logarithmic return.

    Sources:
        * [stackoverflow](https://stackoverflow.com/questions/31287552/logarithmic-returns-in-pandas-dataframe)

    Parameters:
        close (pd.Series): ```close``` Series
        length (int): The period. Default: ```20```
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
        r = np_close / np_close[0]
    else:
        r = np_close / roll(np_close, length)
        r[:length] = nan
    log_return = Series(log(r), index=close.index)

    # Offset
    if offset != 0:
        log_return = log_return.shift(offset)

    # Fill
    if "fillna" in kwargs:
        log_return.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    log_return.name = f"{'CUM' if cumulative else ''}LOGRET_{length}"
    log_return.category = "performance"

    return log_return
