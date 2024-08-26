from ...core.models import AccountInfo, SymbolInfo, TickInfo
from .get_data import Data, GetData
from MetaTrader5 import Tick, SymbolInfo

class TestData:
    def __init__(self, data: Data):
        self._data = data
        self.account = data['account']
        self.symbols = data['symbols']
        self.prices = data['prices']
        self.ticks = data['ticks']
        self.rates = data['rates']
        self.interval = data['interval']
        self.cursor = 0
        self.iter = iter(self.interval)
    
    def __next__(self):
        self.cursor = next(self.iter)
        return self.cursor
    
    def reset(self):
        self.iter = iter(self.interval)
        return self.iter

    def get_symbol_info_tick(self, symbol: str) -> Tick:
        tick = self.prices[symbol].iloc[self.cursor]
        return Tick(**tick)
    
    def get_symbol_info(self, symbol: str) -> SymbolInfo:
        symbol = self.symbols[symbol]
        symbol |= {'bid': tick.bid, 'bidhigh': tick.bid, 'bidlow': tick.bid, 'bid': tick.bid, 'bidhigh': tick.bid, 'bidlow': tick.bid}
        symbol = SymbolInfo(**symbol)
        tick = self.get_symbol_info_tick(symbol)
        symbol.bid = tick.bid
        symbol.bidhigh = 120.506
        symbol.bidlow = tick.
        ask=120.041
        askhigh=120.526
        asklow=118.828
        symbol.update()


        

