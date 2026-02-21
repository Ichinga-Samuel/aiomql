"""Synchronous Strategy module for creating trading strategies.

This module provides the synchronous Strategy base class for implementing
custom trading strategies without async/await. It handles session management,
sleep functions, and the main trading loop.

Example:
    Creating a custom sync strategy::

        class MyStrategy(Strategy):
            def trade(self):
                # Synchronous trading logic
                candles = self.symbol.copy_rates_from_pos(timeframe=TimeFrame.H1, count=100)
                # Analyze and trade
                self.sleep(secs=3600)
"""

import time
from datetime import time as dtime
from logging import getLogger

from .sessions import Sessions, Session
from .symbol import Symbol
from ...core import Config
from ...core.exceptions import StopTrading
from ...core.meta_trader import MetaTrader
from ..strategy import Strategy as BaseStrategy


logger = getLogger(__name__)


class Strategy(BaseStrategy):
    """The base class for creating strategies.

    Attributes:
        name (str): The name of the strategy.
        symbol (Symbol): The Financial Instrument as a Symbol Object
        parameters (Dict): A dictionary of parameters for the strategy.
        sessions (Sessions): The sessions to use for the strategy.
        running (bool): A flag to indicate if the strategy is running.
        current_session (Session): The current session.
        mt5 MetaTrader: The MetaTrader object.
        config (Config): The config object.

    Notes:
        Define the name of a strategy as a class attribute. If not provided, the class name will be used as the name.
    """
    name: str
    symbol: Symbol
    sessions: Sessions
    mt5: MetaTrader
    config: Config
    running: bool
    parameters = {}
    current_session = Session

    def __init__(self, *, symbol: Symbol, params: dict = None, sessions: Sessions = None, name=""):
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
        self.mt5 = MetaTrader()

    def __repr__(self):
        return f"{self.name}({self.symbol!r})"

    def __getattr__(self, item):
        if item in self.parameters:
            return self.parameters[item]
        raise AttributeError(f"{item} not an attribute of {self.name}")

    def __setattr__(self, key, value):
        if key in self.parameters:
            self.parameters[key] = value
        super().__setattr__(key, value)

    def __enter__(self):
        self.sessions.check()
        self.running = True
        self.current_session = self.sessions.current_session

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.current_session.close() if self.current_session else ...
            self.running = False
        except Exception as err:
            logger.error(f"Error: {err}")

    def initialize(self):
        return self.symbol.initialize_sync()

    @staticmethod
    def live_sleep(*, secs: float):
        """Sleep for the needed amount of seconds in between requests to the terminal.
        computes the accurate amount of time needed to sleep ensuring that the next request is made at the start of
        a new bar and making cooperative multitasking possible.

        Args:
            secs (float): The time in seconds. Usually the timeframe you are trading on.
        """
        mod = time.time() % secs
        secs = secs - mod if mod != 0 else mod
        time.sleep(secs + 0.1)

    def sleep(self, *, secs: float):
        """Sleep for the needed amount of seconds in between requests to the terminal.
        computes the accurate amount of time needed to sleep ensuring that the next request is made at the start of
        a new bar and making cooperative multitasking possible.

        Args:
            secs (float): The time in seconds. Usually the timeframe you are trading on.
        """
        self.live_sleep(secs=secs)

    def delay(self, *, secs: float):
        """Sleep for the input amount of seconds"""
        time.sleep(secs)

    def run_strategy(self):
        """Run the strategy."""
        self.live_strategy()

    def live_strategy(self):
        """Run the strategy"""
        with self as _:
            logger.info("Running %s strategy on %s", self.name, self.symbol.name)
            while self.running:
                try:
                    self.sessions.check()
                    self.trade()

                except StopTrading:
                    self.running = False
                    break

                except Exception as err:
                    logger.error("Error: %s in live_strategy", err)
                    self.running = False
                    break

    def trade(self):
        """Place trades using this method. This is the main method of the strategy.
        It will be called by the strategy runner.
        """
        raise NotImplementedError("Implement this method in your subclass")

    def test(self):
        self.trade()
