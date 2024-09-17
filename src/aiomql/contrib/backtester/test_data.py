import asyncio
from collections import namedtuple
from datetime import datetime
from typing import Literal
from itertools import zip_longest
import random
import json
from functools import cached_property

import pandas as pd
import pytz
import numpy as np
from pandas import DataFrame
from MetaTrader5 import (Tick, SymbolInfo, AccountInfo, TradeOrder, TradePosition, TradeDeal,
                         TradeRequest, OrderCheckResult, OrderSendResult, TerminalInfo)

from ...core.meta_trader import MetaTrader
from ...core.constants import TimeFrame, CopyTicks, OrderType, TradeAction, AccountStopOutMode
from ...core.config import Config
from .get_data import Data, GetData
from .test_account import AccountInfo as Account
from ...utils import round_down, round_up, error_handler, error_handler_sync, async_cache

tz = pytz.timezone('Etc/UTC')
Cursor = namedtuple('Cursor', ['index', 'time'])


class TestData:
    history_orders: DataFrame
    history_deals: DataFrame
    
    def __init__(self, data: Data = None, speed: int = 1, start: float | datetime = 0, end: float | datetime = 0):
        self._data = data or Data()
        self._account: Account = Account(**self._data.account)
        self.prices: dict[str, DataFrame] = self._data.prices
        self.ticks: dict[str, DataFrame] = self._data.ticks
        self.rates: dict[str, dict[str, DataFrame]] = self._data.rates
        span_start = (int(start.timestamp()) if isinstance(start, datetime) else int(start)) or self._data.span.start
        span_end = (int(end.timestamp()) if isinstance(end, datetime) else int(end)) or self._data.span.stop
        self.span: range = range(span_start, span_end, speed)
        self.range: range = range(0, span_end - span_start, speed)
        self.orders: dict[str, dict[int, TradeOrder]] = {}
        self.deals: dict[str, dict[int, TradeDeal]] = {}
        self.open_orders: dict[int, TradeOrder] = {}
        self.positions: dict[str, dict[int, TradePosition]] = {}
        self.open_positions: dict[int, TradePosition] = {}
        self.history_orders = self._data.history_orders
        self.history_deals = self._data.history_deals
        self.margins: dict[int, float] = {}
        self.mt5 = MetaTrader()
        self.iter = zip_longest(self.range, self.span)
        self.cursor: Cursor = Cursor(index=self.range.start, time=self.span.start)
        self.config = Config()
        self._data.name = self._data.name or f"{datetime.fromtimestamp(span_start):%d-%m-%y}_{datetime.fromtimestamp(span_end):%d-%m-%y}"
        self.fh = open(f'{self.config.test_data_dir}/data.json', 'a')

    def __next__(self) -> Cursor:
        index, time = next(self.iter)
        self.cursor = Cursor(index=index, time=time)
        return self.cursor

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def next(self) -> Cursor:
        return next(self)

    @property
    def data(self):
        return self._data

    def to_json(self, data):
        json.dump(data, self.fh)
    
    def reset(self):
        self.iter = zip_longest(self.range, self.span)
        self.cursor = Cursor(index=self.range.start, time=self.span.start)

    def go_to(self, time: datetime | int):
        time =  int(time.timestamp()) if isinstance(time, datetime) else int(time)
        steps = time - self.cursor.time
        if steps > 0:
            self.fast_forward(steps)
            return
        span = range(time, self.span.stop, self.span.step)
        start = span.start - self.span.start
        range_ = range(start, self.range.stop, self.range.step)
        self.iter = zip_longest(range_, span)
        self.cursor = Cursor(index=range_.start, time=span.start)

    def fast_forward(self, steps: int):
        for _ in range(steps):
            self.next()

    def get_dtype(self, df: DataFrame) -> list[tuple[str, str]]:
        return [(c, t) for c, t in zip(df.columns, df.dtypes)]

    @async_cache
    async def get_price_tick(self, symbol, time: int) -> Tick | None:
        if self.config.use_terminal_for_backtesting:
            tick = await self.mt5.copy_ticks_from(symbol, time, 1, CopyTicks.ALL)
            return Tick(tick[-1]) if tick else None
        return self.prices[symbol].loc[self.cursor.time]

    async def tracker(self):
        pos_tasks = [self.check_position(ticket) for ticket in self.open_positions]
        await asyncio.gather(*pos_tasks)
        order_tasks = [self.check_order(ticket) for ticket in self.open_orders]
        await asyncio.gather(*order_tasks)
        profit = sum(pos.profit for pos in self.open_positions.values())
        self.update_account(profit=profit)

    def save(self):
        self.fh.close()
        try:
            if len(self.orders) or len(self.deals):
                for symbol in self.orders:
                    self.history_orders = pd.concat([DataFrame(self.orders[symbol].values()), self.history_orders])
                self._data.history_orders = self.history_orders

                for symbol in self.deals:
                    self.history_deals = pd.concat([DataFrame(self.deals[symbol].values()), self.history_deals])
                self._data.history_deals = self.history_deals

                path = self.config.test_data_dir/f"{self._data.name}.pkl"
                GetData.dump_data(data=self._data, name=path, compress=self.config.compress_test_data)
        except Exception as err:
            print(err)

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
        self.update_account(gain=position.profit, margin=-margin)  # ToDo: Create a deal object here? modify update account

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

    def update_account(self, *, profit: float = None, margin: float = 0, gain: float = 0):
        self._account.balance += gain
        self._account.profit = profit if profit is not None else self._account.profit
        self._account.equity = self._account.balance + self._account.profit
        self._account.margin += margin
        self._account.margin_free = self._account.equity - self._account.margin

        if self._account.margin == 0:
            self._account.margin_level = 0
        else:
            mode = self._account.margin_mode
            level = self._account.equity / self._account.margin * 100
            self._account.margin_level = level if mode == AccountStopOutMode.PERCENT else self._account.margin_free

    def deposit(self, amount: float):
        self.update_account(gain=amount)

    def withdraw(self, amount: float):
        self.update_account(gain=-amount)

    @error_handler
    async def setup_account(self):
        if self.config.use_terminal_for_backtesting:
            acc = self._account
            default = {'profit': acc.profit, 'margin': acc.margin, 'equity': acc.equity, 'margin_free': acc.margin_free,
                       'margin_level': acc.margin_level, 'balance': acc.balance}
            acc = await self.mt5.account_info()
            acc = acc._asdict() | default
            self._account.set_attrs(**acc)

    @cached_property
    def symbols(self) -> dict[str, SymbolInfo]:
        return {symbol: SymbolInfo(info.values()) for symbol, info in self._data.symbols.items()}

    @error_handler
    async def order_send(self, request: dict, use_terminal: bool = True) -> OrderSendResult:
        print('sending orders')
        ticket = random.randint(100_000_000, 999_999_999)
        osr = {'retcode': 10009, 'comment': 'Request completed', 'request': TradeRequest(request)}
        if (position := request.get('position')) in self.open_positions:
            pos = self.open_positions[position]
            order_type = OrderType(request['type'])
            pos_type = OrderType(pos.type)
            if order_type.opposite == pos_type:  # ToDo: is there another way to check if the order is a close order?
                # close position
                self.close_position(pos.ticket)
                self.to_json(osr) # ToDo: remove later
                return OrderSendResult(osr)  # ToDo: Create a deal object here
            action = request['action']
            if action == TradeAction.SLTP:
                self.modify_stops(position, request['sl'], request['tp'])
                return OrderSendResult(osr)

        if (action := request.get('action')) == TradeAction.DEAL:
            ocr = await self.order_check(request, use_terminal=use_terminal)
            if ocr.retcode != 0:
                osr.update({'comment': ocr.comment, 'retcode': ocr.retcode})
                self.to_json(osr) # ToDo: remove later
                return OrderSendResult(osr)

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
            self.to_json(osr) # ToDo: remove later
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

    @error_handler
    async def get_terminal_info(self) -> TerminalInfo:
        if self.config.use_terminal_for_backtesting:
            res = await self.mt5.terminal_info()
            return res
        return TerminalInfo(self._data.terminal)

    @error_handler
    async def get_version(self) -> tuple[int, int, str]:
        if self.config.use_terminal_for_backtesting:
            res = await self.mt5.version()
            return res
        return self._data.version

    @error_handler
    async def get_symbols_total(self) -> int:
        if self.config.use_terminal_for_backtesting:
            syms = await self.mt5.symbols_total()
            return syms
        return len(self.symbols)

    @error_handler
    async def get_symbols(self, group: str = '') -> tuple[SymbolInfo, ...]:
        if self.config.use_terminal_for_backtesting:
            syms = await self.mt5.symbols_get(group=group)
            return syms
        return tuple(list(self.symbols.values()))

    @error_handler_sync
    def get_account_info(self) -> AccountInfo:
        return AccountInfo(self._account.asdict().values())

    @error_handler
    async def get_symbol_info_tick(self, symbol: str) -> Tick | None:
        tick = await self.get_price_tick(symbol, self.cursor.time)
        return tick

    @error_handler
    async def get_symbol_info(self, symbol: str) -> SymbolInfo:
        if self.config.use_terminal_for_backtesting:
            info = await self.mt5.symbol_info(symbol)
            return info

        info = self.symbols[symbol]
        tick = await self.get_symbol_info_tick(symbol)
        info = info._asdict()
        info |= {'bid': tick.bid, 'bidhigh': tick.bid, 'bidlow': tick.bid, 'ask': tick.ask,
                 'askhigh': tick.ask, 'asklow': tick.bid, 'last': tick.last, 'volume_real': tick.volume_real}
        return SymbolInfo(info)

    @error_handler
    async def get_rates_from(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float, count: int) -> np.ndarray:
        if self.config.use_terminal_for_backtesting:
            rates = await self.mt5.copy_rates_from(symbol, timeframe, date_from, count)
            return rates

        rates = self.rates[symbol][timeframe.name]
        start = int(datetime.timestamp(date_from)) if isinstance(date_from, datetime) else int(date_from)
        start = round_down(start, timeframe.time)
        rates = rates[rates.time <= start].iloc[-count:]
        return np.fromiter((tuple(i) for i in rates.iloc), dtype=self.get_dtype(rates))

    @error_handler
    async def get_rates_from_pos(self, symbol: str, timeframe: TimeFrame, start_pos: int, count: int) -> np.ndarray:
        if self.config.use_terminal_for_backtesting:
            now = datetime.now(tz=tz)
            b_now = self.cursor.time
            diff = (now.timestamp() - b_now) // timeframe.time
            start_pos = int(diff + start_pos)
            res = await self.mt5.copy_rates_from_pos(symbol, timeframe, start_pos, count)
            return res

        rates = self.rates[symbol][timeframe.name]
        end = abs(self.cursor.index - start_pos)
        start = abs(end - count)
        rates = rates.iloc[start:end]
        return np.fromiter((tuple(i) for i in rates.iloc), dtype=self.get_dtype(rates))

    @error_handler
    async def get_rates_range(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float, date_to: datetime | float) -> np.ndarray:
        if self.config.use_terminal_for_backtesting:
            rates = await self.mt5.copy_rates_range(symbol, timeframe, date_from, date_to)
            return rates

        rates = self.rates[symbol][timeframe.name]
        start = int(datetime.timestamp(date_from)) if isinstance(date_from, datetime) else int(date_from)
        start = round_down(start, timeframe.time)
        end = int(datetime.timestamp(date_to)) if isinstance(date_to, datetime) else int(date_to)
        end = round_up(end, timeframe.time)
        rates = rates[(rates.time >= start) & (rates.time <= end)]
        return np.fromiter((tuple(i) for i in rates.iloc), dtype=self.get_dtype(rates))

    @error_handler
    async def get_ticks_from(self, symbol: str, date_from: datetime | float, count: int, flags: CopyTicks) -> np.ndarray:
        if self.config.use_terminal_for_backtesting:
            ticks = await self.mt5.copy_ticks_from(symbol, date_from, count, flags)
            return ticks

        ticks = self.ticks[symbol]
        start = int(datetime.timestamp(date_from)) if isinstance(date_from, datetime) else int(date_from)
        ticks = ticks[ticks.time <= start].iloc[-count:]
        return np.fromiter((tuple(i) for i in ticks.iloc), dtype=self.get_dtype(ticks))

    @error_handler
    async def get_ticks_range(self, symbol: str, date_from: datetime | float, date_to: datetime | float, flags) -> np.ndarray:
        ticks = self.ticks[symbol]
        start = int(datetime.timestamp(date_from)) if isinstance(date_from, datetime) else int(date_from)
        end = int(datetime.timestamp(date_to)) if isinstance(date_to, datetime) else int(date_to)
        ticks = ticks[(ticks.time >= start) & (ticks.time <= end)]
        return np.fromiter((tuple(i) for i in ticks.iloc), dtype=self.get_dtype(ticks))

    @error_handler
    async def order_calc_margin(self, action: Literal[OrderType.BUY, OrderType.SELL], symbol: str, volume: float,
                                price: float):
        if self.mt5.config.use_terminal_for_backtesting:
            return await self.mt5.order_calc_margin(action, symbol, volume, price)

        sym = self.symbols[symbol]
        margin = (volume * sym.trade_contract_size * price) / (self._account.leverage / (sym.margin_initial or 1))
        return round(margin, self._account.currency_digits)

    @error_handler
    async def order_calc_profit(self, action: Literal[OrderType.BUY, OrderType.SELL], symbol: str, volume: float,
                                price_open: float, price_close: float):

        if self.mt5.config.use_terminal_for_backtesting:
            return await self.mt5.order_calc_profit(action, symbol, volume, price_open, price_close)

        sym = self.symbols[symbol]
        profit = (volume * sym.trade_contract_size *
                  ((price_close - price_open) if action == OrderType.BUY else (price_open - price_close)))
        return round(profit, self._account.currency_digits)

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
        orders = self.history_orders[self.history_orders.time >= start & self.history_orders.time <= end]
        return orders.shape[0]

    @error_handler_sync
    def get_history_orders(self, date_from: datetime | float, date_to: datetime | float, group: str = '',
                           ticket: int = None, position: int = None) -> tuple[TradeOrder, ...]:
        start =  int(date_from.timestamp()) if isinstance(date_from, datetime) else int(date_from)
        end = int(date_to.timestamp()) if isinstance(date_to, datetime) else int(date_to)
        orders = self.history_orders[self.history_orders.time >= start & self.history_orders.time <= end]

        if ticket:
            orders = orders[orders.ticket == ticket]

        elif position:
            orders = orders[orders.position == position]

        elif group:
            ...
        return tuple(TradeOrder(order) for order in orders.iloc)

    @error_handler_sync
    def get_history_deals_total(self, date_from: datetime | float, date_to: datetime | float) -> int:
        start =  int(date_from.timestamp()) if isinstance(date_from, datetime) else int(date_from)
        end = int(date_to.timestamp()) if isinstance(date_to, datetime) else int(date_to)
        deals = self.history_deals[self.history_deals.time >= start & self.history_deals.time <= end]
        return deals.shape[0]

    @error_handler_sync
    def get_history_deals(self, date_from: datetime | float, date_to: datetime | float, group: str = '',
                          position: int = None, ticket: int = None) -> tuple[TradeDeal, ...]:
        start = int(date_from.timestamp()) if isinstance(date_from, datetime) else int(date_from)
        end = int(date_to.timestamp()) if isinstance(date_to, datetime) else int(date_to)
        deals = self.history_deals[self.history_deals.time >= start & self.history_deals.time <= end]

        if ticket:
            deals = deals[deals.ticket == ticket]

        elif position:
            deals = deals[deals.position == position]

        elif group:
            ...
        
        return tuple(TradeDeal(deal) for deal in deals.iloc)
