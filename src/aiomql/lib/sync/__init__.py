"""Synchronous API for aiomql library.

This package exports synchronous versions of all core classes
with a 'Sync' suffix for use in non-async contexts.
"""

from .history import History as HistorySync
from .order import Order as OrderSync
from .positions import Positions as PositionsSync
from ..ram import RAM as RAMSync
from .sessions import Session as SessionSync, Sessions as SessionsSync
from .strategy import Strategy as StrategySync
from .symbol import Symbol as SymbolSync
from .trader import Trader as TraderSync

__all__ = [
    "HistorySync",
    "OrderSync",
    "PositionsSync",
    "RAMSync",
    "SessionSync",
    "SessionsSync",
    "StrategySync",
    "SymbolSync",
    "TraderSync",
]
