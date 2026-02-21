# account

`aiomql.lib.account` — Trading account connection manager.

## Overview

The `Account` class is a singleton that manages the connection to a MetaTrader 5 trading
account. It supports both async and sync context managers for connecting and disconnecting,
and provides access to account properties such as balance, equity, and margin.

Inherits from [`_Base`](../core/base.md).

## Classes

### `Account`

> Singleton for managing the MT5 account connection.

| Attribute | Type | Description |
|-----------|------|-------------|
| `connected` | `bool` | Whether the account is currently connected |

All `AccountInfo` fields (e.g. `login`, `balance`, `equity`, `margin`, `leverage`, `currency`)
are available as instance attributes after a successful connection.

#### `__aenter__()` / `__aexit__(…)`

Async context manager — initializes the terminal, logs in, and populates account info.

#### `__enter__()` / `__exit__(…)`

Sync context manager — same as above using synchronous calls.

#### `refresh()`

Re-fetches account info from the terminal and updates instance attributes.

**Returns:** `bool` — `True` if the account info was successfully refreshed.

## Synchronous API

The sync context manager (`with Account() as acc:`) uses `initialize_sync` and `login_sync`
internally. See [`sync/account.py`] for the full synchronous wrapper.
