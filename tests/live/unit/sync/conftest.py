from aiomql.core.sync.meta_trader import MetaTrader
import pytest


@pytest.fixture(scope="class")
def sync_mt():
    """Provides a synchronous MetaTrader instance for the test class."""
    mt = MetaTrader()
    mt.initialize()
    mt.login()
    yield mt
    mt.shutdown()


@pytest.fixture(scope="function")
def buy_order_sync(btc_usd):
    """Creates a buy order request for BTCUSD."""
    mt = MetaTrader()
    sym_info = mt.symbol_info(btc_usd.name)
    dsl = (sym_info.trade_stops_level + sym_info.spread) * 2 * sym_info.point
    sl = sym_info.ask - dsl
    tp = sym_info.ask + dsl
    return {
        "action": mt.TRADE_ACTION_DEAL,
        "symbol": btc_usd.name,
        "volume": sym_info.volume_min,
        "type": mt.ORDER_TYPE_BUY,
        "price": sym_info.ask,
        "sl": sl,
        "tp": tp,
    }


@pytest.fixture(scope="function")
def sell_order_sync(eth_usd):
    """Creates a sell order request for ETHUSD."""
    mt = MetaTrader()
    sym_info = mt.symbol_info(eth_usd.name)
    return {
        "action": mt.TRADE_ACTION_DEAL,
        "symbol": eth_usd.name,
        "volume": sym_info.volume_min,
        "type": mt.ORDER_TYPE_SELL,
        "price": sym_info.bid,
    }


@pytest.fixture(scope="class")
def make_buy_sell_orders_sync():
    """Creates buy and sell orders for BTCUSD to ensure open positions exist."""
    mt = MetaTrader()
    sym_info = mt.symbol_info("BTCUSD")
    dsl = (sym_info.trade_stops_level + sym_info.spread) * 2 * sym_info.point
    sl = sym_info.ask - dsl
    tp = sym_info.ask + dsl
    req = {
        "action": mt.TRADE_ACTION_DEAL,
        "symbol": "BTCUSD",
        "volume": sym_info.volume_min,
        "type": mt.ORDER_TYPE_BUY,
        "price": sym_info.ask,
        "sl": sl,
        "tp": tp,
    }
    mt.order_send(req)
    req["type"] = mt.ORDER_TYPE_SELL
    req["price"] = sym_info.bid
    req["sl"] = sym_info.bid + dsl
    req["tp"] = sym_info.bid - dsl
    mt.order_send(req)
