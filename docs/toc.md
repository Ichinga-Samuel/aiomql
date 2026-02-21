# aiomql Documentation

API reference for the **aiomql** asynchronous MetaTrader 5 trading library.

---

## Core

Low-level infrastructure: configuration, database, MT5 interface, data models, and shared state.

| Module | Description |
|--------|-------------|
| [_core](core/_core.md) | Metaclass that dynamically binds MT5 constants and functions |
| [base](core/base.md) | Base classes for attribute management and MT5 integration |
| [config](core/config.md) | Singleton configuration manager (`Config`) |
| [constants](core/constants.md) | MT5 enumerations (`TimeFrame`, `OrderType`, `TradeAction`, …) |
| [db](core/db.md) | SQLite ORM base class (`DB`) for dataclass-backed tables |
| [errors](core/errors.md) | MT5 error wrapper (`Error`) |
| [exceptions](core/exceptions.md) | Custom exception hierarchy |
| [meta_trader](core/meta_trader.md) | Async/sync singleton interface to the MT5 terminal |
| [models](core/models.md) | Data models (`AccountInfo`, `SymbolInfo`, `TradeRequest`, …) |
| [state](core/state.md) | Singleton persistent key-value store (`State`) |
| [store](core/store.md) | Per-key persistent store (`Store`) |
| [task_queue](core/task_queue.md) | Async priority task queue (`TaskQueue`, `QueueItem`) |

---

## Lib

High-level trading components: account, orders, positions, strategies, and the bot orchestrator.

| Module | Description |
|--------|-------------|
| [account](lib/account.md) | Trading account connection manager |
| [bot](lib/bot.md) | Bot orchestrator for running strategies |
| [candle](lib/candle.md) | Candlestick/bar data and technical analysis |
| [executor](lib/executor.md) | Strategy and task executor |
| [history](lib/history.md) | Historical deals and orders retrieval |
| [order](lib/order.md) | Trade order creation, checking, and sending |
| [positions](lib/positions.md) | Open position management |
| [ram](lib/ram.md) | Risk Assessment and Money management |
| [result](lib/result.md) | Trade result recording (CSV / JSON / SQL) |
| [result_db](lib/result_db.md) | SQLite-backed trade result storage |
| [sessions](lib/sessions.md) | Trading session time windows |
| [strategy](lib/strategy.md) | Strategy base class |
| [symbol](lib/symbol.md) | Trading instrument interface |
| [terminal](lib/terminal.md) | Terminal information retrieval |
| [ticks](lib/ticks.md) | Tick-level price data and analysis |
| [trader](lib/trader.md) | Trader base class for order management |
| [trade_records](lib/trade_records.md) | Trade record file management |

---

## Contrib

Community-contributed extensions: strategies, specialised symbols, position trackers, and traders.

| Module | Description |
|--------|-------------|
| [chaos](contrib/strategies/chaos.md) | Random buy/sell demo strategy |
| [forex_symbol](contrib/symbols/forex_symbol.md) | Forex-specific symbol with pip calculations |
| [open_position](contrib/trackers/open_position.md) | Open position data container |
| [position_trackers](contrib/trackers/position_trackers.md) | Position and open-positions tracker classes |
| [position_tracking_functions](contrib/trackers/position_tracking_functions.md) | Pre-built tracking functions (trailing stop, etc.) |
| [scalp_trader](contrib/traders/scalp_trader.md) | Scalp trader (no stop levels) |
| [simple_trader](contrib/traders/simple_trader.md) | Simple trader (with stop loss) |
| [strategy_tracker](contrib/utils/strategy_tracker.md) | Strategy state tracking dataclass |

---

## Utils

General-purpose utilities: math helpers, price calculations, and parallel processing.

| Module | Description |
|--------|-------------|
| [utils](utils/utils.md) | Decorators, rounding, and async caching |
| [price_utils](utils/price_utils.md) | Percentage-based price calculations |
| [process_pool](utils/process_pool.md) | Multi-process parallel execution |
