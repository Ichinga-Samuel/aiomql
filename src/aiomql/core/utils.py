import asyncio
import time
from logging import getLogger

from .config import Config

logger = getLogger(__name__)

async def auto_commit():
    config = Config()
    try:
        with config.state.conn as conn:
            while config.shutdown is False:
                await config.state.acommit(conn=conn, close=False)
                await sleep(config.db_commit_interval)
    except Exception as err:
        logger.error("%s: Error occurred in auto_commit", err)


async def backtest_sleep(secs):
    """An async sleep function for use during backtesting."""
    config = Config()
    secs = config.backtest_engine.cursor.time + secs
    while secs > config.backtest_engine.cursor.time:
        await asyncio.sleep(0)


async def sleep(secs):
    if Config.mode == "backtest":
        await backtest_sleep(secs)
    else:
        await asyncio.sleep(secs)

def sleep_sync(secs):
    if Config.mode == "backtest":
        backtest_sleep_sync(secs)
    else:
        time.sleep(secs)

def backtest_sleep_sync(secs):
    """A sleep function for use during backtesting."""
    config = Config()
    secs = config.backtest_engine.cursor.time + secs
    while secs > config.backtest_engine.cursor.time:
        time.sleep(0)
