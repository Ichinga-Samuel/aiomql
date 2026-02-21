# result_db

`aiomql.lib.result_db` — SQLite-backed trade result storage.

## Overview

The `ResultDB` dataclass stores trade results in a SQLite database via the [`DB`](../core/db.md)
ORM base class. Each instance represents a single trade record with fields for order details,
strategy parameters, and profit/loss.

## Classes

### `ResultDB`

> Dataclass for persisting trade results to SQLite.

Inherits from `DB`. Decorated with `@dataclass`.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Primary key (auto-incremented) |
| `symbol` | `str` | Trading instrument |
| `order_type` | `str` | Order type string |
| `strategy` | `str` | Strategy name |
| `volume` | `float` | Trade volume |
| `points` | `float` | Profit in points |
| `profit` | `float` | Profit in account currency |
| `actual_profit` | `float` | Actual profit after close |
| `*` | … | Additional strategy-specific fields |

#### Methods

| Method | Description |
|--------|-------------|
| `save(commit, update, data, conn)` | Inserts or updates the record |
| `get(**kwargs)` | Retrieves a single matching record |
| `filter(**kwargs)` | Retrieves all matching records |
