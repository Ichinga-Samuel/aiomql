"""
Combine error_handler and error_handler_sync into one function

Author: Abel Nagy
"""
import asyncio
from functools import wraps, partial
from logging import getLogger

logger = getLogger(__name__)


def error_handler(func=None, *, msg="", exe=Exception, response=None, log_error_msg=True):
    """A decorator to handle errors in an sync or async function.
    Args:
        func (callable, optional): The function to decorate. Defaults to None.
        msg (str, optional): The error message to log. Defaults to "".
        exe (Exception, optional): The exception to catch. Defaults to Exception.
        response (Any, optional): The response to return when an error occurs. Defaults to None.
        log_error_msg (bool, optional): If True, log the error message. Defaults to True.
    """
    if func is None:
        return partial(
            error_handler,
            msg=msg,
            exe=exe,
            response=response,
            log_error_msg=log_error_msg,
        )

    is_async = asyncio.iscoroutinefunction(func)

    if is_async:
        # This is the original error_handler for async functions
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                res = await func(*args, **kwargs)
                return res
            except exe as err:
                if log_error_msg:
                    logger.error(f"Error in {func.__name__}: {msg or err}")
                return response

        return async_wrapper
    else:

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                return res
            except exe as err:
                if log_error_msg:
                    logger.error(f"Error in {func.__name__}: {msg or err}")
                return response

        return sync_wrapper
