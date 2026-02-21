# positions

`aiomql.lib.positions` — Open position management.

## Overview

The `Positions` class provides methods for retrieving, counting, and closing open positions
in the MetaTrader 5 terminal.

Inherits from [`_Base`](../core/base.md).

## Classes

### `Positions`

> Manages open positions in MetaTrader 5.

#### Retrieval

| Method | Returns | Description |
|--------|---------|-------------|
| `positions_get(symbol, group, ticket)` | `tuple[TradePosition, …] \| None` | Get positions matching criteria |
| `positions_total()` | `int` | Total number of open positions |
| `get_by_ticket(ticket)` | `TradePosition \| None` | Get a position by ticket |
| `get_by_symbol(symbol)` | `tuple[TradePosition, …] \| None` | Get positions for a symbol |

#### Closing

| Method | Returns | Description |
|--------|---------|-------------|
| `close(*, ticket, symbol, volume, price, order_type)` | `OrderSendResult` | Close a position |
| `close_all()` | `None` | Close all open positions |

#### Counting

| Method | Returns | Description |
|--------|---------|-------------|
| `get_total_positions()` | `int` | Number of open positions |
