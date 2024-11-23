import asyncio
import json
import shutil
from logging import getLogger
from pathlib import Path

import pytest
from aiomql.core import Config
from aiomql.core.meta_trader import MetaTrader

logger = getLogger(__name__)


async def cleanup():
    try:
        shutil.rmtree(Path("tests/live/configs"), ignore_errors=True)
        Path.unlink(Path("tests/live/test.json"), missing_ok=True)
        shutil.rmtree(Path("tests/live/trade_records"), ignore_errors=True)
        shutil.rmtree(Path("tests/live/backtesting"), ignore_errors=True)
        await close_all_positions()
        await MetaTrader().shutdown()
    except Exception as err:
        logger.error(f"Failed to complete cleanup: {err}")


async def close_all_positions():
    try:
        mt = MetaTrader()
        positions = await mt.positions_get()
        tasks = []
        for position in positions:
            order_type = mt.ORDER_TYPE_BUY if position.type == mt.ORDER_TYPE_SELL else mt.ORDER_TYPE_SELL
            req = {
                "action": mt.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": position.ticket,
                "price": position.price_current,
            }
            tasks.append(mt.order_send(req))
        await asyncio.gather(*tasks)
    except Exception as err:
        logger.error(f"Failed to close all positions: {err}")


@pytest.fixture(scope="package", autouse=True)
async def config(request):
    Path("tests/live/configs").mkdir(exist_ok=True)
    with open("aiomql.json", "r") as fh, open("tests/live/configs/test2.json", "w") as fh1, open(
        "tests/live/test.json", "w"
    ) as fh2:
        data = json.load(fh)
        json.dump(data, fh1, indent=2)
        json.dump(data, fh2, indent=2)
    config = Config(root="tests/live", config_file="tests/live/test.json")
    yield config
    await cleanup()


@pytest.fixture(scope="package", autouse=True)
async def mt():
    mt = MetaTrader()
    await mt.initialize()
    await mt.login()
    yield mt
    await mt.shutdown()
