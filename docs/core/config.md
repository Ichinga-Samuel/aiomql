# config

`aiomql.core.config` — Singleton configuration manager for the aiomql package.

## Overview

The `Config` class manages all runtime settings — login credentials, paths, database names,
trade-recording preferences, and shutdown signals. It implements the singleton pattern and can
load values from a JSON file (default `aiomql.json`) or be configured programmatically.

## Classes

### `Config`

> Singleton configuration class.

#### Key Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `login` | `int` | `None` | MetaTrader account number |
| `password` | `str` | `""` | Account password |
| `server` | `str` | `""` | Account server name |
| `path` | `str \| Path` | `""` | Path to the MT5 terminal executable |
| `timeout` | `int` | `60000` | Connection timeout (ms) |
| `filename` | `str` | `"aiomql.json"` | Config file name to search for |
| `root` | `Path` | CWD | Project root directory |
| `trade_record_mode` | `Literal["csv","json","sql"]` | `"sql"` | Trade recording format |
| `record_trades` | `bool` | `True` | Enable/disable trade recording |
| `records_dir_name` | `str` | `"trade_records"` | Trade records directory name |
| `db_dir_name` | `str` | `"db"` | Database directory name |
| `db_name` | `str \| Path` | `""` | SQLite database file name |
| `shutdown` | `bool` | `False` | Graceful shutdown signal |
| `force_shutdown` | `bool` | `False` | Forced shutdown signal |
| `stop_trading` | `bool` | `False` | Stop opening new trades |
| `db_commit_interval` | `float` | `30` | Database commit interval (seconds) |
| `auto_commit` | `bool` | `False` | Auto-commit database changes |
| `flush_state` | `bool` | `False` | Flush state on init |
| `state` | `State` | — | Persistent key-value store |
| `store` | `Store` | — | Key-value database store |
| `task_queue` | `TaskQueue` | — | Background task queue |
| `bot` | `Bot` | `None` | Associated bot instance |

#### `__init__(**kwargs)`

Loads the config file and sets attributes. If already initialised and no `root` or
`config_file` is provided, only the extra `kwargs` are applied.

#### `load_config(*, config_file=None, filename=None, root=None, **kwargs)`

Sets the project root, locates/loads the JSON config file, initialises the database,
and applies all settings. Returns `self` for chaining.

#### `set_root(root=None)`

Resolves and creates the project root directory. Falls back to CWD.

#### `find_config_file()`

Searches up from CWD through parent directories for the config filename.

**Returns:** `Path | None`

#### `set_attributes(**kwargs)`

Sets attributes, but prevents `root` and `config_file` from being changed here
(use `load_config` instead).

#### `state` *(property)*

Lazily initialised `State` instance.

#### `store` *(property)*

Lazily initialised `Store` instance.

#### `records_dir` *(cached property)*

Path to the trade records directory. Created on first access.

#### `plots_dir` *(cached property)*

Path to the plots directory. Created on first access.

#### `account_info` *(property)*

Returns `{"login": …, "password": …, "server": …}`.
