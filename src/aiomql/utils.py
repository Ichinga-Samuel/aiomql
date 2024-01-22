"""Utility functions for aiomql."""

import decimal


def dict_to_string(data: dict, multi=True) -> str:
    """Convert a dict to a string. Useful for logging.

    Args:
        data (dict): The dict to convert.
        multi (bool, optional): If True, each key-value pair will be on a new line. Defaults to True.

    Returns:
        str: The string representation of the dict.
    """
    sep = '\n' if multi else ', '
    return f"{sep}".join(f"{key}: {value}" for key, value in data.items())


def round_off(value: float, step: float, round_down: bool = True) -> float:
    """Round off a number to the nearest step."""
    with decimal.localcontext() as ctx:
        ctx.rounding = decimal.ROUND_DOWN if round_down else decimal.ROUND_UP
        return float(decimal.Decimal(str(value)).quantize(decimal.Decimal(str(step))))