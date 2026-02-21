"""Executor module for concurrent strategy execution.

This module provides the Executor class for running multiple trading
strategies concurrently using a ThreadPoolExecutor. It handles
strategy lifecycle, signal handling, and graceful shutdown.

Example:
    Running strategies::

        executor = Executor()
        executor.add_strategy(strategy=my_strategy)
        executor.execute(workers=5)
"""

import asyncio
import inspect
import os
import time
from concurrent.futures import ThreadPoolExecutor
from signal import signal, SIGINT
from typing import Coroutine, Callable
from logging import getLogger

from ..core.config import Config
from .strategy import Strategy

logger = getLogger(__name__)


class Executor:
    """Executor class for running multiple strategies on multiple symbols concurrently.

    Attributes:
        executor (ThreadPoolExecutor): The executor object.
        strategy_runners (list): List of strategies.
        coroutines (dict[Coroutine, dict]): A list of coroutines to run in the executor
        coroutine_threads (dict[Coroutine, dict]): A list of coroutines to run in the executor
        functions (dict[Callable, dict]): A dictionary of functions to run in the executor
    """
    executor: ThreadPoolExecutor
    config: Config

    def __init__(self):
        """Initializes the Executor with empty task collections.

        Sets up empty lists and dictionaries for strategies, coroutines,
        and functions. Registers a SIGINT handler for graceful shutdown.

        Attributes:
            strategy_runners (list[Strategy]): Strategies to execute.
            coroutines (dict): Coroutines to run on the shared event loop.
            coroutine_threads (dict): Coroutines to run on separate threads.
            functions (dict): Synchronous functions to run as tasks.
            config (Config): The global configuration singleton.
            timeout (float | None): Executor timeout in seconds. For
                testing purposes only.
        """
        self.strategy_runners: list[Strategy] = []
        self.coroutines: dict[Coroutine: dict] = {}
        self.coroutine_threads: dict[Coroutine: dict] = {}
        self.functions: dict[Callable:dict] = {}
        self.config = Config()
        self.timeout = None  # Timeout for the executor. For testing purposes only
        signal(SIGINT, self.sigint_handle)

    def add_function(self, *, function: Callable, kwargs: dict = None):
        """Registers a synchronous function to run in the executor.

        Args:
            function: The callable to execute.
            kwargs: Optional keyword arguments for the function.
        """
        kwargs = kwargs or {}
        self.functions[function] = kwargs

    def add_coroutine(self, *, coroutine: Callable | Coroutine, kwargs: dict = None, on_separate_thread=False):
        """Registers a coroutine to run in the executor.

        Args:
            coroutine: The async callable or coroutine to execute.
            kwargs: Optional keyword arguments for the coroutine.
            on_separate_thread: If True, the coroutine runs on its own
                thread with a dedicated event loop. If False, it runs on
                the shared event loop. Defaults to False.
        """
        kwargs = kwargs or {}
        if on_separate_thread:
            self.coroutine_threads[coroutine] = kwargs
        else:
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

    @staticmethod
    def run_strategy(strategy: Strategy):
        """Wraps the coroutine trade method of each strategy with 'asyncio.run'.

        Args:
            strategy (Strategy): A strategy object
        """
        if inspect.iscoroutinefunction(strategy.run_strategy):
            asyncio.run(strategy.run_strategy())
        else:
            strategy.run_strategy()

    async def run_coroutine_tasks(self):
        """Run all coroutines in the executor"""
        try:
            await asyncio.gather(*[coroutine(**kwargs) for coroutine, kwargs in self.coroutines.items()],
                                 return_exceptions=True)
        except Exception as err:
            logger.error("%s: Error occurred in run_coroutine_tasks", err)

    @staticmethod
    def run_coroutine_task(coroutine, kwargs):
        """Runs a single coroutine on a new event loop in a separate thread.

        Args:
            coroutine: The async callable to execute.
            kwargs: Keyword arguments for the coroutine.
        """
        asyncio.run(coroutine(**kwargs))

    @staticmethod
    def run_function(function: Callable, kwargs: dict):
        """Run a function
        Args:
            function: The function to run
            kwargs: A dictionary of keyword arguments for the function
        """
        function(**kwargs)

    def sigint_handle(self, signum, frame):
        """Handles SIGINT (Ctrl+C) by signaling a shutdown.

        Args:
            signum: The signal number received.
            frame: The current stack frame.
        """
        self.config.shutdown = True

    def exit(self):
        """Monitors for shutdown signals and gracefully shuts down the executor.

        Runs in a loop checking for shutdown or timeout conditions.
        When triggered, stops all strategies, cancels the task queue,
        and shuts down the thread pool executor.
        """
        start = time.time()
        try:
            while self.config.shutdown is False and self.config.force_shutdown is False:
                if self.timeout is not None and self.timeout < (time.time() - start):
                    self.config.shutdown = True
                    break
                timeout = self.timeout or 1
                time.sleep(timeout)
            for strategy in self.strategy_runners:
                strategy.running = False
            self.config.task_queue.cancel()
            self.executor.shutdown(wait=False, cancel_futures=False)

            if self.config.force_shutdown:
                os._exit(1)
        except Exception as err:
            logger.error("%s: Unable to shutdown executor", err)
            os._exit(1)

    def execute(self, *, workers: int = 5):
        """Run the strategies with a threadpool executor.

        Args:
            workers: Number of workers to use in executor pool. Defaults to 5.

        Notes:
            No matter the number specified, the executor will always use a minimum of 5 workers.
        """
        workers_ = len(self.strategy_runners) + len(self.functions) + len(self.coroutine_threads) + 3
        workers = max(workers, workers_)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            self.executor = executor
            [self.executor.submit(self.run_strategy, strategy) for strategy in self.strategy_runners]
            [self.executor.submit(function, **kwargs) for function, kwargs in self.functions.items()]
            [self.executor.submit(self.run_coroutine_task, coroutine, kwargs) for coroutine, kwargs in
             self.coroutine_threads.items()]
            self.executor.submit(asyncio.run, self.run_coroutine_tasks())
