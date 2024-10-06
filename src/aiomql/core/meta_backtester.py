from datetime import datetime
from logging import getLogger
from typing import Literal, TypeVar

from numpy import ndarray
from MetaTrader5 import (Tick, SymbolInfo, AccountInfo, TerminalInfo, TradeOrder, TradePosition, TradeDeal,
                         OrderCheckResult, OrderSendResult)

from .meta_trader import MetaTrader
from .constants import TimeFrame, CopyTicks, OrderType
from .._utils import error_handler

logger = getLogger(__name__)

BackTestEngine = TypeVar('BackTestEngine')

class MetaBackTester(MetaTrader):
    """A class for testing trading strategies in the MetaTrader 5 terminal. A subclass of MetaTrader."""
    backtest_engine: BackTestEngine

    def __init__(self, *, backtest_engine: BackTestEngine = None):
        super().__init__()
        self.backtest_engine = backtest_engine

    @property
    def backtest_engine(self) -> BackTestEngine:
        return self.config.backtest_engine

    @backtest_engine.setter
    def backtest_engine(self, value: BackTestEngine):
        if BackTestEngine is not None:
            self.config.backtest_engine = value

    async def last_error(self) -> tuple[int, str]:
        return -1, ''
    
    async def initialize(self, *, path: str = "", login: int = 0, password: str = "", server: str = "",
                         timeout: int | None = None, portable=False) -> bool:
        if self.config.use_terminal_for_backtesting:
            return await super().initialize(path=path, login=login, password=password, server=server, timeout=timeout)

        return True
    
    async def login(self, *, login: int = 0, password: str = '', server: str = '', timeout: int = 60000) -> bool:
        if self.config.use_terminal_for_backtesting:
            return await super().login(login=login, password=password, server=server, timeout=timeout)
        return True

    async def shutdown(self) -> None:
        await super().shutdown() if self.config.use_terminal_for_backtesting else ...

    @error_handler(msg='test data not available', exe=AttributeError)
    async def terminal_info(self) -> TerminalInfo:
        res = await self.backtest_engine.get_terminal_info()
        return res

    @error_handler(msg='test data not available', exe=AttributeError)
    async def account_info(self) -> AccountInfo:
        """"""
        return self.backtest_engine.get_account_info()

    @error_handler(msg='test data not available', exe=AttributeError)
    async def symbols_total(self) -> int:
        tot = await self.backtest_engine.get_symbols_total()
        return tot

    @error_handler(msg='test data not available', exe=AttributeError)
    async def symbols_get(self, group: str = "") -> tuple[SymbolInfo, ...] | None:
        """"""
        syms = await self.backtest_engine.get_symbols(group=group)
        return syms

    @error_handler(msg='test data not available', exe=AttributeError)
    async def symbol_info(self, symbol: str) -> SymbolInfo | None:
        sym = await self.backtest_engine.get_symbol_info(symbol=symbol)
        return sym

    @error_handler(msg='test data not available', exe=AttributeError)
    async def symbol_info_tick(self, symbol: str) -> Tick | None:
        tick = await self.backtest_engine.get_symbol_info_tick(symbol=symbol)
        return tick

    @error_handler(msg='test data not available', exe=AttributeError)
    async def copy_rates_from(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float,
                              count: int) -> ndarray | None:
        rates = await self.backtest_engine.get_rates_from(symbol=symbol, timeframe=timeframe, date_from=date_from,
                                                          count=count)
        return rates

    @error_handler(msg='test data not available', exe=AttributeError)
    async def copy_rates_from_pos(self, symbol: str, timeframe: TimeFrame, start_pos: int,
                                  count: int) -> ndarray | None:
        rates = await self.backtest_engine.get_rates_from_pos(symbol=symbol, timeframe=timeframe, start_pos=start_pos,
                                                              count=count)
        return rates

    @error_handler(msg='test data not available', exe=AttributeError)
    async def copy_rates_range(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float,
                               date_to: datetime | float) -> ndarray | None:
        rates = await self.backtest_engine.get_rates_range(symbol=symbol, timeframe=timeframe, date_from=date_from,
                                                           date_to=date_to)
        return rates

    @error_handler(msg='test data not available', exe=AttributeError)
    async def copy_ticks_from(self, symbol: str, date_from: datetime | float, count: int,
                              flags: CopyTicks) -> ndarray | None:
        ticks = await self.backtest_engine.get_ticks_from(symbol=symbol, date_from=date_from, count=count, flags=flags)
        return ticks

    @error_handler(msg='test data not available', exe=AttributeError)
    async def copy_ticks_range(self, symbol: str, date_from: datetime | float, date_to: datetime | float,
                               flags: CopyTicks) -> ndarray | None:
        ticks = await self.backtest_engine.get_ticks_range(symbol=symbol, date_from=date_from, date_to=date_to,
                                                           flags=flags)
        return ticks

    @error_handler(msg='test data not available', exe=AttributeError)
    async def orders_total(self) -> int:
        return self.backtest_engine.get_orders_total()

    @error_handler(msg='test data not available', exe=AttributeError)
    async def orders_get(self, group: str = "", ticket: int = 0, symbol: str = "") -> tuple[TradeOrder, ...] | None:
        kwargs = {key: value for key, value in (('group', group), ('ticket', ticket), ('symbol', symbol)) if value}
        return self.backtest_engine.get_orders(**kwargs)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def order_calc_margin(self, action: OrderType, symbol: str, volume: float, price: float) -> float | None:
        res = await self.backtest_engine.order_calc_margin(action=action, symbol=symbol, volume=volume, price=price)
        return res

    @error_handler(msg='test data not available', exe=AttributeError)
    async def order_calc_profit(self, action: Literal[0, 1], symbol: str, volume: float, price_open: float,
                                price_close: float) -> float | None:

        profit = await self.backtest_engine.order_calc_profit(action=action, symbol=symbol, volume=volume,
                                                      price_open=price_open, price_close=price_close)
        return profit

    @error_handler(msg='test data not available', exe=AttributeError)
    async def order_check(self, request: dict) -> OrderCheckResult:
        ocr = await self.backtest_engine.order_check(request=request)
        return ocr

    async def order_send(self, request: dict) -> OrderSendResult:
        osr = await self.backtest_engine.order_send(request=request)
        return osr

    @error_handler(msg='test data not available', exe=AttributeError)
    async def positions_total(self) -> int:
        return self.backtest_engine.get_positions_total()

    @error_handler(msg='test data not available', exe=AttributeError)
    async def positions_get(self, group: str = "", ticket: int = None,
                            symbol: str = "") -> tuple[TradePosition, ...] | None:
        kwargs = {key: value for key, value in (('group', group), ('ticket', ticket), ('symbol', symbol)) if value}
        return self.backtest_engine.get_positions(**kwargs)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def history_orders_total(self, date_from: datetime | float, date_to: datetime | float) -> int | None:
        return self.backtest_engine.get_history_orders_total(date_from=date_from, date_to=date_to)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def history_orders_get(self, date_from: datetime | float = None, date_to: datetime | float = None,
                                 group: str = '', ticket: int = None,
                                 position: int = None) -> tuple[TradeOrder, ...] | None:
        args = (('date_from', date_from), ('date_to', date_to), ('group', group), ('ticket', ticket),
                ('position', position))
        kwargs = {key: value for key, value in args if value}
        return self.backtest_engine.get_history_orders(**kwargs)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def history_deals_total(self, date_from: datetime | float, date_to: datetime | float) -> int | None:
        return self.backtest_engine.get_history_deals_total(date_from=date_from, date_to=date_to)

    @error_handler(msg='test data not available', exe=AttributeError)
    async def history_deals_get(self, date_from: datetime | float = None, date_to: datetime | float = None,
                                group: str = '', ticket: int = None,
                                position: int = None) -> tuple[TradeDeal, ...] | None:
        args = (('date_from', date_from), ('date_to', date_to), ('group', group), ('ticket', ticket),
                ('position', position))
        kwargs = {key: value for key, value in args if value}
        return self.backtest_engine.get_history_deals(**kwargs)
