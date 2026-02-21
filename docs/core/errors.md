# errors

`aiomql.core.errors` — MetaTrader 5 error wrapper.

## Overview

Provides the `Error` class for representing and inspecting errors returned by the MetaTrader 5
terminal. Wraps numeric error codes with human-readable descriptions.

## Classes

### `Error`

> Wraps an MT5 error code with a description and category helpers.

| Attribute | Type | Description |
|-----------|------|-------------|
| `code` | `int` | Numeric error code |
| `description` | `str` | Human-readable description |
| `descriptions` | `dict[int, str]` | Class-level mapping of known error codes → descriptions |
| `conn_errors` | `tuple[int, ...]` | Codes that indicate connection-level failures |

#### `__init__(code=1, description="")`

Creates an `Error`. If `description` is empty, the description is looked up from
`descriptions`. Defaults to `"unknown error"` for unrecognised codes.

#### `is_connection_error()`

Returns `True` if `code` is in `conn_errors`.

#### `__repr__()`

Returns `"code: description"`.
