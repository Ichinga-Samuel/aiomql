# terminal

`aiomql.lib.terminal` — Terminal information retrieval.

## Overview

The `Terminal` class retrieves information about the MetaTrader 5 terminal, such as its
version, connection status, and data paths.

Inherits from [`_Base`](../core/base.md).

## Classes

### `Terminal`

> Retrieves MetaTrader 5 terminal details.

All `TerminalInfo` fields (e.g. `connected`, `trade_allowed`, `name`, `path`, `build`)
are available as instance attributes after initialisation.

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `info()` | `TerminalInfo \| None` | Fetches and caches terminal info |
| `version()` | `tuple[int, int, str] \| None` | Terminal version |

## Synchronous API

Available in `aiomql.lib.sync.terminal`.
