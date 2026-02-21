# ram

`aiomql.lib.ram` — Risk Assessment and Money management.

## Overview

The `RAM` class calculates position sizes based on risk parameters and account balance.
It checks open positions against configured limits and determines the volume for new trades.

Inherits from [`_Base`](../core/base.md).

## Classes

### `RAM`

> Calculates trade volumes using risk-based sizing.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `risk_to_reward` | `float` | `2` | Risk-to-reward ratio |
| `risk` | `float` | `0.01` | Risk per trade as a fraction of balance |
| `min_amount` | `float` | `0` | Minimum trade amount in account currency |
| `max_amount` | `float` | `0` | Maximum trade amount (0 = unlimited) |
| `max_open_positions` | `int` | `0` | Maximum concurrent positions (0 = unlimited) |
| `fixed_amount` | `float` | `0` | Fixed trade amount (overrides risk calculation) |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `check_open_positions()` | `bool` | `True` if under the open-position limit |
| `get_amount()` | `float` | Calculates the trade amount based on risk parameters |
| `calc_volume(symbol, amount, pips, …)` | `float` | Calculates lot size from amount and stop distance |

## Synchronous API

Available in `aiomql.lib.sync.ram`.
