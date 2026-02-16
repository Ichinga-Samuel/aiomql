"""Position trackers for monitoring and managing open trading positions.

This module provides classes for tracking open positions and executing
tracking functions at regular intervals.

Classes:
    PositionTracker: Wraps a tracking function to be executed on an open position.
    OpenPositionsTracker: Manages and tracks all open positions in the trading system.
"""
import asyncio

from collections.abc import Callable
from typing import Any, TypeVar, ClassVar
from logging import getLogger
import logging

from ...core import Config, State, sleep
from ...lib import Positions

logger = getLogger(__name__)

OpenPosition = TypeVar('OpenPosition')


class PositionTracker:
    """Wraps a tracking function to be executed on an open position.
    
    A PositionTracker binds a callable tracking function to an OpenPosition
    instance, allowing it to be executed with specified parameters during
    position tracking cycles.
    
    Attributes:
        params: Dictionary of parameters to pass to the tracking function.
        function: The callable tracking function to execute.
        name: Name identifier for this tracker.
        rank: Execution priority (lower numbers execute first).
        open_position: The OpenPosition instance this tracker is bound to.
    """
    params: dict[str, Any]
    function: Callable
    name: str
    rank: int | None
    open_position: OpenPosition

    def __init__(self, open_position: OpenPosition, function: Callable, /, rank: int = None, 
                 name: str = None, function_params: dict[str, Any] = None) -> None:
        """Initialize a PositionTracker.
        
        Args:
            open_position: The OpenPosition instance to track.
            function: The async callable to execute during tracking. Should
                accept the OpenPosition as its first argument.
            rank: Execution priority. Lower numbers execute first. Defaults to None.
            name: Name identifier for this tracker. Defaults to the function name.
            function_params: Dictionary of keyword arguments to pass to the
                function on each call. Defaults to None.
        """
        self.function = function
        self.params = function_params or {}
        self.rank = rank
        self.open_position = open_position
        self.name = name or function.__name__
        self.set_tracker()

    async def __call__(self, **kwargs):
        """Execute the tracking function asynchronously.
        
        Calls the bound tracking function with the open position and
        any configured or provided keyword arguments.
        
        Args:
            **kwargs: Additional keyword arguments to pass to the function.
                These are merged with the configured params, with kwargs
                taking precedence.
        """
        try:
            kwargs = self.params | kwargs
            await self.function(self.open_position, **kwargs)
        except Exception as exe:
            logger.error("%s: Error occurred in %s for %s:%d", exe, self.function.__name__,
                         self.open_position.symbol.name, self.open_position.ticket)

    def set_tracker(self, name: str = None, rank: int = None):
        """Register this tracker with its open position.
        
        Adds this tracker to the open position's tracker collection,
        optionally updating the name and rank.
        
        Args:
            name: Override name for the tracker. Defaults to the current name.
            rank: Override rank for the tracker. Defaults to the current rank.
        """
        self.open_position.add_tracker(tracker=self, name=name or self.name, rank=rank or self.rank)


class OpenPositionsTracker:
    """Manages and tracks all open positions in the trading system.
    
    Runs a continuous loop that executes all trackers on all tracked
    positions at a specified interval. Supports automatic cleanup of
    closed positions and optional state persistence.
    
    Attributes:
        config: Shared configuration instance.
        positions: Positions handler for querying position data.
        state: State manager for persisting tracked positions.
        interval: Time between tracking cycles in seconds.
        state_key: Key used to store tracked positions in state.
        autocommit: Whether to automatically commit state changes.
        auto_remove_closed: Whether to automatically remove closed positions.
    """
    config: ClassVar[Config]
    positions: ClassVar[Positions]
    state: ClassVar[State]

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "config"):
            cls.config = Config()

        if not hasattr(cls, "positions"):
            cls.positions = Positions()

        if not hasattr(cls, "state"):
            cls.state = State()

        return super().__new__(cls)

    def __init__(self, interval: int = 10, state_key: str = "tracked_positions", 
                 autocommit: bool = False, auto_remove_closed: bool = False):
        """Initialize the OpenPositionsTracker.
        
        Args:
            interval: Time between tracking cycles in seconds. Defaults to 10.
            state_key: Key used to store tracked positions in the state
                dictionary. Defaults to "tracked_positions".
            autocommit: If True, automatically commit state changes after
                each tracking cycle. Defaults to False.
            auto_remove_closed: If True, automatically remove closed positions
                from tracking after each cycle. Defaults to False.
        """
        self.interval = interval
        self.state_key = state_key
        self.autocommit = autocommit
        self.auto_remove_closed = auto_remove_closed

    async def track(self):
        """Main tracking loop that monitors all open positions.
        
        Continuously executes all trackers on all tracked positions at
        the configured interval. Optionally removes closed positions and
        commits state changes.
        
        Note:
            This method runs until config.shutdown is True. The connection
            is automatically closed when the loop exits.
        """
        conn = self.config.state.conn
        while not self.config.shutdown:
            try:
                await sleep(self.interval)
                tracked_positions = self.state.get("tracked_positions", {})
                await asyncio.gather(*(pos.track() for pos in tracked_positions.values()), return_exceptions=True)
                if self.auto_remove_closed:
                    await self.remove_closed_positions(tracked_positions)
                if self.autocommit:
                    await self.state.acommit(conn=conn, close=False)
            except Exception as exe:
                logger.error("%s: Error occurred in %s.track", exe, self.__class__.__name__)
        conn.close()

    async def remove_closed_positions(self, tracked_positions: dict):
        """Remove closed positions from the tracked positions.
        
        Queries the broker for all current positions and removes any
        tracked positions that are no longer open.
        
        Args:
            tracked_positions: Dictionary mapping ticket numbers to
                OpenPosition instances.
        """
        all_pos = await self.positions.get_positions()
        all_pos = {pos.ticket for pos in all_pos}
        self.state[self.state_key] = {pos.ticket: pos for pos in tracked_positions.values() if pos.ticket in all_pos}
