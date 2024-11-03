from threading import RLock
import asyncio
import json
from datetime import datetime, UTC
from typing import Literal
from itertools import zip_longest
import random
from functools import cached_property
from logging import getLogger
from pathlib import Path

import pandas as pd
import numpy as np
from pandas import DataFrame
from MetaTrader5 import (
    Tick,
    SymbolInfo,
    AccountInfo,
    TradeOrder,
    TradePosition,
    TradeDeal,
    TradeRequest,
    OrderCheckResult,
    OrderSendResult,
    TerminalInfo,
)

from ..meta_trader import MetaTrader
from ..constants import (
    TimeFrame,
    OrderType,
    TradeAction,
    AccountStopOutMode,
    PositionReason,
    DealType,
    DealReason,
    DealEntry,
    OrderReason,
    CopyTicks,
)

from ..._utils import (
    round_down,
    round_up,
    error_handler,
    error_handler_sync,
    async_cache,
)

from .get_data import BackTestData, GetData, Cursor
from .backtest_account import BackTestAccount
from .trades_manager import PositionsManager, OrdersManager, DealsManager

logger = getLogger(__name__)


class BackTestEngine:
    mt5: MetaTrader
    span: range
    range: range
    speed: int
    cursor: Cursor
    iter: zip_longest
    rates: dict[str, dict[int, DataFrame]]
    ticks: dict[str, DataFrame]
    prices: dict[str, DataFrame]
    orders: OrdersManager
    deals: DealsManager
    positions: PositionsManager
    _account: BackTestAccount
    stop_testing: bool
    use_terminal: bool
    restart: bool
    stop_time: int | None
    close_open_positions_on_exit: bool
    preloaded_ticks: dict[str, DataFrame]
    preload: bool
    account_lock: RLock
    use_termial_in_tracker: bool

    def __init__(
        self,
        *,
        data: BackTestData = None,
        speed: int = 60,
        start: float | datetime = 0,
        end: float | datetime = 0,
        restart: bool = True,
        use_terminal: bool = None,
        name: str = "",
        stop_time: float | datetime = None,
        close_open_positions_on_exit: bool = False,
        preload=True,
        assign_to_config: bool = False,
        use_termial_in_tracker: bool = False,
    ):
        self._data = data or BackTestData()
        self.mt5 = MetaTrader()
        self.config = self.mt5.config
        if assign_to_config:
            self.config.backtest_engine = self
        self.setup_test_range(start=start, end=end, speed=speed, restart=restart)
        self.setup_data(restart=restart)
        start, end = (
            (self.span[0], self.span[-1])
            if len(self.span) >= 2
            else ((now := datetime.now(UTC).timestamp()), now)
        )
        start, end = datetime.fromtimestamp(start, tz=UTC), datetime.fromtimestamp(
            end, tz=UTC
        )
        self.name = (
            name or self._data.name or f"backtest_data_{start:%d_%m_%y}_{end:%d_%m_%y}"
        )
        self.stop_testing = False
        self.use_terminal = (
            self.config.use_terminal_for_backtesting
            if use_terminal is None
            else use_terminal
        )
        self.close_open_positions_on_exit = close_open_positions_on_exit
        if stop_time is not None:
            val = (
                stop_time.astimezone(tz=UTC)
                if isinstance(stop_time, datetime)
                else datetime.fromtimestamp(stop_time, tz=UTC)
            )
            stop_time = int(val.timestamp())
        self.stop_time = stop_time
        self.preload = preload
        self.preloaded_ticks = {}
        self.account_lock = RLock()

    def __next__(self) -> Cursor:
        try:
            index, time = next(self.iter)
            if self.stop_time and time >= self.stop_time:
                raise StopIteration
            self.cursor = Cursor(index=index, time=time)
            return self.cursor
        except StopIteration:
            logger.critical("End of the test range")
            self.stop_testing = True

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def setup_test_range(
        self,
        *,
        start: float | datetime = None,
        end: float | datetime = None,
        speed: int = 60,
        restart: bool = True,
    ):
        if self._data.span and self._data.range:
            start = start or self._data.span[0]
            end = end or self._data.span[-1] + 1
        start = (
            start.astimezone(tz=UTC)
            if isinstance(start, datetime)
            else datetime.fromtimestamp(start, tz=UTC)
        )
        end = (
            end.astimezone(tz=UTC)
            if isinstance(end, datetime)
            else datetime.fromtimestamp(end, tz=UTC)
        )
        span_start = int(start.timestamp())
        span_end = int(end.timestamp())
        self.speed = speed
        self.span = range(span_start, span_end, speed)
        self.range = range(0, span_end - span_start, speed)
        self.iter = zip_longest(self.range, self.span)

        if restart is False and self._data.cursor is not None:
            self.cursor = self._data.cursor
            self.go_to(time=self.cursor.time)
        else:
            self.cursor = Cursor(index=self.range.start, time=self.span.start)

    def setup_data(self, *, restart: bool = True):
        if restart is True:
            self.orders = OrdersManager()
            self.positions = PositionsManager()
            self.deals = DealsManager()
            self._account = BackTestAccount()
            return

        orders = {}
        for ticket, order in self._data.orders.items():
            orders[ticket] = TradeOrder(
                (order.get(k) for k in TradeOrder.__match_args__)
            )
        self.orders = OrdersManager(data=orders)

        positions = {}
        for ticket, position in self._data.positions.items():
            positions[ticket] = TradePosition(
                (position.get(k) for k in TradePosition.__match_args__)
            )
        self.positions = PositionsManager(
            data=positions,
            open_positions=self._data.open_positions,
            margins=self._data.margins,
        )

        deals = {}
        for ticket, deal in self._data.deals.items():
            deals[ticket] = TradeDeal((deal.get(k) for k in TradeDeal.__match_args__))
        self.deals = DealsManager(data=deals)

        self._account = BackTestAccount(**self._data.account)

    def next(self) -> Cursor:
        return next(self)

    @property
    def data(self):
        return self._data

    def reset(self, clear_data: bool = False):
        self.iter = zip_longest(self.range, self.span)
        self.cursor = Cursor(index=self.range.start, time=self.span.start)
        if clear_data:
            self.setup_data(restart=True)

    def go_to(self, *, time: datetime | float):
        time = (
            time.astimezone(tz=UTC)
            if isinstance(time, datetime)
            else datetime.fromtimestamp(time, tz=UTC)
        )
        time = int(time.timestamp())
        steps = time - self.cursor.time
        steps = steps // self.speed
        if 0 <= steps < (len(self.range) - 1):
            self.fast_forward(steps=steps)
            return
        raise ValueError("Can't go back in time or beyond the limits of the range")

    def fast_forward(self, *, steps: int):
        for _ in range(steps):
            self.next()

    @staticmethod
    def get_dtype(*, df: DataFrame) -> list[tuple[str, str]]:
        return [(c, t) for c, t in zip(df.columns, df.dtypes)]

    async def tracker(self):
        try:
            pos_tasks = [
                self.check_position(ticket=ticket)
                for ticket in self.positions._open_positions
            ]
            await asyncio.gather(*pos_tasks)
            profit = sum(pos.profit for pos in self.positions.open_positions)
            self.update_account(profit=profit)
            self.check_account()
        except Exception as exe:
            logger.critical("Error in tracker: %s at %d", exe, self.cursor.time)

    @error_handler_sync
    def save_result_to_json(self):
        data = self._account.get_dict(
            include={
                "balance",
                "profit",
                "equity",
                "margin",
                "margin_free",
                "margin_level",
            }
        )
        wins = [
            position
            for ticket in self.positions
            if (position := self.positions.get(ticket)).profit > 0
        ]
        losses = [
            position
            for ticket in self.positions
            if (position := self.positions.get(ticket)).profit <= 0
        ]
        win = round(
            sum(position.profit for position in wins), self._account.currency_digits
        )
        loss = round(
            sum(position.profit for position in losses), self._account.currency_digits
        )
        profit_factor = round(abs(win / loss), 2) if loss != 0 else 0
        wins, losses, total = len(wins), len(losses), len(self.positions._data)
        win_percentage = round(wins / total * 100, 2) if total > 0 else 0
        net_profit = round(win - abs(loss), self._account.currency_digits)
        profitability = (
            net_profit / (self._account.balance - net_profit) * 100
            if net_profit != 0
            else 0
        )
        profitability = round(profitability, 2)
        data.update(
            {
                "wins": wins,
                "losses": losses,
                "total": total,
                "win_percentage": win_percentage,
                "win": win,
                "loss": loss,
                "net_profit": net_profit,
                "profit_factor": profit_factor,
                "profitability": profitability,
            }
        )
        path = Path(self.config.backtest_dir / f"{self.name}.json")
        with path.open("w") as file:
            json.dump(data, file, indent=4)

    async def close_all_open(self):
        tasks = [
            self.check_position(ticket=position.ticket)
            for position in self.positions.open_positions
        ]
        await asyncio.gather(*tasks)
        for position in self.positions.open_positions:
            await self.close_position_manually(ticket=position.ticket)

    @error_handler
    async def wrap_up(self):
        if self.close_open_positions_on_exit:
            await self.close_all_open()
        self.save_result_to_json()
        self._data.deals = self.deals.to_dict()
        self._data.orders = self.orders.to_dict()
        self._data.positions = self.positions.to_dict()
        self._data.open_positions = self.positions._open_positions
        self._data.margins = self.positions.margins
        self._data.account = self._account.asdict()
        self._data.cursor = self.cursor
        self._data.span = self.span
        self._data.range = self.range
        self._data.account = self._account.asdict()
        name = self._data.name or self.name
        self._data.name = name
        path = self.config.backtest_dir / f"{name}.pkl"
        GetData.pickle_data(data=self._data, name=path)

    async def preload_ticks(self, *, symbol: str):
        """Pull a month data on ticks from the terminal. Starting from the current time"""
        try:
            start = self.cursor.time
            end = start + (30 * 24 * 60 * 60)
            end = end if end < self.span.stop else self.span.stop
            span = range(start, end)
            start = datetime.fromtimestamp(start, tz=UTC)
            end = datetime.fromtimestamp(end, tz=UTC)
            ticks = await self.mt5.copy_ticks_range(symbol, start, end, CopyTicks.ALL)
            ticks = pd.DataFrame(ticks)
            ticks.drop_duplicates(subset=["time"], keep="last", inplace=True)
            ticks.set_index("time", inplace=True, drop=False)
            ticks = ticks.reindex(span, method="nearest", copy=True)
            self.preloaded_ticks[symbol] = ticks
        except Exception as exe:
            logger.error(f"Error Preloading Ticks: {exe}")

    @async_cache
    async def get_price_tick(self, *, symbol: str, time: int) -> Tick | None:
        try:
            if self.use_terminal and self.preload:
                if (
                    ticks := self.preloaded_ticks.get(symbol)
                ) is not None and time in ticks.index:
                    return Tick(ticks.loc[time])
                await self.preload_ticks(symbol=symbol)
                tick = self.preloaded_ticks[symbol].loc[time]
                return Tick(tick)

            elif self.use_terminal and self.preload is False:
                time = datetime.fromtimestamp(time, tz=UTC)
                tick = await self.mt5.copy_ticks_from(symbol, time, 1, CopyTicks.ALL)
                return Tick(tick[-1]) if tick is not None else None
            else:
                tick = self.prices[symbol].loc[time]
                return Tick(tick)
        except Exception as exe:
            logger.error("Error Getting Price Tick: %s", exe)

    @error_handler
    async def check_order(self, *, ticket: int):
        """ "
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

        deal = {
            "ticket": random.randint(100_000_000, 199_999_999),
            "order": ticket,
            "symbol": symbol,
            "commission": 0,
            "swap": 0,
            "position_id": ticket,
            "fee": 0,
            "time": self.cursor.time,
            "time_msc": self.cursor.time * 1000,
            "price": tick.bid,
            "type": DealType(order_type),
            "reason": DealReason.EXPERT,
            "entry": DealEntry.OUT,
            "profit": 0,
        }

        match order_type:
            case OrderType.BUY:
                if tick.bid >= tp or tick.bid <= sl:
                    res = await self.close_position(ticket=ticket)
                    if res:
                        pos = self.positions.get(ticket)
                        deal.update({"profit": pos.profit, "volume": pos.volume})
                        self.deals[deal["ticket"]] = TradeDeal(
                            (deal.get(k, 0) for k in TradeDeal.__match_args__)
                        )

            case OrderType.SELL:
                if tick.ask <= tp or tick.ask >= sl:
                    res = await self.close_position(ticket=ticket)
                    if res:
                        pos = self.positions.get(ticket)
                        deal.update({"profit": pos.profit, "volume": pos.volume})
                        self.deals[deal["ticket"]] = TradeDeal(
                            (deal.get(k, 0) for k in TradeDeal.__match_args__)
                        )
            case _:
                ...

    def check_account(self):
        account = self._account
        level = (
            account.margin_level
            if account.margin_so_mode == AccountStopOutMode.PERCENT
            else account.margin_so_call
        )
        if level < account.margin_so_call and level != 0 and account.equity < 0:
            logger.critical(
                "Account has burned out!!! Please top up to continue trading"
            )
            self.stop_testing = True

    async def check_position(self, *, ticket: int):
        """
        Update the profit of an open position based on the current price of the symbol.

        Args:
            ticket (int): Position ticket
        """
        pos = self.positions[ticket]
        order_type, symbol, volume, price_open, prev_profit = (
            pos.type,
            pos.symbol,
            pos.volume,
            pos.price_open,
            pos.profit,
        )
        tick = await self.get_price_tick(symbol=symbol, time=self.cursor.time)
        price_current = tick.bid if order_type == OrderType.BUY else tick.ask
        profit = await self.order_calc_profit(
            action=order_type,
            symbol=symbol,
            volume=volume,
            price_open=price_open,
            price_close=price_current,
        )
        kwargs = dict(price_current=price_current, time_update=self.cursor.time)
        kwargs.update(profit=profit) if profit is not None else ...
        self.positions.update(ticket=pos.ticket, **kwargs)
        await self.check_order(ticket=ticket)

    @error_handler_sync
    async def close_position_manually(self, *, ticket: int):
        res = await self.close_position(ticket=ticket)
        if not res:
            return
        position = self.positions.get(ticket)
        order_ticket = random.randint(800_000_000, 899_999_999)
        deal_ticket = random.randint(100_000_000, 199_999_999)
        time = position.time_update
        time_msc = position.time_update_msc
        order_type = (
            OrderType.BUY if position.type == OrderType.SELL else OrderType.SELL
        )
        order = {
            "position_id": position.ticket,
            "ticket": order_ticket,
            "comment": "",
            "external_id": "",
            "time_setup": time,
            "time_setup_msc": time_msc,
            "time_done": time,
            "time_done_msc": time_msc,
            "type": order_type,
            "symbol": position.symbol,
            "sl": position.sl,
            "tp": position.tp,
            "price_current": position.price_current,
            "reason": OrderReason.EXPERT,
            "volume_initial": position.volume,
        }

        # TODO: calculate commission and swap if possible or necessary
        deal = {
            "ticket": deal_ticket,
            "position_id": position.ticket,
            "order": order_ticket,
            "symbol": position.symbol,
            "time": time,
            "profit": position.profit,
            "time_msc": time_msc,
            "volume": position.volume,
            "price": position.price_current,
            "type": DealType(order_type),
            "reason": DealReason.EXPERT,
            "entry": DealEntry.OUT,
            "comment": "",
            "external_id": "",
        }
        order = TradeOrder((order.get(k, 0) for k in TradeOrder.__match_args__))
        deal = TradeDeal((deal.get(k, 0) for k in TradeDeal.__match_args__))
        self.orders[order.ticket] = order
        self.deals[deal.ticket] = deal

    async def close_position(self, *, ticket: int) -> bool:
        """
        Close an open position for the trading account using the position ticket.

        Args:
            ticket: Position ticket

        Returns:
            bool: True if the position is closed successfully, False otherwise
        """
        try:
            position = self.positions[ticket]
            margin = self.positions.get_margin(ticket=ticket)
            self.positions.delete_margin(ticket=ticket)
            self.positions.close(ticket=ticket)
            self.orders.update(
                ticket=ticket,
                time_done=self.cursor.time,
                time_done_msc=self.cursor.time * 1000,
            )
            profit = sum(
                [position.profit for position in self.positions.open_positions]
            )
            profit = round(profit, self._account.currency_digits)
            self.update_account(gain=position.profit, profit=profit, margin=-margin)
            return True
        except Exception as exe:
            logger.error("Error Closing Position %d: %s", ticket, exe)
            return False

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
        self.positions.update(
            ticket=ticket,
            sl=sl,
            tp=tp,
            time_update=self.cursor.time,
            time_update_msc=self.cursor.time * 1000,
        )
        return True

    def update_account(
        self, *, profit: float = None, margin: float = 0, gain: float = 0
    ):
        self.account_lock.acquire()
        try:
            self._account.balance += round(gain, self._account.currency_digits)
            self._account.profit = (
                round(profit, self._account.currency_digits)
                if profit is not None
                else self._account.profit
            )
            self._account.equity = self._account.balance + self._account.profit
            self._account.margin += round(margin, self._account.currency_digits)
            self._account.margin_free = round(
                self._account.equity - self._account.margin,
                self._account.currency_digits,
            )
            self._account.balance = round(
                self._account.balance, self._account.currency_digits
            )
            self._account.equity = round(
                self._account.equity, self._account.currency_digits
            )
            self._account.margin = round(
                self._account.margin, self._account.currency_digits
            )
            self._account.margin_free = round(
                self._account.margin_free, self._account.currency_digits
            )
            self._account.profit = round(
                self._account.profit, self._account.currency_digits
            )

            if self._account.margin == 0:
                self._account.margin_level = 0
            else:
                mode = self._account.margin_so_mode
                level = self._account.equity / self._account.margin * 100
                self._account.margin_level = (
                    level
                    if mode == AccountStopOutMode.PERCENT
                    else self._account.margin_free
                )
        except Exception as exe:
            logger.critical("Error Updating Account: %s", exe)

        finally:
            self.account_lock.release()

    def deposit(self, *, amount: float):
        self.update_account(gain=amount)

    def withdraw(self, *, amount: float):
        assert amount <= self._account.balance, "Insufficient funds"
        self.update_account(gain=-amount)

    @error_handler
    async def setup_account(self, **kwargs):
        default = {
            "profit": self._account.profit,
            "margin": self._account.margin,
            "equity": self._account.equity,
            "margin_free": self._account.margin_free,
            "margin_level": self._account.margin_level,
            "balance": self._account.balance,
            **{k: v for k, v in kwargs.items() if k in self._account.__match_args__},
        }

        if self.use_terminal:
            acc_info = await self.mt5.account_info()
            default = {**acc_info._asdict(), **default}

        self._account.set_attrs(**default)
        self.update_account()

    @cached_property
    def prices(self) -> dict[str, DataFrame]:
        prices = {}
        for symbol in self._data.ticks.keys():
            res = self._data.ticks[symbol]
            res = pd.DataFrame(res)
            res.drop_duplicates(subset=["time"], keep="last", inplace=True)
            res.set_index("time", inplace=True, drop=False)
            res = res.reindex(
                self.span, copy=True, method="nearest"
            )  # fill in missing values with NaN
            prices[symbol] = res
        return prices

    @cached_property
    def ticks(self) -> dict[str, DataFrame]:
        ticks = {}
        for symbol in self._data.ticks.keys():
            res = self._data.ticks[symbol]
            res = pd.DataFrame(res)
            ticks[symbol] = res
        return ticks

    @cached_property
    def rates(self) -> dict[str, dict[int, DataFrame]]:
        rates = {}
        for symbol in self._data.rates.keys():
            for timeframe in self._data.rates[symbol].keys():
                res = self._data.rates[symbol][timeframe]
                res = pd.DataFrame(res)
                rates.setdefault(symbol, {})[timeframe] = res
        return rates

    @cached_property
    def symbols(self) -> dict[str, SymbolInfo]:
        symbols = {}
        for symbol, info in self._data.symbols.items():
            symbols[symbol] = SymbolInfo(
                (info.get(key) for key in SymbolInfo.__match_args__)
            )
        return symbols

    @error_handler
    async def order_send(self, *, request: dict, use_terminal=False) -> OrderSendResult:
        use_terminal = self.use_terminal or use_terminal
        osr = {
            "retcode": 10013,
            "comment": "Invalid request",
            "request": TradeRequest(
                request.get(k, (0 if k != "comment" else ""))
                for k in TradeRequest.__match_args__
            ),
        }
        current_tick = await self.get_price_tick(
            symbol=request.get("symbol"), time=self.cursor.time
        )
        if current_tick is None:
            osr["comment"] = "Market is closed"
            osr["retcode"] = 10018
            return OrderSendResult(
                (osr.get(k, 0) for k in OrderSendResult.__match_args__)
            )

        trade_order = {
            "external_id": "",
            "comment": "",
            **{k: v for k, v in request.items() if k in TradeOrder.__match_args__},
        }
        order_type, symbol = request.get("type"), request.get("symbol", "")
        action, position_id = request.get("action"), request.get("position")
        sl, tp, volume, symbol = (
            request.get("sl"),
            request.get("tp"),
            request.get("volume"),
            request.get("symbol"),
        )
        order_type = OrderType(order_type)
        current_position = self.positions.get(position_id)
        order_ticket = random.randint(800_000_000, 899_999_999)
        deal_ticket = random.randint(100_000_000, 199_999_999)

        # closing an order by an opposite order using a position ticket and Deal action
        if (
            action == TradeAction.DEAL
            and current_position
            and order_type.opposite == current_position.type
        ):
            res = await self.close_position(ticket=current_position.ticket)
            if res:
                price_current = (
                    current_tick.ask
                    if order_type == OrderType.BUY
                    else current_tick.bid
                )
                trade_order.update(
                    {
                        "position_id": current_position.ticket,
                        "ticket": order_ticket,
                        "time_setup": current_tick.time,
                        "time_setup_msc": current_tick.time_msc,
                        "time_done": current_tick.time,
                        "time_done_msc": current_tick.time_msc,
                        "type": order_type,
                        "symbol": symbol,
                        "sl": current_position.sl,
                        "tp": current_position.tp,
                        "price_current": price_current,
                        "reason": OrderReason.EXPERT,
                        "volume_initial": current_position.volume,
                    }
                )

                # TODO: calculate commission and swap if possible or necessary
                deal = {
                    "ticket": deal_ticket,
                    "position_id": current_position.ticket,
                    "order": order_ticket,
                    "symbol": symbol,
                    "time": current_tick.time,
                    "profit": current_position.profit,
                    "time_msc": current_tick.time_msc,
                    "volume": current_position.volume,
                    "price": price_current,
                    "type": DealType(order_type),
                    "reason": DealReason.EXPERT,
                    "entry": DealEntry.OUT,
                    "comment": "",
                    "external_id": "",
                }

                order = TradeOrder(
                    (trade_order.get(k, 0) for k in TradeOrder.__match_args__)
                )
                self.orders[order.ticket] = order
                deal = TradeDeal((deal.get(k, 0) for k in TradeDeal.__match_args__))
                self.deals[deal.ticket] = deal
                osr.update(
                    {
                        "comment": "Request completed",
                        "retcode": 10009,
                        "order": order_ticket,
                        "deal": deal_ticket,
                    }
                )
            return OrderSendResult(
                (osr.get(k, 0) for k in OrderSendResult.__match_args__)
            )

        if action == TradeAction.SLTP and current_position:
            check = await self.order_check(request=request, use_terminal=use_terminal)
            if check.retcode != 0:
                osr = {
                    "retcode": check.retcode,
                    "comment": check.comment,
                    "request": check.request,
                }
                return OrderSendResult(
                    (osr.get(k, 0) for k in OrderSendResult.__match_args__)
                )
            res = self.modify_stops(ticket=position_id, sl=sl, tp=tp)
            if res:
                osr.update(
                    {
                        "comment": "Request completed",
                        "retcode": 10009,
                        "order": order_ticket,
                        "deal": deal_ticket,
                    }
                )
            return OrderSendResult(
                (osr.get(k, 0) for k in OrderSendResult.__match_args__)
            )

        if action == TradeAction.DEAL and order_type in (OrderType.BUY, OrderType.SELL):
            check = await self.order_check(request=request, use_terminal=use_terminal)
            if check.retcode != 0:
                osr = {
                    "retcode": check.retcode,
                    "comment": check.comment,
                    "request": check.request,
                }
                return OrderSendResult(
                    (osr.get(k, 0) for k in OrderSendResult.__match_args__)
                )

            price = (
                current_tick.ask if order_type == OrderType.BUY else current_tick.bid
            )
            position = {
                "ticket": order_ticket,
                "symbol": symbol,
                "volume": volume,
                "price_open": price,
                "price_current": price,
                "type": order_type,
                "profit": 0,
                "reason": PositionReason.EXPERT,
                "identifier": order_ticket,
                "sl": sl,
                "tp": tp,
                "time": current_tick.time,
                "time_msc": current_tick.time_msc,
                "time_update": current_tick.time,
                "time_update_msc": current_tick.time_msc,
            }

            deal = {
                "ticket": deal_ticket,
                "order": order_ticket,
                "symbol": symbol,
                "commission": 0,
                "swap": 0,
                "position_id": order_ticket,
                "fee": 0,
                "time": current_tick.time,
                "time_msc": current_tick.time_msc,
                "volume": volume,
                "price": price,
                "type": DealType(order_type),
                "reason": DealReason.EXPERT,
                "entry": DealEntry.IN,
                "profit": 0,
            }

            # ToDo: set time_expiration based on order_type_time
            trade_order.update(
                {
                    "ticket": order_ticket,
                    "symbol": symbol,
                    "volume": volume,
                    "price": price,
                    "price_current": price,
                    "sl": sl,
                    "time_setup_msc": current_tick.time_msc,
                    "tp": tp,
                    "price_open": price,
                    "type": order_type,
                    "time_setup": current_tick.time,
                    "volume_current": volume,
                    "volume_initial": volume,
                    "position_id": order_ticket,
                }
            )

            pos = TradePosition(
                (position.get(k, 0) for k in TradePosition.__match_args__)
            )
            order = TradeOrder(
                (trade_order.get(k, 0) for k in TradeOrder.__match_args__)
            )
            deal = TradeDeal((deal.get(k, 0) for k in TradeDeal.__match_args__))
            self.deals[deal_ticket] = deal
            self.positions[order.ticket] = pos
            self.orders[order.ticket] = order
            osr.update(
                {
                    "comment": "Request completed",
                    "retcode": 10009,
                    "order": order_ticket,
                    "price": price,
                    "volume": volume,
                    "bid": current_tick.bid,
                    "ask": current_tick.ask,
                    "deal": deal_ticket,
                }
            )
            margin = await self.order_calc_margin(
                action=action,
                symbol=symbol,
                volume=volume,
                price=price,
                use_terminal=use_terminal,
            )
            self.positions.set_margin(ticket=order_ticket, margin=margin)
            self.update_account(margin=margin)
            return OrderSendResult(
                (osr.get(k, 0) for k in OrderSendResult.__match_args__)
            )

    @error_handler
    async def order_check(
        self, *, request: dict, use_terminal: bool = False
    ) -> OrderCheckResult:
        use_terminal = self.use_terminal or use_terminal
        ocr = {
            "retcode": 10013,
            "balance": 0,
            "profit": 0,
            "margin": 0,
            "equity": 0,
            "margin_free": 0,
            "margin_level": 0,
            "comment": "Invalid request",
            "request": TradeRequest(
                request.get(k, (0 if k != "comment" else ""))
                for k in TradeRequest.__match_args__
            ),
        }

        action, symbol, volume = (
            request.get("action"),
            request.get("symbol"),
            request.get("volume"),
        )
        price, order_type, position_id = (
            request.get("price"),
            request.get("type"),
            request.get("position"),
        )

        # check margin and confirm order can go through for a deal action and buy or sell order type
        if (
            action == TradeAction.DEAL
            and order_type in (OrderType.BUY, OrderType.SELL)
            and position_id is None
        ):
            margin = await self.order_calc_margin(
                action=action,
                symbol=symbol,
                volume=volume,
                price=price,
                use_terminal=use_terminal,
            )
            if margin is None:
                return OrderCheckResult(
                    (ocr.get(k, 0) for k in OrderCheckResult.__match_args__)
                )

            used_margin = self._account.margin + margin
            free_margin = self._account.margin_free - margin

            level = (
                self._account.equity / used_margin * 100
                if used_margin
                else float("inf")
            )
            margin_level = (
                level
                if self._account.margin_so_mode == AccountStopOutMode.PERCENT
                else free_margin
            )
            ocr.update(
                {
                    "margin_level": margin_level,
                    "margin": margin,
                    "margin_free": free_margin,
                }
            )

            # check if the account has enough money
            if margin_level < self._account.margin_so_call:
                ocr["retcode"] = 10019
                ocr["comment"] = "No money"
                return OrderCheckResult(
                    (ocr.get(k, 0) for k in OrderCheckResult.__match_args__)
                )

        # check if the stops level is valid
        sym = await self.get_symbol_info(symbol=symbol)
        sl, tp = request.get("sl"), request.get("tp")
        current_price = price
        if tp and sl:
            if action == TradeAction.SLTP:
                pos = self.positions.get(request.get("position"))
                sym = await self.get_symbol_info(symbol=pos.symbol)
                current_tick = sym or await self.get_price_tick(
                    pos.symbol, self.cursor.time
                )
                current_price = (
                    current_tick.bid if pos.type == OrderType.BUY else current_tick.ask
                )

            min_sl = min(sl, tp)
            dsl = abs(current_price - min_sl) / sym.point
            tsl = sym.trade_stops_level + sym.spread
            if dsl < tsl:
                ocr["retcode"] = 10016
                ocr["comment"] = "Invalid stops"
                return OrderCheckResult(
                    (ocr.get(k, 0) for k in OrderCheckResult.__match_args__)
                )

            elif action == TradeAction.SLTP:
                ocr["comment"] = "Done"
                ocr["retcode"] = 0
                return OrderCheckResult(
                    (ocr.get(k, 0) for k in OrderCheckResult.__match_args__)
                )

        if use_terminal or self.use_terminal:
            ocr_t = await self.mt5.order_check(request)
            if ocr_t.retcode in (10013, 10014):
                return ocr_t
        elif action == TradeAction.DEAL and order_type in (
            OrderType.BUY,
            OrderType.SELL,
        ):
            # check volume
            if volume < sym.volume_min or volume > sym.volume_max:
                ocr["retcode"] = 10014
                ocr["comment"] = "Invalid volume"
                return OrderCheckResult(
                    (ocr.get(k, 0) for k in OrderCheckResult.__match_args__)
                )

        ocr.update(
            {
                "balance": self._account.balance,
                "profit": self._account.profit,
                "equity": self._account.equity,
                "comment": "Done",
                "retcode": 0,
            }
        )

        return OrderCheckResult(
            (ocr.get(k, 0) for k in OrderCheckResult.__match_args__)
        )

    @error_handler
    async def get_terminal_info(self) -> TerminalInfo:
        if self.use_terminal:
            res = await self.mt5.terminal_info()
            return res
        return TerminalInfo(self._data.terminal)

    @error_handler
    async def get_version(self) -> tuple[int, int, str]:
        if self.use_terminal:
            res = await self.mt5.version()
            return res
        return self._data.version

    @error_handler
    async def get_symbols_total(self) -> int:
        if self.use_terminal:
            syms = await self.mt5.symbols_total()
            return syms
        return len(self.symbols)

    @error_handler
    async def get_symbols(self, *, group: str = "") -> tuple[SymbolInfo, ...]:
        if self.use_terminal:
            syms = await self.mt5.symbols_get(group=group)
            return syms
        return tuple(list(self.symbols.values()))

    @error_handler_sync
    def get_account_info(self) -> AccountInfo:
        return AccountInfo(self._account.asdict().values())

    @error_handler
    async def get_symbol_info_tick(self, *, symbol: str) -> Tick | None:
        tick = await self.get_price_tick(symbol=symbol, time=self.cursor.time)
        return tick

    @async_cache
    async def _symbol_info(self, *, symbol: str) -> SymbolInfo:
        if self.use_terminal:
            info = await self.mt5.symbol_info(symbol)
        else:
            info = self.symbols[symbol]
        return info

    @error_handler
    async def get_symbol_info(self, *, symbol: str) -> SymbolInfo:
        if self.use_terminal:
            info = await self._symbol_info(symbol=symbol)
        else:
            info = self.symbols[symbol]
        tick = await self.get_symbol_info_tick(symbol=symbol)

        info = info._asdict() | {
            "bid": tick.bid,
            "bidhigh": tick.bid,
            "bidlow": tick.bid,
            "ask": tick.ask,
            "askhigh": tick.ask,
            "asklow": tick.bid,
            "last": tick.last,
            "volume_real": tick.volume_real,
        }
        return SymbolInfo((info.get(key) for key in SymbolInfo.__match_args__))

    @error_handler
    async def get_rates_from(
        self,
        *,
        symbol: str,
        timeframe: TimeFrame,
        date_from: datetime | float,
        count: int,
    ) -> np.ndarray:
        date_from = (
            date_from.astimezone(tz=UTC)
            if isinstance(date_from, datetime)
            else datetime.fromtimestamp(date_from, tz=UTC)
        )
        if self.use_terminal:
            rates = await self.mt5.copy_rates_from(symbol, timeframe, date_from, count)
            return rates

        rates = self.rates[symbol][timeframe]
        start = int(date_from.timestamp())
        start = round_down(start, timeframe.seconds)
        rates = rates[rates.time <= start].iloc[-count:]
        return np.fromiter(
            (tuple(i) for i in rates.iloc), dtype=self.get_dtype(df=rates)
        )

    @error_handler
    async def get_rates_from_pos(
        self, *, symbol: str, timeframe: TimeFrame, start_pos: int, count: int
    ) -> np.ndarray:
        if self.use_terminal:
            current_time = (
                self.cursor.time
                if start_pos == 0
                else self.cursor.time - start_pos * timeframe.seconds
            )
            current_time = round_up(current_time, timeframe.seconds)
            start = datetime.fromtimestamp(current_time, tz=UTC)
            rates = await self.mt5.copy_rates_from(symbol, timeframe, start, count)
            return rates

        rates = self.rates[symbol][timeframe]

        # the current time rounded up to a multiple of the timeframe in seconds and then subtracted by the start_pos
        # multiplied by the timeframe in seconds gives the time of the last candlestick in the range when using
        # copy_rates_from_pos
        end = (
            int(round_down(self.cursor.time, timeframe.seconds))
            - start_pos * timeframe.seconds
        )
        start = end - count * timeframe.seconds
        rates = rates[(rates.time > start) & (rates.time <= end)]
        return np.fromiter(
            (tuple(i) for i in rates.iloc), dtype=self.get_dtype(df=rates)
        )

    @error_handler
    async def get_rates_range(
        self,
        *,
        symbol: str,
        timeframe: TimeFrame,
        date_from: datetime | float,
        date_to: datetime | float,
    ) -> np.ndarray:
        date_from = (
            date_from.astimezone(tz=UTC)
            if isinstance(date_from, datetime)
            else datetime.fromtimestamp(date_from, tz=UTC)
        )
        date_to = (
            date_to.astimezone(tz=UTC)
            if isinstance(date_to, datetime)
            else datetime.fromtimestamp(date_to, tz=UTC)
        )
        if self.use_terminal:
            rates = await self.mt5.copy_rates_range(
                symbol, timeframe, date_from, date_to
            )
            return rates

        rates = self.rates[symbol][timeframe]
        start = round_up(int(date_from.timestamp()), timeframe.seconds)
        end = round_up(int(date_to.timestamp()), timeframe.seconds)
        rates = rates[(rates.time >= start) & (rates.time <= end)]
        return np.fromiter(
            (tuple(i) for i in rates.iloc), dtype=self.get_dtype(df=rates)
        )

    @error_handler
    async def get_ticks_from(
        self,
        *,
        symbol: str,
        date_from: datetime | float,
        count: int,
        flags: CopyTicks = CopyTicks.ALL,
    ) -> np.ndarray:
        date_from = (
            date_from.astimezone(tz=UTC)
            if isinstance(date_from, datetime)
            else datetime.fromtimestamp(date_from, tz=UTC)
        )
        if self.use_terminal:
            ticks = await self.mt5.copy_ticks_from(symbol, date_from, count, flags)
            return ticks

        ticks = self.ticks[symbol]
        start = int(date_from.timestamp())
        rates = ticks[ticks.time <= start].iloc[-count:]
        return np.fromiter(
            (tuple(i) for i in rates.iloc), dtype=self.get_dtype(df=rates)
        )

    @error_handler
    async def get_ticks_range(
        self,
        *,
        symbol: str,
        date_from: datetime | float,
        date_to: datetime | float,
        flags: CopyTicks = CopyTicks.ALL,
    ) -> np.ndarray:
        date_from = (
            date_from.astimezone(tz=UTC)
            if isinstance(date_from, datetime)
            else datetime.fromtimestamp(date_from, tz=UTC)
        )
        date_to = (
            date_to.astimezone(tz=UTC)
            if isinstance(date_to, datetime)
            else datetime.fromtimestamp(date_to, tz=UTC)
        )
        if self.use_terminal:
            ticks = await self.mt5.copy_ticks_range(symbol, date_from, date_to, flags)
            return ticks

        ticks = self.ticks[symbol]
        start = int(date_from.timestamp())
        end = int(date_to.timestamp())
        rates = ticks[(ticks.time >= start) & (ticks.time <= end)]
        return np.fromiter(
            (tuple(i) for i in rates.iloc), dtype=self.get_dtype(df=ticks)
        )

    @error_handler
    async def order_calc_margin(
        self,
        *,
        action: Literal[OrderType.BUY, OrderType.SELL],
        symbol: str,
        volume: float,
        price: float,
        use_terminal: bool = None,
    ):
        use_terminal = use_terminal if use_terminal is not None else self.use_terminal
        if use_terminal:
            return await self.mt5.order_calc_margin(action, symbol, volume, price)

        sym = self.symbols.get(symbol)
        if sym is None and self.use_terminal:
            sym = await self._symbol_info(symbol=symbol)
        margin = (volume * sym.trade_contract_size * price) / (
            self._account.leverage / (sym.margin_initial or 1)
        )
        return round(margin, self._account.currency_digits)

    @error_handler
    async def order_calc_profit(
        self,
        *,
        action: Literal[OrderType.BUY, OrderType.SELL],
        symbol: str,
        volume: float,
        price_open: float,
        price_close: float,
        use_terminal=None,
    ):
        use_terminal = use_terminal if use_terminal is not None else self.use_terminal

        if use_terminal:
            return await self.mt5.order_calc_profit(
                action, symbol, volume, price_open, price_close
            )

        sym = self.symbols.get(symbol)
        if sym is None and self.use_terminal:
            sym = await self._symbol_info(symbol=symbol)
        profit = (
            volume
            * sym.trade_contract_size
            * (
                (price_close - price_open)
                if action == OrderType.BUY
                else (price_open - price_close)
            )
        )
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
    def get_orders(
        self, *, symbol: str = "", group: str = "", ticket: int = None
    ) -> tuple[TradeOrder, ...]:
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
    def get_positions(
        self, *, symbol: str = None, group: str = None, ticket: int = None
    ) -> tuple[TradePosition, ...]:
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
    def get_history_orders_total(
        self, *, date_from: datetime | float, date_to: datetime | float
    ) -> int:
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
    def get_history_orders(
        self,
        *,
        date_from: datetime | float = None,
        date_to: datetime | float = None,
        group: str = "",
        ticket: int = None,
        position: int = None,
    ) -> tuple[TradeOrder, ...]:
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
        return self.orders.history_orders_get(
            date_from=date_from,
            date_to=date_to,
            group=group,
            ticket=ticket,
            position=position,
        )

    @error_handler_sync
    def get_history_deals_total(
        self, *, date_from: datetime | float, date_to: datetime | float
    ) -> int:
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
    def get_history_deals(
        self,
        *,
        date_from: datetime | float = None,
        date_to: datetime | float = None,
        group: str = None,
        position: int = None,
        ticket: int = None,
    ) -> tuple[TradeDeal, ...]:
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
        return self.deals.history_deals_get(
            date_from=date_from,
            date_to=date_to,
            group=group,
            position=position,
            ticket=ticket,
        )
