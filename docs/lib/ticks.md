# ticks

`aiomql.lib.ticks` — Tick-level price data and technical analysis.

## Overview

Provides `Tick` (a single tick) and `Ticks` (an ordered collection). Like `Candles`, the
`Ticks` class wraps a `pandas.DataFrame` and integrates with `pandas_ta`.

## Classes

### `Tick`

> A single tick (price update).

| Attribute | Type | Description |
|-----------|------|-------------|
| `time` | `int` | Tick time (unix timestamp) |
| `bid` | `float` | Bid price |
| `ask` | `float` | Ask price |
| `last` | `float` | Last price |
| `volume` | `float` | Volume |
| `flags` | `int` | Tick flags |
| `volume_real` | `float` | Real volume |
| `time_msc` | `int` | Tick time in milliseconds |
| `Index` | `int` | Position index within a `Ticks` collection |

#### Properties

| Property | Description |
|----------|-------------|
| `dict` | Attribute dictionary |

---

### `Ticks`

> Ordered collection of ticks backed by a DataFrame.

| Attribute | Type | Description |
|-----------|------|-------------|
| `data` | `DataFrame` | The underlying tick data |
| `Index` | `Series` | Positional index column |

#### Data Access

| Method / Property | Description |
|-------------------|-------------|
| `__getitem__(index)` | Get a `Tick` by position or slice |
| `__len__()` | Number of ticks |
| `__iter__()` | Iterate over `Tick` objects |
| `columns` | DataFrame column names |
| `ta` | Access to `pandas_ta` indicators |
| `rename(inplace=True, **kwargs)` | Rename columns |

#### Technical Analysis

| Method | Description |
|--------|-------------|
| `ta_lib(func, *args, **kwargs)` | Run any `pandas_ta` indicator |
