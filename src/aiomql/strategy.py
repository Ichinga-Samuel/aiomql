"""The base class for creating strategies."""
import asyncio
from time import time
from typing import TypeVar
from abc import ABC, abstractmethod
from datetime import time as dtime

from .core.meta_trader import MetaTrader
from .symbol import Symbol as _Symbol
from .account import Account
from .core import Config
from .sessions import Sessions, Session

Symbol = TypeVar('Symbol', bound=_Symbol)


class Strategy(ABC):
    """The base class for creating strategies.

    Attributes:
        symbol (Symbol): The Financial Instrument as a Symbol Object
        parameters (Dict): A dictionary of parameters for the strategy.

    Class Attributes:
        name (str): A name for the strategy.
        account (Account): Account instance.
        mt5 (MetaTrader): MetaTrader instance.
        config (Config): Config instance.

    Notes:
        Define the name of a strategy as a class attribute. If not provided, the class name will be used as the name.
    """
    name: str = ''
    account = Account()
    mt5: MetaTrader()
    config = Config()

    def __init__(self, *, symbol: Symbol, params: dict = None, sessions: Sessions = None):
        """Initiate the parameters dict and add name and symbol fields.
        Use class name as strategy name if name is not provided

        Args:
            symbol (Symbol): The Financial instrument
            params (Dict): Trading strategy parameters
        """
        self.symbol = symbol
        self.parameters = params.copy() if isinstance(params, dict) else {}
        self.parameters['symbol'] = symbol.name
        self.parameters['name'] = self.name or self.__class__.__name__
        self.sessions = sessions or Sessions(Session(start=0, end=dtime(hour=23, minute=59, second=59,
                                                                        microsecond=999999)))

    def __repr__(self):
        return f"{self.name}({self.symbol!r})"

    @staticmethod
    async def sleep(secs: float):
        """Sleep for the needed amount of seconds in between requests to the terminal.
        computes the accurate amount of time needed to sleep ensuring that the next request is made at the start of
        a new bar and making cooperative multitasking possible.

        Args:
            secs (float): The time in seconds. Usually the timeframe you are trading on.
        """
        mod = time() % secs
        secs = secs - mod if mod != 0 else mod
        await asyncio.sleep(secs + 0.1)


    @abstractmethod
    async def trade(self):
        """Place trades using this method. This is the main method of the strategy.
        It will be called by the strategy runner.
        """
