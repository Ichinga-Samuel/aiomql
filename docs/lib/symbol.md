# symbol

`aiomql.lib.symbol` — Trading instrument interface.

## Overview

The `Symbol` class represents a financial instrument (forex pair, stock, etc.) and provides
methods for querying market data, selecting symbols, and retrieving rates and ticks.

Inherits from [`_Base`](../core/base.md).

## Classes

### `Symbol`

> Interface for a MetaTrader 5 trading instrument.

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Symbol name (e.g. `"EURUSD"`) |
| `select` | `bool` | Whether the symbol is selected in Market Watch |

All `SymbolInfo` fields are available as instance attributes after initialisation.

#### Initialisation

| Method | Description |
|--------|-------------|
| `init()` | Fetches symbol info from the terminal and sets all attributes |

#### Market Data

| Method | Returns | Description |
|--------|---------|-------------|
| `info_tick()` | `Tick` | Current tick for the symbol |
| `copy_rates_from(timeframe, date_from, count)` | `Candles` | Historical bars from a date |
| `copy_rates_from_pos(timeframe, start_pos, count)` | `Candles` | Historical bars from a position |
| `copy_rates_range(timeframe, date_from, date_to)` | `Candles` | Historical bars in a range |
| `copy_ticks_from(date_from, count, flags)` | `Ticks` | Historical ticks from a date |
| `copy_ticks_range(date_from, date_to, flags)` | `Ticks` | Historical ticks in a range |

#### Helpers

| Property | Returns | Description |
|----------|---------|-------------|
| `pip` | `float` | The pip size for the symbol |
| `spread` | `float` | Current bid-ask spread |

## Synchronous API

Available in `aiomql.lib.sync.symbol`.
