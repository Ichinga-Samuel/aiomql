# from datetime import datetime
# from collections import defaultdict
# from pickle import HIGHEST_PROTOCOL
# import _pickle as pickle
# import lzma
# import asyncio
# from itertools import product
# from typing import Iterable, TypeAlias
#
# from .meta_trader import MetaTrader
# from .constants import TimeFrame
# from .. import account, Account, Ticks, Symbol, Candles
#
# Rates: TypeAlias = dict[Symbol, dict[TimeFrame, Candles]]
# PriceTicks: TypeAlias = dict[Symbol, Ticks]
#
#
# class MetaTester(MetaTrader):

#     def __init__(self, *, file=None, data: 'TestData' = None):
#         self.file = file
#
#     @property
#     def data(self):
#         return TestData.load(self.file)
#
#
# class TestData:
#     rates: Rates
#     ticks: PriceTicks
#     account: Account
#
#     def __init__(self, symbols: Iterable[Symbol], timeframes: Iterable[TimeFrame],  start: datetime, end: datetime, file: str):
#         self.symbols = symbols
#         self.timeframes = timeframes
#         self.start = start
#         self.end = end
#         self.file = file
#
#     @property
#     async def _account(self) -> Account:
#         await account.refresh()
#         return account
#
#     @property
#     async def _ticks(self) -> PriceTicks:
#         tasks = []
#         symbols = []
#         for symbol in self.symbols:
#             coro = symbol.copy_ticks_range(date_from=self.start, date_to=self.end)
#             symbols.append(symbol)
#             tasks.append(asyncio.create_task(coro))
#         ticks = await asyncio.gather(*tasks)
#         return {symbol: ticks for symbol, ticks in zip(symbols, ticks)}
#
#     @property
#     async def _rates(self) -> Rates:
#         _data = {'tasks': [], 'symbols': [], 'timeframes': []}
#         args: Iterable[tuple[Symbol, TimeFrame]] = product(self.symbols, self.timeframes)
#         for symbol, timeframe in args:
#             coro = symbol.copy_rates_range(date_from=self.start, date_to=self.end, timeframe=timeframe)
#             _data['tasks'].append(asyncio.create_task(coro))
#             _data['symbols'].append(symbol)
#             _data['timeframes'].append(timeframe)
#         _data['rates'] = await asyncio.gather(*_data['tasks'])
#
#         data = defaultdict(dict)
#         for rates, symbol, timeframe in zip(_data['rates'], _data['symbols'], _data['timeframes']):
#             data[symbol] |= {timeframe: rates}
#         return data
#
#     async def copy_data(self):
#         self.rates, self.ticks, self.account = await asyncio.gather(self._rates, self._ticks, self._account)
#
#     async def dumps(self):
#         return pickle.dumps(self, protocol=HIGHEST_PROTOCOL)
#
#     async def dump(self):
#         await self.copy_data()
#         with lzma.open(self.file, 'wb') as fh:
#             pickle.dump(self, fh, protocol=HIGHEST_PROTOCOL)
#
#     @classmethod
#     def load(cls, file) -> 'TestData':
#         with lzma.open(file, 'rb') as fh:
#             return pickle.load(fh)
#
#     @classmethod
#     def loads(cls, obj):
#         return pickle.loads(obj)
#
