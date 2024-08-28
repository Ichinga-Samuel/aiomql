from datetime import datetime, tzinfo

import pytz
import numpy as np
import pandas as pd
from pandas import DataFrame
from MetaTrader5 import Tick, SymbolInfo, AccountInfo, TradeOrder, TradePosition, TradeDeal
import MetaTrader5

from ..constants import TimeFrame, CopyTicks
from .get_data import Data, GetData
from ...utils import round_down, round_up

tz = pytz.timezone('Etc/UTC')


class TestData:
    history_orders: DataFrame
    history_deals: DataFrame
    
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
        self.orders: dict[str, dict[int, TradeOrder]] = {}
        self.open_orders: dict[int, TradeOrder] = {}
        self.positions: dict[str, dict[int, TradePosition]] = {}
        self.open_positions = dict[int, TradePosition] = {}
        self.history_deals = dict[str, dict[int, TradeDeal]] = {}

    def __next__(self):
        self.cursor = next(self.iter)
        return self.cursor
    
    def reset(self):
        self.iter = iter(self.interval)
        return self.iter

    def get_symbols_total(self) -> int:
        return len(self.symbols)

    def get_symbols(self) -> list:
        return list(self.symbols.keys())

    def get_account_info(self) -> AccountInfo:
        return AccountInfo(**self.account.dict)

    def get_symbol_info_tick(self, symbol: str) -> Tick:
        tick = self.prices[symbol].iloc[self.cursor]
        return Tick(**tick)
    
    def get_symbol_info(self, symbol: str) -> SymbolInfo:
        info = self.symbols[symbol]
        tick = self.get_symbol_info_tick(symbol)
        info = info.dict
        info |= {'bid': tick.bid, 'bidhigh': tick.bid, 'bidlow': tick.bid, 'ask': tick.ask,
                 'askhigh': tick.ask, 'asklow': tick.bid, 'last': tick.last, 'volume_real': tick.volume_real}
        return SymbolInfo(**info)

    def get_rates_from(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float, count: int) -> np.ndarray:
        rates = self.rates[symbol][timeframe.name]
        start = int(datetime.timestamp(date_from)) if isinstance(date_from, datetime) else int(date_from)
        start = round_down(start, timeframe.time)
        start = rates[rates.index <= start].iloc[-1].name
        start = rates.index.get_loc(start)
        end = start + count
        return rates.iloc[start:end].to_numpy()

    def get_rates_from_pos(self, symbol: str, timeframe: TimeFrame, start_pos: int, count: int) -> np.ndarray:
        rates = self.rates[symbol][timeframe.name]
        end = -start_pos + count
        end = end or None
        return rates.iloc[-start_pos:end].to_numpy()

    def get_rates_range(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float, date_to: datetime | float) -> np.ndarray:
        rates = self.rates[symbol][timeframe.name]
        start = int(datetime.timestamp(date_from)) if isinstance(date_from, datetime) else int(date_from)
        start = round_down(start, timeframe.time)
        start = rates[rates.index <= start].iloc[-1].name
        end = int(datetime.timestamp(date_to)) if isinstance(date_to, datetime) else int(date_to)
        end = round_up(end, timeframe.time)
        end = rates[rates.index >= end].iloc[-1].name
        return rates.loc[start:end].to_numpy()

    def get_ticks_from(self, symbol: str, date_from: datetime | float, count: int, flags: CopyTicks) -> np.ndarray:
        ticks = self.ticks[symbol]
        start = int(datetime.timestamp(date_from)) if isinstance(date_from, datetime) else int(date_from)
        start = ticks[ticks.index <= start].iloc[-1].name
        start = ticks.index.get_loc(start)
        end = start + count
        return ticks.iloc[start:end]
    
    def get_ticks_range(self, symbol: str, date_from: datetime | float, date_to: datetime | float, flags) -> np.ndarray:
        ticks = self.ticks[symbol]
        start = int(datetime.timestamp(date_from)) if isinstance(date_from, datetime) else int(date_from)
        start = ticks[ticks.index <= start].iloc[-1].index
        end = int(datetime.timestamp(date_to)) if isinstance(date_to, datetime) else int(date_to)
        end = ticks[ticks.index >= end].iloc[-1].index
        return ticks.loc[start:end].to_numpy()
    
    def get_orders_total(self) -> int:
        return len(self.live_orders)
    
    def get_orders(self, symbol: str = '', group: str = '', ticket: int = None) -> tuple[TradeOrder, ...]:
        if ticket:
            return self.live_orders.get(ticket, ())
        
        elif symbol:
            return tuple(order for order in self.orders.get(symbol, ()) if order.ticket in self.live_orders)
        
        elif group:
            return tuple(self.live_orders.values())
    
        else:
            return tuple(self.live_orders.values())
    
    def history_orders_total(self, date_from: datetime | float, date_to: datetime | float):
        start =  




