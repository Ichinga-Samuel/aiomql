from math import floor
import pytest

from aiomql.lib.ram import RAM
from aiomql.contrib.traders import SimpleTrader
from aiomql.contrib.symbols import ForexSymbol
from aiomql.core.constants import OrderType
from aiomql.lib.account import Account
from aiomql._utils import round_down

class TestTrader:
    @classmethod
    def setup_class(cls):
        ram = RAM(fixed_amount=10)
        cls.trader = SimpleTrader(symbol=ForexSymbol(name="BTCUSD"), ram=ram)
        cls.simple_trader2 = SimpleTrader(symbol=ForexSymbol(name="EURJPY"), ram=ram)
        cls.account = Account()

    @pytest.fixture(scope="class", autouse=True)
    async def initialize(self):
        await self.trader.symbol.initialize()
        await self.simple_trader2.symbol.initialize()
        await self.account.refresh()

    async def test_create_order_no_stops(self):
        await self.trader.create_order_no_stops(order_type=OrderType.BUY)
        assert self.trader.order.volume == self.trader.symbol.volume_min
        res = await self.trader.order.send()
        assert res is not None
        assert res.retcode == 10009

    async def test_create_order_with_sl(self):
        sl = (self.trader.symbol.trade_stops_level * 2 + self.trader.symbol.spread) * self.trader.symbol.point
        tick = await self.trader.symbol.info_tick()
        sl = tick.bid + sl
        await self.trader.create_order_with_sl(order_type=OrderType.SELL, sl=sl)
        res = await self.trader.order.send()
        profit = floor(await self.trader.order.calc_profit())
        loss = -floor(abs(await self.trader.order.calc_loss()))
        assert profit == -loss * self.trader.ram.risk_to_reward
        assert abs(profit - self.trader.ram.fixed_amount * self.trader.ram.risk_to_reward) <= 2.5
        assert abs(abs(loss) - abs(-self.trader.ram.fixed_amount)) <= 2
        assert res is not None
        assert res.retcode == 10009

    async def test_create_order_with_points(self):
        points = self.trader.symbol.trade_stops_level * 2 + self.trader.symbol.spread
        await self.trader.create_order_with_points(order_type=OrderType.BUY, points=points)
        res = await self.trader.order.send()
        profit = floor(await self.trader.order.calc_profit())
        loss = -floor(abs(await self.trader.order.calc_loss()))
        assert profit == -loss * self.trader.ram.risk_to_reward
        assert abs(profit - self.trader.ram.fixed_amount * self.trader.ram.risk_to_reward) <= 2.5
        assert abs(abs(loss) - abs(-self.trader.ram.fixed_amount)) <= 2
        assert res is not None
        assert res.retcode == 10009

    async def test_create_order_with_stops(self):
        sl = (self.trader.symbol.trade_stops_level * 2 + self.trader.symbol.spread) * self.trader.symbol.point
        tp = sl * self.trader.ram.risk_to_reward
        tick = await self.trader.symbol.info_tick()
        sl = tick.ask - sl
        tp = tick.ask + tp
        await self.trader.create_order_with_stops(order_type=OrderType.BUY, sl=sl, tp=tp)
        res = await self.trader.order.send()
        assert res is not None
        assert res.retcode == 10009
        profit = round(await self.trader.order.calc_profit(), self.account.currency_digits)
        loss = -round(abs(await self.trader.order.calc_loss()), self.account.currency_digits)
        assert profit == -loss * self.trader.ram.risk_to_reward
        assert abs(profit - (self.trader.ram.fixed_amount * self.trader.ram.risk_to_reward)) <= 2.5
        assert abs(abs(loss) - self.trader.ram.fixed_amount) <= 2.5
