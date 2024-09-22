from dataclasses import dataclass, field, fields
import pickle
from pathlib import Path
import lzma
from datetime import datetime
from logging import getLogger
from typing import Sequence, ClassVar

import pytz
import pandas as pd
from pandas import DataFrame

from ...core.meta_trader import MetaTrader
from ...core.config import Config
from ...core.constants import TimeFrame, CopyTicks
from ...core.task_queue import TaskQueue, QueueItem

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

    def __str__(self):
        return f"""
        Data: {self.name}
        Terminal: {str(list(self.terminal.keys())[0:2]) + '...' if len(self.terminal) > 3 else list(self.terminal.keys())}
        Version: {self.version}
        Account: {str(list(self.account.keys())[0:2]) + '...' if len(self.account) > 3 else list(self.account.keys())}
        Symbols: {len(self.symbols)} symbols
        Prices: Prices for {len(self.prices)} symbols
        Ticks: Ticks for {len(self.ticks)} symbols 
        Rates: Bars for {len(self.rates)} symbols
        Span: {datetime.fromtimestamp(self.span.start)} to {datetime.fromtimestamp(self.span.stop)}
        """

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def set_attrs(self, **kwargs):
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
        self.data = Data(name=name, span=self.span, range=self.range)
        self.mt5 = MetaTrader()
        self.task_queue = TaskQueue(workers=250)

    @classmethod
    def dump_data(cls, data: Data, name: str | Path, compress: bool = False):
        """"""
        try:
            fo = open(name, 'wb')

            if compress:
                data = lzma.compress(pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL))
            else:
                data = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)

            fo.write(data)
            fo.close()
        except Exception as err:
            logger.error(f"Error in dump_data: {err}")


    @classmethod
    def load_data(cls, *, name: str | Path, compressed=False):
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

    async def get_data(self, workers: int = None):
        """"""
        if workers:
            self.task_queue.workers = workers

        q_items = [QueueItem(self.get_symbols_rates, must_complete=True),
                   QueueItem(self.get_symbols_ticks, must_complete=True),
                   QueueItem(self.get_symbols_prices, must_complete=True),
                   QueueItem(self.get_symbols_info, must_complete=True),
                   ]

        [self.task_queue.add(item=item, priority=0) for item in q_items]

        if not self.data.account:
            self.task_queue.add(item=QueueItem(self.get_account_info, must_complete=True))

        if not self.data.terminal:
            self.task_queue.add(item=QueueItem(self.get_terminal_info, must_complete=True))

        if not self.data.version:
            self.task_queue.add(item=QueueItem(self.get_version, must_complete=True))

        await self.task_queue.run()

    def pickle_data(self):
        """"""
        fh = open(f'{self.config.test_data_dir}/{self.name}.pkl', 'wb')
        pickle.dump(self.data, fh, protocol=pickle.HIGHEST_PROTOCOL)
        fh.close()

    async def compress_data(self):
        """"""
        bdata = pickle.dumps(self.data, protocol=pickle.HIGHEST_PROTOCOL)
        name = self.name + 'xz'
        with lzma.open(f'{self.config.test_data_dir}/{name}', 'w') as fh:
            fh.write(bdata)

    async def get_terminal_info(self):
        """"""
        terminal = await self.mt5.terminal_info()
        terminal = terminal._asdict()
        self.data.set_attrs(terminal=terminal)

    async def get_version(self):
        """"""
        version = await self.mt5.version()
        self.data.set_attrs(version=version)

    @backoff_decorator
    async def get_account_info(self):
        """"""
        res = await self.mt5.account_info()
        res = res._asdict()
        self.data.set_attrs(account=res)

    async def get_symbols_info(self):
        """"""
        [self.task_queue.add(item=QueueItem(self.get_symbol_info, symbol))
         for symbol in self.symbols if self.data.symbols.get(symbol) is None]

    async def get_symbols_ticks(self):
        """"""
        [self.task_queue.add(item=QueueItem(self.get_symbol_ticks, symbol))
         for symbol in self.symbols if self.data.ticks.get(symbol) is None]

    async def get_symbols_prices(self):
        """"""
        [self.task_queue.add(item=QueueItem(self.get_symbol_prices, symbol))
         for symbol in self.symbols if self.data.prices.get(symbol) is None]

    async def get_symbols_rates(self):
        """"""
        [self.task_queue.add(item=QueueItem(self.get_symbol_rates, symbol, timeframe), priority=4)
                  for symbol in self.symbols for timeframe in self.timeframes
         if self.data.rates.get(symbol, {}).get(timeframe.name) is None]

    @backoff_decorator
    async def get_symbol_info(self, symbol: str):
        """"""
        res = await self.mt5.symbol_info(symbol)
        self.data.symbols[symbol] = res._asdict()

    @backoff_decorator
    async def get_symbol_ticks(self, symbol: str):
        """"""
        res = await self.mt5.copy_ticks_range(symbol, self.start, self.end, CopyTicks.ALL)
        res = pd.DataFrame(res)
        res.drop_duplicates(subset=['time'], keep='last', inplace=True)
        res.set_index('time', inplace=True, drop=False)
        self.data.ticks[symbol] = res

    @backoff_decorator
    async def get_symbol_prices(self, symbol: str):
        """"""
        res = await self.mt5.copy_ticks_range(symbol, self.start, self.end, CopyTicks.ALL)
        res = pd.DataFrame(res)
        res.drop_duplicates(subset=['time'], keep='last', inplace=True)
        res.set_index('time', inplace=True, drop=False)
        res = res.reindex(self.span) # fill in missing values with NaN
        self.data.prices[symbol] = res

    @backoff_decorator
    async def get_symbol_rates(self, symbol: str, timeframe: TimeFrame):
        """"""
        res = await self.mt5.copy_rates_range(symbol, timeframe, self.start, self.end)
        res = pd.DataFrame(res)
        res.drop_duplicates(subset=['time'], keep='last', inplace=True)
        res.set_index('time', inplace=True, drop=False)
        self.data.rates.setdefault(symbol, {})[timeframe.name] = res
