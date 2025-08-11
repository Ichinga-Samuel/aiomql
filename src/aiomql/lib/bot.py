import asyncio
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Type, Iterable, Callable, Coroutine
import logging

from .executor import Executor
from ..core.config import Config
from ..core.meta_trader import MetaTrader
from ..core.meta_backtester import MetaBackTester
from .symbol import Symbol as Symbol
from .strategy import Strategy as Strategy

logger = logging.getLogger(__name__)


class Bot:
    """The bot class. Creates a bot instance to run strategies.

    Attributes:
        executor: A thread executor.
        config (Config): Config instance
        mt (MetaTrader): MetaTrader instance
    """
    config: Config
    executor: Executor
    mt: MetaTrader
    strategies: list[Strategy]
    initialized: bool
    login: bool

    def __init__(self):
        self.config = Config(bot=self)
        self.executor = Executor()
        self.mt5 = MetaTrader() if self.config.mode != "backtest" else MetaBackTester()
        self.strategies = []
        self.initialized = False
        self.login = False

    @classmethod
    def process_pool(cls, processes: dict[Callable:dict] = None, num_workers: int = None):
        """Run multiple processes in parallel using a ProcessPoolExecutor. Each process should be a callable that accepts
        keyword arguments only.

        Args:
            processes (dict): A dictionary of processes to run with their respective keyword arguments as a dictionary
            num_workers (int): Number of workers to run the processes
        """
        num_workers = num_workers or len(processes) + 1
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            for bot, kwargs in processes.items():
                executor.submit(bot, **kwargs)

    async def start_terminal(self):
        """Start terminal and login asynchronously"""
        res = await self.mt5.initialize()
        if res:
            self.initialized = True
            res = await self.mt5.login()
            if res:
                self.login = True
        return res

    def start_terminal_sync(self):
        """Start terminal and login synchronously"""
        res = self.mt5.initialize_sync()
        if res:
            self.initialized = True
            res = self.mt5.login_sync()
            if res:
                self.login = True
        return res

    async def initialize(self):
        """Prepares the bot by signing in to the trading account and initializing the symbols for each strategy.
        Only strategies with successfully initialized symbols will be added to the executor. Starts the global task queue.

        Raises:
            SystemExit if sign_in was not successful
        """
        try:
            await self.start_terminal()
            if not self.login:
                logger.critical("Unable to sign in to MetaTrder 5 Terminal")
                raise Exception("Unable to sign in to MetaTrader 5 Terminal")
            logger.info("Login Successful")
            await self.init_strategies()
            self.add_coroutine(coroutine=self.config.task_queue.run, on_separate_thread=True)
            self.add_function(function=self.executor.exit)

            if len(self.executor.strategy_runners) == 0:
                logger.warning("No strategies were added to the bot. Exiting in one second")
                await asyncio.sleep(1)
                self.config.shutdown = True
        except Exception as err:
            logger.error("%s: Bot initialization failed", err)
            raise SystemExit

    def initialize_sync(self):
        """Prepares the bot by signing in to the trading account and initializing the symbols for each strategy.
        Only strategies with successfully initialized symbols will be added to the executor.
        Starts the global task queue.

        Raises:
            SystemExit if sign_in was not successful
        """
        try:
            self.start_terminal_sync()
            if not self.login:
                logger.critical("Unable to sign in to MetaTrder 5 Terminal")
                raise Exception("Unable to sign in to MetaTrader 5 Terminal")
            logger.info("Login Successful")
            self.init_strategies_sync()
            self.add_coroutine(coroutine=self.config.task_queue.run, on_separate_thread=True)
            self.add_function(function=self.executor.exit)

            if len(self.executor.strategy_runners) == 0:
                logger.warning("No strategies were added to the bot. Exiting in one second")
                time.sleep(1)
                self.config.shutdown = True
        except Exception as err:
            logger.error("%s: Bot initialization failed", err)
            raise SystemExit

    def add_function(self, *, function: Callable[..., ...], **kwargs):
        """Add a function to the executor.

        Args:
            function (Callable): A function to be executed
        """
        self.executor.add_function(function=function, kwargs=kwargs)

    def add_coroutine(self, *, coroutine: Callable[..., ...] | Coroutine, on_separate_thread=False, **kwargs):
        """Add a coroutine to the executor.

        Args:
            coroutine (Coroutine): A coroutine to be executed
            on_separate_thread (bool): Run the coroutine
        Returns:

        """
        self.executor.add_coroutine(coroutine=coroutine, kwargs=kwargs, on_separate_thread=on_separate_thread)

    def execute(self):
        """Start the bot in sync mode"""
        self.initialize_sync()
        if self.config.shutdown is False:
            self.executor.execute()

    async def start(self):
        """Initialize the bot and call the executor it."""
        await self.initialize()
        if self.config.shutdown is False:
            self.executor.execute()

    def add_strategy(self, *, strategy: Strategy):
        """Add a strategy to the list of strategies.

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
        res = await strategy.initialize()
        if res:
            self.executor.add_strategy(strategy=strategy)
        return res

    async def init_strategies(self):
        """Initialize the symbols for the current trading session. This method is called internally by the bot."""
        tasks = [self.init_strategy(strategy=strategy) for strategy in self.strategies]
        await asyncio.gather(*tasks, return_exceptions=True)

    def init_strategy_sync(self, *, strategy: Strategy) -> bool:
        """Initialize a single strategy. This method is called internally by the bot."""
        res = strategy.initialize_sync()
        if res:
            self.executor.add_strategy(strategy=strategy)
        return res

    def init_strategies_sync(self):
        """Initialize the symbols for the current trading session. This method is called internally by the bot."""
        [self.init_strategy_sync(strategy=strategy) for strategy in self.strategies]
