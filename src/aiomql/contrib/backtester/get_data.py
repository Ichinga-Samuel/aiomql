from dataclasses import dataclass, field, fields
import pickle
from pathlib import Path
import lzma
from datetime import datetime
from logging import getLogger
import asyncio
from typing import Sequence, ClassVar

import pytz
import pandas as pd
from pandas import DataFrame

from ...core.meta_trader import MetaTrader
from ...core.config import Config
from ...core.constants import TimeFrame, CopyTicks

from ...utils import backoff_decorator

logger = getLogger(__name__)
from MetaTrader5 import TradePosition, TradeOrder, TradeDeal

tof = list(TradeOrder.__match_args__)
tof.append('symbol')
tpf = list(TradePosition.__match_args__)
tpf.append('symbol')
tdf = list(TradeDeal.__match_args__)
tdf.append('symbol')


@dataclass
class Data:
    name: str = ''
    terminal: dict[str, [str | int | bool | float]] = field(default_factory=dict)
    version: tuple[int, int, str] = (0, 0, '')
    account: dict = field(default_factory=dict)
    symbols: dict[str, dict] = field(default_factory=dict)
    prices: dict[str, DataFrame] = field(default_factory=dict)
    ticks: dict[str, DataFrame] = field(default_factory=dict)
    rates: dict[str, dict[str, DataFrame]] = field(default_factory=dict)
    span: range = range(0)
    range: range = range(0)
    history_orders: DataFrame = field(default_factory=lambda: DataFrame([], columns=tof))
    history_deals: DataFrame = field(default_factory=lambda: DataFrame([], columns=tdf))
    positions: dict[str, DataFrame] = field(default_factory=dict)
    orders: dict[str, DataFrame] = field(default_factory=dict)

    _fields: list[ClassVar[str]] = field(default_factory=list)

    def setattrs(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items() if k in self.fields]

    @property
    def fields(self):
        return self._fields or [name for f in fields(self) if (name := f.name) != '_fields']


class GetData:
    data: Data | None

    def __init__(self, *, start: datetime, end: datetime, symbols: Sequence[str],
                 timeframes: Sequence[TimeFrame], name: str = '', tz: str = 'Etc/UTC'):
        """"""
        self.config = Config()
        self.tz = pytz.timezone(tz)
        self.start = start.replace(tzinfo=self.tz)
        self.end = end.replace(tzinfo=self.tz)
        self.symbols = set(symbols)
        self.timeframes = set(timeframes)
        self.name = name or f"{start:%d-%m-%y}_{end:%d-%m-%y}"
        diff = int((self.end - self.start).total_seconds())
        self.range = range(diff)
        self.span = range(start := int(self.start.timestamp()), diff + start)
        self.data = Data(name=name)
        self.mt5 = MetaTrader()

    async def get_data(self):
        """"""
        rates, ticks, prices, symbols, account = await asyncio.gather(self.get_symbols_rates(), self.get_symbols_ticks(),
                                                                self.get_symbols_prices(), self.get_symbols_info(),
                                                    self.get_account_info())
        terminal, version = await asyncio.gather(self.get_terminal_info(), self.get_version())

        self.data.setattrs(account=account, symbols=symbols, prices=prices, ticks=ticks, rates=rates,
                           span=self.span, range=self.range, terminal=terminal, version=version, name=self.name)

    def pickle_data(self):
        """"""
        fh = open(f'{self.config.test_data_dir}/{self.name}', 'wb')
        pickle.dump(self.data, fh)
        fh.close()
    
    async def compress_data(self):
        """"""
        bdata = pickle.dumps(self.data)
        name = self.name + 'xz' 
        with lzma.open(f'{self.config.test_data_dir}/{name}', 'w') as fh:
            fh.write(bdata)

    @classmethod
    def dump_data(cls, data: Data, name: str | Path, compress: bool = False) -> None:
        """"""
        try:
            fo = open(name, 'wb')
            if compress:
                data = lzma.compress(pickle.dumps(data))
            else:
                data = pickle.dumps(data)

            fo.write(data)
            fo.close()
        except Exception as err:
            logger.error(f"Error in dump_data: {err}")


    @classmethod
    def load_data(cls, *, name: str | Path, compressed=False) -> Data | None:
        """"""
        try:
            fo = open(name, 'rb')
            data = fo.read()

            if compressed:
                data = lzma.decompress(data)
            else:
                data = pickle.loads(data)

            fo.close()

            return data
        except Exception as err:
            logger.error(f"Error: {err}")
            return None

    async def get_terminal_info(self) -> dict[str, [str | int | bool | float]]:
        """"""
        terminal = await self.mt5.terminal_info()
        return terminal._asdict()

    async def get_version(self) -> tuple[int, int, str]:
        """"""
        version = await self.mt5.version()
        return version

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