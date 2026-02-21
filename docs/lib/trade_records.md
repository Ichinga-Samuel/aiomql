# trade_records

`aiomql.lib.trade_records` — Trade record file management.

## Overview

The `TradeRecords` class manages trade record files in CSV, JSON, and SQL formats. It
provides methods for updating stored records with actual profit/loss data from completed
trades.

Inherits from [`_Base`](../core/base.md).

## Classes

### `TradeRecords`

> Updates and manages trade record files.

| Attribute | Type | Description |
|-----------|------|-------------|
| `config` | `Config` | Global configuration |

#### Methods

| Method | Description |
|--------|-------------|
| `update_rows(records_dir)` | Updates all record files in a directory |
| `update_row(file, row)` | Updates a single record row with actual P/L |
| `update_csv(file)` | Updates records in a CSV file |
| `update_json(file)` | Updates records in a JSON file |
| `update_sql()` | Updates records in the SQLite database |
| `get_actual_profit(order, symbol)` | Calculates actual P/L for a trade |

#### Static Methods

| Method | Description |
|--------|-------------|
| `str_to_bool(val)` | Converts `"true"` / `"false"` strings to `bool` |
