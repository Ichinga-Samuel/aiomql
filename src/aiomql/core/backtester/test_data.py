from collections import namedtuple
from datetime import datetime
from typing import Literal
from itertools import zip_longest
import random

import pytz
import numpy as np
from pandas import DataFrame
from MetaTrader5 import (Tick, SymbolInfo, AccountInfo, TradeOrder, TradePosition, TradeDeal,
                         ORDER_TYPE_BUY, ORDER_TYPE_SELL, TradeRequest, OrderCheckResult, OrderSendResult,
                         ACCOUNT_STOPOUT_MODE_PERCENT)
from ..meta_trader import MetaTrader
from ..constants import TimeFrame, CopyTicks, OrderType, TradeAction
from .get_data import Data
from ...account import Account
from ...utils import round_down, round_up

tz = pytz.timezone('Etc/UTC')
Cursor = namedtuple('Cursor', ['index', 'time'])


class TestData:
    history_orders: DataFrame
    history_deals: DataFrame
    
    def __init__(self, data: Data):
        self._data = data
        self.account = Account(**data.account)
        self.symbols = {symbol: SymbolInfo(**info) for symbol, info in data.symbols.items()}
        self.prices = data.prices
        self.ticks = data.ticks
        self.rates = data.rates
        self.span = data.span
        self.range = data.range
        self.cursor = Cursor(index=self.range[0], time=self.span[0])
        self.iter = zip_longest(self.range, self.span)
        self.orders: dict[str, dict[int, TradeOrder]] = {}
        self.open_orders: dict[int, TradeOrder] = {}
        self.positions: dict[str, dict[int, TradePosition]] = {}
        self.open_positions: dict[int, TradePosition] = {}
        self.history_orders = data.history_orders
        self.history_deals = data.history_deals
        self.margins: dict[int, float] = {}
        self.mt5 = MetaTrader()

    def __next__(self):
        index, time = next(self.iter)
        self.cursor = Cursor(index=index, time=time)
        return self.cursor
    
    def reset(self):
        self.iter = zip_longest(self.range, self.span)
        self.cursor = Cursor(index=self.range[0], time=self.span[0])
        return self.cursor

    def get_symbols_total(self) -> int:
        return len(self.symbols)

    def get_symbols(self) -> list:
        return list(self.symbols.keys())

    def get_account_info(self) -> AccountInfo:
        return AccountInfo(**self.account._asdict())

    def get_symbol_info_tick(self, symbol: str) -> Tick:
        tick = self.prices[symbol].iloc[self.cursor.index]
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

    async def order_calc_margin(self, action: Literal[OrderType.BUY, OrderType.SELL], symbol: str, volume: float,
                                price: float, use_terminal=False):
        if use_terminal and self.mt5.config.use_terminal_for_backtesting:
            return await self.mt5.order_calc_margin(OrderType(action), symbol, volume, price)
        sym = self.symbols[symbol]
        margin = (volume * sym.trade_contract_size * price) / (self.account.leverage / (sym.margin_initial or 1))
        return margin

    async def order_calc_profit(self, action: Literal[OrderType.BUY, OrderType.SELL], symbol: str, volume: float,
                                price_open: float, price_close: float, use_terminal=True):
        if use_terminal and self.mt5.config.use_terminal_for_backtesting:
            return await self.mt5.order_calc_profit(action, symbol, volume, price_open, price_close)
        sym = self.symbols[symbol]
        profit = volume * sym.trade_contract_size * (price_close - price_open)
        return profit

    def check_order(self, ticket: int) -> bool:
        order = self.open_orders[ticket]
        order_type, symbol = order.type, order.symbol
        tick = self.prices[symbol].loc[self.cursor.time]
        tp, sl = order.tp, order.sl

        match order_type:
            case self.mt5._ORDER_TYPE_BUY:
                if tp >= tick.bid or sl <= tick.bid:
                    self.close_position(ticket)
            
            case self.mt5.ORDER_TYPE_SELL:
                if tp <= tick.ask or sl >= tick.ask:
                    self.close_position(ticket)
            
            case _:
                ...

    def check_position(self, ticket: int) -> bool:
        ...

    def close_position(self, ticket: int):        
        position = self.open_positions.pop(ticket)
        margin = self.margins.pop(position.ticket)
        profit = position.profit
        self.update_account(profit, margin=margin)

    async def modify_stops(self, ticket: int, sl: int = None, tp: int = None):
        pos = self.open_positions.pop(ticket)
        sl = sl or pos.sl
        tp = tp or pos.tp
        order_type, symbol, volume, price_open = pos.order_type, pos.symbol, pos.volume
        pos = pos._asdict()
        pos.update(tp=tp, sl=sl, time_update=self.cursor.time)
        profit = await self.mt5.order_calc_profit(order_type, symbol, volume, price_open, sl)
        self.open_positions[ticket] = TradePosition(**pos)

    def update_account(self, profit: float, margin: float = 0):
        self.account.balance += profit
        self.account.equity += profit
        self.account.margin -= margin
        self.account.margin_free = self.account.equity - self.account.margin
        self.account.margin_level = (self.account.equity / self.account.margin) * 100 if self.account.margin_mode 

    async def order_send(self, request: dict, use_terminal: bool = True) -> OrderSendResult:
        osr = {'retcode': 10009, 'comment': 'Request completed', 'request': TradeRequest(**request)}

        if (position := request.get('position')) in self.open_positions:
            pos = self.open_positions[position]
            order_type = OrderType(request['type'])
            pos_type = OrderType(pos.type)
            if order_type.opposite == pos_type:  # ToDo: is there another way to check if the order is a close order?
                # close position
                self.close_position(pos)
                return OrderSendResult(**osr)  # ToDo: Create a deal object here
            action = request['action']
            if action == TradeAction.SLTP:
                self.modify_stops(position, request['sl'], request['tp'])
                return OrderSendResult(**osr)

        if (action := request.get('action')) == TradeAction.DEAL:
            ocr = await self.order_check(request, use_terminal=use_terminal)
            if ocr.retcode != 0:
                osr.update({'comment': ocr.comment, 'retcode': ocr.retcode})
                return OrderSendResult(**osr)

            ticket = random.randint(100_000_000, 999_999_999)
            deal_ticket = random.randint(100_000_000, 999_999_999)
            tick = self.get_symbol_info_tick(request['symbol'])
            order_type = request['type']
            price = tick.ask if request['type'] == ORDER_TYPE_BUY else tick.bid
            volume = request['volume']
            sl, tp = request.get('sl', 0), request.get('tp', 0)
            symbol = request['symbol']
            pos = {'comment': 'open position', 'ticket': ticket, 'symbol': symbol, 'volume': volume,
                   'price_open': price, 'price_current': price, 'type': order_type, 'profit': 0,
                   'sl': sl, 'tp': tp, 'time': tick.time,
                   'time_msc': tick.time_msc}
            order = {'ticket': ticket, 'symbol': symbol, 'volume': volume, 'price': price, 'price_current': price,
                     'price_open': price, 'type': order_type, 'time_setup': tick.time,
                     'time_setup_msc': tick.time_msc, 'volume_current': volume, 'sl': sl, 'tp': tp,}
            pos = TradePosition(**pos)
            order = TradeOrder(**order)
            # ToDo: Create a deal object here
            self.open_positions[pos.ticket] = pos
            self.open_orders[order.ticket] = order
            self.orders.setdefault(order.symbol, {})[order.ticket] = order
            self.positions.setdefault(pos.symbol, {})[pos.ticket] = pos
            osr.update({'order': ticket, 'price': price, 'volume': volume, 'bid': tick.bid,
                        'ask': tick.ask, 'deal': deal_ticket})
            margin = await self.order_calc_margin(action, symbol, volume, price)
            self.margins[ticket] = margin
            return OrderSendResult(**osr)

    async def order_check(self, request: dict, use_terminal=True) -> OrderCheckResult:
        action, symbol, volume = request.get('action'), request.get('symbol'), request.get('volume')
        price = request.get('price')
        ocr = {'retcode': 0, 'balance': 0, 'profit': 0, 'margin': 0, 'equity': 0, 'margin_free': 0,
               'margin_level': 0, 'comment': 'Done', request: TradeRequest(**request)}

        margin = 0
        if all([action, symbol, volume, price]):
            margin = await self.order_calc_margin(action, symbol, volume, price)

        acc = self.get_account_info()
        equity = acc.equity
        used_margin = acc.margin + margin
        free_margin = acc.margin_free - margin
        margin_level = (equity / used_margin) * 100 if (acc.margin_mode == ACCOUNT_STOPOUT_MODE_PERCENT and used_margin > 0) else free_margin

        if use_terminal and self.mt5.config.use_terminal_for_backtesting:
            ocr_t = await self.mt5.order_check(request)
            # return order check result if invalid stops level are detected or bad request
            if ocr_t.retcode in (10016, 10013, 10014):
                return ocr_t
        else:
            sym = self.symbols[symbol]
            tsl = sym.trade_stops_level
            sl, tp = request.get('sl', 0), request.get('tp', 0)

            if tp or sl:
                min_sl = min(sl, tp)
                dsl = abs(price - min_sl) / sym.point
                if dsl < tsl:
                    ocr['retcode'] = 10016
                    ocr['comment'] = 'Invalid stops'
                    return OrderCheckResult(**ocr)
                
        if margin_level < acc.margin_so_call:
            ocr['retcode'] = 10019
            ocr['comment'] = 'No money'

        ocr.update({'balance': acc.balance, 'profit': acc.profit, 'margin': used_margin, 'equity': equity,
                    'margin_free': free_margin, 'margin_level': margin_level})

        return OrderCheckResult(**ocr)
    
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
