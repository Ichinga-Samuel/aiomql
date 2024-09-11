from datetime import datetime
from logging import getLogger

from numpy import ndarray
from MetaTrader5 import (Tick, SymbolInfo, AccountInfo, TerminalInfo, TradeOrder, TradePosition, TradeDeal,
                         OrderCheckResult, OrderSendResult)

from .test_data import TestData
from .get_data import GetData

from ...core.meta_trader import MetaTrader
from ...core.constants import TimeFrame, CopyTicks, OrderType
from ...utils import error_handler

logger = getLogger(__name__)


class MetaTester(MetaTrader):
    """A class for testing trading strategies in the MetaTrader 5 terminal. A subclass of MetaTrader."""

    def __init__(self, test_data: TestData = None):
        super().__init__()
        if self.test_data:
            self.config.test_data = test_data

    @property
    def test_data(self) -> TestData | None:
        test_data = self.config.test_data
        if test_data is None:
            ...
            # logger.error('No Test Data Available')
        return test_data

    @test_data.setter
    def test_data(self, value: TestData):
        self.config.test_data = value
    
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
                    self.test_data = TestData(data)
                    success = True

        except Exception as err:
            logger.error(f'{err}: unable to load test data')
            success = False

        return success

    async def login(self, login: int, password: str, server: str, timeout: int = 60000) -> bool:
        return await super().login(login, password, server, timeout) if self.config.use_terminal_for_backtesting else True

    async def shutdown(self) -> None:
        await super().shutdown() if self.config.use_terminal_for_backtesting else ...

        # self.test_data.save()
        # name = self.test_data.data.name
        # if self.config.compress_test_data:
        #     name += '.xz'
        # name = self.config.test_data_dir/name
        # GetData.dump_data(data=self.test_data.data, name=name, compress=self.config.compress_test_data)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def terminal_info(self) -> TerminalInfo:
        return self.test_data.get_terminal_info()

    @error_handler(msg='test data not available', exe=AttributeError)
    async def account_info(self) -> AccountInfo:
        """"""
        return self.test_data.get_account_info()

    @error_handler(msg='test data not available', exe=AttributeError)
    async def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        return symbol in self.test_data.symbols and enable

    @error_handler(msg='test data not available', exe=AttributeError)
    async def symbols_total(self) -> int:
        return self.test_data.get_symbols_total()

    @error_handler(msg='test data not available', exe=AttributeError)
    async def symbols_get(self, group: str = "") -> tuple[SymbolInfo, ...] | None:
        """"""
        return self.test_data.get_symbols(group)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def symbol_info(self, symbol: str) -> SymbolInfo | None:
        return self.test_data.symbols.get(symbol)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def symbol_info_tick(self, symbol: str) -> Tick | None:
        return self.test_data.get_symbol_info_tick(symbol)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def copy_rates_from(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float,
                              count: int) -> ndarray | None:
        return self.test_data.get_rates_from(symbol, timeframe, date_from, count)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def copy_rates_from_pos(self, symbol: str, timeframe: TimeFrame, start_pos: int,
                                  count: int) -> ndarray | None:
        return self.test_data.get_rates_from_pos(symbol, timeframe, start_pos, count)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def copy_rates_range(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float,
                               date_to: datetime | float) -> ndarray | None:
        return self.test_data.get_rates_range(symbol, timeframe, date_from, date_to)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def copy_ticks_from(self, symbol: str, date_from: datetime | float, count: int,
                              flags: CopyTicks) -> ndarray | None:
        return self.test_data.get_ticks_from(symbol, date_from, count, flags)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def copy_ticks_range(self, symbol: str, date_from: datetime | float, date_to: datetime | float,
                               flags: CopyTicks) -> ndarray | None:
        return self.test_data.get_ticks_range(symbol, date_from, date_to, flags)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def orders_total(self) -> int:
        return self.test_data.get_orders_total()

    @error_handler(msg='test data not available', exe=AttributeError)
    async def orders_get(self, group: str = "", ticket: int = 0, symbol: str = "") -> tuple[TradeOrder, ...] | None:
        kwargs = {key: value for key, value in (('group', group), ('ticket', ticket), ('symbol', symbol)) if value}
        return self.test_data.get_orders(**kwargs)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def order_calc_margin(self, action: OrderType, symbol: str, volume: float,
                                price: float, use_terminal: bool = True) -> float | None:
        res = await self.test_data.order_calc_margin(action, symbol, volume, price, use_terminal=use_terminal)
        return res

    @error_handler(msg='test data not available', exe=AttributeError)
    async def order_calc_profit(self, action: OrderType, symbol: str, volume: float, price_open: float,
                                price_close: float, use_terminal: bool = True) -> float | None:
        return await self.test_data.order_calc_profit(action, symbol, volume,
                                                      price_open, price_close, use_terminal=use_terminal)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def order_check(self, request: dict, use_terminal: bool = True) -> OrderCheckResult:
        return await self.test_data.order_check(request, use_terminal=use_terminal)

    async def order_send(self, request: dict, use_terminal: bool = True) -> OrderSendResult:
        return await self.test_data.order_send(request, use_terminal=use_terminal)

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
