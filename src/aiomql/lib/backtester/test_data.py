from ...core.models import AccountInfo, SymbolInfo
from .get_data import Data, GetData


class TestData:
    def __init__(self, data: Data):
        self._data = data
        self.account = data['account']
        self.symbols = data['symbols']
        self.prices = data['prices']
        self.ticks = data['ticks']
        self.rates = data['rates']
        self.span = data['span']
        self.cursor = 0
