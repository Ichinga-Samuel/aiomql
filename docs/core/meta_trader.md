# meta_trader

`aiomql.core.meta_trader` — Async/sync singleton interface to the MetaTrader 5 terminal.

## Overview

The `MetaTrader` class wraps every MT5 API call with async execution via
`asyncio.to_thread` and automatic retry logic for transient connection errors.
It is a **singleton** — only one instance exists per process.

A synchronous counterpart lives in `aiomql.core.sync.meta_trader`.

## Classes

### `MetaTrader`

> Asynchronous interface to the MetaTrader 5 terminal.

| Attribute | Type | Description |
|-----------|------|-------------|
| `error` | `Error` | The last error from the terminal |
| `config` | `Config` | The global configuration instance |

#### Connection

| Method | Description |
|--------|-------------|
| `initialize(path, login, password, server, timeout, portable)` | Initialises the terminal connection |
| `initialize_sync(…)` | Synchronous variant of `initialize` |
| `login(*, login, password, server, timeout)` | Logs into a trading account |
| `login_sync(…)` | Synchronous variant of `login` |
| `shutdown()` | Closes the terminal connection |
| `__aenter__` / `__aexit__` | Async context manager for connect/disconnect |

#### Account & Terminal

| Method | Returns | Description |
|--------|---------|-------------|
| `account_info()` | `AccountInfo \| None` | Current account details |
| `terminal_info()` | `TerminalInfo \| None` | Terminal information |
| `version()` | `tuple[int,int,str] \| None` | Terminal version |
| `last_error()` | `tuple[int,str]` | Last error code and description |

#### Symbols

| Method | Returns |
|--------|---------|
| `symbols_total()` | `int` |
| `symbols_get(group)` | `tuple[SymbolInfo, …] \| None` |
| `symbol_info(symbol)` | `SymbolInfo \| None` |
| `symbol_info_tick(symbol)` | `Tick \| None` |
| `symbol_select(symbol, enable)` | `bool` |

#### Market Data

| Method | Returns |
|--------|---------|
| `copy_rates_from(symbol, timeframe, date_from, count)` | `ndarray \| None` |
| `copy_rates_from_pos(symbol, timeframe, start_pos, count)` | `ndarray \| None` |
| `copy_rates_range(symbol, timeframe, date_from, date_to)` | `ndarray \| None` |
| `copy_ticks_from(symbol, date_from, count, flags)` | `ndarray \| None` |
| `copy_ticks_range(symbol, date_from, date_to, flags)` | `ndarray \| None` |

#### Orders & Positions

| Method | Returns |
|--------|---------|
| `positions_total()` | `int` |
| `positions_get(group, symbol, ticket)` | `tuple[TradePosition, …] \| None` |
| `orders_total()` | `int` |
| `orders_get(group, symbol, ticket)` | `tuple[TradeOrder, …] \| None` |
| `history_orders_total(date_from, date_to)` | `int` |
| `history_orders_get(date_from, date_to, group, ticket, position)` | `tuple[TradeOrder, …] \| None` |
| `history_deals_total(date_from, date_to)` | `int` |
| `history_deals_get(date_from, date_to, group, ticket, position)` | `tuple[TradeDeal, …] \| None` |

#### Trade Execution

| Method | Returns | Description |
|--------|---------|-------------|
| `order_check(request)` | `OrderCheckResult \| None` | Validates a trade request |
| `order_send(request)` | `OrderSendResult \| None` | Sends a trade request |
| `order_calc_margin(action, symbol, volume, price)` | `float \| None` | Calculates required margin |
| `order_calc_profit(action, symbol, volume, price_open, price_close)` | `float \| None` | Calculates expected profit |

#### Market Book

| Method | Description |
|--------|-------------|
| `market_book_add(symbol)` | Subscribes to market depth |
| `market_book_get(symbol)` | Gets current market depth |
| `market_book_release(symbol)` | Unsubscribes from market depth |

#### Internal

| Method | Description |
|--------|-------------|
| `_handler(api, retries=3)` | Executes API calls with connection-error retry |
