def percentage_difference(first: float, second: float) -> float:
    """Find the percentage difference between two values"""
    diff = abs(first - second)
    div = (first + second) / 2
    return (diff / div) * 100


def percentage_position(start: float, end: float, value: float):
    """Find the percentage position of a value between two values"""
    return ((value - start) / (end - start)) * 100


def get_percentage_position(start: float, end: float, rate: float):
    """Find position within an interval based on a percentage"""
    span = end - start
    position = start + ((rate/100) * span)
    return position


def extend_interval_by_percentage(start: float, end: float, rate: float):
    """Extend the end of an interval by a factor"""
    span = end - start
    span *= (rate/100)
    return end + span


def percentage_change(start_value: float, end_value: float) -> float:
    """Find the percentage change from one value to another"""
    return ((end_value - start_value) / start_value) * 100


def percentage_increase(value: float, rate: float) -> float:
    """Increase the value by a factor"""
    return value * ((100 + rate) / 100)


def percentage_decrease(value: float, rate: float) -> float:
    """Increase the value by a factor"""
    return value * ((100 - rate) / 100)
