# candle

`aiomql.lib.candle` — Candlestick / bar data and technical analysis.

## Overview

Provides `Candle` (a single OHLCV bar) and `Candles` (an ordered collection). The `Candles`
class wraps a `pandas.DataFrame` and integrates with `pandas_ta` for technical analysis.

## Classes

### `Candle`

> A single candlestick bar.

| Attribute | Type | Description |
|-----------|------|-------------|
| `time` | `int` | Bar open time (unix timestamp) |
| `open` | `float` | Open price |
| `high` | `float` | High price |
| `low` | `float` | Low price |
| `close` | `float` | Close price |
| `tick_volume` | `float` | Tick volume |
| `real_volume` | `float` | Real volume |
| `spread` | `float` | Spread |
| `Index` | `int` | Position index within a `Candles` collection |

#### Properties

| Property | Description |
|----------|-------------|
| `mid` | Midpoint `(high + low) / 2` |
| `is_bullish` | `True` if `close >= open` |
| `is_bearish` | `True` if `close < open` |
| `dict` | Attribute dictionary |

---

### `Candles`

> Ordered collection of candlestick bars backed by a DataFrame.

| Attribute | Type | Description |
|-----------|------|-------------|
| `data` | `DataFrame` | The underlying OHLCV data |
| `Index` | `Series` | Positional index column |
| `timeframe` | `TimeFrame` | The chart timeframe |

#### Data Access

| Method / Property | Description |
|-------------------|-------------|
| `__getitem__(index)` | Get a `Candle` by position or slice |
| `__len__()` | Number of bars |
| `__iter__()` | Iterate over `Candle` objects |
| `columns` | DataFrame column names |
| `ta` | Access to `pandas_ta` indicators |
| `rename(inplace=True, **kwargs)` | Rename columns |

#### Technical Analysis

| Method | Description |
|--------|-------------|
| `ta_lib(func, *args, **kwargs)` | Run any `pandas_ta` indicator |
| `ta.sma(length)`, `ta.ema(length)`, etc. | Standard TA indicators via `pandas_ta` |
