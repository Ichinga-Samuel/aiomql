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
        shutil.rmtree(Path('tests/configs'), ignore_errors=True)
        Path.unlink(Path('tests/test.json'), missing_ok=True)
        shutil.rmtree(Path('tests/trade_records'), ignore_errors=True)
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
            req = {'action': mt.TRADE_ACTION_DEAL, 'symbol': position.symbol, 'volume': position.volume,
                   'type': order_type, 'position': position.ticket, 'price': position.price_current}
            tasks.append(mt.order_send(req))
        await asyncio.gather(*tasks)
    except Exception as err:
        logger.error(f"Failed to close all positions: {err}")


@pytest.fixture(scope='session', autouse=True)
async def config(request):
    Path('tests/configs').mkdir(exist_ok=True)
    with open('aiomql.json', 'r') as fh, open('tests/configs/test2.json', 'w') as fh1, open('tests/test.json', 'w') as fh2:
        data = json.load(fh)
        json.dump(data, fh1, indent=2)
        json.dump(data, fh2, indent=2)
    config = Config(filename='test.json', root='tests')
    yield config
    await cleanup()


@pytest.fixture(scope='session')
async def mt():
    mt = MetaTrader()
    await mt.initialize()
    await mt.login()
    yield mt
    await mt.shutdown()


@pytest.fixture(scope='function')
async def sell_order(mt):
    sym = 'BTCUSD'
    sym_info = await mt.symbol_info(sym)
    return {'action': mt.TRADE_ACTION_DEAL, 'symbol': sym, 'volume': sym_info.volume_min,
           'type': mt.ORDER_TYPE_SELL, 'price': sym_info.bid}


@pytest.fixture(scope='function')
async def buy_order(mt):
    sym = 'BTCUSD'
    sym_info = await mt.symbol_info(sym)
    dsl = (sym_info.trade_stops_level + sym_info.spread) * 2 * sym_info.point
    sl = sym_info.ask - dsl
    tp = sym_info.ask + dsl
    return {'action': mt.TRADE_ACTION_DEAL, 'symbol': sym, 'volume': sym_info.volume_min,
           'type': mt.ORDER_TYPE_BUY, 'price': sym_info.ask, 'sl': sl, 'tp': tp}

@pytest.fixture(scope='class')
async def make_buy_sell_orders(mt):
    sym = 'BTCUSD'
    sym_info = await mt.symbol_info(sym)
    dsl = (sym_info.trade_stops_level + sym_info.spread) * 2 * sym_info.point
    sl = sym_info.ask - dsl
    tp = sym_info.ask + dsl
    req = {'action': mt.TRADE_ACTION_DEAL, 'symbol': sym, 'volume': sym_info.volume_min,
           'type': mt.ORDER_TYPE_BUY, 'price': sym_info.ask, 'sl': sl, 'tp': tp}
    await mt.order_send(req)
    req['type'] = mt.ORDER_TYPE_SELL
    req['price'] = sym_info.bid
    req['sl'] = sym_info.bid + dsl
    req['tp'] = sym_info.bid - dsl
    await mt.order_send(req)
