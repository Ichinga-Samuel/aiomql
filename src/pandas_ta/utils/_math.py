# -*- coding: utf-8 -*-
from collections.abc import Callable
from functools import reduce
from math import floor as mfloor
from operator import mul
from sys import float_info as sflt

from numpy import (
    all, append, array, broadcast_to, concatenate, corrcoef, diff, dot, exp,
    fabs, float64, full, isnan, log, logical_and, nan, nanmean,
    nansum, ndarray, newaxis, ones, pad, seterr, sign, sqrt, sum, triu, zeros
)
from numpy import max as np_max
from numpy import min as np_min
from numpy.lib.stride_tricks import sliding_window_view

from pandas import DataFrame, Series
from numba import njit
from pandas_ta._typing import (
    Array,
    DictLike,
    Float,
    Int,
    IntFloat,
    List,
    Optional
)
from pandas_ta.maps import Imports
from pandas_ta.utils._validate import (
    v_float,
    v_int,
    v_lowerbound,
    v_offset,
    v_pos_default,
    v_scalar,
    v_series
)

__all__ = [
    "combination",
    "cube",
    "consecutive_streak",
    "df_error_analysis",
    "erf",
    "fibonacci",
    "geometric_mean",
    "hpoly",
    "ifisher",
    "log_geometric_mean",
    "pascals_triangle",
    "percent_rank",
    "remap",
    "strided_window",
    "sum_signed_rolling_deltas",
    "symmetric_triangle",
    "weights",
    "zero",
]



def combination(
    n: Int = 1, r: Int = 0,
    repetition: bool = False, multichoose: bool = False
) -> Int:
    """Combination

    Combination computation.

    Sources:
        * [stackoverflow](https://stackoverflow.com/questions/4941753/is-there-a-math-ncr-function-in-python)

    Parameters:
        n (Int): ```n```
        r (Int): ```r```
        repetition (bool): Apply repetition.
        multichoose (bool): Apply multichoose.

    Returns:
        (Int): Combination value

    Note:
        ```n``` Choose ```r```: ```(n r)```
    """
    n, r = int(fabs(n)), int(fabs(r))

    if repetition or multichoose:
        n = n + r - 1

    # if r < 0: return None
    r = min(n, n - r)
    if r == 0:
        return 1

    numerator = reduce(mul, range(n, n - r, -1), 1)
    denominator = reduce(mul, range(1, r + 1), 1)
    return numerator // denominator



def consecutive_streak(x: Array) -> Array:
    """Consecutive Streak

    Computes the streak of consecutive value increases or decreases.

    Parameters:
        x (Array): Numpy array.

    Returns:
        (Array): Streak array of element changes.

    Note: Logic
        Yield an array where each value represents the streak value
        for that bar.

        1. Computes the difference between consecutive values.
        2. Assigns 1 for each positive change, -1 for each negative
           change -1 and 0 for no change.

    Note: Streaks
        * Positive: Consecutive bars of value increases
        * Negative: Consecutive bars of value decreases
        * Zero: When direction of the value change reverses

    Example:
        ```py
        prices = np.array([100, 101, 102, 100, 100, 101, 102, 103])
        result = consecutive_streak(prices)
        expected_result = np.array([0, 1, 1, -1, 0, 1, 1, 1])
        np.array_equal(result, expected_result)
        ```
    """
    return concatenate(([0], sign(diff(x))))



def cube(
    src: Series, pwr: IntFloat = None, signal_offset: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Cube Transform

    This transform, by John Ehlers, is used to compress Svalues near zero for
    a normalized oscillator like the Inverse Fisher Transform.

    In other words, a Power Transform/Function: ```result = src ^ pwr```

    Sources:
        * [rengel8](https://github.com/rengel8) based on Markus K.
          (cryptocoinserver)'s source
        * "Cycle Analytics for Traders", 2014, by John Ehlers, page 200

    Parameters:
        src (pd.Series): Source
        pwr (float): The transform power. Default: ```3```
        signal_offset (int): Signal offset. Default: ```-1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 2 columns

    Note:
        * Values near ```-1``` and ```1``` are nearly unchanged, whereas
          values near zero are reduced.
        * Input effects of spectral dilation should have been removed
          (i.e. roofing filter).

    """
    # Validate
    src = v_series(src)
    pwr = v_lowerbound(pwr, 3.0, 3.0, strict=False)
    signal_offset = v_int(signal_offset, -1, 0)
    offset = v_offset(offset)

    # Calculate
    result = src ** pwr
    ct = Series(result, index=src.index)
    ct_signal = Series(result, index=src.index)

    # Offset
    if offset != 0:
        ct = ct.shift(offset)
        ct_signal = ct_signal.shift(offset)
    if signal_offset != 0:
        ct = ct.shift(signal_offset)
        ct_signal = ct_signal.shift(signal_offset)

    if all(isnan(ct)) and all(isnan(ct_signal)):
        return  # Emergency Break

    # Fill
    if "fillna" in kwargs:
        ct.fillna(kwargs["fillna"], inplace=True)
        ct_signal.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{pwr}_{signal_offset}"
    ct.name = f"CUBE{_props}"
    ct_signal.name = f"CUBEs{_props}"
    ct.category = ct_signal.category = "transform"

    data = {ct.name: ct, ct_signal.name: ct_signal}
    df = DataFrame(data, index=src.index)
    df.name = f"CUBE{_props}"
    df.category = ct.category

    return df



def erf(x: IntFloat) -> Float:
    """Error Function

    Computes the erf(x)

    Sources:
        * Handbook of Mathematical Functions, formula 7.1.26.
        * [stackoverflow](https://stackoverflow.com/questions/457408/is-there-an-easily-available-implementation-of-erf-for-python)

    Parameters:
        x (IntFloat): ```x``` value.

    Returns:
        (Float): Error value
    """
    x_sign = sign(x)
    x = abs(x)

    # constants
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911

    # A&S formula 7.1.26
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2)
               * t + a1) * t * exp(-x * x)
    return x_sign * y  # erf(-x) = -erf(x)



@njit(cache=True)
def fibonacci(n: Int = 2, weighted: bool = False) -> Array:
    """Fibonacci

    Computes Fibonacci values using it's closed form.

    Parameters:
        n (Int): Number of terms (n >= 2)
        weighted (bool): Return weighted version.

    Returns:
        (Array): Numpy array results
    """
    n = n if n > 1 else 2
    sqrt5 = sqrt(5.0)
    phi, psi = 0.5 * (1.0 + sqrt5), 0.5 * (1.0 - sqrt5)

    result = zeros(n)
    for i in range(0, n):
        result[i] = float(phi ** (i + 1) - psi ** (i + 1)) / sqrt5

    if weighted:
        return result / result.sum()
    return result



def geometric_mean(x: Series) -> Float:
    """Geometric Mean

    Computes the Geometric Mean of positive values.

    Parameters:
        x (Series): Values

    Returns:
        (Float): Geometric Mean
    """
    n = x.size
    if n < 1:
        return x.iloc[0]

    has_zeros = 0 in x.to_numpy()
    if has_zeros:
        x = x.fillna(0) + 1
    if all(x > 0):
        mean = x.prod() ** (1 / n)
        return mean if not has_zeros else mean - 1
    return 0



def hpoly(x: Array, v: IntFloat) -> Float:
    """Horner's Polynomial

    Evaluates a polynomial with an array of polynomial coefficients, ```x```,
    and a value, ```v```, using Horner's Calculation for Polynomial
    Evaluation.

    Parameters:
        x (Array): Polynomial coefficients as ```np.array```
        v (IntFloat): Value

    Tip: Performance
        Use a ```np.array``` for best performance.

    Example:
        ```py
        coeffs_0 = [4, -3, 0, 1] # 4x^3 - 3x^2 + 0x + 1
        coeffs_1 = np.array(coeffs_0) # Faster
        coeffs_2 = pd.Series(coeffs_0).to_numpy()
        x = -6.5

        hpoly(coeffs_0, x) => -1224.25
        hpoly(coeffs_1, x) or hpoly(coeffs_2, x) => -1224.25 # Faster
        ```
    """
    if not isinstance(x, ndarray):
        x = array(x)

    m, y = x.size, x[0]

    for i in range(1, m):
        y = x[i] + v * y
    return y



def ifisher(
    x: Series,
    amp: IntFloat = None, signal_offset: Int = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Inverse Fisher Transform

    This transform function, by John Ehlers, attempts to create clearer
    signals by changing the Probability Distribution Function (pdf) for the
    results of known oscillator-indicators.

    Sources:
        * [rengel8](https://github.com/rengel8) based on Markus K.
          (cryptocoinserver)'s source
        * "Cycle Analytics for Traders", 2014, by John Ehlers, page 198
        * [mesasoftware](https://www.mesasoftware.com/papers/TheInverseFisherTransform.pdf)

    Parameters:
        x (pd.Series): Normalized to range ```[-1, 1]```
        amp (float): Amplifier. Default: ```1```
        signal_offset (int): Signal line offset. Default: ```-1```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame): 2 columns

    Note:
        * Normalized input, ```x```, with range ```[-1, 1]```
        * Data range of ```[-0.5, 0.5]``` would not have a significant impact

    Example: Preparation Examples
        Or use _ta.remap()_ function to prep

        (RSI - 50) * 0.1        RSI [0 to 100] -> -5 to 5

        (RSI - 50) * 0.02       RSI [0 to 100] -> -1 to 1 (use amp of 5 to match input of example above)
    """
    # Validate
    x = v_series(x)
    amp = v_scalar(amp, 1.0)
    signal_offset = v_int(signal_offset, -1, 0)
    offset = v_offset(offset)

    # Calculate
    np_x = x.to_numpy()
    is_remapped = logical_and(np_x >= -1, np_x <= 1)
    if not all(is_remapped):
        _np_max, _np_min = np_max(np_x), np_min(np_x)
        x_map = remap(x,
            from_min=_np_min, from_max=_np_max,
            to_min=-1, to_max=1
        )
        if x_map is None or all(isnan(x_map.to_numpy())):
            return  # Emergency Break
        np_x = x_map.to_numpy()

    amped = exp(amp * np_x)
    result = (amped - 1) / (amped + 1)

    inv_fisher = Series(result, index=x.index)
    signal = Series(result, index=x.index)

    # Offset
    if offset != 0:
        inv_fisher = inv_fisher.shift(offset)
        signal = signal.shift(offset)

    if signal_offset != 0:
        inv_fisher = inv_fisher.shift(offset)
        signal = signal.shift(offset)

    # Fill
    if "fillna" in kwargs:
        inv_fisher.fillna(kwargs["fillna"], inplace=True)
        signal.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = f"_{amp}"
    inv_fisher.name = f"INVFISHER{_props}"
    signal.name = f"INVFISHERs{_props}"

    data = {inv_fisher.name: inv_fisher, signal.name: signal}
    df = DataFrame(data, index=x.index)
    df.name = f"INVFISHER{_props}"

    return df



def log_geometric_mean(x: Series) -> Float:
    """Logarithmic Geometric Mean

    Computes the Logarithmic Geometric Mean of positive values.

    Parameters:
        x (Series): Values

    Returns:
        (Float): LogGeometric Mean or zero
    """
    n = x.size
    if n > 1:
        x = x.fillna(0) + 1
        if all(x > 0):
            return exp(log(x).sum() / n) - 1
    return 0



def pascals_triangle(
    n: Int = None, inverse: bool = False, weighted: bool = False
) -> Array:
    """Pascal's Triangle

    The ```n```th row of Pascal's Triangle.

    Parameters:
        n (Int): ```n^th``` row of Pascal' Triange
        inverse (bool): Return Inverse weighted.
        weighted (bool): Return weighted.

    Returns:
        (Array): Classical, Weighted, or Inversely

    Example:
        ```py
        # Classical
        pt4 = pascals_triangle(4)
        # pt4 = [1, 4, 6, 4, 1]

        # Inverse
        invpt4 = pascals_triangle(4, inverse=True)
        # invpt4 = [0.9375, 0.75, 0.625, 0.75, 0.9375]

        # Weighted
        wpt4 = pascals_triangle(4, weighted=True)
        # wpt4 = [0.0625, 0.25, 0.375, 0.25, 0.0625]
        ```
    """
    n = int(fabs(n)) if n is not None else 0

    # Calculation
    triangle = array([combination(n=n, r=i) for i in range(0, n + 1)])
    triangle_sum = sum(triangle)
    triangle_weights = triangle / triangle_sum
    inverse_weights = 1 - triangle_weights

    if weighted and inverse:
        return inverse_weights
    if weighted:
        return triangle_weights
    if inverse:
        return None

    return triangle



def percent_rank(x: Series, length: int) -> Series:
    """Percent Rank

    Percent Rank of values over a specified length.

    Parameters:
        x (Series): ```x``` values
        length (int): The period.

    Returns:
        (Series): Percent Rank values.

    Note: Logic
        Yield a Series where the initial part (up to ```length - 1```) is
        padded with NaNs, and the rest contains the Percent Rank values.

        1. Computes the daily percentage returns.
        2. Creates a rolling window of these returns.
        3. Compares each value in the window to the current value (the
           last value in each window).
        4. Percent Rank is calculated as the percentage of values in each
           window that are less than the current value.

    Example:
        ```py
        x = Series([100, 80, 75, 123, 140, 80, 70, 40, 100, 120]).to_numpy()
        result = percent_rank(x, 3)
        expected_result = Series([np.nan, np.nan, np.nan, 66.666667, 66.666667, 0.0, 33.333333, 0.0, 100.0, 66.666667])
        np.allclose(result, expected_result, rtol=1e-6, equal_nan=True)
        ```
    """
    np_pctchg = x.pct_change().to_numpy()

    rws = sliding_window_view(np_pctchg, window_shape=(length + 1,))
    comparison_matrix = rws[:, :-1] < rws[:, -1, newaxis]

    prs = 100 * nanmean(comparison_matrix, axis=1)
    result = full(len(x), nan)
    result[length:] = prs

    # return Series(padded_percent_ranks, index=x.index)
    return result



def remap(
    x: Series, from_min: IntFloat = None, from_max: IntFloat = None,
    to_min: IntFloat = None, to_max: IntFloat = None,
    offset: Int = None, **kwargs: DictLike
) -> Series:
    """remap

    The standard method of transforming from a source range to a target range
    using Max-Min. Useful for bounded sources; not unbounded sources
    like _ohlcv_ data.

    Sources:
        * Linear (Max-Min) Normalization

    Parameters:
        x (pd.Series): Series of 'x's
        from_min (IntFloat): Input minimum. Default: ```0.0```
        from_max (IntFloat): Input maximum. Default: ```100.0```
        to_min (IntFloat): Output minimum. Default: ```0.0```
        to_max (IntFloat): Output maximum. Default: ```100.0```
        offset (Int): Post shift. Default: ```0```

    Other Parameters:
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.Series): 1 column
    """
    # Validate
    x = v_series(x)
    from_min = v_float(from_min, 0.0, 0.0)
    from_max = v_float(from_max, 100.0, 0.0)
    to_min = v_float(to_min, -1.0, 0.0)
    to_max = v_float(to_max, 1.0, 0.0)
    offset = v_offset(offset)

    # Calculate
    frange, trange = from_max - from_min, to_max - to_min
    if frange <= 0 or trange <= 0:
        return
    result = to_min + (trange / frange) * (x.to_numpy() - from_min)
    result = Series(result, index=x.index)

    # Offset
    if offset != 0:
        result = result.shift(offset)

    # Fill
    if "fillna" in kwargs:
        result.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    result.name = f"REMAP_{from_min}_{from_max}_{to_min}_{to_max}"
    # result.name = f"{x.name}_{from_min}_{from_max}_{to_min}_{to_max}" # OR

    return result



def strided_window(x: Array, length: Int) -> Array:
    """Strided Window

    Creates a strided window view.

    Source:
        * [numpy](https://numpy.org/devdocs/reference/generated/numpy.lib.stride_tricks.as_strided.html)
        * [Issue #285](https://github.com/twopirllc/pandas-ta/issues/285)

    Parameters:
        x (Array): Source
        length (Int): Window period.

    Returns:
        (Array): Numpy Array of Strided Window Arrays

    Warning:
        Use if necessary, otherwise avoid when possible!
    """
    from numpy.lib.stride_tricks import as_strided
    strides = x.strides + (x.strides[-1],)
    shape = x.shape[:-1] + (x.shape[-1] - length + 1, length)
    return as_strided(x, shape=shape, strides=strides, writeable=False)



def sum_signed_rolling_deltas(
    open_: Series, close: Series, length: Int, exclusive: bool = True
) -> Series:
    """Sum of Signed Rolling Series Deltas

    Calculates the sum of signed differences between the current closing bar
    and a rolling window of preceding opening bars. This sum is then padded
    to match the original series length.

    Parameters:
        open_ (pd.Series): ```open``` Series
        close (pd.Series): ```close``` Series
        length (Int): Window length. Default: ```4```
        exclusive (bool): Exclusive rolling window. Inclusive rolling window
            when ```False```.  Default: ```True```

    Returns:
        (pd.Series): 1 column

    Notes: Mode
        **Exclusive**: Rolling window excludes the current bar in the
        lookback period.

        **Inclusive**: Rolling window includes the current bar in the
        lookback period.

    Example:
        ```py
        open_ = Series([95, 83,  71, 132, 129, 145, 133, 101, 68, 96])
        close = Series([100, 110, 140,  80,  90,  60,  50,  40, 90, 110])

        result = sum_signed_rolling_deltas(close, open_, 4, exclusive=True)
        expected_result = Series([np.nan, np.nan, np.nan, np.nan, 0.0, -4.0, -4.0, -4.0, -4.0, 0.0])
        np.allclose(result, expected_result, rtol=1e-6, equal_nan=True)

        result = sum_signed_rolling_deltas(close, open_, 4, exclusive=False)
        expected_result = Series([np.nan, np.nan, np.nan, -1.0, 1.0, -3.0, -3.0, -3.0, -3.0, 1.0])
        np.allclose(result, expected_result, rtol=1e-6, equal_nan=True)
        ```
    """
    length = v_pos_default(length, 4)
    if not exclusive:
        length -= 1

    rolling_open = sliding_window_view(open_, window_shape=length)[:-1]

    close_broadcasted = broadcast_to(
        close[length:].to_numpy()[:, newaxis], rolling_open.shape
    )

    signed_deltas = sign(close_broadcasted - rolling_open)
    sum_signed_deltas = nansum(signed_deltas, axis=1).astype(float)

    return Series(
        pad(sum_signed_deltas, (length, 0), mode="constant", constant_values=nan),
        index=close.index,
    )


def symmetric_triangle(
    n: Int = None, weighted: bool = False
) -> List[IntFloat]:
    """Symmetric Triangle

    Symmetric Triangle creation

    Parameters:
        n (Int): Array return size
        weighted (bool): Return weighted.

    Returns:
        (List[IntFloat]): List of Symmetric Triangle values.

    Example:
        ```py
        # Default
        symt4 = ta.symmetric_triangle(4)
        # symt4 = [1, 2, 2, 1]

        # Weighted
        wsymt4 = ta.symmetric_triangle(4, weighted=True)
        # wsymt4 = [0.16666667 0.33333333 0.33333333 0.16666667]
        ```
    """
    n = int(fabs(n)) if n is not None else 2

    triangle = None
    if n == 2:
        triangle = [1, 1]

    if n > 2:
        if n % 2 == 0:
            front = [i + 1 for i in range(0, mfloor(n / 2))]
            triangle = front + front[::-1]
        else:
            front = [i + 1 for i in range(0, mfloor(0.5 * (n + 1)))]
            triangle = front.copy()
            front.pop()
            triangle += front[::-1]

    if weighted and isinstance(triangle, list):
        return triangle / sum(triangle)

    return triangle



def weights(w: Array) -> Callable:
    """Weights

    Prepares weights for the dot product

    Parameters:
        w (Array): Input

    Returns:
        (Callable): Weights function for dot product.
    """
    def _dot(x):
        return dot(w, x)
    return _dot



def zero(x: IntFloat) -> IntFloat:
    """Zero

    Zeros inputs near zero.

    Parameters:
        x (IntFloat): Value to attempt to zero

    Returns:
        (IntFloat): ```0``` or ```x```
    """
    return 0 if abs(x) < sflt.epsilon else x



# TESTING



def df_error_analysis(
    A: DataFrame, B: DataFrame,
    plot: bool = False, triangular: bool = False,
    method: str = "pearson",
) -> DataFrame:
    """DataFrame Correlation Analysis"""
    _r_method = ["pearson", "kendall", "spearman"]
    corr_method = method if method in _r_method else _r_method[0]

    # Find their differences and correlation
    diff = A - B
    result = A.corr(B, method=corr_method)

    # For plotting
    if plot:
        diff.hist()
        if diff[diff > 0].any():
            diff.plot(kind="kde")

    if triangular:
        return result.where(triu(ones(result.shape)).astype(bool))

    return result
