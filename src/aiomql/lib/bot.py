"""Bot module for orchestrating trading strategies.

This module provides the Bot class which serves as the main orchestrator
for running trading strategies. It handles terminal initialization,
strategy management, and execution coordination.

Example:
    Running a trading bot synchronously::

        from aiomql import Bot
        from my_strategies import MyStrategy

        bot = Bot()
        bot.add_strategy(strategy=MyStrategy(symbol=my_symbol))
        bot.execute()

    Running a trading bot asynchronously::

        import asyncio
        from aiomql import Bot
        from my_strategies import MyStrategy

        async def main():
            bot = Bot()
            bot.add_strategy(strategy=MyStrategy(symbol=my_symbol))
            await bot.start()

        asyncio.run(main())

    Running multiple bot instances in parallel::

        from aiomql import Bot

        def run_bot1():
            bot = Bot()
            # configure bot1
            bot.execute()

        def run_bot2():
            bot = Bot()
            # configure bot2
            bot.execute()

        Bot.process_pool(processes={run_bot1: {}, run_bot2: {}})
"""

import asyncio
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Type, Iterable, Callable, Coroutine
import logging

from .executor import Executor
from ..core.config import Config
from ..core.meta_trader import MetaTrader
from .symbol import Symbol as Symbol
from .strategy import Strategy as Strategy

logger = logging.getLogger(__name__)


class Bot:
    """The main bot class for orchestrating trading strategies.

    Creates a bot instance that manages the connection to MetaTrader 5,
    initializes strategies, and coordinates their execution through the
    Executor. Supports both synchronous and asynchronous operation modes.

    Attributes:
        config (Config): Configuration instance that holds bot settings and
            references to shared resources like the task queue.
        executor (Executor): Thread pool executor that manages the concurrent
            execution of strategies, coroutines, and functions.
        mt5 (MetaTrader): MetaTrader 5 interface instance.
            Uses MetaTrader for live/demo trading
        strategies (list[Strategy]): List of strategy instances to be
            initialized and run by the bot.
        initialized (bool): Flag indicating whether the terminal has been
            successfully initialized.
        login (bool): Flag indicating whether the login to the trading
            account was successful.

    Example:
        Basic usage with a single strategy::

            bot = Bot()
            bot.add_strategy(strategy=MyStrategy(symbol=Symbol(name="EURUSD")))
            bot.execute()

        Adding multiple strategies at once::

            bot = Bot()
            strategies = [
                Strategy1(symbol=symbol1),
                Strategy2(symbol=symbol2),
            ]
            bot.add_strategies(strategies=strategies)
            await bot.start()
    """
    config: Config
    executor: Executor
    mt5: MetaTrader
    strategies: list[Strategy]
    initialized: bool
    login: bool

    def __init__(self):
        """Initialize a new Bot instance.

        Creates and configures a new bot with a Config instance, Executor,
        and the appropriate MetaTrader interface based on the configuration
        mode. Initializes all tracking flags and the empty strategies list.

        Note:
            The bot automatically selects MetaTrader for live/demo trading.
        """
        self.config = Config(bot=self)
        self.executor = Executor()
        self.mt5 = MetaTrader()
        self.strategies = []
        self.initialized = False
        self.login = False

    @classmethod
    def process_pool(cls, processes: dict[Callable:dict] = None, num_workers: int = None):
        """Run multiple bot processes in parallel using a ProcessPoolExecutor.

        This class method enables running multiple independent bot instances
        in separate processes for parallel execution. Each process should be
        a callable that accepts keyword arguments only.

        Args:
            processes (dict[Callable, dict]): A dictionary mapping callables
                (typically bot runner functions) to their respective keyword
                arguments. Each callable will be submitted to the process pool.
            num_workers (int, optional): Maximum number of worker processes.
                Defaults to len(processes) + 1 if not specified.

        Example:
            Running two bot configurations in parallel::

                def run_scalper(**kwargs):
                    bot = Bot()
                    # configure scalper bot
                    bot.execute()

                def run_swing(**kwargs):
                    bot = Bot()
                    # configure swing bot
                    bot.execute()

                Bot.process_pool(
                    processes={
                        run_scalper: {"param": "value1"},
                        run_swing: {"param": "value2"}
                    },
                    num_workers=3
                )
        """
        num_workers = num_workers or len(processes) + 1
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            for bot, kwargs in processes.items():
                executor.submit(bot, **kwargs)

    async def start_terminal(self) -> bool:
        """Start the MetaTrader 5 terminal and login asynchronously.

        Initializes the connection to the MetaTrader 5 terminal and attempts
        to login to the trading account. Updates the `initialized` and `login`
        flags based on the results.

        Returns:
            bool: True if both initialization and login were successful,
                False otherwise.

        Note:
            This method sets `self.initialized` to True if terminal
            initialization succeeds, and `self.login` to True only if
            both initialization and login succeed.
        """
        res = await self.mt5.initialize()
        if res:
            self.initialized = True
            res = await self.mt5.login()
            if res:
                self.login = True
        return res

    def start_terminal_sync(self) -> bool:
        """Start the MetaTrader 5 terminal and login synchronously.

        Synchronous version of start_terminal(). Initializes the connection
        to the MetaTrader 5 terminal and attempts to login to the trading
        account. Updates the `initialized` and `login` flags based on results.

        Returns:
            bool: True if both initialization and login were successful,
                False otherwise.

        Note:
            This method sets `self.initialized` to True if terminal
            initialization succeeds, and `self.login` to True only if
            both initialization and login succeed.
        """
        res = self.mt5.initialize_sync()
        if res:
            self.initialized = True
            res = self.mt5.login_sync()
            if res:
                self.login = True
        return res

    async def initialize(self) -> None:
        """Prepare the bot for trading asynchronously.

        Performs complete bot initialization including:
        1. Starting the terminal and logging into the trading account
        2. Initializing all added strategies (only those with successfully
           initialized symbols are added to the executor)
        3. Starting the global task queue on a separate thread
        4. Adding the executor's exit function for graceful shutdown

        If no strategies are successfully initialized, the bot will set
        the shutdown flag after a 1-second delay.

        Raises:
            SystemExit: If login to the MetaTrader 5 terminal fails or
                any other exception occurs during initialization.

        Note:
            This method is called internally by the start() method.
            Strategies that fail initialization are silently skipped
            and not added to the executor.
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

    def initialize_sync(self) -> None:
        """Prepare the bot for trading synchronously.

        Synchronous version of initialize(). Performs complete bot
        initialization including:
        1. Starting the terminal and logging into the trading account
        2. Initializing all added strategies (only those with successfully
           initialized symbols are added to the executor)
        3. Starting the global task queue on a separate thread
        4. Adding the executor's exit function for graceful shutdown

        If no strategies are successfully initialized, the bot will set
        the shutdown flag after a 1-second delay.

        Raises:
            SystemExit: If login to the MetaTrader 5 terminal fails or
                any other exception occurs during initialization.

        Note:
            This method is called internally by the execute() method.
            Strategies that fail initialization are silently skipped
            and not added to the executor.
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

    def add_function(self, *, function: Callable[..., ...], **kwargs) -> None:
        """Add a synchronous function to the executor for execution.

        The function will be executed in a thread pool when the bot starts.
        Any additional keyword arguments passed to this method will be
        forwarded to the function when it is called.

        Args:
            function (Callable): A synchronous function to be executed.
                Must accept keyword arguments.
            **kwargs: Keyword arguments to pass to the function when executed.

        Example:
            Adding a monitoring function::

                def log_status(interval=60):
                    while True:
                        print("Bot is running...")
                        time.sleep(interval)

                bot.add_function(function=log_status, interval=30)
        """
        self.executor.add_function(function=function, kwargs=kwargs)

    def add_coroutine(
        self, *, coroutine: Callable[..., ...] | Coroutine, on_separate_thread: bool = False, **kwargs
    ) -> None:
        """Add an asynchronous coroutine to the executor for execution.

        The coroutine will be executed when the bot starts. By default,
        coroutines run in the main event loop, but can optionally run
        in a separate thread with its own event loop.

        Args:
            coroutine (Callable | Coroutine): An async function or coroutine
                to be executed. Must accept keyword arguments if any are provided.
            on_separate_thread (bool, optional): If True, the coroutine runs
                in a separate thread with its own event loop. Useful for
                long-running tasks that should not block the main loop.
                Defaults to False.
            **kwargs: Keyword arguments to pass to the coroutine when executed.

        Example:
            Adding a data collection coroutine::

                async def collect_data(symbol, interval=60):
                    while True:
                        data = await fetch_market_data(symbol)
                        save_data(data)
                        await asyncio.sleep(interval)

                bot.add_coroutine(
                    coroutine=collect_data,
                    symbol="EURUSD",
                    interval=30
                )

            Running on a separate thread::

                bot.add_coroutine(
                    coroutine=long_running_task,
                    on_separate_thread=True
                )
        """
        self.executor.add_coroutine(coroutine=coroutine, kwargs=kwargs, on_separate_thread=on_separate_thread)

    def execute(self) -> None:
        """Start the bot in synchronous mode.

        This is the main entry point for running the bot synchronously.
        Initializes the bot (terminal connection, login, strategies) and
        then starts the executor to run all strategies and tasks.

        The executor will continue running until a shutdown signal is
        received or all strategies complete.

        Example:
            Starting the bot::

                bot = Bot()
                bot.add_strategy(strategy=MyStrategy(symbol=my_symbol))
                bot.execute()  # Blocks until shutdown

        Note:
            If initialization sets the shutdown flag (e.g., no strategies
            were successfully initialized), the executor will not start.
        """
        self.initialize_sync()
        if self.config.shutdown is False:
            self.executor.execute()

    async def start(self) -> None:
        """Start the bot in asynchronous mode.

        This is the main entry point for running the bot asynchronously.
        Initializes the bot (terminal connection, login, strategies) and
        then starts the executor to run all strategies and tasks.

        The executor will continue running until a shutdown signal is
        received or all strategies complete.

        Example:
            Starting the bot asynchronously::

                async def main():
                    bot = Bot()
                    bot.add_strategy(strategy=MyStrategy(symbol=my_symbol))
                    await bot.start()  # Blocks until shutdown

                asyncio.run(main())

        Note:
            If initialization sets the shutdown flag (e.g., no strategies
            were successfully initialized), the executor will not start.
        """
        await self.initialize()
        if self.config.shutdown is False:
            self.executor.execute()

    def add_strategy(self, *, strategy: Strategy) -> None:
        """Add a strategy to the list of strategies.

        Adds a single strategy instance to the bot's strategy list. The
        strategy will be initialized when the bot starts and, if successful,
        will be executed by the executor.

        Args:
            strategy (Strategy): A Strategy instance to run on the bot.
                Must have a valid symbol assigned.

        Example:
            Adding a single strategy::

                from aiomql import Symbol
                from my_strategies import ScalperStrategy

                symbol = Symbol(name="EURUSD")
                strategy = ScalperStrategy(symbol=symbol, params={"risk": 0.01})
                bot.add_strategy(strategy=strategy)

        Note:
            Strategies are only initialized and added to the executor when
            the bot starts. Make sure the symbol is valid and available
            in the market.
        """
        self.strategies.append(strategy)

    def add_strategies(self, *, strategies: Iterable[Strategy]) -> None:
        """Add multiple strategies at the same time.

        Convenience method for adding multiple strategy instances at once.
        Each strategy will be initialized when the bot starts.

        Args:
            strategies (Iterable[Strategy]): An iterable of Strategy instances
                to run on the bot. Can be a list, tuple, or any iterable.

        Example:
            Adding multiple strategies::

                strategies = [
                    ScalperStrategy(symbol=Symbol(name="EURUSD")),
                    SwingStrategy(symbol=Symbol(name="GBPUSD")),
                    TrendStrategy(symbol=Symbol(name="USDJPY")),
                ]
                bot.add_strategies(strategies=strategies)
        """
        [self.add_strategy(strategy=strategy) for strategy in strategies]

    def add_strategy_all(
        self, *, strategy: Type[Strategy], params: dict | None = None, symbols: list[Symbol] = None, **kwargs
    ) -> None:
        """Run a single strategy type on multiple symbols.

        Creates and adds multiple instances of the same strategy class,
        one for each provided symbol. All instances share the same
        parameters and keyword arguments.

        Args:
            strategy (Type[Strategy]): The Strategy class (not instance) to
                instantiate for each symbol.
            params (dict, optional): A dictionary of parameters to pass to
                each strategy instance. Defaults to None.
            symbols (list[Symbol]): A list of Symbol instances to run the
                strategy on. One strategy instance is created per symbol.
            **kwargs: Additional keyword arguments passed to each strategy
                constructor.

        Example:
            Running a strategy on multiple symbols::

                symbols = [
                    Symbol(name="EURUSD"),
                    Symbol(name="GBPUSD"),
                    Symbol(name="USDJPY"),
                ]
                bot.add_strategy_all(
                    strategy=ScalperStrategy,
                    params={"risk": 0.01, "take_profit": 50},
                    symbols=symbols,
                    timeframe=TimeFrame.M5
                )
        """
        [self.add_strategy(strategy=strategy(symbol=symbol, params=params, **kwargs)) for symbol in symbols]

    async def init_strategy(self, *, strategy: Strategy) -> bool:
        """Initialize a single strategy asynchronously.

        Calls the strategy's initialize method and, if successful, adds
        the strategy to the executor's strategy runners list.

        Args:
            strategy (Strategy): The Strategy instance to initialize.

        Returns:
            bool: True if the strategy was successfully initialized and
                added to the executor, False otherwise.

        Note:
            This method is called internally by init_strategies() during
            bot initialization. Strategies that fail initialization are
            not added to the executor.
        """
        res = await strategy.initialize()
        if res:
            self.executor.add_strategy(strategy=strategy)
        return res

    async def init_strategies(self) -> None:
        """Initialize all strategies for the current trading session.

        Concurrently initializes all strategies in the strategies list.
        Each strategy is initialized in parallel using asyncio.gather.
        Only strategies that successfully initialize are added to the
        executor.

        Note:
            This method is called internally by initialize() during
            bot startup. Failed initializations are handled gracefully
            and do not prevent other strategies from initializing.
        """
        tasks = [self.init_strategy(strategy=strategy) for strategy in self.strategies]
        await asyncio.gather(*tasks, return_exceptions=True)

    def init_strategy_sync(self, *, strategy: Strategy) -> bool:
        """Initialize a single strategy synchronously.

        Synchronous version of init_strategy(). Calls the strategy's
        initialize_sync method and, if successful, adds the strategy
        to the executor's strategy runners list.

        Args:
            strategy (Strategy): The Strategy instance to initialize.

        Returns:
            bool: True if the strategy was successfully initialized and
                added to the executor, False otherwise.

        Note:
            This method is called internally by init_strategies_sync()
            during bot initialization. Strategies that fail initialization
            are not added to the executor.
        """
        res = strategy.initialize_sync()
        if res:
            self.executor.add_strategy(strategy=strategy)
        return res

    def init_strategies_sync(self) -> None:
        """Initialize all strategies for the current trading session synchronously.

        Synchronous version of init_strategies(). Initializes all strategies
        in the strategies list sequentially. Only strategies that successfully
        initialize are added to the executor.

        Note:
            This method is called internally by initialize_sync() during
            bot startup. Failed initializations are handled gracefully
            and do not prevent other strategies from initializing.
        """
        [self.init_strategy_sync(strategy=strategy) for strategy in self.strategies]
