# store

`aiomql.core.store` — Per-key persistent key-value store backed by SQLite.

## Overview

The `Store` class provides a persistent dict-like interface backed by SQLite. Unlike
[`State`](state.md) (which stores all data as a single pickled row), `Store` keeps each
key-value pair as a separate database row. This makes it more suitable for large or
independently-accessed data sets.

## Classes

### `Store`

> Persistent key-value store with per-row storage.

| Attribute | Type | Description |
|-----------|------|-------------|
| `db_name` | `str \| Path` | Path to the SQLite database |
| `table_name` | `str` | Table name (default: `"store"`) |
| `autocommit` | `bool` | If `True`, commits after every modification |

#### `__init__(db_name="", table_name="store", data=None, flush=False, autocommit=True)`

Initialises the store, optionally flushing existing data.

#### Dict-like Interface

| Method | Description |
|--------|-------------|
| `__getitem__(key)` | Get a value by key |
| `__setitem__(key, value)` | Set or replace a value |
| `__delitem__(key)` | Delete a key-value pair |
| `__contains__(key)` | Check if a key exists |
| `__len__()` | Number of items |
| `__iter__()` | Iterate over keys |
| `get(key, default=None)` | Get with default |
| `pop(key, default=SENTINEL)` | Remove and return |
| `update(data, **kwargs)` | Bulk update |
| `setdefault(key, default=None)` | Get or set default |
| `keys()` / `values()` / `items()` | Standard list accessors |
| `iterkeys()` / `itervalues()` / `iteritems()` | Generator-based accessors |
| `clear()` | Remove all entries |

#### Persistence

| Property | Description |
|----------|-------------|
| `data` | Returns all key-value pairs as a dict |
| `commit()` | Commits pending changes |
