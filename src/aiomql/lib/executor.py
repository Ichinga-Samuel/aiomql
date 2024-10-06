import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Coroutine, Callable
from logging import getLogger

from .strategy import Strategy

logger = getLogger(__name__)


class Executor:
    """Executor class for running multiple strategies on multiple symbols concurrently.

    Attributes:
        executor (ThreadPoolExecutor): The executor object.
        strategy_runners (list): List of strategies.
        coroutines (dict[Coroutine, dict]): A dictionary of coroutines to run in the executor
        functions (dict[Callable, dict]): A dictionary of functions to run in the executor
        loop (asyncio.AbstractEventLoop): The event loop
    """
    loop: asyncio.AbstractEventLoop

    def __init__(self):
        self.executor = ThreadPoolExecutor
        self.strategy_runners: list[Strategy] = []
        self.coroutines: dict[Coroutine | Callable: dict] = {}
        self.functions: dict[Callable: dict] = {}

    def add_function(self, *, function: Callable, kwargs: dict):
        self.functions[function] = kwargs

    def add_coroutine(self, *, coroutine: Coroutine, kwargs: dict):
        self.coroutines[coroutine] = kwargs

    def add_strategies(self, *, strategies: tuple[Strategy]):
        """Add multiple strategies at once

        Args:
            strategies (Sequence[Strategy]): A sequence of strategies.
        """
        self.strategy_runners.extend(strategies)

    def add_strategy(self, *, strategy: Strategy):
        """Add a strategy instance to the list of workers

        Args:
            strategy (Strategy): A strategy object
        """
        self.strategy_runners.append(strategy)

    def run_strategy(self, strategy: Strategy):
        """Wraps the coroutine trade method of each strategy with 'asyncio.run'.

        Args:
            strategy (Strategy): A strategy object
        """
        self.loop.run_until_complete(strategy.run_strategy())

    def run_coroutine(self, func, kwargs: dict):
        """
        Run a coroutine function

        Args:
            func: The coroutine. A variadic function.
            kwargs: A dictionary of keyword arguments for the function
        """
        try:
            self.loop.run_until_complete(func(**kwargs))
        except Exception as err:
            logger.error(f'Error: {err}. Unable to run function')

    async def execute(self, *, workers: int = 5):
        """Run the strategies with a threadpool executor.

        Args:
            workers: Number of workers to use in executor pool. Defaults to 5.

        Notes:
            No matter the number specified, the executor will always use a minimum of 5 workers.
        """
        workers_ = sum([len(self.strategy_runners), len(self.functions), len(self.coroutines)])
        workers = max(workers, workers_)
        self.loop = asyncio.get_running_loop()
        with self.executor(max_workers=workers) as executor:
            [self.loop.run_in_executor(executor, self.run_strategy, worker) for worker in self.strategy_runners]
            [self.loop.run_in_executor(executor, self.run_coroutine, coroutine, kwargs) for coroutine,
            kwargs in self.coroutines.items()]
            [self.loop.run_in_executor(executor, function, kwargs) for function, kwargs in self.functions.items()]
