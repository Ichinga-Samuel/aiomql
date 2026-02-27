"""Utility functions for the aiomql trading library.

This module provides utility functions for common operations such as sleeping
automatic database commits, and other helper functions
used throughout the library.

Functions:
    auto_commit: Automatically commits state changes to the database.
    sleep: Async sleep that works in both live.
    sleep_sync: Synchronous sleep that works in both live.

Example:
    Using sleep in a trading bot::

        from aiomql.core.utils import sleep

        async def my_strategy():
            await sleep(60)  # Wait 60 seconds
"""

import asyncio
import time
from logging import getLogger

from .config import Config

logger = getLogger(__name__)


async def auto_commit():
    """Automatically commits state changes to the database at regular intervals.

    Runs continuously in the background, committing the state to the database
    based on the configured commit interval until shutdown is signaled.

    Note:
        Uses Config.db_commit_interval to determine the commit frequency.
        Stops when Config.shutdown is set to True.
    """
    config = Config()
    try:
        with config.state.conn as conn:
            while config.shutdown is False:
                await config.state.acommit(conn=conn, close=False)
                await sleep(config.db_commit_interval)
    except Exception as err:
        logger.error("%s: Error occurred in auto_commit", err)


async def sleep(secs):
    """Async sleep that works in live mode.
    Args:
        secs: Number of seconds to sleep.

    Example:
        >>> await sleep(5)  # Sleeps 5 seconds (real or simulated)
    """
    await asyncio.sleep(secs)


def sleep_sync(secs):
    """Synchronous sleep that works in live mode.

    Automatically uses the appropriate sleep mechanism based on the
    Args:
        secs: Number of seconds to sleep.

    Example:
        >>> sleep_sync(5)  # Sleeps 5 seconds (real or simulated)
    """
    time.sleep(secs)
