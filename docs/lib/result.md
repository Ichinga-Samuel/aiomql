# result

`aiomql.lib.result` — Trade result recording (CSV / JSON / SQL).

## Overview

The `Result` class records trade outcomes and strategy parameters to files in CSV, JSON,
or SQL format. It integrates with the `Config` to determine the recording directory and
format.

Inherits from [`_Base`](../core/base.md).

## Classes

### `Result`

> Saves trade results to persistent storage.

| Attribute | Type | Description |
|-----------|------|-------------|
| `config` | `Config` | Global configuration |

#### Methods

| Method | Description |
|--------|-------------|
| `save(result, parameters, name)` | Dispatches to the configured format (CSV/JSON/SQL) |
| `save_csv(result, parameters, name)` | Appends a result row to a CSV file |
| `save_json(result, parameters, name)` | Appends a result object to a JSON file |
| `save_sql(result, parameters, name)` | Saves the result to the SQLite database |
| `get_data(result, parameters)` | Prepares a unified dict from result and parameters |

## Synchronous API

Available in `aiomql.lib.sync.result`.
