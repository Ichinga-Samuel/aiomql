# forex_symbol

`aiomql.contrib.symbols.forex_symbol` — Forex-specific symbol with pip and volume calculations.

## Overview

Extends [`Symbol`](../../lib/symbol.md) with forex-specific logic for pip size
and volume calculations based on price movements and stop-loss levels.

## Classes

### `ForexSymbol`

> Symbol subclass tailored for forex instruments.

Inherits from [`Symbol`](../../lib/symbol.md).

| Attribute | Type | Description |
|-----------|------|-------------|
| `pip` | `float` | Pip size for the pair (`point * 10`) |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `compute_points(amount, volume)` | `float` | Computes points of price movement needed for a given amount and volume |
| `compute_volume_points(amount, points, round_down=False)` | `float` | Computes lot size from risk amount and point distance |
| `compute_volume_sl(amount, price, sl, round_down=False)` | `float` | Computes lot size from risk amount, entry price, and stop-loss price |
