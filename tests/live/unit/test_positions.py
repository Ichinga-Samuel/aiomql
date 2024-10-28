import pytest

from aiomql.lib.positions import Positions


class TestPositions:
    @pytest.fixture(scope='class', autouse=True)
    async def init(self, make_buy_sell_orders):
        await self.positions.get_positions()

    @classmethod
    def setup_class(cls):
        cls.positions = Positions()

    @pytest.mark.order(1)
    async def test_get_positions(self):
        await self.positions.get_positions()
        assert len(self.positions.positions) >= 0

    async def test_get_position_by_ticket(self):
        ticket = self.positions.positions[0].ticket
        position = await self.positions.get_position_by_ticket(ticket=ticket)
        assert position is not None
        assert position.ticket == ticket

    async def test_get_position_by_symbol(self):
        symbol = self.positions.positions[0].symbol
        positions = await self.positions.get_position_by_symbol(symbol=symbol)
        assert len(positions) >= 0
        assert positions[0].symbol == symbol
