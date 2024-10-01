from datetime import datetime, timedelta

import pytest
import pytz
import pytest_asyncio
from aiomql import MetaTrader, TimeFrame, OrderType, CopyTicks

from . import metatrader5


class TestMetaTrader:

    @classmethod
    def setup_class(cls, metatrader5):
        tz = pytz.timezone('Etc/UTC')
        cls.mt = MetaTrader()
        cls.mt5 = metatrader5
        cls.symbol = "Volatility 100 Index"
        now = datetime.now(tz=tz)
        cls.start = now - timedelta(hours=24)
        cls.end = now + timedelta(hours=2)
        cls.tf = cls.mt.TIMEFRAME_H1

    @pytest.mark.asyncio
    async def test_initialize(self):
        res = await self.mt.initialize()
        assert res == True

    @pytest.mark.asyncio
    async def test_login(self):
        res = await self.mt.login()
        assert res == True

    @pytest.mark.asyncio
    async def test_last_error(self):
        res = await self.mt.last_error()
        assert isinstance(res, tuple)
        assert res[0] == 1
        assert res[1] == 'Successful'
    
    @pytest.mark.asyncio
    async def test_version(self):
        res = await self.mt.version()
        res2 =  self.mt5.version()
        assert res is not None
        assert res == res2
    
    @pytest.mark.asyncio
    async def test_account_info(self):
        res = await self.mt.account_info()
        res2 = self.mt5.account_info()
        assert res is not None
        assert res == res2
    
    @pytest.mark.asyncio
    async def test_terminal_info(self):
        res = await self.mt.terminal_info()
        res2 = await self.mt5.terminal_info()
        assert res is not None
        assert res == res2

    @pytest.mark.asyncio
    async def test_symbols_total(self):
        res = await self.mt.symbols_total()
        res2 = await self.mt5.symbols_total()
        assert isinstance(res, int)
        assert res
    
    @pytest.mark.asyncio
    async def test_symbols_get(self):
        res = await self.mt.symbols_get()
        res2 = await self.mt5.symbols_get()
        assert res is not None
        assert res == res2
    
    @pytest.mark.asyncio
    async def test_symbol_info(self):
        res = await self.mt.symbol_info(self.symbol)
        res2 = await self.mt5.symbol_info(self.symbol)
        assert res is not None
        assert res == res2
    
    @pytest.mark.asyncio
    async def test_symbol_info_tick(self):
        res = await self.mt.symbol_info_tick(self.symbol)
        res2 = await self.mt5.symbol_info_tick(self.symbol)
        assert res is not None
        assert res == res2
    
    @pytest.mark.asyncio
    async def test_symbol_select(self):
        res = await self.mt.symbol_select(self.symbol, True)
        assert res == True
    
    @pytest.mark.asyncio
    async def test_market_book_add(self):
        res = await self.mt.market_book_add(self.symbol)
        assert res == True
    
    @pytest.mark.asyncio
    async def test_market_book_get(self):
        res = await self.mt.market_book_get(self.symbol)
        res2 = await self.mt5.market_book_get(self.symbol)
        assert res is not None
        assert res == res2
    
    @pytest.mark.asyncio
    async def test_market_book_release(self):
        res = await self.mt.market_book_release(self.symbol)
        assert res == True
    
    @pytest.mark.asyncio
    async def test_copy_rates_from(self):
        res = await self.mt.copy_rates_from(self.symbol, self.tf, self.start, 10)
        assert res is not None
        assert res.shape[0] == 10
    
    @pytest.mark.asyncio
    async def test_copy_rates_from_pos(self):
        res = await self.mt.copy_rates_from_pos(self.symbol, self.tf, 0, 10)
        assert res is not None
        assert res.shape[0] == 10
    
    @pytest.mark.asyncio
    async def test_copy_rates_range(self):
        res = await self.mt.copy_rates_range(self.symbol, TimeFrame.M1, datetime.now(), datetime.now())
        assert res is not None
    
    @pytest.mark.asyncio
    async def test_copy_ticks_from(self):
        res = await self.mt.copy_ticks_from(self.symbol, datetime.now(), 10, CopyTicks.ALL)
        assert res is not None
    
    @pytest.mark.asyncio
    async def test_copy_ticks_range(self):
        res = await self.mt.copy_ticks_range(self.symbol, datetime.now(), datetime.now(), CopyTicks.ALL)
        assert res is not None
    
    @pytest.mark.asyncio
    async def test_orders_total(self):
        res = await self.mt.orders_total()
        assert isinstance(res, int)
    
    @pytest.mark.asyncio
    async def test_orders_get(self):
        res = await self.mt.orders_get()
        assert res is not None
    
    @pytest.mark.asyncio
    async def test_order_calc_margin(self):
        res = await self.mt.order_calc_margin(OrderType.BUY, self.symbol, 1.0, 1.0)
        assert isinstance(res, float)
    
    @pytest.mark.asyncio
    async def test_order_calc_profit(self):
        res = await self.mt.order_calc_profit(OrderType.BUY, self.symbol, 1.0, 1.0, 1.1)
        assert isinstance(res, float)
    
    @pytest.mark.asyncio
    async def test_order_check(self):
        request = {"action": OrderType.BUY, "symbol": self.symbol, "volume": 1.0, "price": 1.0}
        res = await self.mt.order_check(request)
        assert res is not None
    
    @pytest.mark.asyncio
    async def test_order_send(self):
        request = {"action": OrderType.BUY, "symbol": self.symbol, "volume": 1.0, "price": 1.0}
        res = await self.mt.order_send(request)
        assert res is not None
    
    @pytest.mark.asyncio
    async def test_positions_total(self):
        res = await self.mt.positions_total()
        assert isinstance(res, int)
    
    @pytest.mark.asyncio
    async def test_positions_get(self):
        res = await self.mt.positions_get()
        assert res is not None
    
    @pytest.mark.asyncio
    async def test_history_orders_total(self):
        res = await self.mt.history_orders_total(datetime.now(), datetime.now())
        assert isinstance(res, int)
    
    @pytest.mark.asyncio
    async def test_history_orders_get(self):
        res = await self.mt.history_orders_get(datetime.now(), datetime.now())
        assert res is not None
    
    @pytest.mark.asyncio
    async def test_history_deals_total(self):
        res = await self.mt.history_deals_total(datetime.now(), datetime.now())
        assert isinstance(res, int)
    
    @pytest.mark.asyncio
    async def test_history_deals_get(self):
        res = await self.mt.history_deals_get(datetime.now(), datetime.now())
        assert res is not None
