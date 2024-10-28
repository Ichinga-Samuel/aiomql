from datetime import datetime, UTC
import asyncio
import json
import shutil
from logging import getLogger
from pathlib import Path

import pytest
from aiomql.core import Config
from aiomql.core.meta_backtester import MetaBackTester
from aiomql.contrib import BackTestEngine
from aiomql.lib import Positions, History, Order

logger = getLogger(__name__)


async def cleanup():
    try:
        shutil.rmtree(Path('tests/backtest/configs'), ignore_errors=True)
        Path.unlink(Path('tests/backtest/test.json'), missing_ok=True)
        shutil.rmtree(Path('tests/backtest/trade_records'), ignore_errors=True)
        shutil.rmtree(Path('tests/backtest/backtesting'), ignore_errors=True)
        await close_all_positions()
        await MetaBackTester().shutdown()
    except Exception as err:
        logger.error(f"Failed to complete cleanup: {err}")


async def close_all_positions():
    try:
        mt = MetaBackTester()
        positions = await mt.positions_get()
        tasks = []
        for position in positions:
            order_type = mt.ORDER_TYPE_BUY if position.type == mt.ORDER_TYPE_SELL else mt.ORDER_TYPE_SELL
            req = {'action': mt.TRADE_ACTION_DEAL, 'symbol': position.symbol, 'volume': position.volume,
                   'type': order_type, 'position': position.ticket, 'price': position.price_current}
            tasks.append(mt.order_send(req))
        await asyncio.gather(*tasks)
    except Exception as err:
        logger.error(f"Failed to close all positions: {err}")


@pytest.fixture(scope='package', autouse=True)
async def config(request):
    Path('tests/backtest/configs').mkdir(exist_ok=True)
    with open('aiomql.json', 'r') as fh, open('tests/backtest/configs/test2.json', 'w') as fh1, open('tests/backtest/test.json', 'w') as fh2:
        data = json.load(fh)
        data['mode'] = 'backtest'
        json.dump(data, fh1, indent=2)
        json.dump(data, fh2, indent=2)
    config = Config(filename='test.json', root='tests/backtest')
    yield config
    await cleanup()


@pytest.fixture(scope='package', autouse=True)
async def mt():
    mt = MetaBackTester()
    await mt.initialize()
    await mt.login()
    yield mt
    await mt.shutdown()

@pytest.fixture(scope='package')
async def period():
    return {'start': datetime(2024, 2, 1, hour=8, tzinfo=UTC),
            'end': datetime(2024, 2, 7, hour=16, tzinfo=UTC)}

@pytest.fixture(scope='package')
async def backtest_engine(period):
    start = period['start']
    end = period['end']
    return BackTestEngine(start=start, end=end, name='backtest_data')


@pytest.fixture(scope='function')
def order_sell(sell_order):
    return Order(**sell_order)


@pytest.fixture(scope='function')
def order_buy(buy_order):
    return Order(**buy_order)


@pytest.fixture(scope='package')
def positions():
    return Positions()


@pytest.fixture(scope='package')
def history(period):
    start = period['start']
    end = period['end']
    return History(date_from=start, date_to=end)
