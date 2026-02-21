# trader

`aiomql.lib.trader` — Trader base class for order management.

## Overview

The `Trader` class is the base for creating and managing trade orders. It brings together
`Symbol`, `RAM`, `Order`, and `Result` to provide a complete workflow for placing trades
with risk management and result recording.

Inherits from [`_Base`](../core/base.md).

## Classes

### `Trader`

> Base class for placing risk-managed trades.

| Attribute | Type | Description |
|-----------|------|-------------|
| `symbol` | `Symbol` | The trading instrument |
| `ram` | `RAM` | Risk Assessment and Money manager |
| `order` | `Order` | The current trade order |
| `result` | `Result` | Trade result recorder |
| `parameters` | `dict` | Strategy parameters to record |

#### Lifecycle

| Method | Description |
|--------|-------------|
| `__init__(symbol, ram, params, …)` | Initialises with a symbol and risk parameters |
| `create_order(order_type, …)` | Creates an `Order` with calculated volume and stops |
| `set_stop_levels(order_type, sl, tp)` | Sets stop loss and take profit prices |

#### Trade Placement

| Method | Description |
|--------|-------------|
| `place_trade(*, order_type, sl, tp, …)` | **Abstract** — subclasses implement to place trades |

## Synchronous API

Available in `aiomql.lib.sync.trader`.
