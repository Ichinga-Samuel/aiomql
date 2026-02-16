"""Utility functions for the aiomql trading library.

This module provides utility functions for common operations such as sleeping
(with backtest support), automatic database commits, and other helper functions
used throughout the library.

Functions:
    auto_commit: Automatically commits state changes to the database.
    sleep: Async sleep that works in both live and backtest modes.
    sleep_sync: Synchronous sleep that works in both live and backtest modes.
    backtest_sleep: Async sleep for backtest mode using simulated time.
    backtest_sleep_sync: Sync sleep for backtest mode using simulated time.

Example:
    Using sleep in a trading bot::

        from aiomql.core.utils import sleep

        async def my_strategy():
            # This works in both live and backtest modes
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
                print("committing state to the database")
                await config.state.acommit(conn=conn, close=False)
                await sleep(config.db_commit_interval)
    except Exception as err:
        logger.error("%s: Error occurred in auto_commit", err)


async def backtest_sleep(secs):
    """Async sleep function for use during backtesting.

    Uses the backtest engine's simulated time cursor instead of real time,
    allowing backtests to run faster than real-time.

    Args:
        secs: Number of simulated seconds to sleep.
    """
    config = Config()
    secs = config.backtest_engine.cursor.time + secs
    while secs > config.backtest_engine.cursor.time:
        await asyncio.sleep(0)


async def sleep(secs):
    """Async sleep that works in both live and backtest modes.

    Automatically uses the appropriate sleep mechanism based on the
    current trading mode (live or backtest).

    Args:
        secs: Number of seconds to sleep.

    Example:
        >>> await sleep(5)  # Sleeps 5 seconds (real or simulated)
    """
    if Config.mode == "backtest":
        await backtest_sleep(secs)
    else:
        await asyncio.sleep(secs)


def sleep_sync(secs):
    """Synchronous sleep that works in both live and backtest modes.

    Automatically uses the appropriate sleep mechanism based on the
    current trading mode (live or backtest).

    Args:
        secs: Number of seconds to sleep.

    Example:
        >>> sleep_sync(5)  # Sleeps 5 seconds (real or simulated)
    """
    if Config.mode == "backtest":
        backtest_sleep_sync(secs)
    else:
        time.sleep(secs)


def backtest_sleep_sync(secs):
    """Synchronous sleep function for use during backtesting.

    Uses the backtest engine's simulated time cursor instead of real time,
    allowing backtests to run faster than real-time.

    Args:
        secs: Number of simulated seconds to sleep.
    """
    config = Config()
    secs = config.backtest_engine.cursor.time + secs
    while secs > config.backtest_engine.cursor.time:
        time.sleep(0)

