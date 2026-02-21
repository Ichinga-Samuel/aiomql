# strategy_tracker

`aiomql.contrib.utils.strategy_tracker` — Strategy state tracking dataclass.

## Overview

The `StrategyTracker` dataclass keeps track of a strategy's runtime state, including
trend information, entry prices, and flags.

## Classes

### `StrategyTracker`

> Tracks strategy data and state.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `trend` | `str` | `""` | Current detected trend |
| `new_trend` | `str` | `""` | Newly detected trend (before confirmation) |
| `order_type` | `OrderType \| None` | `None` | Current order type |
| `snooze` | `bool` | `False` | Whether the strategy is in a cool-down period |
| `entry_price` | `float` | `0.0` | Entry price of the last trade |
| `exit_price` | `float` | `0.0` | Exit price of the last trade |
| `sl` | `float` | `0.0` | Current stop loss |
| `tp` | `float` | `0.0` | Current take profit |
| `profit` | `float` | `0.0` | Current profit/loss |
| `*` | … | … | — Additional custom fields —  |
