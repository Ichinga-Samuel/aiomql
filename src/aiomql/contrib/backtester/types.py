from typing import TypeVar, Generic

from MetaTrader5 import TradePosition, TradeOrder, TradeDeal

from aiomql.utils import logger

TradeData = TypeVar('TradeData', bound=TradePosition | TradeOrder | TradeDeal)


class TradingData(Generic[TradeData]):
    _data: dict[int, TradeData]

    def __init__(self, open_items: set[int] = None, data: dict = None):
        self._data = data or {}

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value: TradeData):
        self._data[key] = value

    def __contains__(self, item: int):
        return item in self._open_items

    def __iter__(self):
        return iter(self._data)

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

    def get_by_symbol(self, *, symbol: str) -> tuple[TradeData, ...]:
        return tuple(position for position in self._data.values() if position.symbol == symbol)
    
    def get_by_ticket(self, *, ticket: int) -> tuple[TradeData, ...]:
        return tuple(position for position in self._data.values() if position.ticket == ticket)


class PositionsManager(TradingData):
    _data: dict[int, TradePosition]

    def __init__(self, open_items: set[int] = None, data: dict = None):
        super().__init__(data=data)
        self._open_items = open_items or {trade.ticket for trade in self._data.values()}
    
    def __len__(self):
        return len(self._open_items)

    def __setitem__(self, key, value: TradeData):
        self._open_items.add(value.ticket)
        self._data[key] = value

    def __delitem__(self, key):
        try:
            self._open_items.discard(key)
        except KeyError:
            logger.warning(f'{key} not found')

    def get(self, key, default=None) -> TradeData | None:
        return self._data.get(key, default) if key in self._open_items else default

    def pop(self, key, default=None) -> TradeData | None:
        self._open_items.discard(key)
        return self._data.get(key, default)
    
    def positions_get(self, *, ticket: int = None, symbol: str = None, group: None) -> tuple[TradePosition, ...]:
        if ticket and (symbol == group == None):
            return self.get_by_ticket(ticket=ticket)
        if symbol and (ticket == group == None):
            return self.get_by_symbol(symbol=symbol)
        if group and (ticket == symbol == None):
            return tuple(position for position in self._data.values())
        if ticket == group == symbol == None:
            return tuple(position for position in self._data.values())
        return tuple()
    
    def positions_total(self) -> int:
        return len(self)

    @property
    def open_positions(self) -> tuple[TradePosition, ...]:
        return tuple(position for position in self._data.values() if position.ticket in self.open_items)


class OrdersManager(TradingData):
    _data = dict[int, TradeOrder]

    def get_orders_range(self, *, date_from: float, date_to: float) -> tuple[TradeData, ...]:
        start = date_from.timestamp() if isinstance(date_from, datetime) else date_from
        end = date_to.timestamp() if isinstance(date_to, datetime) else date_to
        return tuple(v for v in self._data.values() if start <= v.time_setup <= end)
    
    def history_orders_get(self, *, date_from: float | datetime, date_to: float | datetime,
                          group: str = '', ticket: int = None, position: int = None) -> tuple[TradeOrder, ...]:
        orders = self.get_orders_range(date_from=date_from, date_to=date_to)
        if ticket and (position == None):
            return tuple(order for order in orders if order.ticket == ticket)
        if position and (ticket == None):
            return tuple(order for order in orders if order.position == position)
        return orders

class DealsManager(TradingData):
    _data = dict[int, TradeDeal]

    def get_deals_range(self, *, date_from: float, date_to: float) -> tuple[TradeData, ...]:
        start = date_from.timestamp() if isinstance(date_from, datetime) else date_from
        end = date_to.timestamp() if isinstance(date_to, datetime) else date_to
        return tuple(v for v in self._data.values() if start <= v.time <= end)

    def history_deals_get(self, date_from: float | datetime, date_to: float | datetime,
                          group: str = '', ticket: int = None, position: int = None) -> tuple[TradeDeal, ...]:
        deals = self.get_deals_range(date_from, date_to)
        if ticket and (position == None):
            return tuple(deal for deal in deals if deal.ticket == ticket)
        if position and (ticket == None):
            return tuple(deal for deal in deals if deal.position == position)
        return deals
