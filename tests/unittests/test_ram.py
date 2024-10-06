from aiomql.lib.ram import RAM


class TestRAM:
    @classmethod
    def setup_class(cls):
        cls.ram = RAM(min_amount=5, max_amount=10, loss_limit=3, open_limit=5)

    async def test_get_amount(self):
        res = await self.ram.get_amount()
        assert self.ram.min_amount <= res <= self.ram.max_amount

    async def test_checks(self, buy_order, sell_order, mt):
        for i in range(self.ram.open_limit+1):
            if i % 2 == 0:
                await mt.order_send(buy_order)
            else:
                await mt.order_send(sell_order)
        res1 = await self.ram.check_losing_positions()
        res2 = await self.ram.check_open_positions()
        assert res2 is False
        assert isinstance(res1, bool)
