from dataclasses import dataclass
import pickle
import lzma
from datetime import datetime
from logging import getLogger
import asyncio

import pytz
import pandas as pd
from pandas import DataFrame

from ...core.meta_trader import MetaTrader
from ...core.config import Config
from ...core.constants import TimeFrame, CopyTicks

from ...utils import backoff_decorator

logger = getLogger(__name__)
from MetaTrader5 import TradePosition, TradeOrder, TradeDeal

tof = list(TradeOrder._fields)
tof.append('symbol')
tpf = list(TradePosition._fields)
tpf.append('symbol')
tdf = list(TradeDeal._fields)
tdf.append('symbol')


@dataclass
class Data:
    account: dict
    symbols: dict[str, dict]
    prices: dict[str, DataFrame]
    ticks: dict[str, DataFrame]
    rates: dict[str, dict[str, DataFrame]]
    span: range
    range: range
    history_orders: DataFrame = DataFrame([], columns=tof)
    history_deals: DataFrame = DataFrame([], columns=tdf)
    positions: DataFrame = DataFrame([], columns=tpf)


class GetData:

    def __init__(self, *, start: datetime, end: datetime, timeframes: set[TimeFrame], symbols: set[str],
                 name: str = '', tz: str = 'Etc/UTC'):
        """"""
        self.config = Config()
        self.tz = pytz.timezone(tz)
        self.start = start.replace(tzinfo=self.tz)
        self.end = end.replace(tzinfo=self.tz)
        self.symbols = symbols
        self.timeframes = timeframes
        self.name = name or f"{start:%d-%m-%y}_{end:%d-%m-%y}"
        diff = int((self.end - self.start).total_seconds())
        self.range = range(diff)
        self.span = range(start := int(self.start.timestamp()), diff + start)
        self.mt5 = MetaTrader()

    async def get_data(self) -> Data:
        """"""

        rates, ticks, prices, symbols, account = await asyncio.gather(self.get_symbols_rates(), self.get_symbols_ticks(),
                                                                self.get_symbols_prices(), self.get_symbols_info(),
                                                    self.get_account_info())
        return Data(account=account, symbols=symbols, prices=prices, ticks=ticks, rates=rates,
                    span=self.span, range=self.range)

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

    async def get_symbols_info(self) -> dict[str, dict]:
        """"""
        tasks = [self.get_symbol_info(symbol) for symbol in self.symbols]
        res = await asyncio.gather(*tasks)
        return {symbol: info for symbol, info in res}

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
