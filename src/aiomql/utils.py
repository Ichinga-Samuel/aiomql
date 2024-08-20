"""Utility functions for aiomql."""

import decimal
import random
from functools import wraps, partial
import asyncio

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


def backoff_decorator(func=None, *, max_retries: int = 3, retries: int = 0, delay: int = 1, error=None) -> callable:
    if func is None:
        return partial(backoff_decorator, max_retries=max_retries, retries=retries, delay=delay, error=error)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        nonlocal delay, retries

        try:
            res = await func(*args, **kwargs)
            if res == error:
                raise Exception('Invalid return type')
            return res

        except Exception as _:
            await asyncio.sleep(delay * 2 ** retries + random.uniform(0, 1))
            delay += 1
            retries += 1
            return await wrapper(*args, **kwargs)
    return wrapper
