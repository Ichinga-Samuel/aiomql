"""Utility functions for percentage-based calculations.

This module provides a collection of mathematical utility functions for
calculating percentage differences, positions, changes, and adjustments.
"""


def get_price_diff_pct(first: float, second: float) -> float:
    """Calculate the percentage difference between two values.

    Computes the absolute difference between two values as a percentage
    of their average. This is useful for comparing how different two
    values are relative to their magnitude.

    Args:
        first: The first numeric value.
        second: The second numeric value.

    Returns:
        The percentage difference between the two values.

    Examples:
        >>> get_price_diff_pct(100, 110)
        9.523809523809524
        >>> get_price_diff_pct(50, 50)
        0.0
        >>> get_price_diff_pct(200, 100)
        66.66666666666666
    """
    diff = abs(first - second)
    div = (first + second) / 2
    return (diff / div) * 100


def get_price_in_range_pct(start: float, end: float, value: float) -> float:
    """Calculate the percentage position of a value within an interval.

    Determines where a given value falls within a range, expressed as
    a percentage. A value equal to `start` returns 0%, and a value
    equal to `end` returns 100%.

    Args:
        start: The starting value of the interval.
        end: The ending value of the interval.
        value: The value whose position is to be calculated.

    Returns:
        The percentage position of the value within the interval.

    Examples:
        >>> get_price_in_range_pct(0, 100, 50)
        50.0
        >>> get_price_in_range_pct(10, 20, 15)
        50.0
        >>> get_price_in_range_pct(0, 100, 25)
        25.0
    """
    return ((value - start) / (end - start)) * 100


def get_price_at_pct(start: float, end: float, rate: float) -> float:
    """Calculate the value at a given percentage within an interval.

    Finds the value that corresponds to a specific percentage position
    within the range defined by `start` and `end`.

    Args:
        start: The starting value of the interval.
        end: The ending value of the interval.
        rate: The percentage (0-100) at which to find the value.

    Returns:
        The value at the specified percentage position within the interval.

    Examples:
        >>> get_price_at_pct(0, 100, 50)
        50.0
        >>> get_price_at_pct(10, 20, 50)
        15.0
        >>> get_price_at_pct(0, 200, 25)
        50.0
    """
    span = end - start
    position = start + ((rate / 100) * span)
    return position


def extend_range_by_pct(start: float, end: float, rate: float) -> float:
    """Extend the end of an interval by a given percentage.

    Calculates a new endpoint by extending the interval beyond `end`
    by a percentage of the interval's span.

    Args:
        start: The starting value of the interval.
        end: The ending value of the interval.
        rate: The percentage by which to extend the interval.

    Returns:
        The new extended endpoint value.

    Examples:
        >>> extend_range_by_pct(0, 100, 50)
        150.0
        >>> extend_range_by_pct(10, 20, 100)
        30.0
        >>> extend_range_by_pct(0, 50, 20)
        60.0
    """
    span = end - start
    span *= (rate / 100)
    return end + span


def get_price_change_pct(start_value: float, end_value: float) -> float:
    """Calculate the percentage change from one value to another.

    Computes how much a value has changed from its starting point to
    its ending point, expressed as a percentage of the starting value.

    Args:
        start_value: The initial value.
        end_value: The final value.

    Returns:
        The percentage change from start_value to end_value.
        Positive values indicate an increase, negative values indicate a decrease.

    Examples:
        >>> get_price_change_pct(100, 150)
        50.0
        >>> get_price_change_pct(200, 100)
        -50.0
        >>> get_price_change_pct(50, 50)
        0.0
    """
    return ((end_value - start_value) / start_value) * 100


def increase_value_by_pct(value: float, rate: float) -> float:
    """Increase a value by a given percentage.

    Computes the result of increasing a value by a specified percentage.

    Args:
        value: The original value to be increased.
        rate: The percentage by which to increase the value.

    Returns:
        The increased value.

    Examples:
        >>> round(increase_value_by_pct(100, 10), 2)
        110.0
        >>> increase_value_by_pct(50, 20)
        60.0
        >>> increase_value_by_pct(200, 50)
        300.0
    """
    return value * ((100 + rate) / 100)


def decrease_value_by_pct(value: float, rate: float) -> float:
    """Decrease a value by a given percentage.

    Computes the result of decreasing a value by a specified percentage.

    Args:
        value: The original value to be decreased.
        rate: The percentage by which to decrease the value.

    Returns:
        The decreased value.

    Examples:
        >>> decrease_value_by_pct(100, 10)
        90.0
        >>> decrease_value_by_pct(50, 20)
        40.0
        >>> decrease_value_by_pct(200, 50)
        100.0
    """
    return value * ((100 - rate) / 100)
