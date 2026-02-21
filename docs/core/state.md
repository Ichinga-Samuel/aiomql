# state

`aiomql.core.state` — Singleton persistent key-value store backed by SQLite.

## Overview

The `State` class implements `MutableMapping`, providing dict-like access to data that is
automatically persisted to a SQLite database. The entire state is stored as a single pickled
row — ideal for small, frequently-accessed configuration data. It uses the singleton pattern
so all parts of the application share the same state.

## Classes

### `State`

> Singleton persistent key-value store.

| Attribute | Type | Description |
|-----------|------|-------------|
| `db_name` | `str \| Path` | Path to the SQLite database |
| `autocommit` | `bool` | If `True`, commits after every modification |

#### `__init__(db_name="", data=None, flush=False, autocommit=True)`

Initialises the state. If `flush` is `True`, all existing data is cleared.

#### Dict-like Interface

| Method | Description |
|--------|-------------|
| `__getitem__(key)` | Get a value by key |
| `__setitem__(key, value)` | Set a value |
| `__delitem__(key)` | Delete a key-value pair |
| `__contains__(key)` | Check if a key exists |
| `__len__()` | Number of items |
| `__iter__()` | Iterate over keys |
| `get(key, default=None)` | Get with default |
| `pop(key, default=SENTINEL)` | Remove and return |
| `update(data, **kwargs)` | Bulk update |
| `setdefault(key, default=None)` | Get or set default |
| `keys()` / `values()` / `items()` | Standard views |

#### Persistence

| Method | Description |
|--------|-------------|
| `commit()` | Writes current state to the database |
| `load()` | Loads state from the database |
| `flush()` | Clears all data (in-memory and on disk) |
