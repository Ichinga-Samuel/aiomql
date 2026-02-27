# order

`aiomql.lib.order` — Trade order creation, checking, and sending.

## Overview

The `Order` class creates and manages trade orders for the MetaTrader 5 terminal. It handles
margin calculations, profit projections, order validation, modification, and cancellation.

Inherits from [`_Base`](../core/base.md) and `TradeRequest`.

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

#### Initialisation

| Method | Description |
|--------|-------------|
| `__init__(**kwargs)` | Requires `symbol`. Defaults: `action=TradeAction.DEAL`, `type_time=OrderTime.DAY`, `type_filling=OrderFilling.FOK` |

#### `request` *(property)*

Returns the trade request as a dict, filtering to keys valid for `TradeRequest`.

#### Validation

| Method | Returns | Description |
|--------|---------|-------------|
| `check(**kwargs)` | `OrderCheckResult` | Validates the order; raises `OrderError` on failure |

#### Execution

| Method | Returns | Description |
|--------|---------|-------------|
| `send()` | `OrderSendResult` | Sends the order via `send_order()` |
| `send_order(request, connection_retries=0)` | `OrderSendResult` | Class method. Sends a trade request; retries up to 3 times on connection loss (retcode 10031). Raises `OrderError` on failure |

#### Calculations

| Method | Returns | Description |
|--------|---------|-------------|
| `calc_margin()` | `float \| None` | Required margin for the order |
| `calc_profit()` | `float \| None` | Projected profit at `tp` (take profit) price |
| `calc_loss()` | `float \| None` | Projected loss at `sl` (stop loss) price |
| `profit_to_price(profit, order_type, volume, symbol, price_open)` | `float` | Class method. Reverse-calculates the close price needed to achieve a target profit |

#### Modification

| Method | Returns | Description |
|--------|---------|-------------|
| `modify(**kwargs)` | — | Updates the order's attributes |
| `cancel_order(order, symbol="")` | `OrderSendResult` | Class method. Cancels a pending order by ticket; raises `OrderError` on failure |

#### Pending & Historical Orders

| Method | Returns | Description |
|--------|---------|-------------|
| `orders_total()` | `int` | Class method. Total number of active pending orders |
| `get_pending_order(ticket)` | `TradeOrder \| None` | Class method. Gets a single pending order by ticket |
| `get_pending_orders(ticket, symbol, group)` | `tuple[TradeOrder, ...]` | Class method. Gets pending orders filtered by ticket, symbol, or group |
| `get_history_order_by_ticket(ticket)` | `TradeOrder \| None` | Class method. Gets a historical order by ticket |

## Synchronous API

Available in `aiomql.lib.sync.order`. All async methods become synchronous with the same signatures.
