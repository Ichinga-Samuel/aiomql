"""Position tracking and management for open trades.

This package provides classes and functions for tracking open trading positions,
including support for hedging, stacking, trailing stops, and custom tracking
strategies.

Modules:
    open_position: OpenPosition class for managing individual positions.
    position_trackers: PositionTracker and OpenPositionsTracker classes.
    position_tracking_functions: Pre-built tracking functions (exit_at_price,
        extend_take_profit, exit_at_checkpoint).

Classes:
    OpenPosition: Manages an open trading position with full tracking capabilities.
    PendingOrder: Represents a pending order associated with an open position.
    PositionTracker: Wraps a tracking function for execution on a position.
    OpenPositionsTracker: Manages and tracks all open positions.

Functions:
    exit_at_price: Exit a trade when profit reaches a target or stop.
    extend_take_profit: Dynamically extend take profit as price moves favorably.
    exit_at_checkpoint: Trail-based exit strategy using checkpoints.
"""
from .position_trackers import PositionTracker, OpenPositionsTracker
from .open_position import OpenPosition, PendingOrder
from .position_tracking_functions import exit_at_profit, extend_take_profit