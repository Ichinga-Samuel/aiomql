"""Synchronous Symbol module for handling financial instruments.

This module provides the synchronous Symbol class for interacting with trading
instruments in MetaTrader 5 without async/await. It includes methods for retrieving
market data, ticks, rates, and symbol information.

Example:
    Working with a symbol synchronously::

        symbol = Symbol(name='EURUSD')
        symbol.initialize()
        tick = symbol.info_tick()
        candles = symbol.copy_rates_from_pos(timeframe=TimeFrame.H1, count=100)
"""

from datetime import datetime
from logging import getLogger
from ...core.constants import TimeFrame, CopyTicks
from ...core.base import _Base
from ...core.models import SymbolInfo, BookInfo
from ...utils import round_off
from ..ticks import Tick
from ..account import Account
from ..candle import Candles
from ..ticks import Ticks

logger = getLogger(__name__)


class Symbol(_Base, SymbolInfo):
    """Main class for handling a financial instrument. A subclass of SymbolInfo it has attributes and methods
    for working with a financial instrument.

    Attributes:
        tick (Tick): Price tick object for instrument
        account: An instance of the current trading account

    Notes:
        Full properties are on the SymbolInfo Object.
        Make sure a Symbol is always initialized with a name argument
    """
    initialized: bool
    tick: Tick
    account: Account
    mode: str = "sync"

    def __init__(self, **kwargs):
        """Initialize the Symbol object with the name of the financial instrument.

        Args:
            name (str): Name of the financial instrument
        """
        assert "name" in kwargs, "Symbol Object Must be initialized with a name"
        super().__init__(**kwargs)
        self.account = Account()
        self.initialized = False

    def info_tick(self, *, name: str = "") -> Tick | None:
        """Get the current price tick of a financial instrument.

        Args:
            name: if name is supplied, get price tick of that financial instrument. Optional unnamed parameter.

        Returns:
            Tick: Return a Tick Object
            None: If request was unsuccessful
        """
        try:
            if not name:
                tick = self.mt5.symbol_info_tick(self.name)
            else:
                self.mt5.symbol_select(name, True)
                self.mt5.market_book_add(name)
                tick = self.mt5.symbol_info_tick(name)
            if tick is not None:
                tick = Tick(**tick._asdict())
                setattr(self, "tick", tick) if not name else ...
            return tick
        except Exception as err:
            logger.warning("%s: Unable to get tick for %s", err, self.name)
            return None

    def symbol_select(self, *, enable: bool = True) -> bool:
        """Select a symbol in the MarketWatch window or remove a symbol from the window.
        Update the select property

        Args:
            enable (bool): Switch. Optional unnamed parameter. If 'false', a symbol should be removed from
             the MarketWatch window.

        Returns:
            bool: True if successful, otherwise – False.
        """
        self.select = self.mt5.symbol_select(self.name, enable)
        return self.select

    def info(self) -> SymbolInfo | None:
        """Get data on the specified financial instrument and update the symbol object properties

        Returns:
            (SymbolInfo): SymbolInfo if successful
            (None): If request was unsuccessful
        """
        info = self.mt5.symbol_info(self.name)
        if info is not None:
            info = info._asdict()
            self.set_attributes(**info)
            return SymbolInfo(**info)
        return None

    def initialize(self) -> bool:
        """Initialize the symbol by pulling properties from the terminal

        Returns:
             bool: Returns True if symbol info was successfully initialized
        """
        try:
            select = self.mt5.symbol_select(self.name, True)
            self.select = select

            self.mt5.market_book_add(self.name)

            info = self.mt5.symbol_info(self.name)
            if info is not None:
                self.set_attributes(**info._asdict())

            info_tick = self.mt5.symbol_info_tick(self.name)

            if info_tick:
                self.tick = Tick(**info_tick._asdict())

            if info is not None and info_tick is not None:
                self.initialized = True
                return True

            logger.warning("Unable to initialize %s", self.name)
            return False
        except Exception as err:
            logger.warning("%s: Unable to initialize %s", err, self.name)
            return False

    def initialize_sync(self) -> bool:
        """Synchronous version of the initialize method"""
        try:
            select = self.mt5._symbol_select(self.name, True)
            self.select = select

            self.mt5._market_book_add(self.name)

            info = self.mt5._symbol_info(self.name)
            if info is not None:
                self.set_attributes(**info._asdict())

            info_tick = self.mt5._symbol_info_tick(self.name)
            if info_tick:
                self.tick = Tick(**info_tick._asdict())

            if info is not None and info_tick is not None:
                self.initialized = True
                return True
            logger.warning("Unable to initialize %s", self.name)
            return False
        except Exception as err:
            logger.warning("%s: Unable to initialize %s", err, self.name)
            return False

    def book_add(self) -> bool:
        """Subscribes the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.
        If the symbol is not in the list of instruments for the market, This method will return False

        Returns:
             bool: True if successful, otherwise – False.
        """
        res = self.mt5.market_book_add(self.name)
        if res is False:
            logger.debug("Could not add %s to market book", self.name)
        return res

    def book_get(self) -> tuple[BookInfo, ...]:
        """Returns a tuple of BookInfo featuring Market Depth entries for the specified symbol.

        Returns:
            tuple[BookInfo]: Returns the Market Depth contents as a tuples of BookInfo Objects
        """
        book_info = self.mt5.market_book_get(self.name)

        if book_info is not None:
            book_infos = (BookInfo(**info._asdict()) for info in book_info)
            return tuple(book_infos)

        raise ValueError(f"Could not get book info for {self.name}")

    def book_release(self) -> bool:
        """Cancels subscription of the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.

        Returns:
            bool: True if successful, otherwise – False.
        """
        return self.mt5.market_book_release(self.name)

    def check_volume(self, *, volume: float) -> tuple[bool, float]:
        """Check if the volume is within the limits of the symbol. If not, return the nearest limit.

        Args:
            volume (float): Volume to check

        Returns: tuple[bool, float]: Returns a tuple of a boolean and a float. The boolean indicates if the volume is
        within the limits of the symbol. The float is the volume to use if the volume is not within the limits of the
        symbol.
        """
        if check := self.volume_min <= volume <= self.volume_max:
            return check, volume
        else:
            return check, self.volume_min if volume <= self.volume_min else self.volume_max

    def round_off_volume(self, *, volume: float, round_down: bool = False) -> float:
        """Round off the volume to the nearest volume step.

        Args:
            volume (float): Volume to round off
            round_down (bool): If True, round down. If False, round up. Optional unnamed parameter. Defaults to True.

        Returns:
            float: Rounded off volume
        """
        return round_off(value=volume, step=self.volume_step, round_down=round_down)

    def amount_in_quote_currency(self, *, amount: float) -> float:
        """Convert the amount to the quote currency of the symbol."""
        if self.currency_profit != self.account.currency:
            amount = self.convert_currency(
                amount=amount, from_currency=self.account.currency, to_currency=self.currency_profit
            )
        return amount

    def compute_volume(self) -> float:
        """Computes the volume required for a trade usually based on the amount and any other keyword arguments.
        This is a dummy method that returns the minimum volume of the symbol. It is meant to be overridden by a subclass
        that implements the computation of volume.

        Returns:
            float: Returns the volume of the trade
        """
        return self.volume_min

    def convert_currency(self, *, amount: float, from_currency: str, to_currency: str) -> float | None:
        """Convert a given amount from one currency to the other.
        Args:
            amount: Amount to convert
            from_currency: Currency to convert from
            to_currency: Currency to convert to
        """
        base, quote = to_currency, from_currency
        try:
            pair = f"{quote}{base}"
            tick = self.info_tick(name=pair)
            if tick is not None:
                return round(amount * tick.bid, 2)

            pair = f"{base}{quote}"
            tick = self.info_tick(name=pair)
            return round(amount / tick.ask, 2)
        except Exception as err:
            logger.warning(f"{err}: Currency conversion failed: Unable to convert {amount} in {quote} to {base}")
            return None

    def copy_rates_from(self, *, timeframe: TimeFrame, date_from: datetime | int, count: int = 500) -> Candles:
        """
        Get bars from the MetaTrader 5 terminal starting from the specified date.

        Args: timeframe (TimeFrame): Timeframe the bars are requested for. Set by a value from the TimeFrame
        enumeration. Required unnamed parameter.

            date_from (datetime | int): Date of opening of the first bar from the requested sample. Set by the
            'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter.

            count (int): Number of bars to receive. Required unnamed parameter.

        Returns:
            Candles: Returns a Candles object as a collection of rates ordered chronologically

        Raises:
            ValueError: If request was unsuccessful and None was returned
        """
        rates = self.mt5.copy_rates_from(self.name, timeframe, date_from, count)
        if rates is not None:
            return Candles(data=rates)
        raise ValueError(f"Could not get rates for {self.name}.")

    def copy_rates_from_pos(self, *, timeframe: TimeFrame, count: int = 500, start_position: int = 0) -> Candles:
        """Get bars from the MetaTrader 5 terminal starting from the specified index.

        Args:
            timeframe (TimeFrame): TimeFrame value from TimeFrame Enum. Required keyword only parameter

            count (int): Number of bars to return. Keyword argument defaults to 500

            start_position (int): Initial index of the bar the data are requested from. The numbering of bars goes from
             present to past. Thus, the zero bar means the current one. Keyword argument defaults to 0.

        Returns:
             Candles: Returns a Candles object as a collection of rates ordered chronologically.

        Raises:
            ValueError: If request was unsuccessful and None was returned
        """
        rates = self.mt5.copy_rates_from_pos(self.name, timeframe, start_position, count)
        if rates is not None:
            return Candles(data=rates)
        raise ValueError(f"Could not get rates for {self.name}.")

    def copy_rates_range(
        self, *, timeframe: TimeFrame, date_from: datetime | int, date_to: datetime | int
    ) -> Candles:
        """Get bars in the specified date range from the MetaTrader 5 terminal.

        Args:
            timeframe (TimeFrame): Timeframe for the bars using the TimeFrame enumeration. Required unnamed parameter.

            date_from (datetime | int): Date the bars are requested from. Set by the 'datetime' object or as a number
             of seconds elapsed since 1970.01.01. Bars with the open time >= date_from are returned. Required unnamed
              parameter.

            date_to (datetime | int): Date, up to which the bars are requested. Set by the 'datetime' object or as a
             number of seconds elapsed since 1970.01.01. Bars with the open time <= date_to are returned.
              Required unnamed parameter.

        Returns:
           Candles: Returns a Candles object as a collection of rates ordered chronologically.

        Raises:
            ValueError: If request was unsuccessful and None was returned
        """
        rates = self.mt5.copy_rates_range(
            symbol=self.name, timeframe=timeframe, date_from=date_from, date_to=date_to
        )
        if rates is not None:
            return Candles(data=rates)
        raise ValueError(f"Could not get rates for {self.name}.")

    def copy_ticks_from(self, *, date_from: datetime | int, count: int = 100,
                              flags: CopyTicks = CopyTicks.ALL) -> Ticks:
        """
        Get ticks from the MetaTrader 5 terminal starting from the specified date.

        Args: date_from (datetime | int): Date the ticks are requested from. Set by the 'datetime' object or as a
        number of seconds elapsed since 1970.01.01.

            count (int): Number of requested ticks. Defaults to 100

            flags (CopyTicks): A flag to define the type of the requested ticks from CopyTicks enum. INFO is the default

        Returns:
             Candles: Returns a Candles object as a collection of ticks ordered chronologically.

        Raises:
            ValueError: If request was unsuccessful and None was returned
        """
        ticks = self.mt5.copy_ticks_from(self.name, date_from, count, flags)
        if ticks is not None:
            return Ticks(data=ticks)
        raise ValueError(f"Could not get ticks for {self.name}.")

    def copy_ticks_range(
        self, *, date_from: datetime | int, date_to: datetime | int, flags: CopyTicks = CopyTicks.ALL
    ) -> Ticks:
        """Get ticks for the specified date range from the MetaTrader 5 terminal.

        Args:
            date_from: Date the bars are requested from. Set by the 'datetime' object or as a number of seconds elapsed
             since 1970.01.01. Bars with the open time >= date_from are returned. Required unnamed parameter.

            date_to: Date, up to which the bars are requested. Set by the 'datetime' object or as a number of
             seconds elapsed since 1970.01.01. Bars with the open time <= date_to are returned.
              Required unnamed parameter.

            flags (CopyTicks):

        Returns:
            Candles: Returns a Candles object as a collection of ticks ordered chronologically.

        Raises:
            ValueError: If request was unsuccessful and None was returned.
        """
        ticks = self.mt5.copy_ticks_range(self.name, date_from, date_to, flags)
        if ticks is not None:
            return Ticks(data=ticks)
        raise ValueError(f"Could not get ticks for {self.name}.")
