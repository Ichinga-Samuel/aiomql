"""Symbol class for handling a financial instrument."""
from datetime import datetime
from logging import getLogger
from math import log10, ceil

from .core.constants import TimeFrame, CopyTicks
from .core.models import SymbolInfo, BookInfo
from .ticks import Tick
from .account import Account
from .candle import Candles
from .ticks import Ticks

logger = getLogger(__name__)


class Symbol(SymbolInfo):
    """Main class for handling a financial instrument. A subclass of SymbolInfo and Base it has attributes and methods
    for working with a financial instrument.

    Attributes:
        tick (Tick): Price tick object for instrument
        account: An instance of the current trading account

    Notes:
        Full properties are on the SymbolInfo Object.
        Make sure Symbol is always initialized with a name argument
    """
    tick: Tick
    account = Account()

    @property
    def pip(self):
        """Returns the pip value of the symbol. This is ten times the point value for forex symbols.

        Returns:
            float: The pip value of the symbol.
        """
        return self.point * 10

    async def info_tick(self, *, name: str = "") -> Tick:
        """Get the current price tick of a financial instrument.

        Args:
            name: if name is supplied get price tick of that financial instrument

        Returns:
            Tick: Return a Tick Object

        Raises:
            ValueError: If request was unsuccessful and None was returned
        """
        tick = await self.mt5.symbol_info_tick(name or self.name)
        if tick is None:
            raise ValueError(f'Could not get tick for {name or self.name}')
        tick = Tick(**tick._asdict())
        setattr(self, 'tick', tick) if not name else ...
        return tick

    async def symbol_select(self, *, enable: bool = True) -> bool:
        """Select a symbol in the MarketWatch window or remove a symbol from the window.
        Update the select property

        Args:
            enable (bool): Switch. Optional unnamed parameter. If 'false', a symbol should be removed from
             the MarketWatch window.

        Returns:
            bool: True if successful, otherwise – False.
        """
        self.select = await self.mt5.symbol_select(self.name, enable)
        return self.select

    async def info(self) -> SymbolInfo:
        """Get data on the specified financial instrument and update the symbol object properties

        Returns:
            (SymbolInfo): SymbolInfo if successful

        Raises:
            ValueError: If request was unsuccessful and None was returned
        """
        
        info = await self.mt5.symbol_info(self.name)
        if info:
            self.set_attributes(**info._asdict())
            return SymbolInfo(**info._asdict())
        raise ValueError(f'Could not get info for {self.name}')

    async def init(self) -> bool:
        """Initialized the symbol by pulling properties from the terminal

        Returns:
             bool: Returns True if symbol info was successful initialized
        """
        try:
            if await self.symbol_select():
                await self.book_add()
                await self.info()
                return True
            logger.warning(f'Unable to initialized symbol {self}')
            return False
        except Exception as err:
            self.select = False
            logger.warning(err)
            return False

    async def book_add(self) -> bool:
        """Subscribes the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.
        If the symbol is not in the list of instruments for the market, This method will return False

        Returns:
             bool: True if successful, otherwise – False.
        """
        return await self.mt5.market_book_add(self.name)

    async def book_get(self) -> tuple[BookInfo]:
        """Returns a tuple of BookInfo featuring Market Depth entries for the specified symbol.

        Returns:
            tuple[BookInfo]: Returns the Market Depth contents as a tuples of BookInfo Objects

        Raises:
            ValueError: If request was unsuccessful and None was returned
        """
        infos = await self.mt5.market_book_get(self.name)
        if infos is None:
            raise ValueError(f'Could not get book info for {self.name}')
        book_infos = (BookInfo(**info._asdict()) for info in infos)
        return tuple(book_infos)

    async def book_release(self) -> bool:
        """Cancels subscription of the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.

        Returns:
            bool: True if successful, otherwise – False.
        """
        return await self.mt5.market_book_release(self.name)

    def check_volume(self, volume) -> tuple[bool, float]:
        check = self.volume_min <= volume <= self.volume_max
        if check:
            return check, volume
        if not check and volume < self.volume_min:
            return check, self.volume_min
        else:
            return check, self.volume_max

    def round_off_volume(self, volume):
        step = ceil(abs(log10(self.volume_step)))
        return round(volume, step)

    async def compute_volume(self, *, amount: float, pips: float, use_limits: bool = False) -> float:
        """Computes the volume of a trade based on the amount and the number of pips to target.
        This is a dummy method that returns the minimum volume of the symbol. It is meant to be overridden by a subclass
        that implements the computation of volume.

        Args:
            amount (float): Amount to risk in the trade
            pips (float): Number of pips to target
            use_limits (bool): If True, the computed volume is rounded to the nearest step and checked against

        Returns:
            float: Returns the volume of the trade
        """
        return self.volume_min

    async def currency_conversion(self, *, amount: float, base: str, quote: str) -> float:
        """Convert from one currency to the other.

        Args:
            amount: amount to convert given in terms of the quote currency
            base: The base currency of the pair
            quote: The quote currency of the pair

        Returns:
            float: Amount in terms of the base currency or None if it failed to convert

        Raises:
            ValueError: If conversion is impossible
        """
        try:
            pair = f'{base}{quote}'
            if self.account.has_symbol(pair):
                tick = await self.info_tick(name=pair)
                if tick is not None:
                    return amount / tick.ask

            pair = f'{quote}{base}'
            if self.account.has_symbol(pair):
                tick = await self.info_tick(name=pair)
                if tick is not None:
                    amount = amount * tick.bid
                    return amount
        except Exception as err:
            logger.warning(f'Currency conversion failed: Unable to convert {amount} in {quote} to {base}')
            raise ValueError(f'Currency Conversion Failed: {err}')
        else:
            logger.warning(f'Currency conversion failed: Unable to convert {amount} in {quote} to {base}')

    async def copy_rates_from(self, *, timeframe: TimeFrame, date_from: datetime | int, count: int = 500) -> Candles:
        """
        Get bars from the MetaTrader 5 terminal starting from the specified date.

        Args:
            timeframe (TimeFrame): Timeframe the bars are requested for. Set by a value from the TimeFrame enumeration. Required unnamed parameter.

            date_from (datetime | int): Date of opening of the first bar from the requested sample. Set by the 'datetime' object or as a number
                of seconds elapsed since 1970.01.01. Required unnamed parameter.

            count (int): Number of bars to receive. Required unnamed parameter.

        Returns:
            Candles: Returns a Candles object as a collection of rates ordered chronologically

        Raises:
            ValueError: If request was unsuccessful and None was returned
        """
        rates = await self.mt5.copy_rates_from(self.name, timeframe, date_from, count)
        if rates is not None:
            return Candles(data=rates)
        raise ValueError(f'Could not get rates for {self.name}')

    async def copy_rates_from_pos(self, *,timeframe: TimeFrame, count: int = 500, start_position: int = 0) -> Candles:
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
        rates = await self.mt5.copy_rates_from_pos(self.name, timeframe, start_position, count)
        if rates is not None:
            return Candles(data=rates)
        raise ValueError(f'Could not get rates for {self.name}')

    async def copy_rates_range(self, *, timeframe: TimeFrame, date_from: datetime | int,
                               date_to: datetime | int) -> Candles:
        """Get bars in the specified date range from the MetaTrader 5 terminal.

        Args:
            timeframe (TimeFrame): Timeframe for the bars using the TimeFrame enumeration. Required unnamed parameter.

            date_from (datetime | int): Date the bars are requested from. Set by the 'datetime' object or as a number of seconds
                elapsed since 1970.01.01. Bars with the open time >= date_from are returned. Required unnamed parameter.

            date_to (datetime | int): Date, up to which the bars are requested. Set by the 'datetime' object or as a number of
                seconds elapsed since 1970.01.01. Bars with the open time <= date_to are returned. Required unnamed parameter.

        Returns:
           Candles: Returns a Candles object as a collection of rates ordered chronologically.

        Raises:
            ValueError: If request was unsuccessful and None was returned
        """
        rates = await self.mt5.copy_rates_range(symbol=self.name, timeframe=timeframe, date_from=date_from,
                                                date_to=date_to)
        if rates is not None:
            return Candles(data=rates)
        raise ValueError(f'Could not get rates for {self.name}')

    async def copy_ticks_from(self, *, date_from: datetime | int, count: int = 100, flags: CopyTicks = CopyTicks.ALL) -> Ticks:
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
        ticks = await self.mt5.copy_ticks_from(self.name, date_from, count, flags)
        if ticks is not None:
            return Ticks(data=ticks)
        raise ValueError(f'Could not get ticks for {self.name}')

    async def copy_ticks_range(self, *, date_from: datetime | int, date_to: datetime | int, flags: CopyTicks = CopyTicks.ALL) -> Ticks:
        """Get ticks for the specified date range from the MetaTrader 5 terminal.

        Args:
            date_from: Date the bars are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Bars with
                the open time >= date_from are returned. Required unnamed parameter.

            date_to: Date, up to which the bars are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Bars
                with the open time <= date_to are returned. Required unnamed parameter.
                
            flags (CopyTicks):

        Returns:
            Candles: Returns a Candles object as a collection of ticks ordered chronologically.

        Raises:
            ValueError: If request was unsuccessful and None was returned.
        """
        ticks = await self.mt5.copy_ticks_range(self.name, date_from, date_to, flags)
        if ticks is not None:
            return Ticks(data=ticks)
        raise ValueError(f'Could not get ticks for {self.name}')
