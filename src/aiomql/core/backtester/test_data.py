from datetime import datetime, tzinfo
from typing import Literal

import pytz
import numpy as np
import pandas as pd
from pandas import DataFrame
from MetaTrader5 import (Tick, SymbolInfo, AccountInfo, TradeOrder, TradePosition, TradeDeal,
                         ORDER_TYPE_BUY, ORDER_TYPE_SELL)
from ..meta_trader import MetaTrader

from ..constants import TimeFrame, CopyTicks
from .get_data import Data, GetData
from ...utils import round_down, round_up

tz = pytz.timezone('Etc/UTC')


class TestData:
    history_orders: DataFrame
    history_deals: DataFrame
    
    def __init__(self, data: Data):
        self._data = data
        self.account = AccountInfo(**data['account'])
        self.symbols = {symbol: SymbolInfo(**info) for symbol, info in data['symbols'].items()}
        self.prices = data['prices']
        self.ticks = data['ticks']
        self.rates = data['rates']
        self.interval = data['interval']
        self.cursor = 0
        self.iter = iter(self.interval)
        self.orders: dict[str, dict[int, TradeOrder]] = {}
        self.open_orders: dict[int, TradeOrder] = {}
        self.positions: dict[str, dict[int, TradePosition]] = {}
        self.open_positions: dict[int, TradePosition] = {}
        self.mt = MetaTrader()
        self.mt5 = MetaTrader5

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
        return AccountInfo(**self.account._asdict())

    def get_symbol_info_tick(self, symbol: str) -> Tick:
        tick = self.prices[symbol].iloc[self.cursor]
        return Tick(**tick)
    
    def get_symbol_info(self, symbol: str) -> SymbolInfo:
        info = self.symbols[symbol]
        tick = self.get_symbol_info_tick(symbol)
        info = info._asdict()
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

    async def order_calc_margin(self, action: Literal[0, 1], symbol: str, volume: float, price: float, use_terminal=False):
        if use_terminal
        sym = self.symbols[symbol]
        margin = (volume * sym.trade_contract_size * price) / (self.account.leverage / (sym.margin_initial or 1))
        return margin

    def order_send(self, request: dict) -> dict:
        ...

    def order_check(self, request: dict) -> dict:
        ...
    
    def get_orders_total(self) -> int:
        return len(self.open_orders)
    
    def get_orders(self, symbol: str = '', group: str = '', ticket: int = None) -> tuple[TradeOrder, ...]:
        if ticket:
            order = self.open_orders.get(ticket)
            return (order,) if order else ()
        
        elif symbol:
            return tuple(order for order in self.orders.get(symbol, ()) if order.ticket in self.open_orders)
        
        elif group:
            return tuple(order for order in self.open_orders.values())
    
        else:
            return tuple(order for order in self.open_orders.values())

    def get_positions_total(self):
        return len(self.open_positions)

    def get_positions(self, symbol: str = '', group: str = '', ticket: int = None) -> tuple[TradePosition, ...]:
        if ticket:
            position = self.open_positions.get(ticket)
            return (position,) if position else ()

        elif symbol:
            return tuple(position for position in self.positions.get(symbol, ()) if position.ticket in self.open_positions)

        elif group:
            return tuple(position for position in self.open_positions.values())

        else:
            return tuple(position for position in self.open_positions.values())
    
    def history_orders_total(self, date_from: datetime | float, date_to: datetime | float) -> int:
        start =  int(date_from.timestamp()) if isinstance(date_from, datetime) else int(date_from)
        end = int(date_to.timestamp()) if isinstance(date_to, datetime) else int(date_to)
        start = self.history_orders[self.history_orders.index >= start].iloc[0].name
        end = self.history_orders[self.history_orders.index <= end].iloc[-1].name
        return self.history_orders.loc[start:end].shape[0]

    def history_orders_get(self, date_from: datetime | float, date_to: datetime | float, group: str = '',
                           ticket: int = None, position: int = None) -> tuple[TradeOrder, ...]:
        start =  int(date_from.timestamp()) if isinstance(date_from, datetime) else int(date_from)
        end = int(date_to.timestamp()) if isinstance(date_to, datetime) else int(date_to)
        start = self.history_orders[self.history_orders.index >= start].iloc[0].name
        end = self.history_orders[self.history_orders.index <= end].iloc[-1].name
        orders = self.history_orders.loc[start:end]

        if ticket:
            orders = orders[orders.ticket == ticket]

        elif position:
            orders = orders[orders.position == position]

        elif group:
            ...

        orders.drop(columns=['symbol'], inplace=True)
        return tuple(TradeOrder(**order) for order in orders.to_dict(orient='records'))

    def get_history_deals_total(self, date_from: datetime | float, date_to: datetime | float) -> int:
        start =  int(date_from.timestamp()) if isinstance(date_from, datetime) else int(date_from)
        end = int(date_to.timestamp()) if isinstance(date_to, datetime) else int(date_to)
        start = self.history_deals[self.history_deals.index >= start].iloc[0].name
        end = self.history_deals[self.history_deals.index <= end].iloc[-1].name
        return self.history_deals.loc[start:end].shape[0]

    def get_history_deals(self, date_from: datetime | float, date_to: datetime | float, group: str = '',
                          position: int = None, ticket: int = None) -> tuple[TradeDeal, ...]:
        start = int(date_from.timestamp()) if isinstance(date_from, datetime) else int(date_from)
        end = int(date_to.timestamp()) if isinstance(date_to, datetime) else int(date_to)
        start = self.history_deals[self.history_deals.index >= start].iloc[0].name
        end = self.history_deals[self.history_deals.index <= end].iloc[-1].name
        deals = self.history_deals.loc[start:end]

        if ticket:
            deals = deals[deals.ticket == ticket]

        elif position:
            deals = deals[deals.position == position]

        elif group:
            ...

        deals.drop(columns=['symbol'], inplace=True)
        return tuple(TradeDeal(**deal) for deal in deals.to_dict(orient='records'))
