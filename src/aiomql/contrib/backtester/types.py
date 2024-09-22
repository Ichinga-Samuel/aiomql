from MetaTrader5 import TradePosition, TradeOrder, TradeDeal


class TradingData:
    _data: dict
    _open_items: set[int]

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value: TradePosition | TradeOrder | TradeDeal):
        self._open_items.add(value.ticket)
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]
        self._open_items.discard(key)

    def __contains__(self, item):
        return item in self._open_items

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def get(self, key, default=None):
        return self._data.get(key, default) if key in self._open_items else default

    def pop(self, key, default=None):
        self._open_items.discard(key)
        return self._data.pop(key, default)


class PositionsManager(TradingData):
    def __init__(self, open_items: set[int] = None, data: dict = None):
        self._open_items = open_items or set()
        self._data = data or {}


class OrdersManager(TradingData):
    def __init__(self, open_items: set[int] = None, data: dict = None):
        self._open_items = open_items or set()
        self._data = data or {}
