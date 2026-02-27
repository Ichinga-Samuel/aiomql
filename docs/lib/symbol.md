# symbol

`aiomql.lib.symbol` — Trading instrument interface.

## Overview

The `Symbol` class represents a financial instrument (forex pair, stock, etc.) and provides
methods for querying market data, selecting symbols, and retrieving rates and ticks.

Inherits from [`_Base`](../core/base.md) and `SymbolInfo`.

## Classes

### `Symbol`

> Interface for a MetaTrader 5 trading instrument.

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Symbol name (e.g. `"EURUSD"`) |
| `select` | `bool` | Whether the symbol is selected in Market Watch |
| `tick` | `Tick` | Current price tick for the instrument |
| `account` | `Account` | Trading account instance |
| `initialized` | `bool` | Whether the symbol has been successfully initialized |

All `SymbolInfo` fields are available as instance attributes after initialisation.

#### Initialisation

| Method | Returns | Description |
|--------|---------|-------------|
| `__init__(**kwargs)` | — | Requires `name` keyword argument |
| `initialize()` | `bool` | Async. Fetches symbol info, tick, and selects the symbol |
| `initialize_sync()` | `bool` | Synchronous version of `initialize()` |

#### Symbol Info

| Method | Returns | Description |
|--------|---------|-------------|
| `info()` | `SymbolInfo \| None` | Fetches and updates all symbol properties |
| `info_tick(name="")` | `Tick \| None` | Gets the current price tick |
| `symbol_select(enable=True)` | `bool` | Selects or removes the symbol from Market Watch |

#### Market Depth

| Method | Returns | Description |
|--------|---------|-------------|
| `book_add()` | `bool` | Subscribes to Market Depth events |
| `book_get()` | `tuple[BookInfo, ...]` | Returns Market Depth entries |
| `book_release()` | `bool` | Cancels Market Depth subscription |

#### Volume Helpers

| Method | Returns | Description |
|--------|---------|-------------|
| `check_volume(volume)` | `tuple[bool, float]` | Checks if volume is within min/max limits |
| `round_off_volume(volume, round_down=False)` | `float` | Rounds volume to nearest volume step |
| `compute_volume(*args, **kwargs)` | `float` | Returns `volume_min` (override in subclasses) |

#### Currency Conversion

| Method | Returns | Description |
|--------|---------|-------------|
| `amount_in_quote_currency(amount)` | `float` | Converts amount to the symbol's quote currency |
| `convert_currency(amount, from_currency, to_currency)` | `float \| None` | Converts between two currencies via tick data |

#### Market Data

| Method | Returns | Description |
|--------|---------|-------------|
| `copy_rates_from(timeframe, date_from, count)` | `Candles` | Historical bars from a date |
| `copy_rates_from_pos(timeframe, count, start_position)` | `Candles` | Historical bars from a position |
| `copy_rates_range(timeframe, date_from, date_to)` | `Candles` | Historical bars in a date range |
| `copy_ticks_from(date_from, count, flags)` | `Ticks` | Historical ticks from a date |
| `copy_ticks_range(date_from, date_to, flags)` | `Ticks` | Historical ticks in a date range |

#### Properties

| Property | Returns | Description |
|----------|---------|-------------|
| `pip` | `float` | Pip size (`point * 10`) |

#### Overridable Methods

These methods raise `NotImplementedError` in the base `Symbol` and are meant to be implemented by subclasses such as [`ForexSymbol`](../contrib/symbols/forex_symbol.md).

| Method | Returns | Description |
|--------|---------|-------------|
| `compute_volume_sl(amount, price, sl, round_down)` | `float` | Compute volume from stop-loss distance |
| `compute_volume_points(amount, points, round_down)` | `float` | Compute volume from point distance |

## Synchronous API

Available in `aiomql.lib.sync.symbol`. All async methods become synchronous with the same signatures.
