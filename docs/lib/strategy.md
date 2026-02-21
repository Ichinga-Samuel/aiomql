# strategy

`aiomql.lib.strategy` — Strategy base class.

## Overview

The `Strategy` class is the abstract base for all trading strategies. Subclasses implement
`trade()` to define entry/exit logic. The strategy lifecycle is managed by the
[`Bot`](bot.md) / [`Executor`](executor.md).

Inherits from [`_Base`](../core/base.md).

## Classes

### `Strategy`

> Abstract base class for trading strategies.

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Strategy name (defaults to class name) |
| `symbol` | `Symbol` | The trading instrument |
| `sessions` | `Sessions \| None` | Optional session restrictions |
| `params` | `dict` | Strategy parameters |

#### Lifecycle

| Method | Description |
|--------|-------------|
| `__init__(symbol, params, sessions, …)` | Initialises the strategy with a symbol and parameters |
| `init()` | Async setup hook (called once before trading begins) |
| `run()` | Main loop — calls `trade()` repeatedly |
| `sleep(secs)` | Suspends the strategy for a duration |

#### Trading Logic

| Method | Description |
|--------|-------------|
| `trade()` | **Abstract** — implement entry/exit logic here |
