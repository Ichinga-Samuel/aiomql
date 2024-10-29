"""Utility functions for aiomql."""

import decimal
from .candle import Candles, Candle


def dict_to_string(data: dict, multi=False) -> str:
    """Convert a dict to a string. Useful for logging.

    Args:
        data (dict): The dict to convert.
        multi (bool, optional): If True, each key-value pair will be on a new line. Defaults to False.

    Returns:
        str: The string representation of the dict.
    """
    sep = '\n' if multi else ', '
    return f"{sep}".join(f"{key}: {value}" for key, value in data.items())


def round_off(value: float, step: float, round_down: bool = False) -> float:
    """Round off a number to the nearest step."""
    with decimal.localcontext() as ctx:
        ctx.rounding = decimal.ROUND_DOWN if round_down else decimal.ROUND_UP
        return float(decimal.Decimal(str(value)).quantize(decimal.Decimal(str(step))))


def find_bearish_fractal(candles: Candles) -> Candle | None:
    for i in range(len(candles) - 3, 1, -1):
        if candles[i].high > max(candles[i - 1].high, candles[i + 1].high, candles[i - 2].high, candles[i + 2].high):
            return candles[i]


def find_bullish_fractal(candles: Candles) -> Candle | None:
    for i in range(len(candles) - 3, 1, -1):
        if candles[i].low < min(candles[i - 1].low, candles[i + 1].low, candles[i - 2].low, candles[i + 2].low):
            return candles[i]
