# noinspection PyTestUnpassedFixture
async def test_positions_manager(backtest_engine, sell_order, buy_order):
    backtest_engine.reset(clear_data=True)
    await backtest_engine.setup_account(balance=100)
    backtest_engine.fast_forward(steps=100)
    so = await backtest_engine.order_send(request=sell_order)
    bo = await backtest_engine.order_send(request=buy_order)
    all_pos = backtest_engine.positions.positions_get()
    assert len(all_pos) == 2
    so_positions = backtest_engine.positions.positions_get(ticket=so.order)
    so_position = so_positions[0]
    assert so_position.ticket == so.order
    btc_positions = backtest_engine.positions.positions_get(symbol='BTCUSD')
    assert len(btc_positions) == 2
    assert backtest_engine.positions.positions_total() == 2
    backtest_engine.positions.close(ticket=bo.order)
    assert backtest_engine.positions.positions_total() == 1
