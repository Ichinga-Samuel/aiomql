from datetime import datetime, UTC
from math import ceil
from aiomql import TimeFrame
from aiomql.core.backtesting import BackTestEngine
from aiomql.core.backtesting.get_data import GetData
from aiomql.utils import round_down
from aiomql.core.constants import OrderType, TradeAction

import pytest


class TestBackTestEngine:
    @classmethod
    def setup_class(cls):
        cls.start = datetime(2024, 2, 1)
        cls.end = datetime(2024, 2, 7)
        cls.g_data = GetData(
            start=cls.start,
            end=cls.end,
            symbols=["BTCUSD", "SOLUSD"],
            timeframes=[TimeFrame.H1, TimeFrame.H2],
            name="test_engine",
        )
        cls.bte = BackTestEngine(start=cls.start, end=cls.end, assign_to_config=True, preload=False)

    @pytest.fixture(scope="class")
    async def bte2(self):
        await self.g_data.get_data()
        bte2 = BackTestEngine(start=self.start, end=self.end, data=self.g_data.data, use_terminal=False, preload=False)
        await bte2.setup_account(balance=100)
        return bte2

    @pytest.fixture(scope="class")
    async def sell_order(self):
        sym = await self.bte.get_symbol_info(symbol="BTCUSD")
        request = {
            "type": OrderType.SELL,
            "symbol": "BTCUSD",
            "volume": sym.volume_min,
            "price": sym.bid,
            "action": TradeAction.DEAL,
        }
        return request

    @pytest.fixture(scope="class")
    async def buy_order(self):
        sym = await self.bte.get_symbol_info(symbol="BTCUSD")
        dsl = (sym.trade_stops_level + sym.spread) * 2 * sym.point
        sl = sym.ask - dsl
        tp = sym.ask + dsl
        request = {
            "type": OrderType.BUY,
            "symbol": "BTCUSD",
            "volume": sym.volume_min,
            "price": sym.ask,
            "action": TradeAction.DEAL,
            "sl": sl,
            "tp": tp,
        }
        return request

    def modify_stops(self, order):
        ...

    def test_span_and_range(self):
        assert self.bte.range == range(0, int((self.end - self.start).total_seconds()), self.bte.speed)
        assert self.bte.span == range(int(self.start.timestamp()), int(self.end.timestamp()), self.bte.speed)
        assert len(self.bte.span) == len(self.bte.range)

    def test_cursor(self):
        self.bte.next()
        r, t = self.bte.cursor
        self.bte.fast_forward(steps=100)
        assert self.bte.cursor.time == t + 100 * self.bte.speed
        assert self.bte.cursor.index == r + 100 * self.bte.speed
        print(datetime.fromtimestamp(self.bte.cursor.time, tz=UTC), "test_cursor")
        go_to = datetime(2024, 2, 6, tzinfo=UTC)
        self.bte.go_to(time=go_to)
        assert self.bte.cursor.time == int(datetime.timestamp(go_to))
        self.bte.reset()
        assert self.bte.cursor.time == int(self.start.timestamp())

    def test_speed(self):
        self.bte.setup_test_range(start=self.start, end=self.end, speed=3600)
        assert self.bte.speed == 3600
        self.bte.next()
        now = datetime.fromtimestamp(self.bte.cursor.time, tz=UTC)
        index = self.bte.cursor.index
        self.bte.next()
        assert self.bte.cursor.index == index + 3600
        assert self.bte.cursor.time == int(now.timestamp()) + 3600
        self.bte.setup_test_range(start=self.start, end=self.end)
        assert self.bte.speed == 60

    async def test_account(self):
        await self.bte.setup_account(balance=100)
        acc = self.bte.get_account_info()
        self.bte.use_terminal_for_backtesting = False
        self.bte.use_terminal_for_backtesting = True
        assert acc.balance == 100
        assert acc.equity == 100
        assert acc.margin == 0
        assert acc.margin_free == 100
        assert acc.margin_level == 0
        self.bte.deposit(amount=50)
        acc = self.bte.get_account_info()
        assert acc.balance == 150
        assert acc.equity == 150
        assert acc.margin == 0
        assert acc.margin_free == 150
        assert acc.margin_level == 0
        self.bte.withdraw(amount=80)
        acc = self.bte.get_account_info()
        assert acc.balance == 70
        assert acc.equity == 70
        assert acc.margin == 0
        assert acc.margin_free == 70
        assert acc.margin_level == 0
        self.bte.update_account(profit=-5)
        acc = self.bte.get_account_info()
        assert acc.equity == 65
        assert acc.balance == 70
        assert acc.profit == -5
        assert acc.margin == 0
        assert acc.margin_free == 65
        assert acc.margin_level == 0
        self.bte.update_account(margin=2.5)
        acc = self.bte.get_account_info()
        assert acc.balance == 70
        assert acc.equity == 65
        assert acc.margin == 2.5
        assert acc.margin_free == 62.5
        assert acc.margin_level == 2600

    def test_account_sync(self):
        balance = 200
        self.bte.setup_account_sync(balance=balance)
        acc = self.bte.get_account_info()
        assert acc.balance == balance

    async def test_bte2_init(self, bte2):
        assert bte2._data.fully_loaded is True
        assert bte2.span == self.bte.span
        assert bte2.range == self.bte.range
        assert bte2.use_terminal is False

    async def test_get_rates_from(self):
        start = datetime(2024, 2, 3, 12, 43, tzinfo=UTC)
        rates = await self.bte.get_rates_from(symbol="BTCUSD", timeframe=TimeFrame.H1, date_from=start, count=24)
        assert len(rates) == 24

    async def test_get_rates_from_2(self, bte2):
        start = datetime(2024, 2, 3, 12, 12, tzinfo=UTC)
        rates = await bte2.get_rates_from(symbol="BTCUSD", timeframe=TimeFrame.H1, date_from=start, count=24)
        assert len(rates) == 24

    async def test_get_rates_from_pos(self):
        now = datetime(2024, 2, 3, 11, 55, tzinfo=UTC)
        self.bte.go_to(time=now)
        tf = TimeFrame.H2
        start_pos = 2
        rates = await self.bte.get_rates_from_pos(symbol="BTCUSD", timeframe=tf, start_pos=start_pos, count=24)
        assert len(rates) == 24
        assert int(rates[-1][0]) == round_down(int(now.replace(hour=now.hour - start_pos).timestamp()), tf.seconds)

    async def test_get_rates_from_pos2(self, bte2):
        now = datetime(2024, 2, 4, 12, 15, tzinfo=UTC)
        bte2.go_to(time=now)
        tf = TimeFrame.H1
        start_pos = 2
        rates = await bte2.get_rates_from_pos(symbol="BTCUSD", timeframe=tf, start_pos=start_pos, count=24)
        assert int(rates[-1][0]) == round_down(int(now.replace(hour=10).timestamp()), tf.seconds)
        # assert int(rates[-1][0]) == round_up(int(now.timestamp()), tf.seconds) - start_pos * tf.seconds
        assert len(rates) == 24

    async def test_get_rates_range(self):
        start = datetime(2024, 2, 3, 12, tzinfo=UTC)
        end = datetime(2024, 2, 4, 18, tzinfo=UTC)
        rates = await self.bte.get_rates_range(symbol="BTCUSD", timeframe=TimeFrame.H1, date_from=start, date_to=end)
        assert len(rates) == 31
        assert int(rates[-1][0]) == int(end.timestamp())

    async def test_get_rates_range2(self, bte2):
        start = datetime(2024, 2, 3, 12, tzinfo=UTC)
        end = datetime(2024, 2, 4, 18, tzinfo=UTC)
        rates = await bte2.get_rates_range(symbol="BTCUSD", timeframe=TimeFrame.H1, date_from=start, date_to=end)
        assert len(rates) == 31
        assert int(rates[-1][0]) == int(end.timestamp())

    async def test_get_ticks_from(self):
        start = datetime(2024, 2, 3, 12, tzinfo=UTC)
        ticks = await self.bte.get_ticks_from(symbol="BTCUSD", date_from=start, count=24)
        assert len(ticks) == 24

    async def test_get_ticks_from2(self, bte2):
        start = datetime(2024, 2, 3, 12, tzinfo=UTC)
        ticks = await bte2.get_ticks_from(symbol="BTCUSD", date_from=start, count=24)
        assert len(ticks) == 24

    async def test_get_ticks_range(self):
        start = datetime(2024, 2, 3, 12, tzinfo=UTC)
        end = datetime(2024, 2, 3, 15, tzinfo=UTC)
        ticks = await self.bte.get_ticks_range(symbol="BTCUSD", date_from=start, date_to=end)
        approx_total = (end - start).total_seconds() // 2  # assuming 2 ticks per second at least
        assert len(ticks) >= approx_total

    async def test_get_ticks_range2(self, bte2):
        start = datetime(2024, 2, 3, 12, tzinfo=UTC)
        end = datetime(2024, 2, 3, 15, tzinfo=UTC)
        ticks = await bte2.get_ticks_range(symbol="BTCUSD", date_from=start, date_to=end)
        approx_total = (end - start).total_seconds() // 2  # assuming 2 ticks per second at least
        assert len(ticks) >= approx_total

    async def test_price_tick(self, bte2):
        moment = datetime(2024, 2, 3, 12, 12, tzinfo=UTC)
        self.bte.reset()
        self.bte.go_to(time=moment)
        tick = await self.bte.get_price_tick(symbol="BTCUSD", time=self.bte.cursor.time)
        assert tick is not None
        assert isinstance(tick.ask, float)
        assert tick.ask > 0
        bte2.reset()
        bte2.go_to(time=moment)
        tick2 = await bte2.get_price_tick(symbol="BTCUSD", time=bte2.cursor.time)
        assert tick.ask == tick2.ask

    async def test_get_symbol_info(self, bte2):
        moment = datetime(2024, 2, 3, 12, 12, tzinfo=UTC)
        self.bte.reset()
        self.bte.go_to(time=moment)
        bte2.reset()
        bte2.go_to(time=moment)
        sym = "BTCUSD"
        sym_info = await self.bte.get_symbol_info(symbol=sym)
        assert sym_info is not None
        assert sym_info.name == sym
        sym_info2 = await bte2.get_symbol_info(symbol=sym)
        assert sym_info.ask == sym_info2.ask

    async def test_order_profit(self, bte2):
        moment = datetime(2024, 2, 3, 12, 12, tzinfo=UTC)
        self.bte.reset()
        self.bte.go_to(time=moment)
        bte2.reset()
        bte2.go_to(time=moment)
        sym = "BTCUSD"
        sym_info = await self.bte.get_symbol_info(symbol=sym)
        dsl = (sym_info.trade_stops_level + sym_info.spread) * 2 * sym_info.point
        tp = sym_info.ask + dsl

        profit = await self.bte.order_calc_profit(
            action=OrderType.BUY, symbol=sym, volume=sym_info.volume_min, price_open=sym_info.ask, price_close=tp
        )
        assert profit > 0
        sym_info2 = await bte2.get_symbol_info(symbol=sym)
        dsl2 = (sym_info2.trade_stops_level + sym_info2.spread) * 2 * sym_info2.point
        tp2 = sym_info2.ask + dsl2
        profit2 = await bte2.order_calc_profit(
            action=OrderType.BUY, symbol=sym, volume=sym_info2.volume_min, price_open=sym_info2.ask, price_close=tp2
        )
        assert ceil(profit) == ceil(profit2)

    async def test_order_margin(self, bte2):
        moment = datetime(2024, 2, 3, 12, 12, tzinfo=UTC)
        self.bte.reset()
        self.bte.go_to(time=moment)
        bte2.reset()
        bte2.go_to(time=moment)
        sym = "BTCUSD"
        sym_info = await self.bte.get_symbol_info(symbol=sym)
        margin = await self.bte.order_calc_margin(
            action=OrderType.SELL, symbol=sym, volume=sym_info.volume_min, price=sym_info.bid
        )
        assert margin > 0
        sym_info2 = await self.bte.get_symbol_info(symbol=sym)
        margin2 = await bte2.order_calc_margin(
            action=OrderType.SELL, symbol=sym, volume=sym_info2.volume_min, price=sym_info2.bid
        )
        assert margin2 > 0

    async def test_order_check(self, buy_order, sell_order):
        ocr = await self.bte.order_check(request=buy_order)
        assert ocr is not None
        assert ocr.retcode == 0
        ocr2 = await self.bte.order_check(request=sell_order)
        assert ocr2 is not None
        assert ocr2.retcode == 0

    async def test_order_send(self, buy_order, sell_order):
        ocr = await self.bte.order_send(request=buy_order)
        assert ocr is not None
        assert ocr.retcode == 10009
        ocr2 = await self.bte.order_send(request=sell_order)
        assert ocr2 is not None
        assert ocr2.retcode == 10009
