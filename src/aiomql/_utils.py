"""Utility functions for aiomql."""

import decimal
import random
from functools import wraps, partial
import asyncio
from threading import RLock
from logging import getLogger
from .core.config import Config

logger = getLogger(__name__)

async def backtest_sleep(secs):
    """An async sleep function for use during backtesting."""
    config = Config()
    sleep = config.backtest_engine.cursor.time + secs
    while sleep > config.backtest_engine.cursor.time:
        await asyncio.sleep(0)


# async def backtest_sleep(secs: float):
#     config = Config()
#     btc = config.backtest_controller
#     try:
#         if btc.parties == 2:
#             steps = int(secs) // config.backtest_engine.speed
#             steps = max(steps, 1)
#             config.backtest_engine.fast_forward(steps=steps)
#             btc.wait()
#
#         elif btc.parties > 2:
#             _time = config.backtest_engine.cursor.time + secs
#             while _time > config.backtest_engine.cursor.time:
#                 btc.wait()
#         else:
#             btc.wait()
#     except Exception as err:
#         btc.wait()
#         logger.error("Error: %s in backtest_sleep", err)


def dict_to_string(data: dict, multi=False) -> str:
    """Convert a dict to a string. Useful for logging.

    Args:
        data (dict): The dict to convert.
        multi (bool, optional): If True, each key-value pair will be on a new line. Defaults to False.

    Returns:
        str: The string representation of the dict.
    """
    sep = "\n" if multi else ", "
    return f"{sep}".join(f"{key}: {value}" for key, value in data.items())


def backoff_decorator(func=None, *, max_retries: int = 3, retries: int = 0) -> callable:
    """A decorator to retry a function a number of times before giving up.
    Args:
        func (callable, optional): The function to decorate. Defaults to None.
        max_retries (int, optional): The maximum number of retries. The default is 3.
        retries (int, optional): The number of retries. The default is 0
    """
    if func is None:
        return partial(backoff_decorator, max_retries=max_retries, retries=retries)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        nonlocal retries
        try:
            res = await func(*args, **kwargs)
            retries = 0
            return res
        except Exception as err:
            if max_retries == retries:
                retries = 0
                logger.error("An Error %s: occurred in %s", err, func.__name__)
                raise err
            retries += 1
            if Config().mode != "backtest":
                delay = 2 ** retries + random.uniform(0, 1)
                logger.warning("An Error %s: occurred in %s, trying again in %f seconds",
                               err, func.__name__, delay)
                await asyncio.sleep(delay)
            return await wrapper(*args, **kwargs)
    return wrapper


def error_handler(func=None, *, msg="", exe=Exception, response=None, log_error_msg=True):
    """A decorator to handle errors in an async function.
    Args:
        func (callable, optional): The function to decorate. Defaults to None.
        msg (str, optional): The error message to log. Defaults to "".
        exe (Exception, optional): The exception to catch. Defaults to Exception.
        response (Any, optional): The response to return when an error occurs. Defaults to None.
        log_error_msg (bool, optional): If True, log the error message. Defaults to True.
    """
    if func is None:
        return partial(error_handler, msg=msg, exe=exe, response=response, log_error_msg=log_error_msg)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            res = await func(*args, **kwargs)
            return res
        except exe as err:
            if log_error_msg:
                logger.error(f"Error in {func.__name__}: {msg or err}")
            return response

    return wrapper


def error_handler_sync(func=None, *, msg="", exe=Exception, response=None, log_error_msg=True):
    """A decorator to handle errors in a synchronous function.

    Args:
        func (callable, optional): The function to decorate. Defaults to None.
        msg (str, optional): The error message to log. Defaults to "".
        exe (Exception, optional): The exception to catch. Defaults to Exception.
        response (Any, optional): The response to return when an error occurs. Defaults to None.
        log_error_msg (bool, optional): If True, log the error message. Defaults to True.
    """
    if func is None:
        return partial(error_handler, msg=msg, exe=exe, response=response, log_error_msg=log_error_msg)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except exe as err:
            if log_error_msg:
                logger.error(f"Error in {func.__name__}: {msg or err}")
            return response

    return wrapper


def round_down(value: int | float, base: int) -> int | float:
    """Round down a number to the nearest base.
    Args:
        value (int | float): The number to round down.
        base (int): The base to round down to.

    Returns:
        (int | float): The rounded down number.
    """
    return int(value) if value % base == 0 else int(value - (value % base))


def round_up(value: int | float, base: int) -> int:
    return int(value) if value % base == 0 else int(value + base - (value % base))


# noinspection PyShadowingNames
def round_off(value: float, step: float, round_down: bool = False) -> float:
    """Round off a number to the nearest step.

    Args:
        value (float): The number to round off.
        step (float): The step to round off to.
        round_down (bool, optional): If True, the number is rounded down otherwise it is rounded up. Defaults to False.

    Returns:
        float: The rounded off number.
    """
    with decimal.localcontext() as ctx:
        ctx.rounding = decimal.ROUND_DOWN if round_down else decimal.ROUND_UP
        return float(decimal.Decimal(str(value)).quantize(decimal.Decimal(str(step))))


def async_cache(fun):
    """A decorator to cache the result of an async function."""
    @wraps(fun)
    async def wrapper(*args, **kwargs):
        key = (args, frozenset(kwargs.items()))
        with wrapper.lock:
            if key not in wrapper.cache:
                wrapper.cache[key] = await fun(*args, **kwargs)
            return wrapper.cache[key]

    wrapper.lock = RLock()
    wrapper.cache = {}
    return wrapper
