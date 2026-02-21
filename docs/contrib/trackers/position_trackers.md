# position_trackers

`aiomql.contrib.trackers.position_trackers` — Position and open-positions tracker classes.

## Overview

Provides `PositionTracker` (tracks a single position) and `OpenPositionsTracker`
(tracks all open positions). Used for executing automated tracking functions
such as trailing stops and take-profit extensions.

## Classes

### `PositionTracker`

> Tracks a single open position and runs tracking functions.

| Attribute | Type | Description |
|-----------|------|-------------|
| `position` | `OpenPosition` | The tracked position |
| `tracker` | `Callable` | The tracking function to execute |

#### Methods

| Method | Description |
|--------|-------------|
| `track()` | Executes the tracking function for the position |
| `update()` | Refreshes position data from the terminal |

---

### `OpenPositionsTracker`

> Monitors all open positions and runs trackers on each.

| Attribute | Type | Description |
|-----------|------|-------------|
| `trackers` | `dict[int, PositionTracker]` | Active trackers keyed by ticket |
| `tracking_functions` | `dict[str, Callable]` | Registered tracking functions |

#### Methods

| Method | Description |
|--------|-------------|
| `add_tracking_function(name, func)` | Registers a named tracking function |
| `track_positions()` | Updates all trackers and runs their tracking functions |
| `run()` | Main loop — continuously tracks positions |
