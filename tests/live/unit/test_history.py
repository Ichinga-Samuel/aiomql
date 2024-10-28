from datetime import datetime

import pytest
from aiomql.lib.history import History

class TestHistory:
    @pytest.fixture(scope='class', autouse=True)
    async def init(self, make_buy_sell_orders):
        await self.history.initialize()

    @classmethod
    def setup_class(cls):
        now = datetime.now()
        cls.start = now.replace(hour=0)
        cls.end = now.replace(hour=23)
        history = History(date_from=cls.start, date_to=cls.end)
        cls.history = history

    async def test_init(self):
        assert self.history.total_deals > 0
        assert self.history.total_orders > 0

    async def test_get_deals(self):
        deals = await self.history.get_deals()
        assert len(deals) > 0

    async def test_get_deals_by_ticket(self):
        ticket = self.history.deals[0].order
        deals = self.history.get_deals_by_ticket(ticket=ticket)
        assert len(deals) > 0

    async def test_get_deals_by_position(self):
        position = self.history.deals[0].position_id
        deals = self.history.get_deals_by_position(position=position)
        assert len(deals) > 0

    async def test_get_orders(self):
        orders = await self.history.get_orders()
        assert len(orders) > 0

    async def test_get_orders_by_ticket(self):
        ticket = self.history.orders[0].ticket
        orders = self.history.get_orders_by_ticket(ticket=ticket)
        assert len(orders) > 0

    async def test_get_orders_by_position(self):
        position = self.history.orders[0].position_id
        orders = self.history.get_orders_by_position(position=position)
        assert len(orders) > 0
