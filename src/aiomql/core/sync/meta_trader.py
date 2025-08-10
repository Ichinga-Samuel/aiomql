from datetime import datetime
from logging import getLogger
from typing import Literal, Self
from pathlib import Path

import numpy as np
from MetaTrader5 import (
    BookInfo,
    SymbolInfo,
    AccountInfo,
    Tick,
    TerminalInfo,
    TradeOrder,
    TradeDeal,
    TradePosition,
    OrderSendResult,
    OrderCheckResult,
)

from ..constants import OrderType, CopyTicks

from .._core import MetaCore
from ..errors import Error
from ..config import Config

logger = getLogger()


class MetaTrader(MetaCore):
    def __init__(self):
        self.config = Config()
        self.error: Error = Error(code=1)

    def __enter__(self) -> Self:
        """
        Async context manager entry point.
        Initializes the connection to the MetaTrader terminal.

        Returns:
            MetaTrader: An instance of the MetaTrader class.
        """
        self.initialize()
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit point. Closes the connection to the MetaTrader terminal.
        """
        self.shutdown()

    def _handler(self, api: dict, retries=3):
        func = api["func"]
        args = api.get("args", ())
        kwargs = api.get("kwargs", {})
        error_msg = api.get("error_msg", "An error occurred")
        res = func(*args, **kwargs)

        if res is not None:
            return res

        if res is None and self.error.is_connection_error() and retries > 0:
            self.initialize()
            self.login()
            return self._handler(api, retries=retries - 1)
        else:
            err = self.last_error()
            self.error = Error(*err)
            logger.warning(f"{error_msg}:{self.error.description}")
        return res

    def login(self, *, login: int = 0, password: str = "", server: str = "", timeout: int = 60000) -> bool:
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
        acc_details = self.config.account_info
        login = login or acc_details.get("login", 0)
        password = password or acc_details.get("password", "")
        server = server or acc_details.get("server", "")
        return self._login(login, password=password, server=server, timeout=timeout)

    def initialize(self, path: str = None, login: int = 0, password: str = "", server: str = "",
                        timeout: int | None = None, portable=False) -> bool:
        """
        Initializes the connection to the MetaTrader terminal. All parameters are optional.

        Keyword Args:
            path (str): The path to the MetaTrader terminal executable.
            login (int): The trading account number.
            password (str): The trading account password.
            server (str): The trading server name.
            timeout (int): The timeout for the connection in milliseconds.
            portable (bool): If True, the terminal will be launched in portable mode.

        Returns:
            bool: True if successful, False otherwise.
        """
        path = self.config.path if path is None else path
        path = "" if Path(path).exists() is False else path
        args = (str(path),) if path else ()
        acc = self.config.account_info
        kwargs = {key: value for key, value in (("login", login or acc.get("login")),
                                                ("password", password or acc.get("password")),
                                                ("server", server or acc.get("server")), ("timeout", timeout or 45000),
                                                ("portable", portable)) if key is not None}
        res = self._initialize(*args, **kwargs)
        if not res:
            err = self._last_error()
            self.error = Error(*err)
        return res

    def shutdown(self) -> None:
        """Closes the connection to the MetaTrader terminal."""
        self._shutdown()

    def last_error(self) -> tuple[int, str]:
        try:
            return self.last_error()
        except Exception as err:
            logger.warning("%s: Error in obtaining last error.", err)
            return -1, str(err)

    def version(self) -> tuple[int, int, str] | None:
        """"""
        api = {"func": self._version, "error_msg": "Error in obtaining version."}
        return self._handler(api)

    def account_info(self) -> AccountInfo | None:
        """"""
        api = {"func": self._account_info, "error_msg": "Error in obtaining account information"}
        return self._handler(api)

    def terminal_info(self) -> TerminalInfo | None:
        api = {"func": self._terminal_info, "error_msg": "Error in obtaining terminal information"}
        return self._handler(api)

    def symbols_total(self) -> int:
        api = {"func": self._symbols_total, "error_msg": "Error in obtaining total symbols."}
        return self._handler(api)

    def symbols_get(self, group: str = "") -> tuple[SymbolInfo] | None:
        kwargs = {"group": group} if group else {}
        api = {"func": self._symbols_get, "kwargs": kwargs, "error_msg": "Error in obtaining symbols."}
        return self._handler(api)

    def symbol_info(self, symbol: str) -> SymbolInfo | None:
        api = {
            "func": self._symbol_info,
            "args": (symbol,),
            "error_msg": f"Error in obtaining information for {symbol}",
        }
        return self._handler(api)

    def symbol_info_tick(self, symbol: str) -> Tick | None:
        api = {"func": self._symbol_info_tick, "args": (symbol,), "error_msg": f"Error in obtaining tick for {symbol}"}
        return self._handler(api)

    def symbol_select(self, symbol: str, enable: bool) -> bool:
        api = {"func": self._symbol_select, "args": (symbol, enable), "error_msg": f"Error in selecting {symbol}"}
        return self._handler(api)

    def market_book_add(self, symbol: str) -> bool:
        api = {
            "func": self._market_book_add,
            "args": (symbol,),
            "error_msg": f"Error in adding {symbol} to market book",
        }
        return self._handler(api)

    def market_book_get(self, symbol: str) -> tuple[BookInfo] | None:
        api = {
            "func": self._market_book_get,
            "args": (symbol,),
            "error_msg": f"Error in obtaining market depth for {symbol}",
        }
        return self._handler(api)

    def market_book_release(self, symbol: str) -> bool:
        api = {
            "func": self._market_book_release,
            "args": (symbol,),
            "error_msg": f"Error in releasing market depth for {symbol}",
        }
        return self._handler(api)

    def copy_rates_from(
        self, symbol: str, timeframe: int, date_from: datetime | float, count: int
    ) -> np.ndarray | None:
        api = {
            "func": self._copy_rates_from,
            "args": (symbol, timeframe, date_from, count),
            "error_msg": f"Error in obtaining rates for {symbol}",
        }
        return self._handler(api)

    def copy_rates_from_pos(self, symbol: str, timeframe: int, start_pos: int, count: int) -> np.ndarray | None:
        api = {
            "func": self._copy_rates_from_pos,
            "args": (symbol, timeframe, start_pos, count),
            "error_msg": f"Error in obtaining rates for {symbol}",
        }
        return self._handler(api)

    def copy_rates_range(
        self, symbol: str, timeframe: int, date_from: datetime | float, date_to: datetime | float
    ) -> np.ndarray | None:
        api = {
            "func": self._copy_rates_range,
            "args": (symbol, timeframe, date_from, date_to),
            "error_msg": f"Error in obtaining rates for {symbol}",
        }
        return self._handler(api)

    def copy_ticks_from(
        self, symbol: str, date_from: datetime | float, count: int, flags: CopyTicks
    ) -> np.ndarray | None:
        api = {
            "func": self._copy_ticks_from,
            "args": (symbol, date_from, count, flags),
            "error_msg": f"Error in obtaining ticks for {symbol}",
        }
        return self._handler(api)

    def copy_ticks_range(
        self, symbol: str, date_from: datetime | float, date_to: datetime | float, flags: CopyTicks
    ) -> np.ndarray | None:
        api = {
            "func": self._copy_ticks_range,
            "args": (symbol, date_from, date_to, flags),
            "error_msg": f"Error in obtaining ticks for {symbol}",
        }
        return self._handler(api)

    def orders_total(self) -> int:
        api = {"func": self._orders_total, "error_msg": "Error in obtaining total orders."}
        return self._handler(api)

    def orders_get(self, group: str = "", ticket: int = 0, symbol: str = "") -> tuple[TradeOrder] | None:
        kwargs = {key: value for key, value in (("group", group), ("ticket", ticket), ("symbol", symbol)) if value}
        api = {"func": self._orders_get, "kwargs": kwargs, "error_msg": "Error in obtaining orders."}
        return self._handler(api)

    def order_calc_margin(
        self, action: Literal[OrderType.BUY, OrderType.SELL], symbol: str, volume: float, price: float
    ) -> float | None:
        api = {
            "func": self._order_calc_margin,
            "args": (action, symbol, volume, price),
            "error_msg": "Error in calculating margin.",
        }
        return self._handler(api)

    def order_calc_profit(
        self,
        action: Literal[OrderType.BUY, OrderType.SELL],
        symbol: str,
        volume: float,
        price_open: float,
        price_close: float,
    ) -> float | None:
        api = {
            "func": self._order_calc_profit,
            "args": (action, symbol, volume, price_open, price_close),
            "error_msg": "Error in calculating profit.",
        }
        return self._handler(api)

    def order_check(self, request: dict) -> OrderCheckResult:
        api = {"func": self._order_check, "args": (request,), "error_msg": "Error in checking order."}
        return self._handler(api)

    def order_send(self, request: dict) -> OrderSendResult:
        api = {"func": self._order_send, "args": (request,), "error_msg": "Error in sending order."}
        return self._handler(api)

    def positions_total(self) -> int:
        api = {"func": self._positions_total, "error_msg": "Error in obtaining total positions."}
        return self._handler(api)

    def positions_get(self, group: str = "", ticket: int = None, symbol: str = "") -> tuple[TradePosition] | None:
        kwargs = {key: value for key, value in (("group", group), ("ticket", ticket), ("symbol", symbol)) if value}
        api = {"func": self._positions_get, "kwargs": kwargs, "error_msg": "Error in obtaining open positions."}
        return self._handler(api)

    def history_orders_total(self, date_from: datetime | float, date_to: datetime | float) -> int:
        api = {
            "func": self._history_orders_total,
            "args": (date_from, date_to),
            "error_msg": "Error in obtaining total history orders.",
        }
        return self._handler(api)

    def history_orders_get(
        self,
        date_from: datetime | float = None,
        date_to: datetime | float = None,
        group: str = "",
        ticket: int = None,
        position: int = None,
    ) -> tuple[TradeOrder] | None:
        kwargs = {key: value for key, value in (("group", group), ("ticket", ticket), ("position", position)) if value}
        args = tuple(arg for arg in (date_from, date_to) if arg)
        api = {
            "func": self._history_orders_get,
            "args": args,
            "kwargs": kwargs,
            "error_msg": "Error in obtaining history orders",
        }
        return self._handler(api)

    def history_deals_total(self, date_from: datetime | float, date_to: datetime | float) -> int:
        api = {
            "func": self._history_deals_total,
            "args": (date_from, date_to),
            "error_msg": "Error in obtaining total history deals",
        }
        return self._handler(api)

    def history_deals_get(
        self,
        date_from: datetime | float = None,
        date_to: datetime | float = None,
        group: str = "",
        ticket: int = None,
        position: int = None,
    ) -> tuple[TradeDeal] | None:
        kwargs = {key: value for key, value in (("group", group), ("ticket", ticket), ("position", position)) if value}
        args = tuple(arg for arg in (date_from, date_to) if arg)
        api = {
            "func": self._history_deals_get,
            "args": args,
            "kwargs": kwargs,
            "error_msg": "Error in obtaining history deals",
        }
        return self._handler(api)
