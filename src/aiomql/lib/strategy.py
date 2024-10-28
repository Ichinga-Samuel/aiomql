"""The base class for creating strategies."""
import asyncio
from time import time
from typing import TypeVar
from abc import ABC, abstractmethod
from datetime import time as dtime
from logging import getLogger

from ..core.meta_trader import MetaTrader
from ..core import Config
from ..core.meta_backtester import MetaBackTester
from ..core.event_manager import EventManager
from .sessions import Sessions, Session
from .symbol import Symbol as _Symbol

Symbol = TypeVar("Symbol", bound=_Symbol)
logger = getLogger(__name__)


class Strategy(ABC):
    """The base class for creating strategies.

    Attributes:
        name (str): The name of the strategy.
        symbol (Symbol): The Financial Instrument as a Symbol Object
        parameters (Dict): A dictionary of parameters for the strategy.
        sessions (Sessions): The sessions to use for the strategy.
        running (bool): A flag to indicate if the strategy is running.

    Notes:
        Define the name of a strategy as a class attribute. If not provided, the class name will be used as the name.
    """
    name: str
    symbol: Symbol
    sessions: Sessions
    mt5: MetaTrader | MetaBackTester
    config: Config
    running: bool
    parameters = {}
    event_manager = EventManager
    current_session = Session

    def __init__(self, *, symbol: Symbol, params: dict = None, sessions: Sessions = None, name=''):
        """Initiate the parameters dict and add name and symbol fields.
        Use class name as strategy name if name is not provided

        Args:
            symbol (Symbol): The Financial instrument
            params (Dict): Trading strategy parameters
        """
        self.parameters = {**self.parameters} | (params or {})
        self.symbol = symbol
        self.name = name or self.__class__.__name__
        self.parameters["symbol"] = symbol.name
        self.parameters["name"] = self.name
        self.running = True
        self.sessions = sessions or Sessions(sessions=[Session(start=0, end=dtime(hour=23, minute=59, second=59))])
        self.config = Config()
        self.mt5 = MetaTrader() if self.config.mode != 'backtest' else MetaBackTester()
        self.event_manager = EventManager()

    def __repr__(self):
        return f"{self.name}({self.symbol!r})"

    def __getattr__(self, item):
        if item in self.parameters:
            return self.parameters[item]
        raise AttributeError(f'{item} not an attribute of {self.name}')

    def __setattr__(self, key, value):
        if key in self.parameters:
            self.parameters[key] = value
        super().__setattr__(key, value)

    async def __aenter__(self):
        await self.sessions.check()
        self.running = True
        self.current_session = self.sessions.current_session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.current_session.close() if self.current_session else ...
            self.running = False
        except Exception as err:
            logger.error(f"Error: {err}")

    @staticmethod
    async def live_sleep(*, secs: float):
        """Sleep for the needed amount of seconds in between requests to the terminal.
        computes the accurate amount of time needed to sleep ensuring that the next request is made at the start of
        a new bar and making cooperative multitasking possible.

        Args:
            secs (float): The time in seconds. Usually the timeframe you are trading on.
        """
        mod = time() % secs
        secs = secs - mod if mod != 0 else mod
        await asyncio.sleep(secs + 0.1)

    async def sleep(self, *, secs: float):
        """Sleep for the needed amount of seconds in between requests to the terminal.
        computes the accurate amount of time needed to sleep ensuring that the next request is made at the start of
        a new bar and making cooperative multitasking possible.

        Args:
            secs (float): The time in seconds. Usually the timeframe you are trading on.
        """
        if self.config.mode == 'backtest':
            await self.backtest_sleep(secs=secs)
        else:
            await self.live_sleep(secs=secs)

    async def backtest_sleep(self, *, secs: float):
        # print(f"Sleeping for {secs} seconds")
        try:
            _time = self.config.backtest_engine.cursor.time
            mod = _time % secs
            # print('mod', mod)
            secs = secs - mod if mod != 0 else mod
            # print('secs', secs)
            if self.event_manager.num_main_tasks == 1:
                self.config.backtest_engine.fast_forward(steps=int(secs))
                await self.event_manager.wait()

            elif self.event_manager.num_main_tasks > 1:
                _time = self.config.backtest_engine.cursor.time + secs
                # print(_time, self.config.backtest_engine.cursor.time)
                while _time > self.config.backtest_engine.cursor.time:
                    print(f"Time in sleep {self.symbol}: {self.config.backtest_engine.cursor.time}")
                    await self.event_manager.wait()

                # await self.event_manager.wait()
            else:
                await self.event_manager.wait()
        except Exception as err:
            logger.error(f"Error: {err} in backtest_sleep")

    async def run_strategy(self):
        """Run the strategy."""
        if self.config.mode == 'live':
            await self.live_strategy()
        elif self.config.mode == 'backtest':
            await self.backtest_strategy()

    async def live_strategy(self):
        """Run the strategy."""
        async with self as _:
            while self.running:
                await self.sessions.check()
                await self.trade()

    async def backtest_strategy(self):
        """Backtest the strategy."""
        try:
            async with self as _:
                while self.running:
                    async with self.event_manager.condition:
                        await self.sessions.check()
                        await self.event_manager.wait()
                        await self.test()
        except Exception as err:
            logger.error(f"Error: {err} in backtest_strategy")

    @abstractmethod
    async def trade(self):
        """Place trades using this method. This is the main method of the strategy.
         It will be called by the strategy runner.
        """
        raise NotImplementedError("Implement this method in your subclass")

    async def test(self):
        await self.trade()
