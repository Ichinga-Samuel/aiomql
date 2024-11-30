import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Coroutine, Callable
import os
from logging import getLogger

from ..core.config import Config
from .strategy import Strategy

logger = getLogger(__name__)


class Executor:
    """Executor class for running multiple strategies on multiple symbols concurrently.

    Attributes:
        executor (ThreadPoolExecutor): The executor object.
        strategy_runners (list): List of strategies.
        coroutines (list[Coroutine]): A list of coroutines to run in the executor
        functions (dict[Callable, dict]): A dictionary of functions to run in the executor
    """

    executor: ThreadPoolExecutor
    tasks: list[asyncio.Task]
    config: Config

    def __init__(self):
        self.strategy_runners: list[Strategy] = []
        self.coroutines: list[Coroutine] = []
        self.coroutine_threads: list[Coroutine] = []
        self.functions: dict[Callable:dict] = {}
        self.tasks = []
        self.config = Config()
        self.timeout = None  # Timeout for the executor. For testing purposes only

    def add_function(self, *, function: Callable, kwargs: dict = None):
        kwargs = kwargs or {}
        self.functions[function] = kwargs

    def add_coroutine(self, *, coroutine: Callable | Coroutine, kwargs: dict = None, on_separate_thread=False):
        kwargs = kwargs or {}
        coroutine = coroutine(**kwargs)
        self.coroutines.append(coroutine) if on_separate_thread is False else self.coroutine_threads.append(coroutine)

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

    async def create_strategy_task(self, strategy: Strategy):
        task = asyncio.create_task(strategy.run_strategy())
        self.tasks.append(task)
        await task

    def run_strategy(self, strategy: Strategy):
        """Wraps the coroutine trade method of each strategy with 'asyncio.run'.

        Args:
            strategy (Strategy): A strategy object
        """
        asyncio.run(self.create_strategy_task(strategy))

    async def create_coroutine_task(self, coroutine: Coroutine):
        task = asyncio.create_task(coroutine)
        self.tasks.append(task)
        await task

    async def create_coroutines_task(self):
        """"""
        coros = [asyncio.create_task(coroutine) for coroutine in self.coroutines]
        # task = asyncio.create_task(asyncio.gather(*coros, return_exceptions=False))
        self.tasks.extend(coros)
        # loop = asyncio.get_running_loop()
        # loop.run_in_executor()
        task = asyncio.gather(*coros, return_exceptions=True)
        self.tasks.append(task)
        await task
        # await task
        # return task

    def run_coroutine_tasks(self):
        """Run all coroutines in the executor"""
        asyncio.run(self.create_coroutines_task())

    def run_coroutine_task(self, coroutine):
        asyncio.run(self.create_coroutine_task(coroutine))

    @staticmethod
    def run_function(function: Callable, kwargs: dict):
        """Run a function

        Args:
            function: The function to run
            kwargs: A dictionary of keyword arguments for the function
        """
        try:
            function(**kwargs)
        except Exception as err:
            logger.error(f"Error: {err}. Unable to run function: {function.__name__}")

    async def exit(self):
        """Shutdown the executor"""
        start = asyncio.get_event_loop().time()
        try:
            while self.config.shutdown is False and self.config.force_shutdown is False:
                if self.timeout is not None and self.timeout < (asyncio.get_event_loop().time() - start):
                    self.config.shutdown = True
                timeout = self.timeout or 120
                await asyncio.sleep(timeout)

            print("Shutting down executor")
            for strategy in self.strategy_runners:
                strategy.running = False
            self.executor.shutdown(wait=False, cancel_futures=True)

            for task in self.tasks:
                task.cancel()


            # self.executor.shutdown(wait=False, cancel_futures=True)
            if self.config.force_shutdown:
                os._exit(1)
        except Exception as err:
            logger.error(f"Error: {err}. Unable to shutdown executor")

    def execute(self, *, workers: int = 5):
        """Run the strategies with a threadpool executor.

        Args:
            workers: Number of workers to use in executor pool. Defaults to 5.

        Notes:
            No matter the number specified, the executor will always use a minimum of 5 workers.
        """
        workers_ = len(self.strategy_runners) + len(self.functions) + len(self.coroutine_threads) + 2
        workers = max(workers, workers_)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            self.executor = executor
            [self.executor.submit(self.run_strategy, strategy) for strategy in self.strategy_runners]
            [self.executor.submit(function, **kwargs) for function, kwargs in self.functions.items()]
            [self.executor.submit(self.run_coroutine_task, coroutine) for coroutine in self.coroutine_threads]
            self.executor.submit(self.run_coroutine_tasks)
