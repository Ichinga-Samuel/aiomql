"""Utility functions for aiomql."""
import decimal
import random
from functools import wraps, partial
import asyncio
from logging import getLogger

logger = getLogger(__name__)


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


def error_handler(func=None, *, msg='', exe = Exception):
    if func is None:
        return partial(error_handler, msg=msg, exe=exe)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            res = await func(*args, **kwargs)
            return res
        except exe as err:
            logger.error(f'Error in {func.__name__}: {msg or err}')

    return wrapper

def error_handler_sync(func=None, *, msg='', exe=Exception):
    if func is None:
        return partial(error_handler, msg=msg, exe=exe)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except exe as err:
            logger.error(f'Error in {func.__name__}: {msg or err}')

    return wrapper

def round_down(value: int, base: int) -> int:
    return value if value % base == 0 else value  - (value % base)


def round_up(value: int, base: int) -> int:
    return value if value % base == 0 else value + base - (value % base)


def round_off(value: float, step: float, round_down: bool = False) -> float:
    """Round off a number to the nearest step."""
    with decimal.localcontext() as ctx:
        ctx.rounding = decimal.ROUND_DOWN if round_down else decimal.ROUND_UP
        return float(decimal.Decimal(str(value)).quantize(decimal.Decimal(str(step))))
