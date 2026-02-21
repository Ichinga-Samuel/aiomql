# open_position

`aiomql.contrib.trackers.open_position` — Open position data container.

## Overview

Defines the `OpenPosition` dataclass that holds the essential details of an open
MetaTrader 5 position for use by the tracking system.

## Classes

### `OpenPosition`

> Lightweight container for an open position's key fields.

| Field | Type | Description |
|-------|------|-------------|
| `ticket` | `int` | Position ticket number |
| `symbol` | `str` | Trading instrument |
| `volume` | `float` | Position volume |
| `type` | `PositionType` | BUY or SELL |
| `price_open` | `float` | Entry price |
| `sl` | `float` | Stop loss level |
| `tp` | `float` | Take profit level |
| `profit` | `float` | Current profit |
| `swap` | `float` | Accumulated swap |
| `magic` | `int` | EA magic number |
| `comment` | `str` | Position comment |
