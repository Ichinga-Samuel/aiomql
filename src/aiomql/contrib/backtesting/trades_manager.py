from datetime import datetime
from typing import TypeVar, Generic
from logging import getLogger

from MetaTrader5 import TradePosition, TradeOrder, TradeDeal

logger = getLogger(__name__)

TradeData = TypeVar('TradeData', bound=TradePosition | TradeOrder | TradeDeal)


class TradeManager(Generic[TradeData]):
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
        try:
            res = self[ticket]
            klass = type(res)
            res = res._asdict()
            res.update(**kwargs)
            res =  klass(res.get(v) for v in klass.__match_args__)
            self[res.ticket] = res
            return res
        except KeyError:
            logger.error(f"Update Operation Failed: Could Not Find Ticket")

    def values(self) -> tuple[TradeData, ...]:
        return tuple(value for value in self._data.values())

    def keys(self) -> tuple[int, ...]:
        return tuple(key for key in self._data.keys())

    def items(self) -> tuple[tuple[int, TradeData], ...]:
        return tuple((key, value) for key, value in self._data.items())

    def to_dict(self):
        return {key: value._asdict() for key, value in self._data.items()}


class PositionsManager(TradeManager):
    _data: dict[int, TradePosition]
    _open_positions: set[int]
    margins: dict[int, float]

    def __init__(self, *, data: dict = None, open_positions: set = None, margins: dict = None):
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
        raise KeyError('Position not found')

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
        is_open = ticket in self._open_positions
        self._open_positions.discard(ticket)
        return is_open

    def get_margin(self, *, ticket: int) -> float:
        return self.margins.get(ticket, 0.0)

    def delete_margin(self, *, ticket: int):
        return self.margins.pop(ticket, 0)

    def set_margin(self, *, ticket: int, margin: float):
        self.margins[ticket] = margin
    
    def positions_get(self, *, ticket: int = None, symbol: str = None, group: None = None) -> tuple[TradePosition, ...]:
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
        return len(self._open_positions)

    @property
    def open_positions(self) -> tuple[TradePosition, ...]:
        return tuple(position for position in self.values() if position.ticket in self._open_positions)


class OrdersManager(TradeManager):
    _data = dict[int, TradeOrder]

    def get_orders_range(self, *, date_from: float, date_to: float) -> tuple[TradeData, ...]:
        start = date_from.timestamp() if isinstance(date_from, datetime) else date_from
        end = date_to.timestamp() if isinstance(date_to, datetime) else date_to
        return tuple(order for order in self.values() if start <= order.time_setup <= end)
    
    def history_orders_get(self, *, date_from: float | datetime = None, date_to: float | datetime = None,
                          group: str = '', ticket: int = None, position: int = None) -> tuple[TradeOrder, ...]:
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
        return len(self.get_orders_range(date_from=date_from, date_to=date_to))

class DealsManager(TradeManager):
    _data = dict[int, TradeDeal]

    def get_deals_range(self, *, date_from: float, date_to: float) -> tuple[TradeData, ...]:
        start = date_from.timestamp() if isinstance(date_from, datetime) else date_from
        end = date_to.timestamp() if isinstance(date_to, datetime) else date_to
        return tuple(deal for deal in self.values() if start <= deal.time <= end)

    def history_deals_get(self, *, date_from: float | datetime = None, date_to: float | datetime = None,
                          group: str = '', ticket: int = None, position: int = None) -> tuple[TradeDeal, ...]:
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
        return len(self.get_deals_range(date_from=date_from, date_to=date_to))
