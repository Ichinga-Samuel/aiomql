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
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "config"):
            cls.config = Config()
        return super().__new__(cls)

    def __init__(self):
        self.error: Error = Error(code=1)

    def __enter__(self) -> Self:
        """
        Context manager entry point.
        Initializes the connection to the MetaTrader terminal.

        Returns:
            MetaTrader: An instance of the MetaTrader class.
        """
        self.initialize()
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point. Closes the connection to the MetaTrader terminal.
        """
        self.shutdown()

    def _handler(self, api: dict, retries=3):
        """Handles API calls to the MetaTrader terminal with retry logic.

        Executes the specified function and handles connection errors by
        retrying the initialization and login process.

        Args:
            api: A dictionary containing:
                - func: The function to execute.
                - args: Optional tuple of positional arguments.
                - kwargs: Optional dictionary of keyword arguments.
                - error_msg: Optional error message for logging.
            retries: Number of retry attempts for connection errors.
                Defaults to 3.

        Returns:
            The result of the API call, or None if the call failed.
        """
        func = api["func"]
        args = api.get("args", ())
        kwargs = api.get("kwargs", {})
        error_msg = api.get("error_msg", f"An error occurred in {func.__name__} of {self.__class__.__name__}")
        if func.__name__ in ("order_send", "order_check"):
            res = func(args[0])
        else:
            res = func(*args, **kwargs)

        if res is not None:
            return res

        err = self.last_error()
        self.error = Error(*err)

        if self.error.is_connection_error() and retries > 0:
            self.initialize()
            self.login()
            return self._handler(api, retries=retries - 1)
        else:
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
        """Retrieves the last error information from the MetaTrader terminal.

        Returns:
            tuple[int, str]: A tuple containing the error code and error
                description. Returns (-1, error_message) if an exception
                occurs while retrieving the error.
        """
        try:
            return self._last_error()
        except Exception as err:
            logger.warning("%s: Error in obtaining last error.", err)
            return -1, str(err)

    def version(self) -> tuple[int, int, str] | None:
        """Retrieves the MetaTrader terminal version information.

        Returns:
            tuple[int, int, str] | None: A tuple containing (version, build,
                release_date) if successful, None otherwise.
        """
        api = {"func": self._version, "error_msg": "Error in obtaining version."}
        return self._handler(api)

    def account_info(self) -> AccountInfo | None:
        """Retrieves information about the current trading account.

        Returns:
            AccountInfo | None: An AccountInfo object containing account
                details if successful, None otherwise.
        """
        api = {"func": self._account_info, "error_msg": "Error in obtaining account information"}
        return self._handler(api)

    def terminal_info(self) -> TerminalInfo | None:
        """Retrieves information about the MetaTrader terminal.

        Returns:
            TerminalInfo | None: A TerminalInfo object containing terminal
                details if successful, None otherwise.
        """
        api = {"func": self._terminal_info, "error_msg": "Error in obtaining terminal information"}
        return self._handler(api)

    def symbols_total(self) -> int:
        """Retrieves the total number of financial symbols available.

        Returns:
            int: The total number of symbols available in the terminal.
        """
        api = {"func": self._symbols_total, "error_msg": "Error in obtaining total symbols."}
        return self._handler(api)

    def symbols_get(self, group: str = "") -> tuple[SymbolInfo] | None:
        """Retrieves all financial symbols or symbols matching a filter.

        Args:
            group: A filter for selecting symbols by group name. Supports
                wildcards (*) and exclusions (!). Defaults to empty string
                which returns all symbols.

        Returns:
            tuple[SymbolInfo] | None: A tuple of SymbolInfo objects if
                successful, None otherwise.
        """
        kwargs = {"group": group} if group else {}
        api = {"func": self._symbols_get, "kwargs": kwargs, "error_msg": "Error in obtaining symbols."}
        return self._handler(api)

    def symbol_info(self, symbol: str) -> SymbolInfo | None:
        """Retrieves information about a specific financial symbol.

        Args:
            symbol: The name of the financial symbol.

        Returns:
            SymbolInfo | None: A SymbolInfo object containing symbol details
                if successful, None otherwise.
        """
        api = {
            "func": self._symbol_info,
            "args": (symbol,),
            "error_msg": f"Error in obtaining information for {symbol}",
        }
        return self._handler(api)

    def symbol_info_tick(self, symbol: str) -> Tick | None:
        """Retrieves the last tick data for a specified symbol.

        Args:
            symbol: The name of the financial symbol.

        Returns:
            Tick | None: A Tick object containing the last tick data
                if successful, None otherwise.
        """
        api = {"func": self._symbol_info_tick, "args": (symbol,), "error_msg": f"Error in obtaining tick for {symbol}"}
        return self._handler(api)

    def symbol_select(self, symbol: str, enable: bool) -> bool:
        """Selects or removes a symbol from the MarketWatch window.

        Args:
            symbol: The name of the financial symbol.
            enable: If True, the symbol is selected in MarketWatch.
                If False, the symbol is removed.

        Returns:
            bool: True if successful, False otherwise.
        """
        api = {"func": self._symbol_select, "args": (symbol, enable), "error_msg": f"Error in selecting {symbol}"}
        return self._handler(api)

    def market_book_add(self, symbol: str) -> bool:
        """Subscribes to the market depth (order book) for a symbol.

        Args:
            symbol: The name of the financial symbol.

        Returns:
            bool: True if subscription was successful, False otherwise.
        """
        api = {
            "func": self._market_book_add,
            "args": (symbol,),
            "error_msg": f"Error in adding {symbol} to market book",
        }
        return self._handler(api)

    def market_book_get(self, symbol: str) -> tuple[BookInfo] | None:
        """Retrieves the market depth (order book) data for a symbol.

        The symbol must first be subscribed using market_book_add().

        Args:
            symbol: The name of the financial symbol.

        Returns:
            tuple[BookInfo] | None: A tuple of BookInfo objects representing
                the order book entries if successful, None otherwise.
        """
        api = {
            "func": self._market_book_get,
            "args": (symbol,),
            "error_msg": f"Error in obtaining market depth for {symbol}",
        }
        return self._handler(api)

    def market_book_release(self, symbol: str) -> bool:
        """Unsubscribes from the market depth (order book) for a symbol.

        Args:
            symbol: The name of the financial symbol.

        Returns:
            bool: True if unsubscription was successful, False otherwise.
        """
        api = {
            "func": self._market_book_release,
            "args": (symbol,),
            "error_msg": f"Error in releasing market depth for {symbol}",
        }
        return self._handler(api)

    def copy_rates_from(
        self, symbol: str, timeframe: int, date_from: datetime | float, count: int
    ) -> np.ndarray | None:
        """Copies price history (bars/candles) starting from a specified date.

        Args:
            symbol: The name of the financial symbol.
            timeframe: The chart timeframe as a TIMEFRAME constant.
            date_from: The starting date for the data request. Can be a
                datetime object or a Unix timestamp.
            count: The number of bars to retrieve.

        Returns:
            np.ndarray | None: A numpy array with columns (time, open, high,
                low, close, tick_volume, spread, real_volume) if successful,
                None otherwise.
        """
        api = {
            "func": self._copy_rates_from,
            "args": (symbol, timeframe, date_from, count),
            "error_msg": f"Error in obtaining rates for {symbol}",
        }
        return self._handler(api)

    def copy_rates_from_pos(self, symbol: str, timeframe: int, start_pos: int, count: int) -> np.ndarray | None:
        """Copies price history (bars/candles) starting from a specified index.

        Args:
            symbol: The name of the financial symbol.
            timeframe: The chart timeframe as a TIMEFRAME constant.
            start_pos: The starting index position (0 is the current bar).
            count: The number of bars to retrieve.

        Returns:
            np.ndarray | None: A numpy array with columns (time, open, high,
                low, close, tick_volume, spread, real_volume) if successful,
                None otherwise.
        """
        api = {
            "func": self._copy_rates_from_pos,
            "args": (symbol, timeframe, start_pos, count),
            "error_msg": f"Error in obtaining rates for {symbol}",
        }
        return self._handler(api)

    def copy_rates_range(
        self, symbol: str, timeframe: int, date_from: datetime | float, date_to: datetime | float
    ) -> np.ndarray | None:
        """Copies price history (bars/candles) within a specified date range.

        Args:
            symbol: The name of the financial symbol.
            timeframe: The chart timeframe as a TIMEFRAME constant.
            date_from: The starting date. Can be a datetime object or
                Unix timestamp.
            date_to: The ending date. Can be a datetime object or
                Unix timestamp.

        Returns:
            np.ndarray | None: A numpy array with columns (time, open, high,
                low, close, tick_volume, spread, real_volume) if successful,
                None otherwise.
        """
        api = {
            "func": self._copy_rates_range,
            "args": (symbol, timeframe, date_from, date_to),
            "error_msg": f"Error in obtaining rates for {symbol}",
        }
        return self._handler(api)

    def copy_ticks_from(
        self, symbol: str, date_from: datetime | float, count: int, flags: CopyTicks
    ) -> np.ndarray | None:
        """Copies tick data starting from a specified date.

        Args:
            symbol: The name of the financial symbol.
            date_from: The starting date. Can be a datetime object or
                Unix timestamp.
            count: The number of ticks to retrieve.
            flags: A CopyTicks flag specifying the type of ticks to copy
                (ALL, INFO, or TRADE).

        Returns:
            np.ndarray | None: A numpy array with tick data if successful,
                None otherwise.
        """
        api = {
            "func": self._copy_ticks_from,
            "args": (symbol, date_from, count, flags),
            "error_msg": f"Error in obtaining ticks for {symbol}",
        }
        return self._handler(api)

    def copy_ticks_range(
        self, symbol: str, date_from: datetime | float, date_to: datetime | float, flags: CopyTicks
    ) -> np.ndarray | None:
        """Copies tick data within a specified date range.

        Args:
            symbol: The name of the financial symbol.
            date_from: The starting date. Can be a datetime object or
                Unix timestamp.
            date_to: The ending date. Can be a datetime object or
                Unix timestamp.
            flags: A CopyTicks flag specifying the type of ticks to copy
                (ALL, INFO, or TRADE).

        Returns:
            np.ndarray | None: A numpy array with tick data if successful,
                None otherwise.
        """
        api = {
            "func": self._copy_ticks_range,
            "args": (symbol, date_from, date_to, flags),
            "error_msg": f"Error in obtaining ticks for {symbol}",
        }
        return self._handler(api)

    def orders_total(self) -> int:
        """Retrieves the total number of active pending orders.

        Returns:
            int: The total number of active pending orders.
        """
        api = {"func": self._orders_total, "error_msg": "Error in obtaining total orders."}
        return self._handler(api)

    def orders_get(self, group: str = "", ticket: int = 0, symbol: str = "") -> tuple[TradeOrder] | None:
        """Retrieves active pending orders with optional filtering.

        Args:
            group: A filter for symbols by group name. Supports wildcards (*)
                and exclusions (!). Defaults to empty string.
            ticket: Order ticket number to filter by. Defaults to 0.
            symbol: Symbol name to filter by. Defaults to empty string.

        Returns:
            tuple[TradeOrder] | None: A tuple of TradeOrder objects if
                successful, None otherwise.
        """
        kwargs = {key: value for key, value in (("group", group), ("ticket", ticket), ("symbol", symbol)) if value}
        api = {"func": self._orders_get, "kwargs": kwargs, "error_msg": "Error in obtaining orders."}
        return self._handler(api)

    def order_calc_margin(
        self, action: Literal[OrderType.BUY, OrderType.SELL], symbol: str, volume: float, price: float
    ) -> float | None:
        """Calculates the margin required for a specified order.

        Args:
            action: The order type (OrderType.BUY or OrderType.SELL).
            symbol: The name of the financial symbol.
            volume: The trade volume in lots.
            price: The open price.

        Returns:
            float | None: The required margin in the account currency if
                successful, None otherwise.
        """
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
        """Calculates the profit/loss for a specified order.

        Args:
            action: The order type (OrderType.BUY or OrderType.SELL).
            symbol: The name of the financial symbol.
            volume: The trade volume in lots.
            price_open: The open price.
            price_close: The close price.

        Returns:
            float | None: The calculated profit/loss in the account currency
                if successful, None otherwise.
        """
        api = {
            "func": self._order_calc_profit,
            "args": (action, symbol, volume, price_open, price_close),
            "error_msg": "Error in calculating profit.",
        }
        return self._handler(api)

    def order_check(self, request: dict) -> OrderCheckResult:
        """Checks if the funds are sufficient for a specified order.

        Args:
            request: A dictionary containing the order parameters. Required
                keys include action, symbol, volume, type, price, etc.

        Returns:
            OrderCheckResult: The result of the order check containing
                information about margin, balance, and trade validity.
        """
        comment = request.get("comment")
        if comment is not None and len(comment) > 25:
            request["comment"] = comment[:25]
            logger.warning("order comment length exceeds 25 characters.")
        api = {"func": self._order_check, "args": (request,), "error_msg": "Error in checking order."}
        return self._handler(api)

    def order_send(self, request: dict) -> OrderSendResult:
        """Sends a trade request to the MetaTrader terminal.

        Args:
            request: A dictionary containing the trade request parameters.
                Required keys include action, symbol, volume, type, price, etc.

        Returns:
            OrderSendResult: The result of the trade request containing
                the order ticket, deal ticket, and execution details.
        """
        comment = request.get("comment")
        if comment is not None and len(comment) > 25:
            request["comment"] = comment[:25]
            logger.warning("order comment length exceeds 25 characters.")
        api = {"func": self._order_send, "args": (request,), "error_msg": "Error in sending order."}
        return self._handler(api)

    def positions_total(self) -> int:
        """Retrieves the total number of open positions.

        Returns:
            int: The total number of open positions.
        """
        api = {"func": self._positions_total, "error_msg": "Error in obtaining total positions."}
        return self._handler(api)

    def positions_get(self, group: str = "", ticket: int = None, symbol: str = "") -> tuple[TradePosition] | None:
        """Retrieves open positions with optional filtering.

        Args:
            group: A filter for symbols by group name. Supports wildcards (*)
                and exclusions (!). Defaults to empty string.
            ticket: Position ticket number to filter by. Defaults to None.
            symbol: Symbol name to filter by. Defaults to empty string.

        Returns:
            tuple[TradePosition] | None: A tuple of TradePosition objects if
                successful, None otherwise.
        """
        kwargs = {key: value for key, value in (("group", group), ("ticket", ticket), ("symbol", symbol)) if value}
        api = {"func": self._positions_get, "kwargs": kwargs, "error_msg": "Error in obtaining open positions."}
        return self._handler(api)

    def history_orders_total(self, date_from: datetime | float, date_to: datetime | float) -> int:
        """Retrieves the total number of orders in trading history.

        Args:
            date_from: The starting date. Can be a datetime object or
                Unix timestamp.
            date_to: The ending date. Can be a datetime object or
                Unix timestamp.

        Returns:
            int: The total number of orders in the specified date range.
        """
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
        """Retrieves orders from trading history with optional filtering.

        Args:
            date_from: The starting date. Can be a datetime object or
                Unix timestamp. Defaults to None.
            date_to: The ending date. Can be a datetime object or
                Unix timestamp. Defaults to None.
            group: A filter for symbols by group name. Supports wildcards (*)
                and exclusions (!). Defaults to empty string.
            ticket: Order ticket number to filter by. Defaults to None.
            position: Position identifier to filter by. Defaults to None.

        Returns:
            tuple[TradeOrder] | None: A tuple of TradeOrder objects if
                successful, None otherwise.
        """
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
        """Retrieves the total number of deals in trading history.

        Args:
            date_from: The starting date. Can be a datetime object or
                Unix timestamp.
            date_to: The ending date. Can be a datetime object or
                Unix timestamp.

        Returns:
            int: The total number of deals in the specified date range.
        """
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
        """Retrieves deals from trading history with optional filtering.

        Args:
            date_from: The starting date. Can be a datetime object or
                Unix timestamp. Defaults to None.
            date_to: The ending date. Can be a datetime object or
                Unix timestamp. Defaults to None.
            group: A filter for symbols by group name. Supports wildcards (*)
                and exclusions (!). Defaults to empty string.
            ticket: Deal ticket number to filter by. Defaults to None.
            position: Position identifier to filter by. Defaults to None.

        Returns:
            tuple[TradeDeal] | None: A tuple of TradeDeal objects if
                successful, None otherwise.
        """
        kwargs = {key: value for key, value in (("group", group), ("ticket", ticket), ("position", position)) if value}
        args = tuple(arg for arg in (date_from, date_to) if arg)
        api = {
            "func": self._history_deals_get,
            "args": args,
            "kwargs": kwargs,
            "error_msg": "Error in obtaining history deals",
        }
        return self._handler(api)
