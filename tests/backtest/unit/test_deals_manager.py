# noinspection PyTestUnpassedFixture
async def test_deals_manager(backtest_engine, sell_order, buy_order, period, positions):
    backtest_engine.reset(clear_data=True)
    await backtest_engine.setup_account(balance=100)
    backtest_engine.fast_forward(steps=100)
    await backtest_engine.order_send(request=sell_order)
    bo = await backtest_engine.order_send(request=buy_order)
    start = period["start"]
    end = period["end"]
    all_deals = backtest_engine.deals.get_deals_range(date_from=start, date_to=end)
    assert len(all_deals) == 2
    backtest_engine.fast_forward(steps=10_000)
    start2 = backtest_engine.cursor.time
    bo2 = await backtest_engine.order_send(request=buy_order)
    backtest_engine.fast_forward(steps=50)
    end2 = backtest_engine.cursor.time
    deals = backtest_engine.deals.history_deals_get(date_from=start2, date_to=end2)
    assert len(deals) == 1
    assert deals[0].order == bo2.order
    await positions.close_position_by_ticket(ticket=bo.order)
    deals = backtest_engine.deals.history_deals_get(position=bo.order)
    assert len(deals) <= 2
    orders = backtest_engine.deals.get_deals_range(date_from=start, date_to=end)
    assert (
        len(orders)
        == backtest_engine.deals.history_deals_total(date_from=start, date_to=end)
        == len(backtest_engine.deals._data.keys())
    )
