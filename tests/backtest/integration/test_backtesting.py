from aiomql.contrib import ForexSymbol
from aiomql.core import MetaBackTester, BackTestEngine, GetData
from aiomql.lib import Order


async def make_buy_sell_orders():
    sym = ForexSymbol(name="BTCUSD")
    sym_info = await sym.mt5.symbol_info(sym.name)
    dsl = (sym_info.trade_stops_level + sym_info.spread) * 2 * sym_info.point
    sl = sym_info.ask - dsl
    tp = sym_info.ask + dsl
    buy_req = {
        "action": sym.mt5.TRADE_ACTION_DEAL,
        "symbol": sym.name,
        "volume": sym_info.volume_min,
        "type": sym.mt5.ORDER_TYPE_BUY,
        "price": sym_info.ask,
        "sl": sl,
        "tp": tp,
    }

    sell_req = buy_req.copy()
    sell_req["type"] = sym.mt5.ORDER_TYPE_SELL
    sell_req["price"] = sym_info.bid
    del sell_req["tp"]
    del sell_req["sl"]
    return {"buy": Order(**buy_req), "sell": Order(**sell_req)}


def test_trade_mode(config, backtest_engine, history, positions, order_sell, order_buy, btc_usd, capsys):
    print(config.filename, config.root)
    assert config.mode == "backtest"
    assert isinstance(backtest_engine, BackTestEngine)
    assert isinstance(history.mt5, MetaBackTester)
    assert isinstance(positions.mt5, MetaBackTester)
    assert isinstance(order_sell.mt5, MetaBackTester)
    assert isinstance(order_buy.mt5, MetaBackTester)
    assert isinstance(btc_usd.mt5, MetaBackTester)


async def test_order_send(backtest_engine, order_sell, order_buy):
    await backtest_engine.setup_account(balance=100)
    so = await backtest_engine.order_send(request=order_sell.request)
    bo = await backtest_engine.order_send(request=order_buy.request)
    assert so.retcode == 10009
    assert bo.retcode == 10009
    backtest_engine.reset(clear_data=True)


async def test_positions(backtest_engine, positions, order_sell, order_buy):
    await backtest_engine.setup_account(balance=100)
    so = await backtest_engine.order_send(request=order_sell.request)
    bo = await backtest_engine.order_send(request=order_buy.request)
    all_positions = await positions.get_positions()
    assert len(all_positions) == 2
    await positions.close_position_by_ticket(ticket=so.order)
    all_positions = await positions.get_positions()
    assert len(all_positions) == 1
    await positions.close_position_by_ticket(ticket=bo.order)
    all_positions = await positions.get_positions()
    assert len(all_positions) == 0
    backtest_engine.reset(clear_data=True)


async def test_history(backtest_engine, history, order_sell, order_buy, positions):
    await backtest_engine.setup_account(balance=100)
    so = await backtest_engine.order_send(request=order_sell.request)
    await backtest_engine.order_send(request=order_buy.request)
    await history.initialize()
    assert len(history.orders) == 2
    assert len(history.deals) == 2
    await positions.close_position_by_ticket(ticket=so.order)
    deals = await history.get_deals()
    assert len(deals) == 3
    backtest_engine.reset(clear_data=True)


async def test_margin(backtest_engine, order_sell, order_buy):
    await backtest_engine.setup_account(balance=100)
    so_margin = await backtest_engine.order_calc_margin(
        action=order_sell.action, volume=order_sell.volume, symbol=order_sell.symbol, price=order_sell.price
    )
    bo_margin = await backtest_engine.order_calc_margin(
        action=order_buy.action, volume=order_buy.volume, symbol=order_buy.symbol, price=order_buy.price
    )
    total_margin = so_margin + bo_margin
    await backtest_engine.order_send(request=order_sell.request)
    await backtest_engine.order_send(request=order_buy.request)
    # noinspection PyTestUnpassedFixture
    assert backtest_engine.positions.margin == total_margin == backtest_engine._account.margin
    backtest_engine.reset(clear_data=True)


async def test_account(backtest_engine, positions):
    await backtest_engine.setup_account(balance=100)
    backtest_engine.fast_forward(steps=100)
    balance = backtest_engine._account.balance
    equity = backtest_engine._account.equity
    orders = await make_buy_sell_orders()
    buy_order = orders["buy"]
    sell_order = orders["sell"]
    so = await backtest_engine.order_send(request=sell_order.request)
    bo = await backtest_engine.order_send(request=buy_order.request)
    backtest_engine.fast_forward(steps=22000)
    all_pos = await positions.get_positions()
    for _ in range(1000):
        backtest_engine.fast_forward(steps=1)
        await backtest_engine.tracker()
        all_pos = await positions.get_positions()
        if len(all_pos) == 1:
            break

    deal = backtest_engine.deals.history_deals_get(position=bo.order)
    bo_profit = deal[-1].profit
    assert len(all_pos) == 1
    assert (
        backtest_engine.positions.margin
        == backtest_engine._account.margin
        == backtest_engine.positions.margins[so.order]
    )
    profit = sum([pos.profit for pos in all_pos])
    n_balance = backtest_engine._account.balance
    n_equity = backtest_engine._account.equity
    assert backtest_engine._account.profit == profit
    assert n_balance == balance + bo_profit
    assert n_equity == equity + bo_profit + profit
    so_pos = await positions.get_position_by_ticket(ticket=so.order)
    gain = so_pos.profit
    await positions.close_position(position=so_pos)
    assert backtest_engine._account.balance == n_balance + gain
    backtest_engine.reset(clear_data=True)


async def test_wrapup(positions, buy_order, sell_order, backtest_engine, config):
    await backtest_engine.setup_account(balance=100)
    backtest_engine.fast_forward(steps=500)
    bo = await backtest_engine.order_send(request=buy_order)
    await backtest_engine.order_send(request=sell_order)
    backtest_engine.fast_forward(steps=5000)
    await backtest_engine.tracker()
    await positions.close_position_by_ticket(ticket=bo.order)
    await backtest_engine.wrap_up()
    last_balance = backtest_engine._account.balance
    last_equity = backtest_engine._account.equity
    last_profit = backtest_engine._account.profit
    tdata = GetData.load_data(name=config.backtest_dir / f"{backtest_engine.name}.pkl")
    new_bte = BackTestEngine(data=tdata, restart=False, assign_to_config=False, preload=False)
    assert new_bte._account.balance == last_balance
    assert new_bte._account.equity == last_equity
    assert new_bte._account.profit == last_profit
    assert new_bte.span == backtest_engine.span
    assert new_bte.range == backtest_engine.range
    assert new_bte.name == backtest_engine.name
    assert new_bte.cursor.time == backtest_engine.cursor.time
