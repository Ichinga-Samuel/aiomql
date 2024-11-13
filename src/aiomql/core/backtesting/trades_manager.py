from datetime import datetime
from typing import TypeVar, Generic
from logging import getLogger

from MetaTrader5 import TradePosition, TradeOrder, TradeDeal

logger = getLogger(__name__)

TradeData = TypeVar("TradeData", bound=TradePosition | TradeOrder | TradeDeal)


class TradeManager(Generic[TradeData]):
    """A generic class to manage trades data during a backtest. It is the parent class of the
     PositionsManager, OrdersManager, and DealsManager. It implements some dict-like methods to manage the data.
     It has a private attribute _data to store the data. It exposes the data through the values, keys, and items methods.
    It also has a to_dict method to convert the data to a dictionary.

    Attributes:
        _data (dict[int, TradeData]): The data to store the trades.

    Examples:
        >>> manager = TradeManager()
        >>> manager[123456] = TradePosition(ticket=123456, symbol="EURUSD", volume=0.1)
        >>> manager.update(ticket=123456, symbol="EURUSD", volume=0.1)
        >>> manager[123456]
        TradePosition(ticket=123456, symbol='EURUSD', volume=0.1)
        >>> manager.values()
        (TradePosition(ticket=123456, symbol='EURUSD', volume=0.1),)
        >>> manager.keys()
        (123456,)
        >>> manager.items()
        ((123456, TradePosition(ticket=123456, symbol='EURUSD', volume=0.1)),)
        >>> manager.to_dict()
        {123456: {'ticket': 123456, 'symbol': 'EURUSD', 'volume': 0.1}}
        >>> pos = manager.get(123456)
        >>> pos
        TradePosition(ticket=123456, symbol='EURUSD', volume=0.1)
        >>> pos in manager
        True
        >>> len(manager)
        1
        >>> pos in manager
        False
    """
    _data: dict[int, TradeData]

    def __init__(self, *, data: dict = None):
        self._data = data or {}

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __contains__(self, item: TradeData):
        return item.ticket in self._data

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value: TradeData):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def get(self, key, default=None) -> TradeData | None:
        return self._data.get(key, default)

    def update(self, *, ticket: int, **kwargs):
        """Update the data of a trade. Given the ticket of the trade and the new data to update.

        Args:
            ticket (int): The ticket of the trade to update.
            **kwargs: The new data to update.
        """
        try:
            res = self[ticket]
            klass = type(res)
            res = res._asdict()
            res.update(**kwargs)
            res = klass(res.get(v) for v in klass.__match_args__)
            self[res.ticket] = res
            return res
        except KeyError:
            logger.error(f"Update Operation Failed: Could Not Find Ticket")

    def values(self) -> tuple[TradeData, ...]:
        """Returns the values of the data."""
        return tuple(value for value in self._data.values())

    def keys(self) -> tuple[int, ...]:
        """Returns the keys of the data."""
        return tuple(key for key in self._data.keys())

    def items(self) -> tuple[tuple[int, TradeData], ...]:
        """Returns the items of the data."""
        return tuple((key, value) for key, value in self._data.items())

    def to_dict(self):
        """Convert the data to a dictionary."""
        return {key: value._asdict() for key, value in self._data.items()}


class PositionsManager(TradeManager):
    """A class to manage the open positions during a backtest. It is a subclass of TradeManager. It has an additional
    attribute _open_positions to store the open positions. It also has a margins attribute to store the margins of the
    open positions. It overrides some methods of the TradeManager class to manage the open positions.

    Attributes:
        _open_positions (set[int]): The open positions.
        margins (dict[int, float]): The margins of the open positions.
    """
    _data: dict[int, TradePosition]
    _open_positions: set[int]
    margins: dict[int, float]

    def __init__(self, *, data: dict = None, open_positions: set[int] = None, margins: dict = None):
        """Positions manager manages the open positions during a backtest. It is a subclass of TradeManager. It has an
        additional attribute _open_positions to store the open positions. It also has a margins attribute to store the
        margins of the open positions. It overrides some methods of the TradeManager class to manage the open positions.

        Args:
            data (dict, optional): The data to store the trades. This used for continuation of the backtesting, if it
             was stopped with some open positions.

            open_positions (set, optional): The open positions. Defaults to None.

            margins (dict, optional): The margins of the open positions. Defaults to None.
        """
        super().__init__(data=data)
        self._open_positions = open_positions or {trade.ticket for trade in self._data.values()}
        self.margins: dict[int, float] = margins or dict()

    def __len__(self):
        return len(self._open_positions)

    def __contains__(self, item: TradePosition):
        return item.ticket in self._open_positions

    def __getitem__(self, item):
        if item in self._open_positions:
            return super().__getitem__(item)
        raise KeyError("Position not found")

    def __setitem__(self, key, value: TradeData):
        self._open_positions.add(value.ticket)
        self._data[key] = value

    def __delitem__(self, key):
        self._open_positions.discard(key)
        del self._data[key]

    @property
    def margin(self):
        """Returns the total margin of all open positions"""
        return sum(self.margins.values())

    def close(self, *, ticket: int) -> bool:
        """Close a position. Given the ticket of the position to close.

        Args:
            ticket (int): The ticket of the position to close.
        """
        is_open = ticket in self._open_positions
        self._open_positions.discard(ticket)
        return is_open

    def get_margin(self, *, ticket: int) -> float:
        """Get the margin of a position. Given the ticket of the position.

        Args:
            ticket (int): The ticket of the position.

        Returns:
            float: The margin of the position.
        """
        return self.margins.get(ticket, 0.0)

    def delete_margin(self, *, ticket: int):
        """Delete the margin of a position. Given the ticket of the position.

        Args:
            ticket (int): The ticket of the position.
        """
        return self.margins.pop(ticket, 0)

    def set_margin(self, *, ticket: int, margin: float):
        """Set the margin of a position. Given the ticket of the position and the margin.

        Args:
            ticket (int): The ticket of the position.
            margin (float): The margin of the position
        """
        self.margins[ticket] = margin

    def positions_get(self, *, ticket: int = None, symbol: str = None, group: None = None) -> tuple[TradePosition, ...]:
        """Get positions. Given the ticket, symbol, or group of the positions.

        Args:
            ticket (int): The ticket of the position.
            symbol (str): The symbol of the position.
            group (str): The group

        Returns:
            tuple[TradePosition, ...]: The positions
        """
        if ticket:
            return tuple(position for position in self.open_positions if position.ticket == ticket)

        if symbol:
            return tuple(position for position in self.open_positions if position.symbol == symbol)

        if group:
            return self.open_positions

        if ticket == group == symbol is None:
            return self.open_positions

        return tuple()

    def positions_total(self) -> int:
        """Get the total number of open positions.

        Returns:
            int: The total number of open positions.
        """
        return len(self._open_positions)

    @property
    def open_positions(self) -> tuple[TradePosition, ...]:
        """Returns the open positions.

        Args:
            tuple[TradePosition, ...]: The open positions.
        """
        return tuple(position for position in self.values() if position.ticket in self._open_positions)


class OrdersManager(TradeManager):
    """Managers orders data during a backtest. It is a subclass of TradeManager. It manages access to the historical
     orders data
    """
    _data = dict[int, TradeOrder]

    def get_orders_range(self, *, date_from: float, date_to: float) -> tuple[TradeData, ...]:
        """Get orders within a date range. Given the start and end date of the range.

        Args:
            date_from (float): The start date of the range.
            date_to (float): The end date of the range.

        Returns:
            tuple[TradeData, ...]: The orders within the date range.
        """
        start = date_from.timestamp() if isinstance(date_from, datetime) else date_from
        end = date_to.timestamp() if isinstance(date_to, datetime) else date_to
        return tuple(order for order in self.values() if start <= order.time_setup <= end)

    def history_orders_get(self, *, date_from: float | datetime = None, date_to: float | datetime = None,
                           group: str = "", ticket: int = None, position: int = None) -> tuple[TradeOrder, ...]:
        """Get historical orders. Given the start and end date of the range, the group, ticket, or position of the
         orders.

         Args:
            date_from (float, datetime): The start date of the range.
            date_to (float, datetime): The end date of the range.
            group (str): The group of the orders.
            ticket (int): The ticket of the order.
            position (int): The position of the order.

        Returns:
            tuple[TradeOrder, ...]: The historical orders.
         """
        if date_from and date_to:
            orders = self.get_orders_range(date_from=date_from, date_to=date_to)
            if group:
                orders = orders
            return orders

        if ticket:
            return tuple(order for order in self.values() if order.ticket == ticket)

        if position:
            return tuple(order for order in self.values() if order.position_id == position)

        return ()

    def history_orders_total(self, *, date_from: datetime | float, date_to: datetime | float) -> int:
        """Get the total number of historical orders. Given the start and end date of the range.

        Args:
            date_from (datetime, float): The start date of the range.
            date_to (datetime, float): The end date of the range.
        """
        return len(self.get_orders_range(date_from=date_from, date_to=date_to))


class DealsManager(TradeManager):
    _data = dict[int, TradeDeal]

    def get_deals_range(self, *, date_from: float, date_to: float) -> tuple[TradeData, ...]:
        """Get deals within a date range. Given the start and end date of the range.

        Args:
            date_from (float): The start date of the range.
            date_to (float): The end date of the range.

        Returns:
            tuple[TradeData, ...]: The deals within the date range.
        """
        start = date_from.timestamp() if isinstance(date_from, datetime) else date_from
        end = date_to.timestamp() if isinstance(date_to, datetime) else date_to
        return tuple(deal for deal in self.values() if start <= deal.time <= end)

    def history_deals_get(self, *, date_from: float | datetime = None, date_to: float | datetime = None,
                          group: str = "", ticket: int = None, position: int = None) -> tuple[TradeDeal, ...]:
        """History deals get. Given the start and end date of the range, the group, ticket, or position of the deals.

        Args:
            date_from (float, datetime): The start date of the range.
            date_to (float, datetime): The end date of the range.
            group (str): The group of the deals.
            ticket (int): The ticket of the deal.
            position (int): The position of the deal.
        """
        if date_from and date_to:
            deals = self.get_deals_range(date_from=date_from, date_to=date_to)
            if group:
                deals = deals
            return deals

        if ticket:
            return tuple(deal for deal in self.values() if deal.ticket == ticket)

        if position and (ticket is None):
            return tuple(deal for deal in self.values() if deal.position_id == position)

        return ()

    def history_deals_total(self, *, date_from: datetime | float, date_to: datetime | float) -> int:
        """Get the total number of historical deals. Given the start and end date of the range

        Args:
            date_from (datetime, float): The start date of the range.
            date_to (datetime, float): The end date of the range.

        Returns:
            int: The total number of historical deals.
        """
        return len(self.get_deals_range(date_from=date_from, date_to=date_to))
