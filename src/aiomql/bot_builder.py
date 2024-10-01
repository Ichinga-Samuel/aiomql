import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import Type, Iterable, Callable, Coroutine
import logging

from .executor import Executor
from .core.config import Config
from .core.meta_trader import MetaTrader
from .symbol import Symbol as Symbol
from .strategy import Strategy as Strategy

logger = logging.getLogger(__name__)


class Bot:
    """The bot class. Create a bot instance to run your strategies.

    Attributes:
        executor: The default thread executor.
        config (Config): Config instance
        mt (MetaTrader): MetaTrader instance

    """
    config: Config
    executor: Executor
    mt: MetaTrader

    def __init__(self):
        self.config = Config(bot=self)
        self.executor = Executor()
        self.mt = MetaTrader()

    @classmethod
    def run_bots(cls, funcs: dict[Callable: dict] = None, num_workers: int = None):
        """Run multiple scripts or bots in parallel with different accounts.

        Args:
            funcs (dict): A dictionary of functions to run with their respective keyword arguments as a dictionary
            num_workers (int): Number of workers to run the functions
        """
        num_workers = num_workers or len(funcs) * 2
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            for bot, kwargs in funcs.items():
                executor.submit(bot, **kwargs)

    async def initialize(self):
        """Prepares the bot by signing in to the trading account and initializing the symbols for the trading session.
        Starts the global task queue.

        Raises:
            SystemExit if sign in was not successful
        """
        try:
            login = await self.mt.login()
            if not login:
                logger.warning(f"Unable to sign in to MetaTrder 5 Terminal")
                raise SystemExit
            logger.info("Login Successful")
            await self.init_strategies()
            self.add_coroutine(self.config.task_queue.start)
        except Exception as err:
            logger.error(f"{err}. Bot initialization failed")
            raise SystemExit

    def add_function(self, func: Callable[..., ...], **kwargs: dict):
        """Add a function to the executor.

        Args:
            func (Callable): A function to be executed
            **kwargs (dict): Keyword arguments for the function
        """
        self.executor.add_function(func, kwargs)

    def add_coroutine(self, coro: Coroutine[..., ...], **kwargs):
        """Add a coroutine to the executor.

        Args:
            coro (Coroutine): A coroutine to be executed
            **kwargs (dict): keyword arguments for the coroutine

        Returns:

        """
        self.executor.add_coroutine(coro, kwargs)

    def execute(self):
        """Execute the bot."""
        asyncio.run(self.start())

    async def start(self):
        """Initialize the bot and execute it. Similar to calling `execute` method but is a coroutine."""
        await self.initialize()
        await self.executor.execute()

    def add_strategy(self, strategy: Strategy):
        """Add a strategy to the executor. An added strategy will only run if it's symbol was successfully initialized.

        Args:
            strategy (Strategy): A Strategy instance to run on bot

        Notes:
            Make sure the symbol has been added to the market
        """
        self.executor.add_worker(strategy)

    def add_strategies(self, strategies: Iterable[Strategy]):
        """Add multiple strategies at the same time

        Args:
            strategies: A list of strategies
        """
        [self.add_strategy(strategy) for strategy in strategies]

    def add_strategy_all(self, *, strategy: Type[Strategy], params: dict | None = None,
                         symbols: list[Symbol] = None, **kwargs):
        """Use this to run a single strategy on multiple symbols with the same parameters and keyword arguments.

        Keyword Args:
            strategy (Strategy): Strategy class
            params (dict): A dictionary of parameters for the strategy
            symbols (list): A list of symbols to run the strategy on
            **kwargs: Additional keyword arguments for the strategy
        """
        [
            self.add_strategy(strategy(symbol=symbol, params=params, **kwargs))
            for symbol in symbols
        ]

    @staticmethod
    async def init_strategy(strategy: Strategy) -> tuple[bool, Strategy]:
        """Initialize a single strategy. This method is called internally by the bot."""
        res = await strategy.symbol.init()
        return res, strategy

    async def init_strategies(self):
        """Initialize the symbols for the current trading session. This method is called internally by the bot."""
        tasks = [self.init_strategy(strategy) for strategy in self.executor.workers]
        for task in asyncio.as_completed(tasks):
            res = await task
            if not res[0]:
                logger.warning(f"Failed to initialize symbol {res[1].symbol}")
                self.executor.workers.remove(res[1])
