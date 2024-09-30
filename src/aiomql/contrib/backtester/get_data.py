from dataclasses import dataclass, field, fields
import pickle
from pathlib import Path
from datetime import datetime
from logging import getLogger
from typing import Sequence, NamedTuple

import MetaTrader5
import pytz
from numpy import ndarray

from ...core.meta_trader import MetaTrader
from ...core.config import Config
from ...core.constants import TimeFrame
from ...core.task_queue import TaskQueue, QueueItem
from ...utils import backoff_decorator

logger = getLogger(__name__)


class Cursor(NamedTuple):
    index: int
    time: int


@dataclass
class TestData:
    name: str = ''
    terminal: dict[str, [str | int | bool | float]] = field(default_factory=dict)
    version: tuple[int, int, str] = (0, 0, '')
    account: dict = field(default_factory=dict)
    symbols: dict[str, dict] = field(default_factory=dict)
    prices: dict[str, ndarray] = field(default_factory=dict)
    ticks: dict[str, ndarray] = field(default_factory=dict)
    rates: dict[str, dict[int, ndarray]] = field(default_factory=dict)
    span: range = range(0)
    range: range = range(0)
    orders: dict[int, dict] = field(default_factory=lambda: {})
    deals: dict[int, dict] = field(default_factory=lambda: {})
    positions: dict[int, dict] = field(default_factory=lambda: {})
    open_positions: set[int, ...] = field(default_factory=lambda: set())
    cursor: Cursor = None
    margins: dict[int, float] = field(default_factory=lambda: {})

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def set_attrs(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items() if k in self.fields]

    @property
    def fields(self):
        return [f.name for f in fields(self)]


class GetData:
    data: TestData

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
        self.data = TestData(name=name, span=self.span, range=self.range)
        self.mt5 = MetaTrader()
        self.task_queue = TaskQueue(workers=250)

    @classmethod
    def pickle_data(cls, *, data: TestData, name: str | Path):
        """"""
        try:
            with open(name, 'wb') as fo:
                pickle.dump(data, fo, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as err:
            logger.error(f"Error in dump_data: {err}")


    @classmethod
    def load_data(cls, *, name: str | Path) -> TestData:
        """"""
        try:
            with open(name, 'rb') as fo:
                data = pickle.load(fo)
                return data
        except Exception as err:
            logger.error(f"Error: {err}")

    def save_data(self, *, name: str | Path = ''):
        name = name or self.name
        with open(name, 'wb') as fo:
            pickle.dump(self.data, fo, protocol=pickle.HIGHEST_PROTOCOL)

    async def get_data(self, workers: int = None):
        """"""
        if workers:
            self.task_queue.workers = workers

        q_items = [QueueItem(self.get_symbols_rates),
                   QueueItem(self.get_symbols_ticks),
                   QueueItem(self.get_symbols_prices),
                   QueueItem(self.get_symbols_info),
                   ]

        [self.task_queue.add(item=item, priority=0, must_complete=True) for item in q_items]

        if not self.data.account:
            self.task_queue.add(item=QueueItem(self.get_account_info), must_complete=True)

        if not self.data.terminal:
            self.task_queue.add(item=QueueItem(self.get_terminal_info), must_complete=True)

        if not self.data.version:
            self.task_queue.add(item=QueueItem(self.get_version), must_complete=True)

        await self.task_queue.run()

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
        [self.task_queue.add(item=QueueItem(self.get_symbol_info, symbol=symbol))
         for symbol in self.symbols if self.data.symbols.get(symbol) is None]

    async def get_symbols_ticks(self):
        """"""
        [self.task_queue.add(item=QueueItem(self.get_symbol_ticks, symbol=symbol))
         for symbol in self.symbols if self.data.ticks.get(symbol) is None]

    async def get_symbols_prices(self):
        """"""
        [self.task_queue.add(item=QueueItem(self.get_symbol_prices, symbol=symbol))
         for symbol in self.symbols if self.data.prices.get(symbol) is None]

    async def get_symbols_rates(self):
        """"""
        [self.task_queue.add(item=QueueItem(self.get_symbol_rates, symbol=symbol, timeframe=timeframe), priority=4)
                  for symbol in self.symbols for timeframe in self.timeframes
         if self.data.rates.get(symbol, {}).get(timeframe) is None]

    @backoff_decorator
    async def get_symbol_info(self, *, symbol: str):
        """"""
        res = await self.mt5.symbol_info(symbol)
        self.data.symbols[symbol] = res._asdict()

    @backoff_decorator
    async def get_symbol_ticks(self, *, symbol: str):
        """"""
        res = await self.mt5.copy_ticks_range(symbol, self.start, self.end, MetaTrader5.COPY_TICKS_ALL)
        self.data.ticks[symbol] = res

    @backoff_decorator
    async def get_symbol_prices(self, *, symbol: str):
        """"""
        res = await self.mt5.copy_ticks_range(symbol, self.start, self.end, MetaTrader5.COPY_TICKS_ALL)
        self.data.prices[symbol] = res

    @backoff_decorator
    async def get_symbol_rates(self, *, symbol: str, timeframe: TimeFrame):
        """"""
        res = await self.mt5.copy_rates_range(symbol, timeframe, self.start, self.end)
        self.data.rates.setdefault(symbol, {})[timeframe] = res
