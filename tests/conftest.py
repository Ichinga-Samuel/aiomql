from aiomql.lib.symbol import Symbol
import pytest


@pytest.fixture(scope="function")
def btc_usd():
    return Symbol(name="BTCUSD")


@pytest.fixture(scope="function")
def eth_usd():
    return Symbol(name="ETHUSD")


@pytest.fixture(scope="function")
async def buy_order(btc_usd):
    sym = btc_usd
    sym_info = await sym.mt5.symbol_info(sym.name)
    dsl = (sym_info.trade_stops_level + sym_info.spread) * 2 * sym_info.point
    sl = sym_info.ask - dsl
    tp = sym_info.ask + dsl
    return {
        "action": sym.mt5.TRADE_ACTION_DEAL,
        "symbol": sym.name,
        "volume": sym_info.volume_min,
        "type": sym.mt5.ORDER_TYPE_BUY,
        "price": sym_info.ask,
        "sl": sl,
        "tp": tp,
    }


@pytest.fixture(scope="function")
async def sell_order(eth_usd):
    sym = eth_usd
    sym_info = await sym.mt5.symbol_info(sym.name)
    return {
        "action": sym.mt5.TRADE_ACTION_DEAL,
        "symbol": sym.name,
        "volume": sym_info.volume_min,
        "type": sym.mt5.ORDER_TYPE_SELL,
        "price": sym_info.bid,
    }


@pytest.fixture(scope="class")
async def make_buy_sell_orders():
    sym = Symbol(name="BTCUSD")
    sym_info = await sym.mt5.symbol_info(sym.name)
    dsl = (sym_info.trade_stops_level + sym_info.spread) * 2 * sym_info.point
    sl = sym_info.ask - dsl
    tp = sym_info.ask + dsl
    req = {
        "action": sym.mt5.TRADE_ACTION_DEAL,
        "symbol": sym.name,
        "volume": sym_info.volume_min,
        "type": sym.mt5.ORDER_TYPE_BUY,
        "price": sym_info.ask,
        "sl": sl,
        "tp": tp,
    }
    await sym.mt5.order_send(req)
    req["type"] = sym.mt5.ORDER_TYPE_SELL
    req["price"] = sym_info.bid
    req["sl"] = sym_info.bid + dsl
    req["tp"] = sym_info.bid - dsl
    await sym.mt5.order_send(req)
