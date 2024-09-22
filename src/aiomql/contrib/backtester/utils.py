from MetaTrader5 import TradePosition, TradeOrder, TradeDeal
# from .get_data import Data

class LiveDesc:
    """A Descriptor for live trading data"""
    def __set_name__(self, owner, name):
        self.access_name = name

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.access_name, {})

    def __set__(self, instance, value: tuple[int, str]):
        prop = instance.__dict__.setdefault(self.access_name, {})
        prop[value[0]] = value[1]


class Data:
    pos = LiveDesc()
    ords = LiveDesc()


dd = Data()
dd.pos = (1, 'EURUSD')
print(dd.pos)
