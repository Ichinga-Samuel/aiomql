# _core

`aiomql.core._core` — Low-level interface that dynamically binds MetaTrader 5 constants, functions, and types.

## Overview

This module provides the metaclass machinery that introspects the `MetaTrader5` Python package and copies its
attributes into the class hierarchy. It is **not** intended for direct use — the higher-level
[`MetaTrader`](meta_trader.md) class should be used instead.

## Module-Level Attributes

| Name | Type | Description |
|------|------|-------------|
| `constants` | `tuple[str, ...]` | Names of MT5 integer constants to bind (e.g. `TIMEFRAME_M1`) |
| `core_mt5_functions` | `tuple[str, ...]` | Names of MT5 API functions to bind (prefixed with `_` on `MetaCore`) |
| `types` | `tuple[str, ...]` | Names of MT5 named-tuple types to bind |

## Classes

### `MetaBase`

> Metaclass that dynamically binds MetaTrader 5 attributes to classes.

On class creation, `MetaBase.__new__` introspects the `MetaTrader5` module and copies constants,
API functions (prefixed with `_`), and named-tuple types into the new class's namespace.

### `MetaCore`

> Base class exposing all MetaTrader 5 constants, functions, and types.

Created by `MetaBase`, this class holds every MT5 constant, every API function, and every
named-tuple type as class attributes.

**Key attribute groups:**

| Group | Examples |
|-------|---------|
| Timeframes | `TIMEFRAME_M1`, `TIMEFRAME_H1`, `TIMEFRAME_D1`, … |
| Order types | `ORDER_TYPE_BUY`, `ORDER_TYPE_SELL`, `ORDER_FILLING_FOK`, … |
| Trade actions | `TRADE_ACTION_DEAL`, `TRADE_ACTION_PENDING`, … |
| Return codes | `TRADE_RETCODE_DONE`, `TRADE_RETCODE_ERROR`, … |
| API functions | `_initialize`, `_login`, `_order_send`, `_positions_get`, … |
| Named-tuple types | `TradePosition`, `TradeOrder`, `TradeDeal`, `SymbolInfo`, … |
| Config | `config` — the global `Config` instance |
