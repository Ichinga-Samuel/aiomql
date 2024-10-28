from aiomql.lib.order import Order


class TestOrder:
    async def test_check(self, sell_order):
        order = Order(**sell_order)
        check = await order.check()
        assert check.retcode == 0

    async def test_send(self, buy_order):
        order = Order(**buy_order)
        send = await order.send()
        assert send.retcode == 10009

    async def test_margin(self, buy_order):
        order = Order(**buy_order)
        margin = await order.calc_margin()
        assert margin is not None
        assert margin > 0
        assert isinstance(margin, float)

    async def test_profit(self, buy_order):
        order = Order(**buy_order)
        profit = await order.calc_profit()
        assert profit is not None
        assert profit > 0
        assert isinstance(profit, float)
