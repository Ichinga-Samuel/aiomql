import asyncio
from typing import Type, Iterable, TypeVar, Callable, Coroutine
import logging

from .executor import Executor
from .account import Account
from .symbol import Symbol as _Symbol
from .strategy import Strategy as _Strategy

logger = logging.getLogger(__name__)

Strategy = TypeVar('Strategy', bound=_Strategy)
Symbol = TypeVar('Symbol', bound=_Symbol)


class Bot:
    """The bot class. Create a bot instance to run your strategies.

    Attributes:
        account (Account): Account Object.
        executor: The default thread executor.
        symbols (list[Symbols]): A set of symbols for the trading session
    """
    account: Account = Account()

    def __init__(self):
        self.symbols = set()
        self.executor = Executor(bot=self)

    async def initialize(self):
        """Prepares the bot by signing in to the trading account and initializing the symbols for the trading session.

        Raises:
            SystemExit if sign in was not successful
        """
        init = await self.account.sign_in()
        logger.info("Login Successful")
        if not init:
            logger.warning('Unable to sign in to MetaTrder 5 Terminal')
            raise SystemExit
        await self.init_symbols()
        self.executor.remove_workers()

    def add_function(self, func: Callable, **kwargs: dict):
        """Add a function to the executor.

        Args:
            func (Callable): A function to be executed
            **kwargs (dict): Keyword arguments for the function
        """
        self.executor.add_function(func, kwargs)

    def add_coroutine(self, coro: Coroutine, **kwargs):
        """Add a coroutine to the executor.

        Args:
            coro (Coroutine): A coroutine to be executed
            **kwargs (dict): keyword arguments for the coroutine

        Returns:

        """
        self.executor.add_coroutine(coro, kwargs)

    def execute(self):
        """Execute the bot.
        """
        asyncio.run(self.start())

    async def start(self):
        """Starts the bot by calling the initialize method and running the strategies in the executor.
        """
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

    def add_strategy_all(self, *, strategy: Type[Strategy], params: dict | None = None):
        """Use this to run a single strategy on all available instruments in the market using the default parameters
        i.e one set of parameters for all trading symbols

        Keyword Args:
            strategy (Strategy): Strategy class
            params (dict): A dictionary of parameters for the strategy
        """
        [self.add_strategy(strategy(symbol=symbol, params=params)) for symbol in self.symbols]

    async def init_symbols(self):
        """Initialize the symbols for the current trading session. This method is called internally by the bot."""
        syms = [self.init_symbol(strategy.symbol) for strategy in self.executor.workers]
        await asyncio.gather(*syms, return_exceptions=True)

    async def init_symbol(self, symbol: Symbol) -> Symbol:
        """Initialize a symbol before the beginning of a trading sessions.
        Removes it from the list of symbols if it was not successfully initialized or not available
        for the account.

        Args:
            symbol (Symbol): Symbol object to be initialized

        Returns:
            Symbol: if successfully initialized
        """
        if self.account.has_symbol(symbol):
            init = await symbol.init()
            if init:
                self.symbols.add(symbol)
                return symbol
            logger.warning(f'Unable to initialize symbol {symbol}')
        logger.warning(f'{symbol} not a available for this market')
