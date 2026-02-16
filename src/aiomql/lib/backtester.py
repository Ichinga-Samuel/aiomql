"""BackTester module for strategy backtesting.

This module provides the BackTester class for running trading strategies
against historical data using the backtest engine. It coordinates
strategy execution, account simulation, and result collection.

Example:
    Running a backtest::

        from aiomql import BackTester, BackTestEngine
        engine = BackTestEngine(...)
        backtester = BackTester(backtest_engine=engine)
        backtester.add_strategy(strategy=my_strategy)
        backtester.execute()
"""

import asyncio
import logging
import time
from typing import Type, Iterable, Callable, Coroutine

from .executor import Executor
from ..core.config import Config
from ..core.backtesting.backtest_controller import BackTestController
from ..core.meta_backtester import MetaBackTester
from ..core.backtesting.backtest_engine import BackTestEngine
from .symbol import Symbol as Symbol
from .strategy import Strategy as Strategy

logger = logging.getLogger(__name__)


class BackTester:
    """The bot class. Create a bot instance to run your strategies.

    Attributes:
        executor: The default thread executor.
        config (Config): Config instance
        mt (MetaBackTester): MetaTrader instance
    """

    config: Config
    executor: Executor
    mt: MetaBackTester
    backtest_engine: BackTestEngine
    backtest_controller: BackTestController
    strategies: list[Strategy]

    def __init__(self, *, backtest_engine: BackTestEngine):
        self.config = Config()
        self.executor = Executor()
        self.mt = MetaBackTester()
        self.backtest_engine = backtest_engine
        self.backtest_controller = BackTestController()
        self.strategies = []

    def initialize_sync(self):
        """Prepares the bot by signing in to the trading account and initializing the symbols for the trading session.
        Starts the global task queue.

        Raises:
            SystemExit if sign in was not successful
        """
        try:
            self.mt.initialize_sync()
            login = self.mt.login_sync()
            if not login:
                logger.critical(f"Unable to sign in to MetaTrder 5 Terminal")
                raise Exception("Unable to sign in to MetaTrader 5 Terminal")
            logger.info("Login Successful")
            self.backtest_engine.setup_account_sync()
            self.init_strategies_sync()
            if (strategies := len(self.executor.strategy_runners)) == 0:
                self.config.shutdown = True
                logger.warning("No strategies were added to the backtester. Exiting in one second")
                time.sleep(1)
                return
            self.config.task_queue.worker_timeout = 5
            self.add_coroutine(coroutine=self.config.task_queue.run, on_separate_thread=True)
            self.add_coroutine(coroutine=self.executor.exit)
            self.add_coroutine(coroutine=self.backtest_controller.control, on_separate_thread=True)
            parties = strategies + 1
            self.backtest_controller.set_parties(parties=parties)
        except Exception as err:
            logger.error(f"{err}. Backtester initialization failed")
            raise SystemExit

    async def initialize(self):
        """Prepares the bot by signing in to the trading account and initializing the symbols for the trading session.
        Starts the global task queue.

        Raises:
            SystemExit if sign in was not successful
        """
        try:
            await self.mt.initialize()
            login = await self.mt.login()
            if not login:
                logger.critical(f"Unable to sign in to MetaTrder 5 Terminal")
                raise Exception("Unable to sign in to MetaTrader 5 Terminal")
            logger.info("Login Successful")
            await self.backtest_engine.setup_account()
            await self.init_strategies()
            if (strategies := len(self.executor.strategy_runners)) == 0:
                self.config.shutdown = True
                logger.warning("No strategies were added to the backtester. Exiting in one second")
                await asyncio.sleep(1)
                return
            self.config.task_queue.worker_timeout = 5
            self.add_coroutine(coroutine=self.config.task_queue.run, on_separate_thread=True)
            self.add_coroutine(coroutine=self.executor.exit)
            self.add_coroutine(coroutine=self.backtest_controller.control, on_separate_thread=True)
            parties = strategies + 1
            self.backtest_controller.set_parties(parties=parties)
        except Exception as err:
            logger.error(f"{err}. Backtester initialization failed")
            raise SystemExit

    def add_coroutine(self, *, coroutine: Callable[..., ...] | Coroutine, on_separate_thread=False, **kwargs):
        """Add a coroutine to the executor.

        Args:
            coroutine (Coroutine): A coroutine to be executed
            on_separate_thread (bool): Run the coroutine
        Returns:

        """
        self.executor.add_coroutine(coroutine=coroutine, kwargs=kwargs, on_separate_thread=on_separate_thread)

    def execute(self):
        """Execute the bot."""
        self.initialize_sync()
        if self.config.shutdown is False:
            self.executor.execute()

    async def start(self):
        """Initialize the bot and execute it. Similar to calling `execute` method but is a coroutine."""
        await self.initialize()
        if self.config.shutdown is False:
            self.executor.execute()
        self.executor.execute()

    def add_strategy(self, *, strategy: Strategy):
        """Add a strategy to the list of strategies.
        An added strategy will only run if it's symbol was successfully initialized, and it is added to the executor.

        Args:
            strategy (Strategy): A Strategy instance to run on bot

        Notes:
            Make sure the symbol has been added to the market
        """
        self.strategies.append(strategy)

    def add_strategies(self, *, strategies: Iterable[Strategy]):
        """Add multiple strategies at the same time

        Args:
            strategies: A list of strategies
        """
        [self.add_strategy(strategy=strategy) for strategy in strategies]

    def add_strategy_all(
        self, *, strategy: Type[Strategy], params: dict | None = None, symbols: list[Symbol] = None, **kwargs
    ):
        """Use this to run a single strategy on multiple symbols with the same parameters and keyword arguments.

        Keyword Args:
            strategy (Strategy): Strategy class
            params (dict): A dictionary of parameters for the strategy
            symbols (list): A list of symbols to run the strategy on
        """
        [self.add_strategy(strategy=strategy(symbol=symbol, params=params, **kwargs)) for symbol in symbols]

    async def init_strategy(self, *, strategy: Strategy) -> bool:
        """Initialize a single strategy. This method is called internally by the bot."""
        res = await strategy.symbol.initialize()
        if res:
            self.executor.add_strategy(strategy=strategy)
        return res

    def init_strategy_sync(self, *, strategy: Strategy) -> bool:
        """Initialize a single strategy. This method is called internally by the bot."""
        try:
            res = strategy.symbol.initialize_sync()
            if res:
                self.executor.add_strategy(strategy=strategy)
            return res
        except Exception as err:
            logger.error("%s: Unable to initialize strategy", err)
            return False

    async def init_strategies(self):
        """Initialize the symbols for the current trading session. This method is called internally by the bot."""
        tasks = [self.init_strategy(strategy=strategy) for strategy in self.strategies]
        await asyncio.gather(*tasks)

    def init_strategies_sync(self):
        """Initialize the symbols for the current trading session. This method is called internally by the bot."""
        [self.init_strategy_sync(strategy=strategy) for strategy in self.strategies]
