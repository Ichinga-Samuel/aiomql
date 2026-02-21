# position_tracking_functions

`aiomql.contrib.trackers.position_tracking_functions` — Pre-built tracking functions.

## Overview

Provides ready-to-use tracking functions for the [`PositionTracker`](position_trackers.md).
These functions automate common position-management actions like trailing stops and
take-profit extensions.

## Functions

### `trailing_stop(position, *, pips, …)`

> Implements a trailing stop loss.

Adjusts the stop loss to trail behind the current price by a specified pip distance.
Only modifies the stop if the new level is more favourable than the existing one.

### `trailing_take_profit(position, *, pips, …)`

> Extends the take profit as price moves favourably.

Adjusts the take-profit level when the position's profit exceeds a threshold,
locking in additional gains.
