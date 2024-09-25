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
from debugpy.common.timestamp import current
from pandas import DataFrame
from MetaTrader5 import (Tick, SymbolInfo, AccountInfo, TradeOrder, TradePosition, TradeDeal,
                         TradeRequest, OrderCheckResult, OrderSendResult, TerminalInfo)

from ...core.meta_trader import MetaTrader
from ...core.constants import TimeFrame, CopyTicks, OrderType, TradeAction, AccountStopOutMode, PositionReason
from ...core.config import Config
from ...lib.strategies.finger_trap import logger
from ...utils import round_down, round_up, error_handler, error_handler_sync, async_cache

from .get_data import Data, GetData
from .test_account import TestAccount
from .types import PositionsManager, OrdersManager, DealsManager

tz = pytz.timezone('Etc/UTC')
Cursor = namedtuple('Cursor', ['index', 'time'])


class TestData:
    mt5: MetaTrader = MetaTrader()
    span: range
    range: range
    cursor: Cursor
    iter: zip_longest

    def __init__(self, data: Data = None, speed: int = 1, start: float | datetime = 0, end: float | datetime = 0):
        self._data = data or Data()
        self._account: TestAccount = TestAccount(**self._data.account)
        self.positions: PositionsManager = PositionsManager()
        self.orders: OrdersManager = OrdersManager()
        self.deals: DealsManager = DealsManager()
        self.margins: dict[int, float] = {}
        self.config = Config(test_data=self)
        self.set_up(start=start, end=end, speed=speed)
        self._data.name = self._data.name or f"{datetime.fromtimestamp(self.span[0]):%d-%m-%y}_{datetime.fromtimestamp(self.span[-1]):%d-%m-%y}"
        self.fh = open(f'{self.config.test_data_dir}/data.json', 'a')

    def set_up(self, start: float | datetime = 0, end: float | datetime = 0, speed: int = 1):
        span_start = (int(start.timestamp()) if isinstance(start, datetime) else int(start)) or self._data.span.start
        span_end = (int(end.timestamp()) if isinstance(end, datetime) else int(end)) or self._data.span.stop
        self.span = range(span_start, span_end, speed)
        self.range = range(0, span_end - span_start, speed)
        self.iter = zip_longest(self.range, self.span)
        self.cursor: Cursor = Cursor(index=self.range.start, time=self.span.start)

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

        range_start = time - self.span.start
        span = range(time, self.span.stop, self.span.step)
        range_ = range(range_start, self.range.stop, self.range.step)
        self.iter = zip_longest(range_, span)
        self.cursor = Cursor(index=range_.start, time=span.start)

    def fast_forward(self, steps: int):
        for _ in range(steps):
            self.next()

    def get_dtype(self, df: DataFrame) -> list[tuple[str, str]]:
        return [(c, t) for c, t in zip(df.columns, df.dtypes)]

    async def tracker(self):
        pos_tasks = [self.check_position(ticket) for ticket in self.positions.open_items]
        await asyncio.gather(*pos_tasks)
        order_tasks = [self.check_order(ticket) for ticket in self.orders.open_items]
        await asyncio.gather(*order_tasks)
        profit = sum(pos.profit for pos in self.positions.open_positions)
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

    @async_cache
    async def get_price_tick(self, *, symbol: str, time: int) -> Tick | None:
        try:
            if self.config.use_terminal_for_backtesting:
                tick = await self.mt5.copy_ticks_from(symbol, time, 1, CopyTicks.ALL)
                return Tick(tick[-1]) if tick else None
            tick = self.prices[symbol].loc[self.cursor.time]
            return Tick(tick)
        except Exception as exe:
            logger.error(f"Error Getting Price Tick: {exe}")

    @error_handler
    async def check_order(self, ticket: int):
        order = self.orders[ticket]
        order_type, symbol = order.type, order.symbol
        tick = await self.get_price_tick(symbol, self.cursor.time)
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
        pos = self.positions[ticket]
        order_type, symbol, volume, price_open, prev_profit = pos.type, pos.symbol, pos.volume, pos.price_open, pos.profit
        tick = await self.get_price_tick(symbol, self.cursor.time)
        price_current = tick.bid if order_type == OrderType.BUY else tick.ask
        profit = await self.order_calc_profit(order_type, symbol, volume, price_open, price_current, use_terminal)
        self.positions.update(ticket=pos.ticket, profit=profit, price_current=price_current, time_update=self.cursor.time)

    @error_handler(response=False)
    def close_position(self, *, ticket: int) -> bool:
        position = self.positions.pop(ticket)
        margin = self.margins.pop(position.ticket)
        del self.orders[ticket]
        del self.positions[ticket]
        self.orders.update(ticket=ticket, time_done=self.cursor.time)
        self.update_account(gain=position.profit, margin=-margin)
        return True

    @error_handler(response=False)
    def modify_stops(self, *, ticket: int, sl: int = None, tp: int = None) -> bool:
        pos = self.positions[ticket]
        order = self.orders[ticket]
        sl = sl or pos.sl
        tp = tp or pos.tp
        self.positions.update(ticket=ticket, sl=sl, tp=tp, time_update=self.cursor.time)
        sl = sl or order.sl
        tp = tp or order.tp
        self.orders.update(ticket=ticket, sl=sl, tp=tp, time_update=self.cursor.time)
        return True

    def update_account(self, *, profit: float = None, margin: float = 0, gain: float = 0):
        self._account.balance += gain
        self._account.profit = profit if profit is not None else self._account.profit
        self._account.equity = self._account.balance + self._account.profit
        self._account.margin += margin
        self._account.margin_free = self._account.equity - self._account.margin

        if self._account.margin == 0:
            self._account.margin_level = 0
        else:
            mode = self._account.margin_so_mode
            level = self._account.equity / self._account.margin * 100
            self._account.margin_level = level if mode == AccountStopOutMode.PERCENT else self._account.margin_free

    def deposit(self, amount: float):
        self.update_account(gain=amount)

    def withdraw(self, amount: float):
        assert amount <= self._account.balance, 'Insufficient funds'
        self.update_account(gain=-amount)

    @error_handler
    async def setup_account(self, **kwargs):
        default = {'profit': self._account.profit, 'margin': self._account.margin, 'equity': self._account.equity,
                   'margin_free': self._account.margin_free, 'margin_level': self._account.margin_level,
                   'balance': self._account.balance,
                   **{k: v for k, v in kwargs.items() if k in self._account.__match_args__}}

        if self.config.use_terminal_for_backtesting:
            acc_info = await self.mt5.account_info()
            default = {**acc_info._asdict(), **default}

        self._account.set_attrs(**default)
        self.update_account()

    @cached_property
    def prices(self) -> dict[str, DataFrame]:
        return self._data.prices

    @cached_property
    def ticks(self) -> dict[str, DataFrame]:
        return self._data.ticks

    @property
    def rates(self) -> dict[str, dict[str, DataFrame]]:
        return self._data.rates

    @cached_property
    def symbols(self) -> dict[str, SymbolInfo]:
        symbols = {}
        for symbol, info in self._data.symbols.items():
            symbols[symbol] = SymbolInfo((info.get(key) for key in SymbolInfo.__match_args__))
        return symbols

    @error_handler
    async def order_send(self, *, request: dict, use_terminal: bool = True) -> OrderSendResult:
        osr = {'retcode': 10013, 'comment': 'Invalid request',
               'request': TradeRequest(request.get(k, (0 if k != 'comment' else '')) for k in
                                       TradeRequest.__match_args__)}
        trade_order = {'ticket': order_ticket, **{k: v for k, v in request.items() if k in TradeOrder.__match_args__}}
        current_tick = await self.get_price_tick(request.get('symbol'), self.cursor.time)
        if current_tick is None:
            osr['comment'] = 'Market is closed'
            osr['retcode'] = 10018
            return OrderSendResult((osr.get(k, 0) for k in OrderSendResult.__match_args__))
        order_type, symbol = request.get('type'), request.get('symbol', '')
        action, position_ticket = request.get('action'), request.get('position')
        sl, tp, volume, symbol = request.get('sl'), request.get('tp'), request.get('volume'), request.get('symbol')
        order_type = OrderType(order_type)
        current_position = self.positions.get(position_ticket)
        order_ticket = random.randint(100_000_000, 999_999_999)
        deal_ticket = random.randint(100_000_000, 999_999_999)

        # closing an order by an opposite order using a position ticket and Deal action
        if action == TradeAction.DEAL and current_position and order_type.opposite == current_position.type:
            res = self.close_position(current_position.ticket)
            if res:
                trade_order.update({'comment': 'Done', 'position_id': deal_ticket, 'ticket': order_ticket,
                                    'position_by_id': current_position.ticket, 'time_setup': current_tick.time, 'time_expiration': current_tick.time,
                                     'time_setup_msc': current_tick.time_msc, 'time_done': current_tick.time, 'time_done_msc': current_tick.time_msc})
                # ToDo: Create a deal object here?
                # ToDo: Update trade order with more information?
                order = TradeOrder((trade_order.get(k, 0) for k in TradeOrder.__match_args__))
                self.orders[order.ticket] = order
                del self.orders[order.ticket]
                osr.update({'comment': 'Request completed', 'retcode': 10009,
                            'order': order_ticket, 'deal': deal_ticket,})
                # ToDo: remove later
                self.to_json(osr)
            return OrderSendResult((osr.get(k, 0) for k in OrderSendResult.__match_args__))

        if action == TradeAction.SLTP and current_position:
            check = await self.order_check(position_ticket)
            if check.retcode != 0:
                osr = {'retcode': check.retcode, 'comment': check.comment, 'request': check.request}
                return OrderSendResult((osr.get(k, 0) for k in OrderSendResult.__match_args__))

            res = self.modify_stops(ticket=position_ticket, sl=sl, tp=tp)

            if res:
                # ToDo: Create a deal object here
                osr.update({'comment': 'Request completed', 'retcode': 10009, 'order': order_ticket, 'deal': deal_ticket,})
                self.to_json(osr) # ToDo: remove later

            return OrderSendResult((osr.get(k, 0) for k in OrderSendResult.__match_args__))

        if action == TradeAction.DEAL and order_type in (OrderType.BUY, OrderType.SELL):
            check = await self.order_check(request=request)
            if check.retcode != 0:
                osr = {'retcode': check.retcode, 'comment': check.comment, 'request': check.request}
                return OrderSendResult((osr.get(k, 0) for k in OrderSendResult.__match_args__))
            # self.to_json(osr) # ToDo: remove later
            # return OrderSendResult(osr)
            price = current_tick.ask if order_type == OrderType.BUY else current.tick.bid
            # ToDo: Cross check this values with actual values.
            position = {'comment': 'Position Opened', 'ticket': order_ticket, 'symbol': symbol, 'volume': volume,
                   'price_open': price, 'price_current': price, 'type': order_type, 'profit': 0, 'reason': PositionReason.EXPERT,
                   'sl': sl, 'tp': tp, 'time': current_tick.time, 'time_msc': current_tick.time_msc,
                   'time_update': current_tick.time, 'time_update_msc': current_tick.time_msc}

            # ToDo: set time_expiration based on order_type_time
            trade_order.update({'ticket': order_ticket, 'symbol': symbol, 'volume': volume, 'price': price, 'price_current': price, 'sl': sl,
                                 'tp': tp, 'price_open': price, 'type': order_type, 'time_setup': current_tick.time, 'time_setup_msc': current_tick.time_msc,
                                 'volume_current': volume, 'volume_initial': volume, 'position_id': order_ticket})

            pos = TradePosition((position.get(k, 0) for k in TradePosition.__match_args__))
            order = TradeOrder((trade_order.get(k, 0) for k in TradeOrder.__match_args__))
            # ToDo: Create a deal object here

            self.positions[order.ticket] = pos
            self.orders[order.ticket] = order
            osr.update({'order': order_ticket, 'price': price, 'volume': volume, 'bid': tick.bid,
                        'ask': tick.ask, 'deal': deal_ticket})
            margin = await self.order_calc_margin(action, symbol, volume, price, use_)
            self.margins[order_ticket] = margin
            self.update_account(margin=margin)
            self.to_json(osr) # ToDo: remove later
            return OrderSendResult((osr.get(k, 0) for k in OrderSendResult.__match_args__))

    @error_handler
    async def order_check(self, request: dict) -> OrderCheckResult:
        ocr = {'retcode': 10013, 'balance': 0, 'profit': 0, 'margin': 0, 'equity': 0, 'margin_free': 0,
               'margin_level': 0, 'comment': 'Invalid request',
               'request': TradeRequest(request.get(k, (0 if k != 'comment' else '')) for k in
                                       TradeRequest.__match_args__)}

        action, symbol, volume = request.get('action'), request.get('symbol'), request.get('volume')

        price, order_type = request.get('price'), request.get('type')
        if price is None and (action is TradeAction.DEAL and order_type in (OrderType.BUY, OrderType.SELL)):
            ocr['comment'] = 'Market is closed'
            ocr['retcode'] = 10018
            return OrderCheckResult((ocr.get(k, 0) for k in OrderCheckResult.__match_args__))

        # check margin and confirm order can go through
        if action == TradeAction.DEAL and order_type in (OrderType.BUY, OrderType.SELL):
            margin = await self.order_calc_margin(action, symbol, volume, price)
            if margin is None:
                return OrderCheckResult((ocr.get(k, 0) for k in OrderCheckResult.__match_args__))

            used_margin = self._account.margin + margin
            free_margin = self._account.margin_free - margin

            level = self._account.equity / used_margin * 100 if used_margin else float('inf')
            margin_level = level if self._account.margin_so_mode == AccountStopOutMode.PERCENT else free_margin

            ocr.update({'margin_level': margin_level, 'margin': margin, 'margin_free': free_margin})

            # check if the account has enough money
            if margin_level < self._account.margin_so_call:
                ocr['retcode'] = 10019
                ocr['comment'] = 'No money'
                return OrderCheckResult((ocr.get(k, 0) for k in OrderCheckResult.__match_args__))

        # check if the stops level is valid
        sym = await self.get_symbol_info(symbol=symbol)
        sl, tp = request.get('sl', 0), request.get('tp', 0)
        current_price = price
        if tp or sl:
            if action == TradeAction.SLTP:
                pos = self.positions.get(request.get('position')) 
                sym = sym or await self.get_symbol_info(pos.symbol)
                current_tick = sym or await self.get_price_tick(pos.symbol, self.cursor.time)
                current_price = current_tick.bid if pos.type == OrderType.BUY else current_tick.ask
            
            min_sl = min(sl, tp)
            dsl = abs(current_price - min_sl) / sym.point
            tsl = sym.trade_stops_level + sym.spread
            if int(dsl) < int(tsl):
                ocr['retcode'] = 10016
                ocr['comment'] = 'Invalid stops'
                return OrderCheckResult((ocr.get(k, 0) for k in OrderCheckResult.__match_args__))

            elif action == TradeAction.SLTP:
                ocr['comment'] = 'Done'
                ocr['retcode'] = 0
                return OrderCheckResult((ocr.get(k, 0) for k in OrderCheckResult.__match_args__))

        if self.mt5.config.use_terminal_for_backtesting:
            ocr_t = await self.mt5.order_check(request)
            if ocr_t.retcode in (10013, 10014):
                return ocr_t
        elif action == TradeAction.DEAL and order_type in (OrderType.BUY, OrderType.SELL):
            # check volume
            if volume < sym.volume_min or volume > sym.volume_max:
                ocr['retcode'] = 10014
                ocr['comment'] = 'Invalid volume'
                return OrderCheckResult((ocr.get(k, 0) for k in OrderCheckResult.__match_args__))

        ocr.update({'balance': self._account.balance, 'profit': self._account.profit, 'equity': self._account.equity,
                    'comment': 'Done', 'retcode': 0})

        return OrderCheckResult((ocr.get(k, 0) for k in OrderCheckResult.__match_args__))

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
    async def get_symbol_info_tick(self, *, symbol: str) -> Tick | None:
        tick = await self.get_price_tick(symbol, self.cursor.time)
        return tick

    @error_handler
    async def get_symbol_info(self, *, symbol: str) -> SymbolInfo:
        if self.config.use_terminal_for_backtesting:
            info = await self.mt5.symbol_info(symbol)
        else:
            info = self.symbols[symbol]

        tick = await self.get_symbol_info_tick(symbol)
        info = info._asdict() | {'bid': tick.bid, 'bidhigh': tick.bid, 'bidlow': tick.bid, 'ask': tick.ask,
                 'askhigh': tick.ask, 'asklow': tick.bid, 'last': tick.last, 'volume_real': tick.volume_real}
        return SymbolInfo((info.get(key) for key in SymbolInfo.__match_args__))

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
