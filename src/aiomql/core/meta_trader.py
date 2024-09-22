from datetime import datetime
import asyncio
from logging import getLogger
from typing import Callable

import MetaTrader5
import numpy as np
from MetaTrader5 import BookInfo, SymbolInfo, AccountInfo, Tick, TerminalInfo, TradeOrder, TradeDeal, \
    TradePosition, OrderSendResult, OrderCheckResult

from .constants import TimeFrame, CopyTicks, OrderType
from .errors import Error
from .config import Config

logger = getLogger()


class BaseMeta(type):
    def __new__(mcs, cls_name, bases, cls_dict):
        defaults = MetaTrader5.__dict__
        defaults = {f'_{key}': value for key, value in defaults.items() if not key.startswith('_')}
        cls_dict |= defaults
        return super().__new__(mcs, cls_name, bases, cls_dict)


class MetaTrader(metaclass=BaseMeta):
    _account_info: Callable
    _copy_rates_from: Callable
    _copy_rates_from_pos: Callable
    _copy_rates_range: Callable
    _copy_ticks_from: Callable
    _copy_ticks_range: Callable
    _history_deals_get: Callable
    _history_deals_total: Callable
    _history_orders_get: Callable
    _history_orders_total: Callable
    _initialize: Callable
    _last_error: Callable
    _login: Callable
    _market_book_add: Callable
    _market_book_get: Callable
    _market_book_release: Callable
    _order_calc_margin: Callable
    _order_calc_profit: Callable
    _order_check: Callable
    _order_send: Callable
    _orders_get: Callable
    _orders_total: Callable
    _positions_get: Callable
    _positions_total: Callable
    _shutdown: Callable
    _symbol_info: Callable
    _symbol_info_tick: Callable
    _symbol_select: Callable
    _symbols_get: Callable
    _symbols_total: Callable
    _terminal_info: Callable
    _version: Callable
    config: Config

    def __init__(self):
        self.config = Config()
        self.error: Error = Error(1)

    async def __aenter__(self) -> 'MetaTrader':
        """
        Async context manager entry point.
        Initializes the connection to the MetaTrader terminal.

        Returns:
            MetaTrader: An instance of the MetaTrader class.
        """
        await self.initialize(**Config().account_info())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit point. Closes the connection to the MetaTrader terminal.
        """
        await self.shutdown()

    async def _handler(self, api: dict):
        func = api['func']
        args = api.get('args', ())
        kwargs = api.get('kwargs', {})
        error_msg = api.get('error_msg', 'An error occurred')

        res = await asyncio.to_thread(func, *args, **kwargs)
        if res is None:
            err = await self.last_error()
            self.error = Error(*err)

            if self.error.is_connection_error():
                await self.initialize(**self.config.account_info(), path=self.config.path)
                await self.login(**self.config.account_info())
                res = await asyncio.to_thread(func, *args, **kwargs)

                if res is None:
                    err = await self.last_error()
                    self.error = Error(*err)
                    logger.warning(f'{error_msg}:{self.error.description}')
            else:
                logger.warning(f'{error_msg}:{self.error.description}')
        return res

    async def login(self, login: int, password: str, server: str, timeout: int = 60000) -> bool:
        """
        Connects to the MetaTrader terminal using the specified login, password and server.

        Args:
            login (int): The trading account number.
            password (str): The trading account password.
            server (str): The trading server name.
            timeout (int): The timeout for the connection in seconds.

        Returns:
            bool: True if successful, False otherwise.
        """
        return await asyncio.to_thread(self._login, login, password=password, server=server, timeout=timeout)

    async def initialize(self, path: str = "", login: int = 0, password: str = "", server: str = "",
                         timeout: int | None = None, portable=False) -> bool:
        """
        Initializes the connection to the MetaTrader terminal. All parameters are optional.

        Keyword Args:
            path (str): The path to the MetaTrader terminal executable.
            login (int): The trading account number.
            password (str): The trading account password.
            server (str): The trading server name.
            timeout (int): The timeout for the connection in seconds.
            portable (bool): If True, the terminal will be launched in portable mode.

        Returns:
            bool: True if successful, False otherwise.
        """
        args = (str(path),) if path else ()
        kwargs = {key: value for key, value in (('login', login), ('password', password), ('server', server),
                                                ('timeout', timeout), ('portable', portable)) if value}
        res = await asyncio.to_thread(self._initialize, *args, **kwargs)
        return res

    async def shutdown(self) -> None:
        """
        Closes the connection to the MetaTrader terminal.

        Returns:
            None: None
        """
        res = await asyncio.to_thread(self._shutdown)
        return res

    async def last_error(self) -> tuple[int, str]:
        try:
            res = await asyncio.to_thread(self._last_error)
            return res
        except Exception as err:
            logger.warning(f'Error in obtaining last error.')
            return -1, str(err)

    async def version(self) -> tuple[int, int, str] | None:
        """"""
        api = {'func': self._version, 'error_msg': 'Error in obtaining version.'}
        res = await self._handler(api)
        return res

    async def account_info(self) -> AccountInfo | None:
        """"""
        api = {'func': self._account_info, 'error_msg': 'Error in obtaining account information'}
        res = await self._handler(api)
        return res

    async def terminal_info(self) -> TerminalInfo | None:
        api = {'func': self._terminal_info, 'error_msg': 'Error in obtaining terminal information'}
        res = await self._handler(api)
        return res

    async def symbols_total(self) -> int:
        api = {'func': self._symbols_total, 'error_msg': 'Error in obtaining total symbols.'}
        res = await self._handler(api)
        return res

    async def symbols_get(self, group: str = "") -> tuple[SymbolInfo] | None:
        kwargs = {'group': group} if group else {}
        api = {'func': self._symbols_get, 'kwargs': kwargs, 'error_msg': 'Error in obtaining symbols.'}
        res = await self._handler(api)
        return res

    async def symbol_info(self, symbol: str) -> SymbolInfo | None:
        api = {'func': self._symbol_info, 'args': (symbol,), 'error_msg': f'Error in obtaining information for {symbol}'}
        res = await self._handler(api)
        return res

    async def symbol_info_tick(self, symbol: str) -> Tick | None:
        api = {'func': self._symbol_info_tick, 'args': (symbol,), 'error_msg': f'Error in obtaining tick for {symbol}'}
        res = await self._handler(api)
        return res

    async def symbol_select(self, symbol: str, enable: bool) -> bool:
        api = {'func': self._symbol_select, 'args': (symbol, enable), 'error_msg': f'Error in selecting {symbol}'}
        res = await self._handler(api)
        return res

    async def market_book_add(self, symbol: str) -> bool:
        api = {'func': self._market_book_add, 'args': (symbol,), 'error_msg': f'Error in adding {symbol} to market book'}
        res = await self._handler(api)
        return res

    async def market_book_get(self, symbol: str) -> tuple[BookInfo] | None:
        api = {'func': self._market_book_get, 'args': (symbol,), 'error_msg': f'Error in obtaining market depth for {symbol}'}
        res = await self._handler(api)
        return res

    async def market_book_release(self, symbol: str) -> bool:
        api = {'func': self._market_book_release, 'args': (symbol,), 'error_msg': f'Error in releasing market depth for {symbol}'}
        res = await self._handler(api)
        return res

    async def copy_rates_from(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float, count: int) -> np.ndarray | None:
        api = {'func': self._copy_rates_from, 'args': (symbol, timeframe, date_from, count),
               'error_msg': f'Error in obtaining rates for {symbol}'}
        res = await self._handler(api)
        return res

    async def copy_rates_from_pos(self, symbol: str, timeframe: TimeFrame, start_pos: int, count: int) -> np.ndarray | None:
        api = {'func': self._copy_rates_from_pos, 'args': (symbol, timeframe, start_pos, count),
               'error_msg': f'Error in obtaining rates for {symbol}'}
        res = await self._handler(api)
        return res

    async def copy_rates_range(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float,
                               date_to: datetime | float) -> np.ndarray | None:
        api = {'func': self._copy_rates_range, 'args': (symbol, timeframe, date_from, date_to),
               'error_msg': f'Error in obtaining rates for {symbol}'}
        res = await self._handler(api)
        return res

    async def copy_ticks_from(self, symbol: str, date_from: datetime | float, count: int, flags: CopyTicks) -> np.ndarray | None:
        api = {'func': self._copy_ticks_from, 'args': (symbol, date_from, count, flags),
               'error_msg': f'Error in obtaining ticks for {symbol}'}
        res = await self._handler(api)
        return res

    async def copy_ticks_range(self, symbol: str, date_from: datetime | float, date_to: datetime | float,
                               flags: CopyTicks) -> np.ndarray | None:
        api = {'func': self._copy_ticks_range, 'args': (symbol, date_from, date_to, flags),
               'error_msg': f'Error in obtaining ticks for {symbol}'}
        res = await self._handler(api)
        return res

    async def orders_total(self) -> int:
        api = {'func': self._orders_total, 'error_msg': 'Error in obtaining total orders.'}
        res = await self._handler(api)
        return res

    async def orders_get(self, group: str = "", ticket: int = 0, symbol: str = "") -> tuple[TradeOrder] | None:
        kwargs = {key: value for key, value in (('group', group), ('ticket', ticket), ('symbol', symbol)) if value}
        api = {'func': self._orders_get, 'kwargs': kwargs, 'error_msg': 'Error in obtaining orders.'}
        res = await self._handler(api)
        return res

    async def order_calc_margin(self, action: OrderType, symbol: str, volume: float, price: float) -> float | None:
        api = {'func': self._order_calc_margin, 'args': (action, symbol, volume, price),
               'error_msg': 'Error in calculating margin.'}
        res = await self._handler(api)
        return res

    async def order_calc_profit(self, action: OrderType, symbol: str, volume: float, price_open: float,
                                price_close: float) -> float | None:
        api = {'func': self._order_calc_profit, 'args': (action, symbol, volume, price_open, price_close),
               'error_msg': 'Error in calculating profit.'}
        res = await self._handler(api)
        return res

    async def order_check(self, request: dict) -> OrderCheckResult:
        api = {'func': self._order_check, 'args': (request,), 'error_msg': 'Error in checking order.'}
        res = await self._handler(api)
        return res

    async def order_send(self, request: dict) -> OrderSendResult:
        api = {'func': self._order_send, 'args': (request,), 'error_msg': 'Error in sending order.'}
        res = await self._handler(api)
        return res

    async def positions_total(self) -> int:
        api = {'func': self._positions_total, 'error_msg': 'Error in obtaining total positions.'}
        res = await self._handler(api)
        return res

    async def positions_get(self, group: str = "", ticket: int = None, symbol: str = "") -> tuple[TradePosition] | None:
        kwargs = {key: value for key, value in (('group', group), ('ticket', ticket), ('symbol', symbol)) if value}
        api = {'func': self._positions_get, 'kwargs': kwargs,
               'error_msg': 'Error in obtaining open positions.'}
        res = await self._handler(api)
        return res

    async def history_orders_total(self, date_from: datetime | float, date_to: datetime | float) -> int:
        api = {'func': self._history_orders_total, 'args': (date_from, date_to),
               'error_msg': 'Error in obtaining total history orders.'}
        res = await self._handler(api)
        return res

    async def history_orders_get(self, date_from: datetime | float = None, date_to: datetime | float = None,
                                 group: str = '', ticket: int = None, position: int = None) -> tuple[TradeOrder] | None:
        kwargs = {key: value for key, value in (('group', group), ('ticket', ticket), ('position', position)) if value}
        args = tuple(arg for arg in (date_from, date_to) if arg)
        api = {'func': self._history_orders_get, 'args': args, 'kwargs': kwargs,
               'error_msg': 'Error in obtaining history orders'}
        res = await self._handler(api)
        return res

    async def history_deals_total(self, date_from: datetime | float, date_to: datetime | float) -> int:
        api = {'func': self._history_deals_total, 'args': (date_from, date_to),
               'error_msg': 'Error in obtaining total history deals'}
        res = await self._handler(api)
        return res

    async def history_deals_get(self, date_from: datetime | float = None, date_to: datetime | float = None,
                                group: str = '', ticket: int = None, position: int = None) -> tuple[TradeDeal] | None:
        kwargs = {key: value for key, value in (('group', group), ('ticket', ticket), ('position', position)) if value}
        args = tuple(arg for arg in (date_from, date_to) if arg)
        api = {'func': self._history_deals_get, 'args': args, 'kwargs': kwargs,
               'error_msg': 'Error in obtaining history deals'}
        res = await self._handler(api)
        return res
