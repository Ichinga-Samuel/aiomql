# forex_symbol

`aiomql.contrib.symbols.forex_symbol` — Forex-specific symbol with pip calculations.

## Overview

Extends [`Symbol`](../../lib/symbol.md) with forex-specific logic for pip size,
pip value, and volume calculations based on currency pairs.

## Classes

### `ForexSymbol`

> Symbol subclass tailored for forex instruments.

Inherits from [`Symbol`](../../lib/symbol.md).

| Attribute | Type | Description |
|-----------|------|-------------|
| `pip` | `float` | Pip size for the pair |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `pip_value(volume)` | `float` | Value of one pip for a given lot size |
| `pips_to_price(pips)` | `float` | Converts a pip count to a price delta |
| `price_to_pips(price_delta)` | `float` | Converts a price delta to pips |
| `calc_volume(amount, pips)` | `float` | Calculates lot size from risk amount and pip distance |
