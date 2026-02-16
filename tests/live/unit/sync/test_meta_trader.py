from datetime import datetime, timedelta

import pytz
import MetaTrader5

from aiomql.core.sync.meta_trader import MetaTrader


class TestMetaTraderSync:
    @classmethod
    def setup_class(cls):
        cls.mt = MetaTrader()
        cls.mt5 = MetaTrader5
        cls.symbol = "BTCUSD"
        now = datetime.now(tz=pytz.UTC)
        cls.start = now - timedelta(hours=10)
        cls.end = now + timedelta(hours=1)
        cls.tf = cls.mt.TIMEFRAME_H1

    @classmethod
    def teardown_class(cls):
        cls.mt.shutdown()

    def test_initialize(self):
        res = self.mt.initialize()
        assert res == True

    def test_login(self):
        res = self.mt.login()
        assert res == True

    def test_last_error(self):
        res = self.mt.last_error()
        assert isinstance(res, tuple)
        assert res[0] == 1
        assert res[1] == "Success"

    def test_version(self):
        res = self.mt.version()
        res2 = self.mt5.version()
        assert res is not None
        assert res == res2

    def test_account_info(self):
        res = self.mt.account_info()
        res2 = self.mt5.account_info()
        assert res is not None
        assert res == res2

    def test_terminal_info(self):
        res = self.mt.terminal_info()
        res2 = self.mt5.terminal_info()
        assert res is not None
        assert res == res2

    def test_symbols_total(self):
        res = self.mt.symbols_total()
        res2 = self.mt5.symbols_total()
        assert isinstance(res, int)
        assert res == res2

    def test_symbols_get(self):
        res = self.mt.symbols_get()
        res2 = self.mt5.symbols_get()
        assert res is not None
        assert len(res) == len(res2)

    def test_symbol_info(self):
        res = self.mt.symbol_info(self.symbol)
        res2 = self.mt5.symbol_info(self.symbol)
        assert res is not None
        assert res == res2

    def test_symbol_info_tick(self):
        res = self.mt.symbol_info_tick(self.symbol)
        res2 = self.mt5.symbol_info_tick(self.symbol)
        assert res is not None
        assert res == res2

    def test_symbol_select(self):
        res = self.mt.symbol_select(self.symbol, True)
        assert res == True

    def test_market_book_add(self):
        res = self.mt.market_book_add(self.symbol)
        assert res == True

    def test_market_book_get(self):
        res = self.mt.market_book_get(self.symbol)
        res2 = self.mt5.market_book_get(self.symbol)
        assert res is not None
        assert res == res2

    def test_market_book_release(self):
        res = self.mt.market_book_release(self.symbol)
        assert res == True

    def test_copy_rates_from(self):
        res = self.mt.copy_rates_from(self.symbol, self.tf, self.start, 10)
        assert res is not None
        assert res.shape[0] == 10

    def test_copy_rates_from_pos(self):
        res = self.mt.copy_rates_from_pos(self.symbol, self.tf, 0, 10)
        assert res is not None
        assert res.shape[0] == 10

    def test_copy_rates_range(self):
        res = self.mt.copy_rates_range(self.symbol, self.tf, self.start, self.end)
        assert res is not None
        assert res.shape[0] == 10

    def test_copy_ticks_from(self):
        res = self.mt.copy_ticks_from(self.symbol, self.start, 10, self.mt.COPY_TICKS_ALL)
        assert res is not None
        assert res.shape[0] == 10

    def test_copy_ticks_range(self):
        res = self.mt.copy_ticks_range(self.symbol, self.start, self.end, self.mt.COPY_TICKS_ALL)
        res2 = self.mt5.copy_ticks_range(self.symbol, self.start, self.end, self.mt5.COPY_TICKS_ALL)
        assert res is not None
        assert res.shape[0] == res2.shape[0]

    def test_orders_total(self):
        res = self.mt.orders_total()
        assert isinstance(res, int)

    def test_orders_get(self):
        res = self.mt.orders_get()
        assert res is not None
        assert isinstance(res, tuple)
        assert len(res) == 0

    def test_order_calc_margin(self, sell_order_sync):
        price = sell_order_sync["price"]
        volume = sell_order_sync["volume"]
        type_ = sell_order_sync["type"]
        res = self.mt.order_calc_margin(type_, self.symbol, volume, price)
        assert isinstance(res, float)

    def test_order_calc_profit(self, buy_order_sync):
        volume = buy_order_sync["volume"]
        price_open = buy_order_sync["price"]
        price_close = buy_order_sync["tp"]
        type_ = buy_order_sync["type"]
        res = self.mt.order_calc_profit(type_, self.symbol, volume, price_open, price_close)
        assert isinstance(res, float)

    def test_order_check(self, buy_order_sync):
        res = self.mt.order_check(buy_order_sync)
        assert res is not None
        assert res.retcode == 0

    def test_order_send(self, sell_order_sync):
        res = self.mt.order_send(sell_order_sync)
        assert res is not None
        assert res.retcode == 10009

    def test_positions_total(self):
        res = self.mt.positions_total()
        assert isinstance(res, int)
        assert res >= 0

    def test_positions_get(self):
        res = self.mt.positions_get()
        assert res is not None
        assert isinstance(res, tuple)
        assert len(res) >= 0

    def test_history_orders_total(self):
        res = self.mt.history_orders_total(self.start, self.end)
        assert isinstance(res, int)
        assert res >= 0

    def test_history_orders_get(self):
        res = self.mt.history_orders_get(self.start, self.end)
        assert res is not None
        assert isinstance(res, tuple)
        assert len(res) >= 0

    def test_history_deals_total(self):
        res = self.mt.history_deals_total(self.start, self.end)
        assert isinstance(res, int)
        assert res >= 0

    def test_history_deals_get(self):
        res = self.mt.history_deals_get(self.start, self.end)
        assert res is not None
        assert isinstance(res, tuple)
        assert len(res) >= 0
