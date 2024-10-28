# noinspection PyTestUnpassedFixture
async def test_orders_manager(backtest_engine, sell_order, buy_order, period, positions):
    backtest_engine.reset(clear_data=True)
    await backtest_engine.setup_account(balance=100)
    backtest_engine.fast_forward(steps=100)
    await backtest_engine.order_send(request=sell_order)
    bo = await backtest_engine.order_send(request=buy_order)
    start = period['start']
    end = period['end']
    all_orders = backtest_engine.orders.get_orders_range(date_from=start, date_to=end)
    assert len(all_orders) == 2
    backtest_engine.fast_forward(steps=10_000)
    start2 = backtest_engine.cursor.time
    bo2 = await backtest_engine.order_send(request=buy_order)
    backtest_engine.fast_forward(steps=50)
    end2 = backtest_engine.cursor.time
    orders = backtest_engine.orders.history_orders_get(date_from=start2, date_to=end2)
    assert len(orders) == 1
    assert orders[0].ticket == bo2.order
    await positions.close_position_by_ticket(ticket=bo.order)
    orders = backtest_engine.orders.history_orders_get(position=bo.order)
    assert len(orders) <= 2
    orders = backtest_engine.orders.get_orders_range(date_from=start, date_to=end)
    assert len(orders) == backtest_engine.orders.history_orders_total(date_from=start, date_to=end) == len(backtest_engine.orders._data.keys())
