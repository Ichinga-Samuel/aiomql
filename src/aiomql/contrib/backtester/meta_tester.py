from datetime import datetime
from logging import getLogger

from numpy import ndarray
from MetaTrader5 import (Tick, SymbolInfo, AccountInfo, TerminalInfo, TradeOrder, TradePosition, TradeDeal,
                         OrderCheckResult, OrderSendResult)

from .backtest_engine import BackTestEngine
from .get_data import GetData

from ...core.meta_trader import MetaTrader
from ...core.constants import TimeFrame, CopyTicks, OrderType
from ...utils import error_handler

logger = getLogger(__name__)


class MetaTester(MetaTrader):
    """A class for testing trading strategies in the MetaTrader 5 terminal. A subclass of MetaTrader."""

    def __init__(self, test_data: BackTestEngine = None):
        super().__init__()
        if test_data is not None:
            self.config.test_data = test_data

    @property
    def test_data(self) -> BackTestEngine | None:
        return self.config.test_data

    @test_data.setter
    def test_data(self, value: BackTestEngine):
        self.config.test_data = value

    async def last_error(self) -> tuple[int, str]:
        return -1, ''
    
    async def initialize(self, path: str = "", login: int = 0, password: str = "", server: str = "", 
                   timeout: int | None = None, portable=False, load_test_data: bool = False,
                         test_data_file: str = '', use_terminal: bool = True) -> bool:

        success = True
        if self.config.use_terminal_for_backtesting:
            success = await super().initialize(path=path, login=login, password=password, server=server, timeout=timeout)

        try:
            if load_test_data:
                name = f"{self.config.test_data_dir_name}/{test_data_file}"
                data = GetData.load_data(name=name, compressed=self.config.compress_test_data)
                if data is not None:
                    self.test_data = BackTestEngine(data)
                    success = True

        except Exception as err:
            logger.error(f'{err}: unable to load test data')
            success = False

        return success

    async def login(self, login: int, password: str, server: str, timeout: int = 60000) -> bool:
        return await super().login(login, password, server, timeout) if self.config.use_terminal_for_backtesting else True

    async def shutdown(self) -> None:
        await super().shutdown() if self.config.use_terminal_for_backtesting else ...

    @error_handler(msg='test data not available', exe=AttributeError)
    async def terminal_info(self) -> TerminalInfo:
        res = await self.test_data.get_terminal_info()
        return res

    @error_handler(msg='test data not available', exe=AttributeError)
    async def account_info(self) -> AccountInfo:
        """"""
        return self.test_data.get_account_info()

    @error_handler(msg='test data not available', exe=AttributeError)
    async def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        if self.config.use_terminal_for_backtesting:
            res = await super().symbol_select(symbol, enable)
            return res
        res = (symbol in self.test_data.symbols) and enable
        return res

    @error_handler(msg='test data not available', exe=AttributeError)
    async def symbols_total(self) -> int:
        tot = await self.test_data.get_symbols_total()
        return tot

    @error_handler(msg='test data not available', exe=AttributeError)
    async def symbols_get(self, group: str = "") -> tuple[SymbolInfo, ...] | None:
        """"""
        syms = await self.test_data.get_symbols(group)
        return syms

    @error_handler(msg='test data not available', exe=AttributeError)
    async def symbol_info(self, symbol: str) -> SymbolInfo | None:
        sym = await self.test_data.get_symbol_info(symbol)
        return sym

    @error_handler(msg='test data not available', exe=AttributeError)
    async def symbol_info_tick(self, symbol: str) -> Tick | None:
        tick = await self.test_data.get_symbol_info_tick(symbol)
        return tick

    @error_handler(msg='test data not available', exe=AttributeError)
    async def copy_rates_from(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float,
                              count: int) -> ndarray | None:
        rates = await self.test_data.get_rates_from(symbol, timeframe, date_from, count)
        return rates

    @error_handler(msg='test data not available', exe=AttributeError)
    async def copy_rates_from_pos(self, symbol: str, timeframe: TimeFrame, start_pos: int,
                                  count: int) -> ndarray | None:
        rates = await self.test_data.get_rates_from_pos(symbol, timeframe, start_pos, count)
        return rates

    @error_handler(msg='test data not available', exe=AttributeError)
    async def copy_rates_range(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float,
                               date_to: datetime | float) -> ndarray | None:
        rates = await self.test_data.get_rates_range(symbol, timeframe, date_from, date_to)
        return rates

    @error_handler(msg='test data not available', exe=AttributeError)
    async def copy_ticks_from(self, symbol: str, date_from: datetime | float, count: int,
                              flags: CopyTicks) -> ndarray | None:
        ticks = await self.test_data.get_ticks_from(symbol, date_from, count, flags)
        return ticks

    @error_handler(msg='test data not available', exe=AttributeError)
    async def copy_ticks_range(self, symbol: str, date_from: datetime | float, date_to: datetime | float,
                               flags: CopyTicks) -> ndarray | None:
        ticks = await self.test_data.get_ticks_range(symbol, date_from, date_to, flags)
        return ticks

    @error_handler(msg='test data not available', exe=AttributeError)
    async def orders_total(self) -> int:
        return self.test_data.get_orders_total()

    @error_handler(msg='test data not available', exe=AttributeError)
    async def orders_get(self, group: str = "", ticket: int = 0, symbol: str = "") -> tuple[TradeOrder, ...] | None:
        kwargs = {key: value for key, value in (('group', group), ('ticket', ticket), ('symbol', symbol)) if value}
        return self.test_data.get_orders(**kwargs)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def order_calc_margin(self, action: OrderType, symbol: str, volume: float, price: float) -> float | None:
        res = await self.test_data.order_calc_margin(action, symbol, volume, price)
        return res

    @error_handler(msg='test data not available', exe=AttributeError)
    async def order_calc_profit(self, action: OrderType, symbol: str, volume: float, price_open: float,
                                price_close: float) -> float | None:

        profit = await self.test_data.order_calc_profit(action, symbol, volume,
                                                      price_open, price_close)
        return profit

    @error_handler(msg='test data not available', exe=AttributeError)
    async def order_check(self, request: dict) -> OrderCheckResult:
        ocr = await self.test_data.order_check(request)
        return ocr

    async def order_send(self, request: dict) -> OrderSendResult:
        osr = await self.test_data.order_send(request)
        return osr

    @error_handler(msg='test data not available', exe=AttributeError)
    async def positions_total(self) -> int:
        return self.test_data.get_positions_total()

    @error_handler(msg='test data not available', exe=AttributeError)
    async def positions_get(self, group: str = "", ticket: int = None,
                            symbol: str = "") -> tuple[TradePosition, ...] | None:
        kwargs = {key: value for key, value in (('group', group), ('ticket', ticket), ('symbol', symbol)) if value}
        return self.test_data.get_positions(**kwargs)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def history_orders_total(self, date_from: datetime | float, date_to: datetime | float) -> int:
        return self.test_data.get_history_orders_total(date_from, date_to)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def history_orders_get(self, date_from: datetime | float = None, date_to: datetime | float = None,
                                 group: str = '', ticket: int = None,
                                 position: int = None) -> tuple[TradeOrder, ...] | None:
        kwargs = {key: value for key, value in (('group', group), ('ticket', ticket), ('position', position)) if value}
        args = tuple(arg for arg in (date_from, date_to) if arg)
        return self.test_data.get_history_orders(*args, **kwargs)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def history_deals_total(self, date_from: datetime | float, date_to: datetime | float) -> int:
        return self.test_data.get_history_deals_total(date_from, date_to)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def history_deals_get(self, date_from: datetime | float = None, date_to: datetime | float = None,
                                group: str = '', ticket: int = None,
                                position: int = None) -> tuple[TradeDeal, ...] | None:
        kwargs = {key: value for key, value in (('group', group), ('ticket', ticket), ('position', position)) if value}
        args = tuple(arg for arg in (date_from, date_to) if arg)
        return self.test_data.get_history_deals(*args, **kwargs)
