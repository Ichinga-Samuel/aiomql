from typing import TypedDict
import pickle
import lzma
from datetime import datetime
from logging import getLogger
import asyncio

import pytz
from MetaTrader5 import Tick, SymbolInfo
import pandas as pd
from pandas import DataFrame

from ...core.meta_trader import MetaTrader
from ...core.config import Config
from ...core.errors import Error
from ...core.constants import TimeFrame, CopyTicks, OrderType
from ...core.models import (AccountInfo, SymbolInfo, BookInfo, TradeOrder, OrderCheckResult, OrderSendResult,
                            TradePosition, TradeDeal, TickInfo)
from ...utils import backoff_decorator

logger = getLogger(__name__)

class Data(TypedDict):
    account: AccountInfo
    symbols: dict[str, SymbolInfo]
    prices: DataFrame
    ticks: DataFrame
    rates: DataFrame
    span: range


class GetData:
    config: Config = Config()

    def __init__(self, *, start: datetime, end: datetime, timeframes: set[TimeFrame], symbols: set[str],
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

    async def get_data(self) -> Data:
        """"""
        data = {}
        rates, ticks, prices, symbols, account = await asyncio.gather(self.get_symbols_rates(), self.get_symbols_ticks(),
                                                                self.get_symbols_prices(), self.get_symbols_info(),
                                                    self.get_account_info())

        data['rates'] = rates
        data['ticks'] = ticks
        data['prices'] = prices
        data['symbols'] = symbols
        data['account'] = account
        data['range'] = self.span

        return Data(**data)

    async def pickle_data(self) -> None:
        """"""
        data = await self.get_data()
        fh = open(f'{self.config.root}/data/{self.name}', 'wb')
        pickle.dump(data, fh)
        fh.close()
    
    async def compress_data(self):
        """"""
        data = await self.get_data()
        bdata = pickle.dumps(data)
        name = self.name + 'xz' 
        with lzma.open(name, 'w') as fh:
            fh.write(bdata)

    @classmethod
    def load_data(cls, name: str, compressed=False) -> dict:
        """"""
        fo = open(f'{cls.config.root}/data/{name}', 'rb')
        data = fo.read()

        if compressed:
            data = lzma.decompress(data)
        else:
            data = pickle.loads(data)

        fo.close()

        return data

    async def get_symbols_info(self) -> dict[str, SymbolInfo]:
        """"""
        tasks = [self.get_symbol_info(symbol) for symbol in self.symbols]
        res = await asyncio.gather(*tasks)
        return {symbol: SymbolInfo(**info) for symbol, info in res}

    async def get_symbols_ticks(self) -> dict[str, DataFrame]:
        """"""
        tasks = [self.get_symbol_ticks(symbol) for symbol in self.symbols]
        res = await asyncio.gather(*tasks)
        return {symbol: tick for symbol, tick in res}

    async def get_symbols_prices(self) -> dict[str, DataFrame]:
        """"""
        tasks = [self.get_symbol_prices(symbol) for symbol in self.symbols]
        res = await asyncio.gather(*tasks)
        return {symbol: prices for symbol, prices in res}

    async def get_symbols_rates(self) -> dict[str: dict[TimeFrame: DataFrame]]:
        """"""
        tasks = [self.get_symbol_rates(symbol, timeframe) for symbol in self.symbols for timeframe in self.timeframes]
        res = await asyncio.gather(*tasks)
        data = {}
        for symbol, timeframe, rates in res:
            data.setdefault(symbol, {}).setdefault(timeframe.name, rates)
        return data

    @backoff_decorator(max_retries=5)
    async def get_account_info(self) -> dict:
        """"""
        res = await self.mt5.account_info()
        return res._asdict()

    @backoff_decorator(max_retries=5)
    async def get_symbol_info(self, symbol: str) -> tuple[str, dict]:
        """"""
        res = await self.mt5.symbol_info(symbol)
        return symbol, res._asdict()

    @backoff_decorator(max_retries=5)
    async def get_symbol_ticks(self, symbol: str) -> tuple[str, DataFrame]:
        """"""
        res = await self.mt5.copy_ticks_range(symbol, self.start, self.end, CopyTicks.ALL)
        res = pd.DataFrame(res)
        res.drop_duplicates(subset=['time'], keep='last', inplace=True)
        res.set_index('time', inplace=True, drop=False)
        return symbol, res

    @backoff_decorator(max_retries=5)
    async def get_symbol_prices(self, symbol: str) -> tuple[str, DataFrame]:
        """"""
        res = await self.mt5.copy_ticks_range(symbol, self.start, self.end, CopyTicks.ALL)
        res = pd.DataFrame(res)
        res.drop_duplicates(subset=['time'], keep='last', inplace=True)
        res.set_index('time', inplace=True, drop=False)
        res = res.reindex(self.span, method='nearest')
        return symbol, res

    @backoff_decorator(max_retries=5)
    async def get_symbol_rates(self, symbol: str, timeframe: TimeFrame) -> tuple[str, TimeFrame, DataFrame]:
        """"""
        res = await self.mt5.copy_rates_range(symbol, timeframe, self.start, self.end)
        res = pd.DataFrame(res)
        res.drop_duplicates(subset=['time'], keep='last', inplace=True)
        res.set_index('time', inplace=True, drop=False)
        return symbol, timeframe, res
