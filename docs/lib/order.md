# order

`aiomql.lib.order` — Trade order creation, checking, and sending.

## Overview

The `Order` class creates and manages trade orders for the MetaTrader 5 terminal. It handles
margin calculations, profit projections, order validation, modification, and cancellation.

Inherits from [`_Base`](../core/base.md).

## Classes

### `Order`

> Creates, validates, and sends trade orders.

| Attribute | Type | Description |
|-----------|------|-------------|
| `action` | `TradeAction` | Trade action type |
| `type` | `OrderType` | Order type (BUY, SELL, etc.) |
| `symbol` | `str` | Trading instrument |
| `volume` | `float` | Trade volume in lots |
| `price` | `float` | Order price |
| `sl` | `float` | Stop loss level |
| `tp` | `float` | Take profit level |
| `deviation` | `int` | Maximum price deviation |
| `magic` | `int` | Expert Advisor magic number |
| `comment` | `str` | Order comment |
| `type_filling` | `OrderFilling` | Filling policy |
| `type_time` | `OrderTime` | Time-in-force policy |

#### `request` *(property)*

Returns the trade request as a dict, filtering out `None` values.

#### Validation

| Method | Returns | Description |
|--------|---------|-------------|
| `check()` | `OrderCheckResult` | Validates the order, raises `OrderError` on failure |

#### Execution

| Method | Returns | Description |
|--------|---------|-------------|
| `send()` | `OrderSendResult` | Sends the order; retries on requote/timeout |

#### Calculations

| Method | Returns | Description |
|--------|---------|-------------|
| `calc_margin()` | `float \| None` | Required margin for the order |
| `calc_profit(close_price)` | `float \| None` | Projected profit at a given close price |

#### Modification

| Method | Description |
|--------|-------------|
| `modify(**kwargs)` | Modifies a pending order's parameters |
| `cancel()` | Cancels a pending order |
