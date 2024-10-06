import asyncio
from datetime import datetime
from typing import Literal
from itertools import zip_longest
import random
from functools import cached_property
from logging import getLogger

import pandas as pd
import pytz
import numpy as np
from pandas import DataFrame
from MetaTrader5 import (Tick, SymbolInfo, AccountInfo, TradeOrder, TradePosition, TradeDeal,
                         TradeRequest, OrderCheckResult, OrderSendResult, TerminalInfo)

from ...core.meta_trader import MetaTrader
from ...core.constants import (TimeFrame, OrderType, TradeAction, AccountStopOutMode, PositionReason,
                                   DealType, DealReason, DealEntry, OrderReason, CopyTicks)

from ..._utils import round_down, round_up, error_handler, error_handler_sync, async_cache

from .get_data import TestData, GetData, Cursor
from .backtest_account import BackTestAccount
from .trades_manager import PositionsManager, OrdersManager, DealsManager

logger = getLogger(__name__)


class BackTestEngine:
    mt5: MetaTrader
    span: range
    range: range
    cursor: Cursor
    iter: zip_longest
    rates: dict[str, dict[int, DataFrame]]
    ticks: dict[str, DataFrame]
    prices: dict[str, DataFrame]
    orders: OrdersManager
    deals: DealsManager
    positions: PositionsManager
    _account: BackTestAccount


    def __init__(self, *, data: TestData = None, speed: int = 1, start: float | datetime = 0,
                 end: float | datetime = 0, restart: bool = False, name: str = ''):
        self._data = data or TestData()
        self.mt5 = MetaTrader()
        self.config = self.mt5.config
        self.config.backtest_engine = self
        self.set_up(start=start, end=end, speed=speed, restart=restart)
        self.prepare_data()
        start, end = (self.span[0], self.span[-1]) if self.span else ((now := datetime.now(pytz.UTC).timestamp()), now)
        _name = f"{datetime.fromtimestamp(start):%d-%m-%y}_{datetime.fromtimestamp(end):%d-%m-%y}"
        self.name = name or _name

    def __next__(self) -> Cursor:
        try:
            index, time = next(self.iter)
            self.cursor = Cursor(index=index, time=time)
            return self.cursor
        except StopIteration:
            logger.warning('End of time')

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def set_up(self, *, start: float | datetime = 0, end: float | datetime = 0, speed: int = 1, restart: bool = False):
        span_start = (int(start.timestamp()) if isinstance(start, datetime) else int(start)) or self._data.span.start
        span_end = (int(end.timestamp()) if isinstance(end, datetime) else int(end)) or self._data.span.stop
        self.span = range(span_start, span_end, speed)
        self.range = range(0, span_end - span_start, speed)
        self.iter = zip_longest(self.range, self.span)

        if restart and self._data.cursor is not None:
            self.cursor = self._data.cursor
            self.go_to(time=self.cursor.time)
        else:
            self.cursor: Cursor = self._data.cursor or Cursor(index=self.range.start, time=self.span.start)

    def prepare_data(self):
        orders = {}
        for ticket, order in self._data.orders.items():
            orders[ticket] = TradeOrder((order.get(k) for k in TradeOrder.__match_args__))
        self.orders = OrdersManager(data=orders)

        positions = {}
        for ticket, position in self._data.positions.items():
            positions[ticket] = TradePosition((position.get(k) for k in TradePosition.__match_args__))
        self.positions = PositionsManager(data=positions, open_positions=self._data.open_positions,
                                          margins=self._data.margins)

        deals = {}
        for ticket, deal in self._data.deals.items():
            deals[ticket] = TradeDeal((deal.get(k) for k in TradeDeal.__match_args__))
        self.deals = DealsManager(data=deals)

        self._account: BackTestAccount = BackTestAccount(**self._data.account)

    def next(self) -> Cursor:
        return next(self)

    @property
    def data(self):
        return self._data

    def reset(self):
        self.iter = zip_longest(self.range, self.span)
        self.cursor = Cursor(index=self.range.start, time=self.span.start)

    def go_to(self, *, time: datetime | float):
        time =  int(time.timestamp()) if isinstance(time, datetime) else int(time)
        steps = time - self.cursor.time

        if steps > 0:
            self.fast_forward(steps=steps)
            return

        range_start = time - self.span.start
        span = range(time, self.span.stop, self.span.step)
        range_ = range(range_start, self.range.stop, self.range.step)
        self.iter = zip_longest(range_, span)
        self.cursor = Cursor(index=range_.start, time=span.start)

    def fast_forward(self, *, steps: int):
        for _ in range(steps):
            self.next()

    @staticmethod
    def get_dtype(*, df: DataFrame) -> list[tuple[str, str]]:
        return [(c, t) for c, t in zip(df.columns, df.dtypes)]

    async def tracker(self):
        pos_tasks = [self.check_position(ticket=ticket) for ticket in self.positions._open_positions]
        await asyncio.gather(*pos_tasks)
        profit = sum(pos.profit for pos in self.positions.open_positions)
        self.update_account(profit=profit)

    def wrap_up(self):
        try:
            self._data.deals = self.deals.to_dict()
            self._data.orders = self.orders.to_dict()
            self._data.positions = self.positions.to_dict()
            self._data.open_positions = self.positions._open_positions
            self._data.margins = self.positions.margins
            self._data.account = self._account.asdict()
            name = self._data.name or self.name
            path = self.config.backtest_dir/f"{name}.pkl"
            GetData.pickle_data(data=self._data, name=path)
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
    async def check_order(self, *, ticket: int):
        """"
        Check if the order has reached its take profit or stop loss levels and close the order if it has.
        Checks only **OrderType.BUY** and **OrderType.SELL** orders that have reached their take profit or stop loss levels.

        Args:
            ticket (int): Order ticket
        """
        order = self.orders[ticket]
        order_type, symbol = order.type, order.symbol
        tick = await self.get_price_tick(symbol=symbol, time=self.cursor.time)
        tp, sl = order.tp, order.sl

        if not (tp and sl):
            return

        match order_type:
            case OrderType.BUY:
                if tp >= tick.bid or sl <= tick.bid:
                    self.close_position(ticket=ticket)

            case OrderType.SELL:
                if tp <= tick.ask or sl >= tick.ask:
                    self.close_position(ticket=ticket)
            case _:
                ...

    @error_handler
    async def check_position(self, *, ticket: int):
        """
        Update the profit of an open position based on the current price of the symbol.

        Args:
            ticket (int): Position ticket
        """
        pos = self.positions[ticket]
        order_type, symbol, volume, price_open, prev_profit = (pos.type, pos.symbol, pos.volume, pos.price_open,
                                                               pos.profit)
        tick = await self.get_price_tick(symbol=symbol, time=self.cursor.time)
        price_current = tick.bid if order_type == OrderType.BUY else tick.ask
        profit = await self.order_calc_profit(action=order_type, symbol=symbol, volume=volume,
                                              price_open=price_open, price_close=price_current)
        self.positions.update(ticket=pos.ticket, profit=profit, price_current=price_current,
                              time_update=self.cursor.time)
        await self.check_order(ticket=ticket)

    @error_handler_sync(response=False)
    def close_position(self, *, ticket: int) -> bool:
        """
        Close an open position for the trading account using the position ticket.

        Args:
            ticket: Position ticket

        Returns:
            bool: True if the position is closed successfully, False otherwise
        """
        position = self.positions[ticket]
        margin = self.positions.get_margin(ticket=ticket)
        self.positions.delete_margin(ticket=ticket)
        self.positions.close(ticket=ticket)
        self.orders.update(ticket=ticket, time_done=self.cursor.time, time_done_msc=self.cursor.time*1000)
        self.update_account(gain=position.profit, margin=-margin)
        return True

    @error_handler(response=False)
    def modify_stops(self, *, ticket: int, sl: int, tp: int) -> bool:
        """
        Modify the stop loss and take profit levels of an open position.

        Args:
            ticket: Position ticket
            sl: stop loss level
            tp: Take profit level

        Returns:
            bool: True if the stops are modified successfully, False otherwise
        """
        self.positions.update(ticket=ticket, sl=sl, tp=tp, time_update=self.cursor.time,
                              time_update_msc=self.cursor.time*1000)
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
        prices = {}
        for symbol in self._data.prices.keys():
            res = self._data.prices[symbol]
            res = pd.DataFrame(res)
            res.drop_duplicates(subset=['time'], keep='last', inplace=True)
            res.set_index('time', inplace=True, drop=False)
            res.reindex(self.span) # fill in missing values with NaN
            prices[symbol] = res
        return prices

    @cached_property
    def ticks(self) -> dict[str, DataFrame]:
        ticks = {}
        for symbol in self._data.ticks.keys():
            res = self._data.ticks[symbol]
            res = pd.DataFrame(res)
            res.drop_duplicates(subset=['time'], keep='last', inplace=True)
            res.set_index('time', inplace=True, drop=False)
            ticks[symbol] = res
        return ticks

    @cached_property
    def rates(self) -> dict[str, dict[int, DataFrame]]:
        rates = {}
        for symbol in self._data.rates.keys():
            for timeframe in self._data.rates[symbol].keys():
                res = self._data.rates[symbol][timeframe]
                res = pd.DataFrame(res)
                res.drop_duplicates(subset=['time'], keep='last', inplace=True)
                res.set_index('time', inplace=True, drop=False)
                rates[symbol][timeframe] = res
        return rates

    @cached_property
    def symbols(self) -> dict[str, SymbolInfo]:
        symbols = {}
        for symbol, info in self._data.symbols.items():
            symbols[symbol] = SymbolInfo((info.get(key) for key in SymbolInfo.__match_args__))
        return symbols

    @error_handler
    async def order_send(self, *, request: dict) -> OrderSendResult:
        osr = {'retcode': 10013, 'comment': 'Invalid request',
               'request': TradeRequest(request.get(k, (0 if k != 'comment' else '')) for k in
                                       TradeRequest.__match_args__)}
        current_tick = await self.get_price_tick(request.get('symbol'), self.cursor.time)
        if current_tick is None:
            osr['comment'] = 'Market is closed'
            osr['retcode'] = 10018
            return OrderSendResult((osr.get(k, 0) for k in OrderSendResult.__match_args__))

        trade_order = {'external_id': '', 'comment': '',
                       **{k: v for k, v in request.items() if k in TradeOrder.__match_args__}}
        order_type, symbol = request.get('type'), request.get('symbol', '')
        action, position_id = request.get('action'), request.get('position')
        sl, tp, volume, symbol = request.get('sl'), request.get('tp'), request.get('volume'), request.get('symbol')
        order_type = OrderType(order_type)
        current_position = self.positions.get(position_id)
        order_ticket = random.randint(100_000_000, 999_999_999)
        deal_ticket = random.randint(100_000_000, 999_999_999)

        # closing an order by an opposite order using a position ticket and Deal action
        if action == TradeAction.DEAL and current_position and order_type.opposite == current_position.type:
            res = self.close_position(current_position.ticket)
            if res:
                price_current = current_tick.ask if order_type == OrderType.BUY else current_tick.bid
                trade_order.update({'position_id': current_position.ticket, 'ticket': order_ticket,
                                    'time_setup': current_tick.time, 'time_setup_msc': current_tick.time_msc,
                                    'time_done': current_tick.time, 'time_done_msc': current_tick.time_msc,
                                    'type': order_type, 'symbol': symbol, 'sl': current_position.sl,
                                    'tp': current_position.tp,
                                    'price_current': price_current, 'reason': OrderReason.EXPERT,
                                    'volume_initial': current_position.volume})

                # TODO: calculate commission and swap if possible or necessary
                deal = {'ticket': deal_ticket, 'position_id': current_position.ticket, 'order': order_ticket,
                        'symbol': symbol, 'time': current_tick.time,
                        'time_msc': current_tick.time_msc, 'volume': current_position.volume,
                        'price': price_current, 'type': DealType(order_type), 'reason': DealReason.EXPERT,
                        'entry': DealEntry.OUT, 'comment': '', 'external_id': ''}

                order = TradeOrder((trade_order.get(k, 0) for k in TradeOrder.__match_args__))
                self.orders[order.ticket] = order
                deal = TradeDeal((deal.get(k, 0) for k in TradeDeal.__match_args__))
                self.deals[deal.ticket] = deal
                osr.update({'comment': 'Request completed', 'retcode': 10009,
                            'order': order_ticket, 'deal': deal_ticket,})
            return OrderSendResult((osr.get(k, 0) for k in OrderSendResult.__match_args__))

        if action == TradeAction.SLTP and current_position:
            check = await self.order_check(position_id)
            if check.retcode != 0:
                osr = {'retcode': check.retcode, 'comment': check.comment, 'request': check.request}
                return OrderSendResult((osr.get(k, 0) for k in OrderSendResult.__match_args__))
            res = self.modify_stops(ticket=position_id, sl=sl, tp=tp)
            if res:
                osr.update({'comment': 'Request completed', 'retcode': 10009, 'order': order_ticket,
                            'deal': deal_ticket})
            return OrderSendResult((osr.get(k, 0) for k in OrderSendResult.__match_args__))

        if action == TradeAction.DEAL and order_type in (OrderType.BUY, OrderType.SELL):
            check = await self.order_check(request=request)
            if check.retcode != 0:
                osr = {'retcode': check.retcode, 'comment': check.comment, 'request': check.request}
                return OrderSendResult((osr.get(k, 0) for k in OrderSendResult.__match_args__))

            price = current_tick.ask if order_type == OrderType.BUY else current_tick.bid
            position = {'ticket': order_ticket, 'symbol': symbol, 'volume': volume,
                   'price_open': price, 'price_current': price, 'type': order_type, 'profit': 0,
                   'reason': PositionReason.EXPERT, 'identifier': order_ticket,
                   'sl': sl, 'tp': tp, 'time': current_tick.time, 'time_msc': current_tick.time_msc,
                   'time_update': current_tick.time, 'time_update_msc': current_tick.time_msc}

            deal = {'ticket': deal_ticket, 'order': order_ticket, 'symbol': symbol, 'commission': 0, 'swap': 0,
                    'position_id': order_ticket, 'fee': 0, 'time': current_tick.time, 'time_msc': current_tick.time_msc,
                    'volume': volume, 'price': price, 'type': DealType(order_type), 'reason': DealReason.EXPERT,
                    'entry': DealEntry.IN}

            # ToDo: set time_expiration based on order_type_time
            trade_order.update({'ticket': order_ticket, 'symbol': symbol, 'volume': volume, 'price': price,
                                'price_current': price, 'sl': sl, 'time_setup_msc': current_tick.time_msc,
                                'tp': tp, 'price_open': price, 'type': order_type, 'time_setup': current_tick.time,
                                'volume_current': volume, 'volume_initial': volume, 'position_id': order_ticket})

            pos = TradePosition((position.get(k, 0) for k in TradePosition.__match_args__))
            order = TradeOrder((trade_order.get(k, 0) for k in TradeOrder.__match_args__))
            deal = TradeDeal((deal.get(k, 0) for k in TradeDeal.__match_args__))
            self.deals[deal_ticket] = deal
            self.positions[order.ticket] = pos
            self.orders[order.ticket] = order
            osr.update({'order': order_ticket, 'price': price, 'volume': volume, 'bid': current_tick.bid,
                        'ask': current_tick.ask, 'deal': deal_ticket})
            margin = await self.order_calc_margin(action=action, symbol=symbol, volume=volume, price=price)
            self.positions.set_margin(ticket=order_ticket, margin=margin)
            self.update_account(margin=margin)
            return OrderSendResult((osr.get(k, 0) for k in OrderSendResult.__match_args__))

    @error_handler
    async def order_check(self, *, request: dict) -> OrderCheckResult:
        ocr = {'retcode': 10013, 'balance': 0, 'profit': 0, 'margin': 0, 'equity': 0, 'margin_free': 0,
               'margin_level': 0, 'comment': 'Invalid request',
               'request': TradeRequest(request.get(k, (0 if k != 'comment' else '')) for k in
                                       TradeRequest.__match_args__)}

        action, symbol, volume = request.get('action'), request.get('symbol'), request.get('volume')
        price, order_type, position_id = request.get('price'), request.get('type'), request.get('position')

        # check margin and confirm order can go through for a deal action and buy or sell order type
        if action == TradeAction.DEAL and order_type in (OrderType.BUY, OrderType.SELL) and position_id is None:
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
        sl, tp = request.get('sl'), request.get('tp')
        current_price = price
        if tp and sl:
            if action == TradeAction.SLTP:
                pos = self.positions.get(request.get('position'))
                sym = await self.get_symbol_info(pos.symbol)
                current_tick = sym or await self.get_price_tick(pos.symbol, self.cursor.time)
                current_price = current_tick.bid if pos.type == OrderType.BUY else current_tick.ask

            min_sl = min(sl, tp)
            dsl = abs(current_price - min_sl) / sym.point
            tsl = sym.trade_stops_level + sym.spread
            if dsl < tsl:
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

        rates = self.rates[symbol][timeframe]
        start = int(datetime.timestamp(date_from)) if isinstance(date_from, datetime) else int(date_from)
        start = round_down(start, timeframe.time)
        rates = rates[rates.time <= start].iloc[-count:]
        return np.fromiter((tuple(i) for i in rates.iloc), dtype=self.get_dtype(df=rates))

    @error_handler
    async def get_rates_from_pos(self, symbol: str, timeframe: TimeFrame, start_pos: int, count: int) -> np.ndarray:
        if self.config.use_terminal_for_backtesting:
            now = datetime.now(tz=pytz.UTC)
            b_now = self.cursor.time
            diff = (now.timestamp() - b_now) // timeframe.time
            start_pos = int(diff + start_pos)
            res = await self.mt5.copy_rates_from_pos(symbol, timeframe, start_pos, count)
            return res

        rates = self.rates[symbol][timeframe]
        end = abs(self.cursor.index - start_pos)
        start = abs(end - count)
        rates = rates.iloc[start:end]
        return np.fromiter((tuple(i) for i in rates.iloc), dtype=self.get_dtype(df=rates))

    @error_handler
    async def get_rates_range(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float,
                              date_to: datetime | float) -> np.ndarray:
        if self.config.use_terminal_for_backtesting:
            rates = await self.mt5.copy_rates_range(symbol, timeframe, date_from, date_to)
            return rates

        rates = self.rates[symbol][timeframe]
        start = int(datetime.timestamp(date_from)) if isinstance(date_from, datetime) else int(date_from)
        start = round_down(start, timeframe.time)
        end = int(datetime.timestamp(date_to)) if isinstance(date_to, datetime) else int(date_to)
        end = round_up(end, timeframe.time)
        rates = rates[(rates.time >= start) & (rates.time <= end)]
        return np.fromiter((tuple(i) for i in rates.iloc), dtype=self.get_dtype(df=rates))

    @error_handler
    async def get_ticks_from(self, *, symbol: str, date_from: datetime | float, count: int,
                             flags: CopyTicks) -> np.ndarray:
        if self.config.use_terminal_for_backtesting:
            ticks = await self.mt5.copy_ticks_from(symbol, date_from, count, flags)
            return ticks

        ticks = self.ticks[symbol]
        start = int(datetime.timestamp(date_from)) if isinstance(date_from, datetime) else int(date_from)
        ticks = ticks[ticks.time <= start].iloc[-count:]
        return np.fromiter((tuple(i) for i in ticks.iloc), dtype=self.get_dtype(df=ticks))

    @error_handler
    async def get_ticks_range(self, *, symbol: str, date_from: datetime | float,
                              date_to: datetime | float, flags: CopyTicks) -> np.ndarray:
        if self.config.use_terminal_for_backtesting:
            ticks = await self.mt5.copy_ticks_range(symbol, date_from, date_to, flags)
            return ticks

        ticks = self.ticks[symbol]
        start = int(datetime.timestamp(date_from)) if isinstance(date_from, datetime) else int(date_from)
        end = int(datetime.timestamp(date_to)) if isinstance(date_to, datetime) else int(date_to)
        ticks = ticks[(ticks.time >= start) & (ticks.time <= end)]
        return np.fromiter((tuple(i) for i in ticks.iloc), dtype=self.get_dtype(df=ticks))

    @error_handler
    async def order_calc_margin(self, *, action: Literal[OrderType.BUY, OrderType.SELL], symbol: str, volume: float,
                                price: float):
        if self.mt5.config.use_terminal_for_backtesting:
            return await self.mt5.order_calc_margin(action, symbol, volume, price)

        sym = self.symbols[symbol]
        margin = (volume * sym.trade_contract_size * price) / (self._account.leverage / (sym.margin_initial or 1))
        return round(margin, self._account.currency_digits)

    @error_handler
    async def order_calc_profit(self, *, action: Literal[OrderType.BUY, OrderType.SELL], symbol: str, volume: float,
                                price_open: float, price_close: float):

        if self.mt5.config.use_terminal_for_backtesting:
            return await self.mt5.order_calc_profit(action, symbol, volume, price_open, price_close)

        sym = self.symbols[symbol]
        profit = (volume * sym.trade_contract_size *
                  ((price_close - price_open) if action == OrderType.BUY else (price_open - price_close)))
        return round(profit, self._account.currency_digits)

    @error_handler_sync
    def get_orders_total(self) -> int:
        """
        Get the total number of pending orders.

        Returns:
            int: Total number of pending orders
        """
        return 0

    @error_handler_sync
    def get_orders(self, symbol: str = '', group: str = '', ticket: int = None) -> tuple[TradeOrder, ...]:
        """
        Get pending orders from the terminal history. This has to do with pending orders, which this backtester
        doesn't support yet.

        Args:
            symbol: Symbol name
            group: Group name
            ticket: Order ticket

        Returns:
            tuple[TradeOrder]
        """
        if symbol and group and ticket:
            return tuple()
        return ()

    @error_handler_sync
    def get_positions_total(self) -> int:
        """
        Get the total number of open positions.

        Returns:
            int: Total number of open positions
        """
        return self.positions.positions_total()

    @error_handler_sync
    def get_positions(self, *, symbol: str = None, group: str = None, ticket: int = None) -> tuple[TradePosition, ...]:
        """
        Get open positions from the terminal history.

        Keyword Args:
            symbol: The symbol name
            group: Group argument to filter by
            ticket: Position ticket

        Returns:
            tuple[TradePosition]: Open positions
        """
        return self.positions.positions_get(ticket=ticket, symbol=symbol, group=group)

    @error_handler_sync
    def get_history_orders_total(self, *, date_from: datetime | float, date_to: datetime | float) -> int:
        """
        Get the total number of orders in the terminal history.

        Args:
            date_from: The start date of the history

            date_to: The end date of the history

        Returns:
            int: Total number of orders in the history
        """
        return self.orders.history_orders_total(date_from=date_from, date_to=date_to)

    @error_handler_sync
    def get_history_orders(self, *, date_from: datetime | float = None, date_to: datetime | float = None,
                           group: str = '', ticket: int = None, position: int = None) -> tuple[TradeOrder, ...]:
        """
        Get orders from the terminal history.

        Keyword Args:
            date_from: Date from which to start the history
            date_to: Date to which to end the history
            group: group keyword to filter by
            ticket: ticket id to filter by
            position: position id to filter by

        Returns:
            tuple[TradeOrder]: Orders in the history
        """
        return self.orders.history_orders_get(date_from=date_from, date_to=date_to, group=group, ticket=ticket,
                                              position=position)

    @error_handler_sync
    def get_history_deals_total(self, *, date_from: datetime | float, date_to: datetime | float) -> int:
        """
        Get the total number of deals in the terminal history.

        Args:
            date_from: Date from which to start the history
            date_to: Date to which to end the history

        Returns:
            int: Total number of deals in the history
        """
        return self.deals.history_deals_total(date_from=date_from, date_to=date_to)

    @error_handler_sync
    def get_history_deals(self, *, date_from: datetime | float = None, date_to: datetime | float = None,
                          group: str = None, position: int = None, ticket: int = None) -> tuple[TradeDeal, ...]:
        """
        Get deals from the terminal history.

        Keyword Args:
            date_from: Date from which to start the history
            date_to: Date to which to end the history
            group: group keyword to filter by
            position: position id to filter by
            ticket: ticket id to filter by

        Returns:
            tuple[TradeDeal, ...]: Deals in the history
        """
        return self.deals.history_deals_get(date_from=date_from, date_to=date_to, group=group, position=position,
                                            ticket=ticket)
