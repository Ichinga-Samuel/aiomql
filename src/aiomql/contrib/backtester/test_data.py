import asyncio
from collections import namedtuple
from datetime import datetime
from typing import Literal
from itertools import zip_longest
import random

import pandas as pd
import pytz
import numpy as np
from pandas import DataFrame
from MetaTrader5 import (Tick, SymbolInfo, AccountInfo, TradeOrder, TradePosition, TradeDeal,
                         TradeRequest, OrderCheckResult, OrderSendResult, TerminalInfo)

from ...core.meta_trader import MetaTrader
from ...core.constants import TimeFrame, CopyTicks, OrderType, TradeAction, AccountStopOutMode
from .get_data import Data
from .test_account import AccountInfo as Account
from ...utils import round_down, round_up, error_handler, error_handler_sync
# from .event_manager import EventManager

tz = pytz.timezone('Etc/UTC')
Cursor = namedtuple('Cursor', ['index', 'time'])


class TestData:
    history_orders: DataFrame
    history_deals: DataFrame
    
    def __init__(self, data: Data):
        self._data = data
        self.version: tuple[int, int, str] = data.version
        self.terminal_info = TerminalInfo(data.terminal)
        self.account: Account = Account(**data.account)
        self.symbols: dict[str, SymbolInfo] = {symbol: SymbolInfo(info) for symbol, info in data.symbols.items()}
        self.prices: dict[str, DataFrame] = data.prices
        self.ticks: dict[str, DataFrame] = data.ticks
        self.rates: dict[str, dict[str, DataFrame]] = data.rates
        self.span: range = data.span
        self.range: range = data.range
        self.orders: dict[str, dict[int, TradeOrder]] = {}
        self.deals: dict[str, dict[int, TradeDeal]] = {}
        self.open_orders: dict[int, TradeOrder] = {}
        self.positions: dict[str, dict[int, TradePosition]] = {}
        self.open_positions: dict[int, TradePosition] = {}
        self.history_orders = data.history_orders
        self.history_deals = data.history_deals
        self.margins: dict[int, float] = {}
        self.mt5 = MetaTrader()
        self.iter = zip_longest(self.range, self.span)
        self.cursor = next(self)
        # self.event_manager = EventManager()

    def __next__(self) -> Cursor:
        index, time = next(self.iter)
        self.cursor = Cursor(index=index, time=time)
        return self.cursor

    def next(self) -> Cursor:
        return next(self)

    @property
    def data(self):
        return self._data
    
    def reset(self):
        self.iter = zip_longest(self.range, self.span)
        self.cursor = Cursor(index=self.range[0], time=self.span[0])
        return self.cursor

    def go_to(self, index: int, time: int):
        range_ = range(time, self.range.stop, self.range.step)
        span = range(index, self.span.stop, self.span.step)
        self.iter = zip_longest(range_, span)
        self.cursor = next(self)

    def get_dtype(self, df: DataFrame) -> list[tuple[str, str]]:
        return [(c, t) for c, t in zip(df.columns, df.dtypes)]

    async def tracker(self):
        pos_tasks = [self.check_position(ticket) for ticket in self.open_positions]
        await asyncio.gather(*pos_tasks)
        order_tasks = [self.check_order(ticket) for ticket in self.open_orders]
        await asyncio.gather(*order_tasks)

    def save(self):
        self._data.history_deals = self.history_deals
        self._data.history_orders = self.history_orders
        for symbol in self.orders:
            self.history_orders = pd.concat([DataFrame(self.orders[symbol].values()), self.history_orders])
        self._data.history_orders = self.history_orders
        for symbol in self.deals:
            self.history_deals = pd.concat([DataFrame(self.deals[symbol].values()), self.history_deals])
        self._data.history_deals = self.history_deals

    @error_handler
    async def check_order(self, ticket: int):
        order = self.open_orders[ticket]
        order_type, symbol = order.type, order.symbol
        tick = self.prices[symbol].loc[self.cursor.time]
        tp, sl = order.tp, order.sl

        match order_type:
            case OrderType.BUY:
                if tp >= tick.bid or sl <= tick.bid:
                    self.close_position(ticket)

            case OrderType.SELL:
                if tp <= tick.ask or sl >= tick.ask:
                    self.close_position(ticket)
            case _:
                ...

    @error_handler
    async def check_position(self, ticket: int, use_terminal=True):
        pos = self.open_positions[ticket]
        order_type, symbol, volume, price_open, prev_profit = pos.type, pos.symbol, pos.volume, pos.price_open, pos.profit
        tick = self.prices[symbol].loc[self.cursor.time]
        price_current = tick.bid if order_type == OrderType.BUY else tick.ask
        profit = await self.order_calc_profit(order_type, symbol, volume, price_open, price_current, use_terminal)
        self.update_account(equity=profit - prev_profit)
        pos = pos._asdict()
        pos.update(profit=profit, price_current=price_current, time_update=self.cursor.time)
        pos = TradePosition(pos)
        self.open_positions[ticket] = pos
        self.positions[symbol][ticket] = pos

    def close_position(self, ticket: int):
        position = self.open_positions.pop(ticket)
        margin = self.margins.pop(position.ticket)
        order = self.open_orders.pop(ticket)
        order = order._asdict()
        order.update(time_done=self.cursor.time)
        self.orders[order['symbol']][ticket] = TradeOrder(order)
        self.update_account(profit=position.profit, margin=-margin)

    def modify_stops(self, ticket: int, sl: int = None, tp: int = None):
        pos = self.open_positions.pop(ticket)
        order = self.open_orders.pop(ticket)
        sl = sl or pos.sl
        tp = tp or pos.tp
        pos = pos._asdict()
        pos.update(tp=tp, sl=sl, time_update=self.cursor.time)
        sl = sl or order.sl
        tp = tp or order.tp
        order = order._asdict()
        order.update(tp=tp, sl=sl)
        pos = TradePosition(pos)
        order = TradeOrder(order)
        self.open_positions[ticket] = pos
        self.open_orders[ticket] = order
        self.positions[pos.symbol][ticket] = pos
        self.orders[order.symbol][ticket] = order

    def update_account(self, *, profit: float = 0, margin: float = 0, equity: float = 0):
        self.account.balance += profit
        self.account.equity += equity
        self.account.margin += margin
        self.account.margin_free = self.account.equity - self.account.margin
        self.account.margin_level = (self.account.equity / (self.account.margin or 1)) * 100 \
            if self.account.margin_mode == AccountStopOutMode.PERCENT else self.account.margin_free

    @error_handler
    async def order_send(self, request: dict, use_terminal: bool = True) -> OrderSendResult:
        osr = {'retcode': 10009, 'comment': 'Request completed', 'request': TradeRequest(request)}

        if (position := request.get('position')) in self.open_positions:
            pos = self.open_positions[position]
            order_type = OrderType(request['type'])
            pos_type = OrderType(pos.type)
            if order_type.opposite == pos_type:  # ToDo: is there another way to check if the order is a close order?
                # close position
                self.close_position(pos.ticket)
                return OrderSendResult(osr)  # ToDo: Create a deal object here
            action = request['action']
            if action == TradeAction.SLTP:
                self.modify_stops(position, request['sl'], request['tp'])
                return OrderSendResult(osr)

        if (action := request.get('action')) == TradeAction.DEAL:
            ocr = await self.order_check(request, use_terminal=use_terminal)
            if ocr.retcode != 0:
                osr.update({'comment': ocr.comment, 'retcode': ocr.retcode})
                return OrderSendResult(osr)

            ticket = random.randint(100_000_000, 999_999_999)
            deal_ticket = random.randint(100_000_000, 999_999_999)
            tick = self.get_symbol_info_tick(request['symbol'])
            order_type = request['type']
            price = tick.ask if request['type'] == OrderType.BUY else tick.bid
            volume = request['volume']
            sl, tp = request.get('sl', 0), request.get('tp', 0)
            symbol = request['symbol']

            pos = {'comment': 'open position', 'ticket': ticket, 'symbol': symbol, 'volume': volume,
                   'price_open': price, 'price_current': price, 'type': order_type, 'profit': 0,
                   'sl': sl, 'tp': tp, 'time': tick.time,
                   'time_msc': tick.time_msc}

            order = {'ticket': ticket, 'symbol': symbol, 'volume': volume, 'price': price, 'price_current': price,
                     'price_open': price, 'type': order_type, 'time_setup': tick.time,
                     'time_setup_msc': tick.time_msc, 'volume_current': volume, 'sl': sl, 'tp': tp, }

            pos = TradePosition(pos)
            order = TradeOrder(order)
            # ToDo: Create a deal object here
            self.open_positions[pos.ticket] = pos
            self.open_orders[order.ticket] = order
            self.orders.setdefault(order.symbol, {})[order.ticket] = order
            self.positions.setdefault(pos.symbol, {})[pos.ticket] = pos
            osr.update({'order': ticket, 'price': price, 'volume': volume, 'bid': tick.bid,
                        'ask': tick.ask, 'deal': deal_ticket})
            margin = await self.order_calc_margin(action, symbol, volume, price, use_terminal=use_terminal)
            self.margins[ticket] = margin
            self.update_account(margin=margin)
            return OrderSendResult(osr)

    @error_handler
    async def order_check(self, request: dict, use_terminal=True) -> OrderCheckResult:
        action, symbol, volume = request.get('action'), request.get('symbol'), request.get('volume')
        price = request.get('price')
        ocr = {'retcode': 0, 'balance': 0, 'profit': 0, 'margin': 0, 'equity': 0, 'margin_free': 0,
               'margin_level': 0, 'comment': 'Done', request: TradeRequest(request)}

        margin = 0
        if all([action, symbol, volume, price]):
            margin = await self.order_calc_margin(action, symbol, volume, price, use_terminal=use_terminal)

        acc = self.get_account_info()
        equity = acc.equity
        used_margin = acc.margin + margin
        free_margin = acc.margin_free - margin
        margin_level = (equity / used_margin) * 100 if (
                    acc.margin_mode == AccountStopOutMode.PERCENT and used_margin > 0) else free_margin

        if use_terminal and self.mt5.config.use_terminal_for_backtesting:
            ocr_t = await self.mt5.order_check(request)
            # return order check result if invalid stops level are detected or bad request
            if ocr_t.retcode in (10016, 10013, 10014):
                return ocr_t

        sym = self.symbols[symbol]
        tsl = sym.trade_stops_level
        sl, tp = request.get('sl', 0), request.get('tp', 0)

        # check if the stops level is valid
        if tp or sl:
            min_sl = min(sl, tp)
            dsl = abs(price - min_sl) / sym.point
            if dsl < tsl:
                ocr['retcode'] = 10016
                ocr['comment'] = 'Invalid stops'
                return OrderCheckResult(ocr)

        # check if the account has enough money
        if margin_level < acc.margin_so_call:
            ocr['retcode'] = 10019
            ocr['comment'] = 'No money'

        # check volume
        if volume < sym.volume_min or volume > sym.volume_max:
            ocr['retcode'] = 10014
            ocr['comment'] = 'Invalid volume'

        ocr.update({'balance': acc.balance, 'profit': acc.profit, 'margin': used_margin, 'equity': equity,
                    'margin_free': free_margin, 'margin_level': margin_level})

        return OrderCheckResult(ocr)

    @error_handler_sync
    def get_terminal_info(self) -> TerminalInfo:
        return self.terminal_info

    @error_handler_sync
    def get_version(self) -> tuple[int, int, str]:
        return self.version

    @error_handler_sync
    def get_symbols_total(self) -> int:
        return len(self.symbols)

    @error_handler_sync
    def get_symbols(self, group: str = '') -> tuple[SymbolInfo, ...]:
        return tuple(list(self.symbols.values()))

    @error_handler_sync
    def get_account_info(self) -> AccountInfo:
        return AccountInfo(self.account.asdict())

    @error_handler_sync
    def get_symbol_info_tick(self, symbol: str) -> Tick:
        tick = self.prices[symbol].iloc[self.cursor.index]
        return Tick(tick)

    @error_handler_sync
    def get_symbol_info(self, symbol: str) -> SymbolInfo:
        info = self.symbols[symbol]
        tick = self.get_symbol_info_tick(symbol)
        info = info._asdict()
        info |= {'bid': tick.bid, 'bidhigh': tick.bid, 'bidlow': tick.bid, 'ask': tick.ask,
                 'askhigh': tick.ask, 'asklow': tick.bid, 'last': tick.last, 'volume_real': tick.volume_real}
        return SymbolInfo(info)

    @error_handler_sync
    def get_rates_from(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float, count: int) -> np.ndarray:
        rates = self.rates[symbol][timeframe.name]
        start = int(datetime.timestamp(date_from)) if isinstance(date_from, datetime) else int(date_from)
        start = round_down(start, timeframe.time)
        start = rates[rates.index <= start].iloc[-1].name
        start = rates.index.get_loc(start)
        end = start + count
        return np.fromiter((tuple(i) for i in rates.iloc[start:end].iloc), dtype=self.get_dtype(rates))

    @error_handler_sync
    def get_rates_from_pos(self, symbol: str, timeframe: TimeFrame, start_pos: int, count: int) -> np.ndarray:
        rates = self.rates[symbol][timeframe.name]
        end = -start_pos + count
        end = end or None
        return np.fromiter((tuple(i) for i in rates.iloc[-start_pos:end].iloc), dtype=self.get_dtype(rates))

    @error_handler_sync
    def get_rates_range(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float, date_to: datetime | float) -> np.ndarray:
        rates = self.rates[symbol][timeframe.name]
        start = int(datetime.timestamp(date_from)) if isinstance(date_from, datetime) else int(date_from)
        start = round_down(start, timeframe.time)
        start = rates[rates.index <= start].iloc[-1].name
        end = int(datetime.timestamp(date_to)) if isinstance(date_to, datetime) else int(date_to)
        end = round_up(end, timeframe.time)
        end = rates[rates.index >= end].iloc[-1].name
        return np.fromiter((tuple(i) for i in rates.loc[start:end].iloc), dtype=self.get_dtype(rates))

    @error_handler_sync
    def get_ticks_from(self, symbol: str, date_from: datetime | float, count: int, flags: CopyTicks) -> np.ndarray:
        ticks = self.ticks[symbol]
        start = int(datetime.timestamp(date_from)) if isinstance(date_from, datetime) else int(date_from)
        start = ticks[ticks.index <= start].iloc[-1].name
        start = ticks.index.get_loc(start)
        end = start + count
        return np.fromiter((tuple(i) for i in ticks.iloc[start:end].iloc), dtype=self.get_dtype(ticks))

    @error_handler_sync
    def get_ticks_range(self, symbol: str, date_from: datetime | float, date_to: datetime | float, flags) -> np.ndarray:
        ticks = self.ticks[symbol]
        start = int(datetime.timestamp(date_from)) if isinstance(date_from, datetime) else int(date_from)
        start = ticks[ticks.index <= start].iloc[-1].index
        end = int(datetime.timestamp(date_to)) if isinstance(date_to, datetime) else int(date_to)
        end = ticks[ticks.index >= end].iloc[-1].index
        return np.fromiter((tuple(i) for i in ticks.loc[start:end].iloc), dtype=self.get_dtype(ticks))

    @error_handler
    async def order_calc_margin(self, action: Literal[OrderType.BUY, OrderType.SELL], symbol: str, volume: float,
                                price: float, use_terminal=False):
        if use_terminal and self.mt5.config.use_terminal_for_backtesting:
            return await self.mt5.order_calc_margin(action, symbol, volume, price)
        sym = self.symbols[symbol]
        margin = (volume * sym.trade_contract_size * price) / (self.account.leverage / (sym.margin_initial or 1))
        return round(margin, self.account.currency_digits)

    @error_handler
    async def order_calc_profit(self, action: Literal[OrderType.BUY, OrderType.SELL], symbol: str, volume: float,
                                price_open: float, price_close: float, use_terminal=True):
        if use_terminal and self.mt5.config.use_terminal_for_backtesting:
            return await self.mt5.order_calc_profit(action, symbol, volume, price_open, price_close)
        sym = self.symbols[symbol]
        profit = (volume * sym.trade_contract_size *
                  ((price_close - price_open) if action == OrderType.BUY else (price_open - price_close)))
        return round(profit, self.account.currency_digits)

    @error_handler_sync
    def get_orders_total(self) -> int:
        return len(self.open_orders)

    @error_handler_sync
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

    @error_handler_sync
    def get_positions_total(self) -> int:
        return len(self.open_positions)

    @error_handler_sync
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

    @error_handler_sync
    def get_history_orders_total(self, date_from: datetime | float, date_to: datetime | float) -> int:
        start =  int(date_from.timestamp()) if isinstance(date_from, datetime) else int(date_from)
        end = int(date_to.timestamp()) if isinstance(date_to, datetime) else int(date_to)
        start = self.history_orders[self.history_orders.index >= start].iloc[0].name
        end = self.history_orders[self.history_orders.index <= end].iloc[-1].name
        return self.history_orders.loc[start:end].shape[0]

    @error_handler_sync
    def get_history_orders(self, date_from: datetime | float, date_to: datetime | float, group: str = '',
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
        return tuple(TradeOrder(order) for order in orders.iloc)

    @error_handler_sync
    def get_history_deals_total(self, date_from: datetime | float, date_to: datetime | float) -> int:
        start =  int(date_from.timestamp()) if isinstance(date_from, datetime) else int(date_from)
        end = int(date_to.timestamp()) if isinstance(date_to, datetime) else int(date_to)
        start = self.history_deals[self.history_deals.index >= start].iloc[0].name
        end = self.history_deals[self.history_deals.index <= end].iloc[-1].name
        return self.history_deals.loc[start:end].shape[0]

    @error_handler_sync
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

        return tuple(TradeDeal(deal) for deal in deals.iloc)