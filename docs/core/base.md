# base

`aiomql.core.base` — Foundational base classes for data structure handling.

## Overview

Provides the `Base` and `_Base` classes that all data-model and trading classes inherit from.
`Base` offers attribute management, dictionary conversion, and filtering.
`_Base` extends it with automatic access to the MetaTrader terminal and configuration.

## Classes

### `BaseMeta`

> Metaclass that lazily initialises `config` and `mt5` on first access.

#### `_setup()`

Attaches `Config()` and `MetaTrader()` (or sync variant) to the class if not already present.

---

### `Base`

> Common base class for all data structures in aiomql.

| Attribute | Type | Description |
|-----------|------|-------------|
| `exclude` | `set[str]` | Attributes excluded from dict conversion (default: `mt5`, `config`, …) |
| `include` | `set[str]` | Attributes always included (overrides `exclude`) |

#### `__init__(**kwargs)`

Sets keyword arguments as instance attributes via `set_attributes`.

#### `set_attributes(**kwargs)`

Sets only attributes that are annotated on the class body. Logs a debug message for unknown or
non-convertible attributes.

#### `annotations` *(property)*

Merged `__annotations__` from all ancestor classes.

#### `class_vars` *(property)*

Annotated class-level attributes from the full MRO.

#### `dict` *(property)*

All instance and class attributes as a dictionary, excluding those in `exclude`.

#### `get_dict(exclude=None, include=None)`

Returns a filtered dictionary. If both `include` and `exclude` are provided, `include` takes precedence.

#### `__repr__()`

Shows up to 3 key attributes; appends `...` with the last attribute if there are more.

---

### `_Base`

> Extended base class with `MetaTrader` and `Config` integration.

Inherits from `Base` with `BaseMeta` as its metaclass.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `mt5` | `MetaTrader \| MetaTraderSync` | — | The MetaTrader interface (auto-initialised) |
| `config` | `Config` | — | The global configuration instance |
| `mode` | `Literal["async", "sync"]` | `"async"` | Determines which MetaTrader variant is used |

#### `__getstate__()`

Removes the `mt5` attribute before pickling to avoid serialization issues.
