from typing import TypeVar, Generic

from MetaTrader5 import TradePosition, TradeOrder, TradeDeal

from aiomql.utils import logger

TradeData = TypeVar('TradeData', bound=TradePosition | TradeOrder | TradeDeal)


class TradingData(Generic[TradeData]):
    _data: dict[int, TradeData]
    _open_items: set[int]

    def __init__(self, open_items: set[int] = None, data: dict = None):
        self._data = data or {}
        self._open_items = open_items or {trade.ticket for trade in self._data.values()}

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value: TradeData):
        self._open_items.add(value.ticket)
        self._data[key] = value

    def __delitem__(self, key):
        try:
            self._open_items.discard(key)

        except KeyError:
            logger.warning(f'{key} not found')

    def __contains__(self, item: int):
        return item in self._open_items

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def get(self, key, default=None) -> TradeData | None:
        return self._data.get(key, default) if key in self._open_items else default

    def pop(self, key, default=None) -> TradeData | None:
        self._open_items.discard(key)
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

    @property
    def open_items(self) -> set[int]:
        return self._open_items


class PositionsManager(TradingData):
    _data: dict[int, TradePosition]

    @property
    def open_positions(self) -> tuple[TradePosition, ...]:
        return tuple(position for position in self._data.values() if position.ticket in self.open_items)


class OrdersManager(TradingData):
    _data = dict[int, TradeOrder]

    @property
    def active_orders(self) -> tuple[TradeOrder, ...]:
        return tuple(order for order in self._data.values() if order.ticket in self.open_items)


class DealsManager(TradingData):
    ...
