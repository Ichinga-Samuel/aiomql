from datetime import datetime

import pytest
import pytest_asyncio
from aiomql import MetaTrader, TimeFrame, OrderType, CopyTicks


class TestMetaTrader:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_method(self):
        self.mt = MetaTrader()


    @pytest.mark.asyncio
    async def test_initialize(self):
        res = await self.mt.initialize(**self.mt.config.account_info())
        assert res == True

    @pytest.mark.asyncio
    async def test_login(self):
        res = await self.mt.login(**self.mt.config.account_info())
        assert res == True

    # @pytest.mark.asyncio
    # async def test_shutdown(self):
    #     res = await self.mt.shutdown()
    #     assert res is None
    #
    # @pytest.mark.asyncio
    # async def test_last_error(self):
    #     res = await self.mt.last_error()
    #     assert isinstance(res, tuple)
    #
    # @pytest.mark.asyncio
    # async def test_version(self):
    #     res = await self.mt.version()
    #     assert isinstance(res, tuple)
    #
    # @pytest.mark.asyncio
    # async def test_account_info(self):
    #     res = await self.mt.account_info()
    #     assert res is not None
    #
    # @pytest.mark.asyncio
    # async def test_terminal_info(self):
    #     res = await self.mt.terminal_info()
    #     assert res is not None
    #
    # @pytest.mark.asyncio
    # async def test_symbols_total(self):
    #     res = await self.mt.symbols_total()
    #     assert isinstance(res, int)
    #
    # @pytest.mark.asyncio
    # async def test_symbols_get(self):
    #     res = await self.mt.symbols_get()
    #     assert res is not None
    #
    # @pytest.mark.asyncio
    # async def test_symbol_info(self):
    #     res = await self.mt.symbol_info("EURUSD")
    #     assert res is not None
    #
    # @pytest.mark.asyncio
    # async def test_symbol_info_tick(self):
    #     res = await self.mt.symbol_info_tick("EURUSD")
    #     assert res is not None
    #
    # @pytest.mark.asyncio
    # async def test_symbol_select(self):
    #     res = await self.mt.symbol_select("EURUSD", True)
    #     assert res == True
    #
    # @pytest.mark.asyncio
    # async def test_market_book_add(self):
    #     res = await self.mt.market_book_add("EURUSD")
    #     assert res == True
    #
    # @pytest.mark.asyncio
    # async def test_market_book_get(self):
    #     res = await self.mt.market_book_get("EURUSD")
    #     assert res is not None
    #
    # @pytest.mark.asyncio
    # async def test_market_book_release(self):
    #     res = await self.mt.market_book_release("EURUSD")
    #     assert res == True
    #
    # @pytest.mark.asyncio
    # async def test_copy_rates_from(self):
    #     res = await self.mt.copy_rates_from("EURUSD", TimeFrame.M1, datetime.now(), 10)
    #     assert res is not None
    #
    # @pytest.mark.asyncio
    # async def test_copy_rates_from_pos(self):
    #     res = await self.mt.copy_rates_from_pos("EURUSD", TimeFrame.M1, 0, 10)
    #     assert res is not None
    #
    # @pytest.mark.asyncio
    # async def test_copy_rates_range(self):
    #     res = await self.mt.copy_rates_range("EURUSD", TimeFrame.M1, datetime.now(), datetime.now())
    #     assert res is not None
    #
    # @pytest.mark.asyncio
    # async def test_copy_ticks_from(self):
    #     res = await self.mt.copy_ticks_from("EURUSD", datetime.now(), 10, CopyTicks.ALL)
    #     assert res is not None
    #
    # @pytest.mark.asyncio
    # async def test_copy_ticks_range(self):
    #     res = await self.mt.copy_ticks_range("EURUSD", datetime.now(), datetime.now(), CopyTicks.ALL)
    #     assert res is not None
    #
    # @pytest.mark.asyncio
    # async def test_orders_total(self):
    #     res = await self.mt.orders_total()
    #     assert isinstance(res, int)
    #
    # @pytest.mark.asyncio
    # async def test_orders_get(self):
    #     res = await self.mt.orders_get()
    #     assert res is not None
    #
    # @pytest.mark.asyncio
    # async def test_order_calc_margin(self):
    #     res = await self.mt.order_calc_margin(OrderType.BUY, "EURUSD", 1.0, 1.0)
    #     assert isinstance(res, float)
    #
    # @pytest.mark.asyncio
    # async def test_order_calc_profit(self):
    #     res = await self.mt.order_calc_profit(OrderType.BUY, "EURUSD", 1.0, 1.0, 1.1)
    #     assert isinstance(res, float)
    #
    # @pytest.mark.asyncio
    # async def test_order_check(self):
    #     request = {"action": OrderType.BUY, "symbol": "EURUSD", "volume": 1.0, "price": 1.0}
    #     res = await self.mt.order_check(request)
    #     assert res is not None
    #
    # @pytest.mark.asyncio
    # async def test_order_send(self):
    #     request = {"action": OrderType.BUY, "symbol": "EURUSD", "volume": 1.0, "price": 1.0}
    #     res = await self.mt.order_send(request)
    #     assert res is not None
    #
    # @pytest.mark.asyncio
    # async def test_positions_total(self):
    #     res = await self.mt.positions_total()
    #     assert isinstance(res, int)
    #
    # @pytest.mark.asyncio
    # async def test_positions_get(self):
    #     res = await self.mt.positions_get()
    #     assert res is not None
    #
    # @pytest.mark.asyncio
    # async def test_history_orders_total(self):
    #     res = await self.mt.history_orders_total(datetime.now(), datetime.now())
    #     assert isinstance(res, int)
    #
    # @pytest.mark.asyncio
    # async def test_history_orders_get(self):
    #     res = await self.mt.history_orders_get(datetime.now(), datetime.now())
    #     assert res is not None
    #
    # @pytest.mark.asyncio
    # async def test_history_deals_total(self):
    #     res = await self.mt.history_deals_total(datetime.now(), datetime.now())
    #     assert isinstance(res, int)
    #
    # @pytest.mark.asyncio
    # async def test_history_deals_get(self):
    #     res = await self.mt.history_deals_get(datetime.now(), datetime.now())
    #     assert res is not None
