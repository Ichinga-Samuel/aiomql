import pickle
from datetime import datetime
from logging import getLogger
import asyncio

import pytz
from MetaTrader5 import Tick, SymbolInfo
import pandas as pd

from ...core.meta_trader import MetaTrader
from ...core.config import Config
from ...core.errors import Error
from ...core.constants import TimeFrame, CopyTicks, OrderType
from ...core.models import (AccountInfo, SymbolInfo, BookInfo, TradeOrder, OrderCheckResult, OrderSendResult,
                            TradePosition, TradeDeal)

logger = getLogger(__name__)


class MetaTester(MetaTrader):

    def __init__(self, start: datetime, end: datetime, timeframes: set[TimeFrame], symbols: set[str],
                 interval: int = 60, name: str = '', tz: str = 'Etc/UTC'):
        """"""
        super().__init__()
        self.tz = pytz.timezone(tz)
        self.start = start.replace(tzinfo=self.tz)
        self.end = end.replace(tzinfo=self.tz)
        self.interval = interval
        self.symbols = symbols
        self.timeframes = timeframes
        self.counter = 0
        self.name = name or f"{start:%d-%m-%y}_{end:%d-%m-%y}"
        diff = int((self.end - self.start).total_seconds())
        self.span = range(start := int(self.start.timestamp()), diff + start)

    def __iter__(self):
        yield

    async def get_test_data(self) -> dict:
        """"""
        data = {}
        rates, ticks, prices = await asyncio.gather(self.get_symbols_rates(), self.get_symbols_ticks(),
                                                                self.get_symbols_prices())

        data['rates'] = rates
        data['ticks'] = ticks
        data['prices'] = prices
        data['symbols'] = await self.get_symbols_info()
        data['account'] = self.get_account_info()

        return data

    async def get_and_save_data(self) -> None:
        """"""
        data = await self.get_test_data()
        fh = open(f'{self.config.root}/data/{self.name}', 'wb')
        data_file = pickle.dump(data, fh)
        # data_file.update(data)
        # data_file.sync()
        # data_file.close()
        fh.close()

    def load_data(self, name: str = '') -> dict:
        """"""
        name = name or self.name
        data_file = shelve.open(f'{self.config.root}/data/{name}', writeback=True)
        data = dict(data_file)
        data_file.close()
        return data

    async def get_symbols_info(self):
        """"""
        tasks = [self.get_symbol_info(symbol) for symbol in self.symbols]
        res = await asyncio.gather(*tasks)
        return {symbol: info for symbol, info in res}

    async def get_symbols_ticks(self):
        """"""
        tasks = [self.get_symbol_ticks(symbol) for symbol in self.symbols]
        res = await asyncio.gather(*tasks)
        return {symbol: ticks for symbol, ticks in res}

    async def get_account_info(self):
        """"""
        res = await super().account_info()
        return res._asdict()

    async def get_symbols_prices(self):
        """"""
        tasks = [self.get_symbol_prices(symbol) for symbol in self.symbols]
        res = await asyncio.gather(*tasks)
        return {symbol: prices for symbol, prices in res}

    async def get_symbols_rates(self):
        """"""
        tasks = [self.get_symbol_rates(symbol, timeframe) for symbol in self.symbols for timeframe in self.timeframes]
        res = await asyncio.gather(*tasks)
        data = {}
        for symbol, timeframe, rates in res:
            data.setdefault(symbol, {}).setdefault(timeframe.name, rates)
        return data

    async def get_symbol_info(self, symbol: str):
        """"""
        res = await super().symbol_info(symbol)
        return symbol, res._asdict()

    async def get_symbol_ticks(self, symbol: str):
        """"""
        res = await super().copy_ticks_range(symbol, self.start, self.end, CopyTicks.ALL)
        # res = pd.DataFrame(res)
        # res.drop_duplicates(subset=['time'], keep='last', inplace=True)
        # res.set_index('time', inplace=True, drop=False)
        return symbol, res

    async def get_symbol_prices(self, symbol: str):
        """"""
        res = await super().copy_ticks_range(symbol, self.start, self.end, CopyTicks.ALL)
        # res = pd.DataFrame(res)
        # res.drop_duplicates(subset=['time'], keep='last', inplace=True)
        # res.set_index('time', inplace=True, drop=False)
        # res = res.reindex(self.span, method='nearest')
        return symbol, res

    async def get_symbol_rates(self, symbol: str, timeframe: TimeFrame):
        """"""
        res = await super().copy_rates_range(symbol, timeframe, self.start, self.end)
        # res = pd.DataFrame(res)
        # res.drop_duplicates(subset=['time'], keep='last', inplace=True)
        # res.set_index('time', inplace=True, drop=False)
        return symbol, timeframe, res

    async def account_info(self) -> AccountInfo | None:
        """"""
        res = await asyncio.to_thread(self._account_info)
        if res is None:
            err = await self.last_error()
            self.error = Error(*err)
            logger.warning(f'Error in obtaining account information.{self.error.description}')
        return res

    async def symbols_total(self) -> int:
        return await asyncio.to_thread(self._symbols_total)

    async def symbols_get(self, group: str = "") -> tuple[SymbolInfo] | None:
        kwargs = {'group': group} if group else {}
        res = await asyncio.to_thread(self._symbols_get, **kwargs)
        if res is None:
            err = await self.last_error()
            self.error = Error(*err)
            logger.warning(f'Error in obtaining symbols.{self.error.description}')
            return res
        return res

    async def symbol_info(self, symbol: str) -> SymbolInfo | None:
        res = await asyncio.to_thread(self._symbol_info, symbol)
        if res is None:
            err = await self.last_error()
            self.error = Error(*err)
            logger.warning(f'Error in obtaining information for {symbol}.{self.error.description}')
            return res
        return res

    async def symbol_info_tick(self, symbol: str) -> Tick | None:
        res = await asyncio.to_thread(self._symbol_info_tick, symbol)
        if res is None:
            err = await self.last_error()
            self.error = Error(*err)
            logger.warning(f'Error in obtaining tick for {symbol}.{self.error.description}')
            return res
        return res

    async def symbol_select(self, symbol: str, enable: bool) -> bool:
        return await asyncio.to_thread(self._symbol_select, symbol, enable)

    async def copy_rates_from(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float, count: int):
        res = await asyncio.to_thread(self._copy_rates_from, symbol, timeframe, date_from, count)
        if res is None:
            err = await self.last_error()
            self.error = Error(*err)
            logger.warning(f'Error in obtaining rates for {symbol}.{self.error.description}')
            return res
        return res

    async def copy_rates_from_pos(self, symbol: str, timeframe: TimeFrame, start_pos: int, count: int):
        res = await asyncio.to_thread(self._copy_rates_from_pos, symbol, timeframe, start_pos, count)
        if res is None:
            err = await self.last_error()
            self.error = Error(*err)
            logger.warning(f'Error in obtaining rates for {symbol}.{self.error.description}')
            return res
        return res

    async def copy_rates_range(self, symbol: str, timeframe: TimeFrame, date_from: datetime | float,
                               date_to: datetime | float):
        res = await asyncio.to_thread(self._copy_rates_range, symbol, timeframe, date_from, date_to)
        if res is None:
            err = await self.last_error()
            self.error = Error(*err)
            logger.warning(f'Error in obtaining rates for {symbol}.{self.error.description}')
            return res
        return res

    async def copy_ticks_from(self, symbol: str, date_from: datetime | float, count: int, flags: CopyTicks):
        res = await asyncio.to_thread(self._copy_ticks_from, symbol, date_from, count, flags)
        if res is None:
            err = await self.last_error()
            self.error = Error(*err)
            logger.warning(f'Error in obtaining ticks for {symbol}.{self.error.description}')
            return res
        return res

    async def copy_ticks_range(self, symbol: str, date_from: datetime | float, date_to: datetime | float,
                               flags: CopyTicks):
        res = await asyncio.to_thread(self._copy_ticks_range, symbol, date_from, date_to, flags)
        if res is None:
            err = await self.last_error()
            self.error = Error(*err)
            logger.warning(f'Error in obtaining ticks for {symbol}.{self.error.description}')
            return res
        return res

    async def orders_total(self) -> int:
        return await asyncio.to_thread(self._orders_total)

    async def orders_get(self, group: str = "", ticket: int = 0, symbol: str = "") -> tuple[TradeOrder] | None:
        """Get active orders with the ability to filter by symbol or ticket. There are three call options.
           Call without parameters. Return active orders on all symbols

        Keyword Args:
            symbol (str): Symbol name. Optional named parameter. If a symbol is specified, the ticket parameter is ignored.

            group (str): The filter for arranging a group of necessary symbols. Optional named parameter. If the group is specified, the function
                returns only active orders meeting a specified criteria for a symbol name.

            ticket (int): Order ticket (ORDER_TICKET). Optional named parameter.

        Returns:
            tuple[TradeOrder]: A list of active trade orders as TradeOrder objects
        """
        kwargs = {key: value for key, value in (('group', group), ('ticket', ticket), ('symbol', symbol)) if value}
        res = await asyncio.to_thread(self._orders_get, **kwargs)
        if res is None:
            err = await self.last_error()
            self.error = Error(*err)
            logger.warning(f'Error in obtaining orders.{self.error.description}')
            return res
        return res

    async def order_calc_margin(self, action: OrderType, symbol: str, volume: float, price: float) -> float | None:
        res = await asyncio.to_thread(self._order_calc_margin, action, symbol, volume, price)
        if res is None:
            err = await self.last_error()
            self.error = Error(*err)
            logger.warning(f'Error in calculating margin.{self.error.description}')
            return res
        return res

    async def order_calc_profit(self, action: OrderType, symbol: str, volume: float, price_open: float,
                                price_close: float) -> float | None:
        res = await asyncio.to_thread(self._order_calc_profit, action, symbol, volume, price_open, price_close)
        if res is None:
            err = await self.last_error()
            self.error = Error(*err)
            logger.warning(f'Error in calculating profit.{self.error.description}')
            return res
        return res

    async def order_check(self, request: dict) -> OrderCheckResult:
        return await asyncio.to_thread(self._order_check, request)

    async def order_send(self, request: dict) -> OrderSendResult:
        return await asyncio.to_thread(self._order_send, request)

    async def positions_total(self) -> int:
        return await asyncio.to_thread(self._positions_total)

    async def positions_get(self, group: str = "", ticket: int = None, symbol: str = "") -> tuple[TradePosition] | None:
        kwargs = {key: value for key, value in (('group', group), ('ticket', ticket), ('symbol', symbol)) if value}
        res = await asyncio.to_thread(self._positions_get, **kwargs)
        if res is None:
            err = await self.last_error()
            self.error = Error(*err)
            logger.warning(f'Error in obtaining open positions.{self.error.description}')
            return res
        return res

    async def history_orders_total(self, date_from: datetime | float, date_to: datetime | float) -> int:
        return await asyncio.to_thread(self._history_orders_total, date_from, date_to)

    async def history_orders_get(self, date_from: datetime | float = None, date_to: datetime | float = None,
                                 group: str = '', ticket: int = None, position: int = None) -> tuple[TradeOrder] | None:
        kwargs = {key: value for key, value in (('group', group), ('ticket', ticket), ('position', position)) if value}
        args = tuple(arg for arg in (date_from, date_to) if arg)
        res = await asyncio.to_thread(self._history_orders_get, *args, **kwargs)
        if res is None:
            err = await self.last_error()
            self.error = Error(*err)
            logger.warning(f'Error in getting orders.{self.error.description}')
            return res
        return res

    async def history_deals_total(self, date_from: datetime | float, date_to: datetime | float) -> int:
        return await asyncio.to_thread(self._history_deals_total, date_from, date_to)

    async def history_deals_get(self, date_from: datetime | float = None, date_to: datetime | float = None,
                                group: str = '', ticket: int = None, position: int = None) -> tuple[TradeDeal] | None:
        kwargs = {key: value for key, value in (('group', group), ('ticket', ticket), ('position', position)) if value}
        args = tuple(arg for arg in (date_from, date_to) if arg)
        res = await asyncio.to_thread(self._history_deals_get, *args, **kwargs)
        if res is None:
            err = await self.last_error()
            self.error = Error(*err)
            logger.warning(f'Error in getting deals.{self.error}')
            return res
        return res
