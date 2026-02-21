# history

`aiomql.lib.history` — Historical deals and orders retrieval.

## Overview

The `History` class retrieves completed trade deals and orders from the MetaTrader 5 terminal
for a specified date range. Results are cached for efficient filtering and querying.

Inherits from [`_Base`](../core/base.md).

## Classes

### `History`

> Retrieves and caches historical deals and orders.

| Attribute | Type | Description |
|-----------|------|-------------|
| `deals` | `tuple[TradeDeal, ...]` | Cached deals |
| `orders` | `tuple[TradeOrder, ...]` | Cached orders |
| `total_deals` | `int` | Total deal count in range |
| `total_orders` | `int` | Total order count in range |

#### Initialization

| Method | Description |
|--------|-------------|
| `init(date_from, date_to)` | Fetches deals and orders for the date range |
| `get_deals(date_from, date_to)` | Fetches deals only |
| `get_orders(date_from, date_to)` | Fetches orders only |

#### Filtering Deals

| Method | Description |
|--------|-------------|
| `filter_deals_by_symbol(symbol)` | Filter deals by symbol name |
| `filter_deals_by_ticket(ticket)` | Filter deals by ticket number |
| `filter_deals_by_position(position)` | Filter deals by position ID |
| `get_deals_by_position(position)` | Get all deals for a position |

#### Filtering Orders

| Method | Description |
|--------|-------------|
| `filter_orders_by_symbol(symbol)` | Filter orders by symbol name |
| `filter_orders_by_ticket(ticket)` | Filter orders by ticket number |
| `filter_orders_by_position(position)` | Filter orders by position ID |
| `get_orders_by_position(position)` | Get all orders for a position |

## Synchronous API

A synchronous variant is available in `aiomql.lib.sync.history`.
