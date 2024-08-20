import pickle
import random
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
from ...utils import backoff_decorator

logger = getLogger(__name__)


class GetData(MetaTrader):

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
        self.mt5 = MetaTrader()

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
        pickle.dump(data, fh)
        fh.close()

    def load_data(self, name: str = '') -> dict:
        """"""
        name = name or self.name
        file = open(f'{self.config.root}/data/{name}', 'rb')
        data = pickle.load(file)
        file.close()
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

    @backoff_decorator(max_retries=5)
    async def get_account_info(self) -> AccountInfo | None:
        """"""
        res = await self.mt5.account_info()
        return res._asdict()

    @backoff_decorator(max_retries=5)
    async def get_symbol_info(self, symbol: str):
        """"""
        res = await self.mt5.symbol_info(symbol)
        return symbol, res._asdict()

    @backoff_decorator(max_retries=5)
    async def get_symbol_ticks(self, symbol: str):
        """"""
        res = await self.mt5.copy_ticks_range(symbol, self.start, self.end, CopyTicks.ALL)
        res = pd.DataFrame(res)
        res.drop_duplicates(subset=['time'], keep='last', inplace=True)
        res.set_index('time', inplace=True, drop=False)
        return symbol, res

    @backoff_decorator(max_retries=5)
    async def get_symbol_prices(self, symbol: str):
        """"""
        res = await self.mt5.copy_ticks_range(symbol, self.start, self.end, CopyTicks.ALL)
        res = pd.DataFrame(res)
        res.drop_duplicates(subset=['time'], keep='last', inplace=True)
        res.set_index('time', inplace=True, drop=False)
        res = res.reindex(self.span, method='nearest')
        return symbol, res

    @backoff_decorator(max_retries=5)
    async def get_symbol_rates(self, symbol: str, timeframe: TimeFrame):
        """"""
        res = await self.mt5.copy_rates_range(symbol, timeframe, self.start, self.end)
        res = pd.DataFrame(res)
        res.drop_duplicates(subset=['time'], keep='last', inplace=True)
        res.set_index('time', inplace=True, drop=False)
        return symbol, timeframe, res
