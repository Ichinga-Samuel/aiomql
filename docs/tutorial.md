# aiomql — The Complete Guide to Building Algorithmic Trading Bots with Python & MetaTrader 5

> **An in-depth tutorial covering every feature of the aiomql framework — from your first async connection to production-grade, multi-instrument trading bots.**

---

## Table of Contents

1. [What is aiomql?](#what-is-aiomql)
2. [Installation & Requirements](#installation--requirements)
3. [Configuration](#configuration)
4. [Connecting to MetaTrader 5](#connecting-to-metatrader-5)
5. [Working with Symbols](#working-with-symbols)
6. [Market Data: Candles & Ticks](#market-data-candles--ticks)
7. [Technical Analysis](#technical-analysis)
8. [Placing Orders](#placing-orders)
9. [The Trader Abstraction](#the-trader-abstraction)
10. [Risk & Money Management (RAM)](#risk--money-management-ram)
11. [Building a Strategy](#building-a-strategy)
12. [Trading Sessions](#trading-sessions)
13. [The Bot Orchestrator](#the-bot-orchestrator)
14. [Position Tracking](#position-tracking)
15. [Trade Result Recording](#trade-result-recording)
16. [Trade History](#trade-history)
17. [Contributed Extensions](#contributed-extensions)
18. [Multi-Process Execution](#multi-process-execution)
19. [Synchronous API](#synchronous-api)
20. [Full Example: EMA Crossover Bot](#full-example-ema-crossover-bot)
21. [Architecture Overview](#architecture-overview)
22. [Summary](#summary)

---

## What is aiomql?

**aiomql** is a Python framework for building algorithmic trading bots on top of
[MetaTrader 5](https://www.metatrader5.com/). Rather than writing raw MT5 API calls
and managing connection boilerplate, aiomql gives you:

- **An async-first MetaTrader 5 interface** — every MT5 function wrapped with
  `asyncio.to_thread` and automatic reconnection on transient errors.
- **High-level abstractions** — Strategy, Bot, Trader, Order, Symbol, Sessions, RAM,
  and more — so you can focus on trading logic.
- **A full synchronous API** — every async class has a sync counterpart for scripts,
  notebooks, and quick prototyping.
- **Built-in technical analysis** — pandas-ta integration with optional TA-Lib support.
- **Trade recording** — persist results to CSV, JSON, or SQLite automatically.
- **Position tracking** — monitor open positions with trailing stops, extending
  take-profits, hedging, and stacking.
- **Multi-process execution** — run independent bots in parallel with a single call.

aiomql is designed for traders who want to build, test, and deploy algorithmic
strategies in Python without reinventing the wheel.

---

## Installation & Requirements

### Prerequisites

| Requirement | Details |
|---|---|
| **Python** | ≥ 3.13 |
| **OS** | Windows (MetaTrader 5 terminal requirement) |
| **Account** | A MetaTrader 5 trading account (demo or live) |

### Install via pip

```bash
pip install aiomql
```

### Optional Extras

```bash
# TA-Lib technical indicators
pip install aiomql[talib]

# Optional accelerators (Cython, Numba, tqdm)
pip install aiomql[optional]

# Everything
pip install aiomql[all]
```

---

## Configuration

aiomql uses a **singleton `Config` class** that can load settings from a JSON file
or be configured programmatically. This single configuration object is shared across
all components.

### Option 1: JSON Configuration File

Create an `aiomql.json` file in your project root:

```json
{
  "login": 12345678,
  "password": "your_password",
  "server": "YourBroker-Demo",
  "trade_record_mode": "csv"
}
```

The `Config` class automatically searches for `aiomql.json` in your project directory
tree, starting from the current working directory and walking up to the root.

### Option 2: Programmatic Configuration

```python
from aiomql import Config

config = Config(
    login=12345678,
    password="your_password",
    server="YourBroker-Demo",
    trade_record_mode="csv"
)
```

### Key Configuration Options

| Setting | Type | Description |
|---|---|---|
| `login` | `int` | MetaTrader account number |
| `password` | `str` | Account password |
| `server` | `str` | Broker server name |
| `path` | `str` | Path to the MT5 terminal executable |
| `trade_record_mode` | `str` | Trade logging format: `"csv"`, `"json"`, or `"sql"` |
| `root` | `str` | Project root directory |

Because `Config` is a **singleton**, any component in your application that creates
a `Config()` instance receives the same shared configuration.

### State & Store

The `Config` class also provides access to two persistent storage mechanisms:

- **`config.state`** — A `State` object for persistent key-value storage (backed by SQLite).
- **`config.store`** — A `Store` object for in-memory shared state accessible across components.

These are useful for sharing data between strategies, trackers, and other components at runtime.

---

## Connecting to MetaTrader 5

The `MetaTrader` class wraps every MT5 API function with async execution and
automatic retry logic. It supports both async context manager usage and direct calls.

### Basic Connection

```python
import asyncio
from aiomql import MetaTrader


async def main():
    async with MetaTrader() as mt5:
        # Get account information
        account = await mt5.account_info()
        print(f"Balance: {account.balance}")
        print(f"Equity: {account.equity}")

        # Get terminal info
        terminal = await mt5.terminal_info()
        print(f"Terminal: {terminal.name}")

        # Get available symbols
        symbols = await mt5.symbols_get()
        print(f"{len(symbols)} symbols available")


asyncio.run(main())
```

### How It Works

Under the hood, `MetaTrader` runs every MT5 call through `asyncio.to_thread`, which
means your event loop stays responsive even during blocking I/O. If a connection
error occurs, the `_handler` method automatically retries initialization and login up
to 3 times.

```python
# The MetaTrader class is also a singleton — every instance shares the same state
mt5_a = MetaTrader()
mt5_b = MetaTrader()
assert mt5_a is mt5_b  # True
```

### Key Methods

| Method | Description |
|---|---|
| `initialize()` | Connect to the MT5 terminal |
| `login()` | Log in with credentials |
| `shutdown()` | Close the connection |
| `account_info()` | Get account details |
| `terminal_info()` | Get terminal details |
| `symbols_get()` | List available symbols |
| `symbol_info()` | Get info for a specific symbol |
| `copy_rates_from()` | Fetch OHLC bar data |
| `copy_rates_from_pos()` | Fetch recent bars by count |
| `copy_ticks_from()` | Fetch tick data |
| `order_check()` | Check if an order can be executed |
| `order_send()` | Send a trade order |
| `positions_get()` | Get open positions |
| `history_deals_get()` | Get historical deals |
| `history_orders_get()` | Get historical orders |

---

## Working with Symbols

The `Symbol` class is a high-level wrapper around a financial instrument. It pulls
properties from MT5 (spread, lot sizes, contract size, etc.) and provides methods
to fetch market data.

### Initializing a Symbol

```python
from aiomql import Symbol


async def main():
    symbol = Symbol(name="EURUSD")
    await symbol.initialize()

    # Now you can access all symbol properties
    print(f"Spread: {symbol.spread}")
    print(f"Point: {symbol.point}")
    print(f"Min volume: {symbol.volume_min}")
    print(f"Max volume: {symbol.volume_max}")
    print(f"Volume step: {symbol.volume_step}")
    print(f"Contract size: {symbol.trade_contract_size}")
```

### Getting Price Data

```python
# Get the current tick
tick = await symbol.info_tick()
print(f"Bid: {tick.bid}, Ask: {tick.ask}")

# Get the last 500 H1 candles
from aiomql import TimeFrame

candles = await symbol.copy_rates_from_pos(
    timeframe=TimeFrame.H1, count=500
)
```

### Volume Utilities

The `Symbol` class includes helpers for working with lot sizes:

```python
# Check if a volume is valid
is_valid, adjusted = symbol.check_volume(volume=0.15)

# Round volume to the nearest step
rounded = symbol.round_off_volume(volume=0.153, round_down=True)
```

### Currency Conversion

```python
# Convert between currencies using live rates
amount_in_usd = await symbol.convert_currency(
    amount=100.0,
    from_currency="EUR",
    to_currency="USD"
)
```

### ForexSymbol — Specialized for Forex

The `ForexSymbol` class extends `Symbol` with forex-specific calculations:

```python
from aiomql import ForexSymbol

eurusd = ForexSymbol(name="EURUSD")
await eurusd.initialize()

# Pip value (point * 10)
print(f"Pip: {eurusd.pip}")  # 0.0001 for most pairs

# Compute volume based on risk amount and stop loss distance
volume = await eurusd.compute_volume_sl(
    amount=100.0,     # risk $100
    price=1.1000,     # entry price
    sl=1.0950,        # stop loss
    round_down=True
)

# Compute volume based on risk amount and points
volume = await eurusd.compute_volume_points(
    amount=100.0,
    points=500,
    round_down=True
)

# Compute points needed for a given profit at a given volume
points = eurusd.compute_points(amount=50.0, volume=0.1)
```

---

## Market Data: Candles & Ticks

### Candles

The `Candles` class wraps pandas `DataFrame` with trading-specific functionality.
When you fetch rates from a `Symbol`, you receive a `Candles` object:

```python
from aiomql import TimeFrame

candles = await symbol.copy_rates_from_pos(
    timeframe=TimeFrame.H1, count=500
)

# It's a DataFrame under the hood
print(candles.data.head())

# Access individual candles by index
last_candle = candles[-1]
print(f"Open: {last_candle.open}, Close: {last_candle.close}")

# Candle properties
print(f"Body: {last_candle.body}")
print(f"Range: {last_candle.range}")
print(f"Is Bullish: {last_candle.is_bullish()}")
print(f"Is Bearish: {last_candle.is_bearish()}")
print(f"Is Doji: {last_candle.is_doji()}")

# DataFrame columns are accessible directly
print(candles.open)   # Series of open prices
print(candles.close)  # Series of close prices
print(candles.high)   # Series of high prices
print(candles.low)    # Series of low prices
```

### Renaming Columns

```python
# Rename DataFrame columns (useful after adding indicators)
candles.rename(
    EMA_34="fast_ema",
    EMA_55="slow_ema",
    inplace=True
)
```

### Ticks

The `Tick` class represents a single price tick, and `Ticks` is a collection:

```python
# Get recent ticks
ticks = await symbol.copy_ticks_from(
    date_from=datetime.now() - timedelta(minutes=5),
    count=1000
)

# Access tick data
for tick in ticks:
    print(f"Time: {tick.time}, Bid: {tick.bid}, Ask: {tick.ask}")

# The Ticks object also supports technical analysis
ticks.ta.sma(length=20, append=True)
```

---

## Technical Analysis

aiomql integrates **pandas-ta** (classic) out of the box, available through the
`.ta` accessor on `Candles` and `Ticks` objects. Every pandas-ta indicator is available
directly.

### Using pandas-ta Indicators

```python
candles = await symbol.copy_rates_from_pos(
    timeframe=TimeFrame.H1, count=500
)

# Moving averages
candles.ta.sma(length=20, append=True)
candles.ta.ema(length=50, append=True)

# RSI
candles.ta.rsi(length=14, append=True)

# MACD
candles.ta.macd(fast=12, slow=26, signal=9, append=True)

# Bollinger Bands
candles.ta.bbands(length=20, std=2, append=True)

# ATR
candles.ta.atr(length=14, append=True)

# Stochastic
candles.ta.stoch(k=14, d=3, append=True)

# Access the results as DataFrame columns
print(candles.data.columns.tolist())
```

### The ta_lib Helper

The `Candles` object also includes a `ta_lib` helper with convenience functions:

```python
# Check if series A is above series B
above = candles.ta_lib.above(candles.fast_ema, candles.slow_ema)

# Check if series A is below series B
below = candles.ta_lib.below(candles.fast_ema, candles.slow_ema)
```

### Optional: TA-Lib Integration

If you install `aiomql[talib]`, you get access to the full C-based TA-Lib library
for high-performance indicator computation.

---

## Placing Orders

The `Order` class handles all trade order operations. It's a subclass of
`TradeRequest` and provides methods for checking, sending, and managing orders.

### Creating and Sending a Market Order

```python
from aiomql import Order, OrderType, TradeAction

# Create a buy order
order = Order(
    symbol="EURUSD",
    type=OrderType.BUY,
    volume=0.1,
    price=1.1000,
    sl=1.0950,
    tp=1.1100
)

# Check if the order can be executed
check_result = await order.check()
print(f"Margin required: {check_result.margin}")

# Send the order
result = await order.send()
print(f"Order ticket: {result.order}")
print(f"Return code: {result.retcode}")
```

### Modifying an Order

```python
order.modify(
    sl=1.0960,
    tp=1.1120
)
```

### Margin and Profit Calculations

```python
# Calculate required margin
margin = await order.calc_margin()
print(f"Margin needed: {margin}")

# Calculate expected profit (at take-profit level)
profit = await order.calc_profit()
print(f"Expected profit: {profit}")

# Calculate expected loss (at stop-loss level)
loss = await order.calc_loss()
print(f"Expected loss: {loss}")
```

### Pending Order Management

```python
# Get total pending orders
total = await Order.orders_total()

# Get all pending orders
pending = await Order.get_pending_orders()

# Get a specific pending order by ticket
order = await Order.get_pending_order(ticket=123456)

# Cancel a pending order
await Order.cancel_order(order=123456, symbol="EURUSD")
```

### Connection Retry Logic

The `send_order` method automatically retries on connection errors (retcode 10031)
with exponential backoff, up to 3 retries.

---

## The Trader Abstraction

While `Order` handles the low-level mechanics, the `Trader` class provides a
higher-level interface for placing trades with proper risk management and trade
recording.

### Why Use Trader?

`Trader` ties together the `Order`, `Symbol`, and `RAM` (risk manager) classes
into a cohesive workflow:

1. **Calculate position size** based on your risk parameters
2. **Set stop-loss and take-profit** levels
3. **Check the order** before sending
4. **Send the order** and handle errors
5. **Record the trade** to your chosen storage format

### Creating Orders with Stops

```python
from aiomql import Trader, ForexSymbol, RAM, OrderType

symbol = ForexSymbol(name="EURUSD")
await symbol.initialize()

ram = RAM(risk=2, risk_to_reward=3)  # 2% risk, 1:3 R:R
trader = Trader(symbol=symbol, ram=ram)

# Create order with stop-loss and take-profit using absolute prices
await trader.create_order_with_stops(
    order_type=OrderType.BUY,
    sl=1.0950,
    tp=1.1150
)

# Create order with just a stop-loss (TP calculated from R:R ratio)
await trader.create_order_with_sl(
    order_type=OrderType.BUY,
    sl=1.0950
)

# Create order using points distance
await trader.create_order_with_points(
    order_type=OrderType.BUY,
    points=500
)

# Create a simple order with no stops
await trader.create_order_no_stops(
    order_type=OrderType.BUY,
    volume=0.01
)
```

### Checking and Sending

```python
# Check if the order passes broker validation
can_trade = await trader.check_order()

if can_trade:
    result = await trader.send_order()
```

### Recording Trades

After sending, trades are automatically recorded via the `record_trade` method:

```python
await trader.record_trade(
    result=result,
    parameters={"strategy": "EMA Crossover"},
    name="EMAXOver",
    expected_profit=25.50
)
```

### Pre-Built Traders

aiomql ships with two ready-to-use `Trader` subclasses in the `contrib` package:

#### SimpleTrader

Places trades with a specified stop-loss. Volume is calculated based on the RAM
risk amount and the distance to the stop-loss.

```python
from aiomql import SimpleTrader, ForexSymbol, OrderType

symbol = ForexSymbol(name="EURUSD")
trader = SimpleTrader(symbol=symbol)

await trader.place_trade(
    order_type=OrderType.BUY,
    sl=1.0950,
    parameters={"name": "MyStrategy"}
)
```

#### ScalpTrader

Places trades using minimum volume and no stop-loss/take-profit levels.
Ideal for scalping strategies where positions are managed manually.

```python
from aiomql import ScalpTrader, ForexSymbol, OrderType

symbol = ForexSymbol(name="EURUSD")
trader = ScalpTrader(symbol=symbol)

await trader.place_trade(
    order_type=OrderType.BUY,
    parameters={"name": "ScalpBot"}
)
```

---

## Risk & Money Management (RAM)

The `RAM` (Risk Assessment & Money) class is at the heart of aiomql's risk
management. It calculates position sizes, enforces trade limits, and manages
your exposure.

### Configuration

```python
from aiomql import RAM

ram = RAM(
    risk=2,              # Risk 2% of free margin per trade
    risk_to_reward=3,    # 1:3 risk-to-reward ratio
    min_amount=5,        # Minimum $5 risk per trade
    max_amount=500,      # Maximum $500 risk per trade
    loss_limit=3,        # Max 3 losing positions at once
    open_limit=5,        # Max 5 total open positions
    fixed_amount=None    # Set to override percentage-based calculation
)
```

### Calculating Risk Amount

```python
# Get the amount to risk per trade (based on free margin)
amount = await ram.get_amount()
print(f"Amount to risk: ${amount:.2f}")

# If fixed_amount is set, it always returns that
ram.modify_ram(fixed_amount=100.0)
amount = await ram.get_amount()  # Always $100
```

### Enforcing Position Limits

```python
# Check if we can open a new position
can_open = await ram.check_open_positions()
if not can_open:
    print("Too many open positions!")

# Check if we've hit the loss limit
can_trade = await ram.check_losing_positions()
if not can_trade:
    print("Too many losing positions!")
```

### How the Amount is Calculated

The calculation flow is:

1. If `fixed_amount` is set → return `fixed_amount`
2. Otherwise → `margin_free × (risk / 100)`
3. If `min_amount` and `max_amount` are set → clamp the result

---

## Building a Strategy

The `Strategy` class is the cornerstone of aiomql. You subclass it, define your
parameters, and implement the `trade()` method. The framework handles everything
else — initialization, the execution loop, session management, and error handling.

### Anatomy of a Strategy

```python
from aiomql import Strategy, ForexSymbol, TimeFrame, Tracker, OrderType, Sessions, ScalpTrader


class MyStrategy(Strategy):
    # Type annotations for strategy-specific parameters
    ttf: TimeFrame
    fast_period: int
    slow_period: int
    tracker: Tracker

    # Default parameter values — these become instance attributes
    parameters = {
        "ttf": TimeFrame.H1,
        "fast_period": 20,
        "slow_period": 50,
    }

    def __init__(self, *, symbol: ForexSymbol, params: dict = None,
                 sessions: Sessions = None, name: str = "MyStrategy"):
        super().__init__(symbol=symbol, params=params, sessions=sessions, name=name)
        self.tracker = Tracker(snooze=self.ttf.seconds)
        self.trader = ScalpTrader(symbol=self.symbol)

    async def trade(self):
        """This method is called repeatedly by the execution loop."""
        # 1. Fetch market data
        candles = await self.symbol.copy_rates_from_pos(
            timeframe=self.ttf, count=200
        )

        # 2. Apply indicators
        candles.ta.sma(length=self.fast_period, append=True)
        candles.ta.sma(length=self.slow_period, append=True)
        candles.rename(
            **{f"SMA_{self.fast_period}": "fast",
               f"SMA_{self.slow_period}": "slow"},
            inplace=True
        )

        # 3. Check for signals
        if candles.ta_lib.above(candles.fast, candles.slow).iloc[-1]:
            self.tracker.update(order_type=OrderType.BUY, snooze=3600)
        elif candles.ta_lib.below(candles.fast, candles.slow).iloc[-1]:
            self.tracker.update(order_type=OrderType.SELL, snooze=3600)
        else:
            self.tracker.update(order_type=None, snooze=self.ttf.seconds)

        # 4. Execute or sleep
        if self.tracker.order_type is not None:
            await self.trader.place_trade(
                order_type=self.tracker.order_type,
                parameters=self.parameters
            )
            await self.delay(secs=self.tracker.snooze)
        else:
            await self.sleep(secs=self.tracker.snooze)
```

### Key Concepts

#### Parameters Dictionary

The `parameters` class attribute defines default values for your strategy. When you
instantiate the strategy, you can override any parameter via the `params` argument:

```python
strategy = MyStrategy(
    symbol=ForexSymbol(name="EURUSD"),
    params={"fast_period": 10, "slow_period": 30}
)
```

Parameters are also accessible as attributes thanks to `__getattr__`:

```python
print(strategy.fast_period)  # 10
```

#### The Tracker

The `Tracker` (from `aiomql.contrib.utils`) is a lightweight state holder for
strategies. It stores the current `order_type`, a `snooze` duration, and any extra
state you want to track:

```python
from aiomql import Tracker

tracker = Tracker(snooze=300)  # default snooze of 5 minutes

# Update tracker state
tracker.update(
    order_type=OrderType.BUY,
    snooze=3600,
    trend="bullish",
    last_price=1.1050
)

# Access state
print(tracker.order_type)  # OrderType.BUY
print(tracker.trend)       # "bullish"
```

#### Sleep vs Delay

- **`self.sleep(secs=...)`** — Computes the exact time until the next bar opens,
  ensuring your strategy wakes up right at the start of a new candle. This is
  critical for cooperative multitasking.
- **`self.delay(secs=...)`** — A simple `asyncio.sleep` for the given duration.

#### Initialization

Override `initialize()` to run one-time setup. By default, it initializes the
symbol:

```python
async def initialize(self):
    """Called once before the strategy starts trading."""
    result = await self.symbol.initialize()
    # Load historical data, train models, etc.
    return result
```

#### Stopping a Strategy

Raise `StopTrading` from within `trade()` to gracefully stop the strategy:

```python
from aiomql.core.exceptions import StopTrading

async def trade(self):
    if some_condition:
        raise StopTrading("Reached daily profit target")
```

---

## Trading Sessions

Sessions let you restrict when a strategy can trade. This is essential for forex
markets where different sessions (London, New York, Tokyo) have different
characteristics.

### Defining Sessions

```python
from datetime import time
from aiomql import Session, Sessions

# Define individual sessions (times are in UTC)
london = Session(
    name="London",
    start=time(8, 0),
    end=time(16, 0)
)

new_york = Session(
    name="New York",
    start=time(13, 0),
    end=time(21, 0)
)

tokyo = Session(
    name="Tokyo",
    start=time(0, 0),
    end=time(9, 0)
)
```

### Session Actions

Sessions can automatically execute actions at their start and end:

```python
# Close all positions when the London session ends
london = Session(
    name="London",
    start=time(8, 0),
    end=time(16, 0),
    on_end="close_all"
)

# Close only losing positions at session end
new_york = Session(
    name="New York",
    start=time(13, 0),
    end=time(21, 0),
    on_end="close_loss"
)

# Close only winning positions
tokyo = Session(
    name="Tokyo",
    start=time(0, 0),
    end=time(9, 0),
    on_end="close_win"
)

# Custom actions
async def my_start_action(session):
    print(f"{session.name} started!")

async def my_end_action(session):
    print(f"{session.name} ended!")

custom = Session(
    name="Custom",
    start=time(10, 0),
    end=time(18, 0),
    on_start="custom_start",
    on_end="custom_end",
    custom_start=my_start_action,
    custom_end=my_end_action
)
```

### Combining Sessions

Group sessions together with the `Sessions` class. When a strategy uses
`Sessions`, the framework automatically:

1. Checks if the current time falls within any session
2. Waits (sleeps) if outside all sessions
3. Handles transitions between sessions (closing the previous, opening the next)

```python
sessions = Sessions(sessions=[london, new_york])

strategy = MyStrategy(
    symbol=ForexSymbol(name="EURUSD"),
    sessions=sessions
)
```

### Session Utilities

```python
# Check if currently in session
print(london.in_session())

# Get session duration
duration = london.duration()
print(f"Duration: {duration.hours}h {duration.minutes}m")

# Seconds until session starts
secs = london.until()
print(f"Session starts in {secs} seconds")
```

---

## The Bot Orchestrator

The `Bot` class is the top-level orchestrator that brings everything together.
It manages the MT5 terminal connection, initializes strategies, and coordinates
their execution.

### Basic Usage

```python
from aiomql import Bot, ForexSymbol
from my_strategies import EMAXOver, RSIStrategy

def main():
    # Create symbols
    symbols = [ForexSymbol(name=s) for s in ["EURUSD", "GBPUSD", "USDJPY"]]

    # Create strategies
    strategies = [EMAXOver(symbol=sym) for sym in symbols]

    # Create bot and add strategies
    bot = Bot()
    bot.add_strategies(strategies)

    # Run (blocks until shutdown)
    bot.execute()


if __name__ == "__main__":
    main()
```

### Adding Coroutines

You can add background coroutines that run alongside your strategies:

```python
async def log_account_status():
    """Periodically log account balances."""
    from aiomql import Account
    account = Account()
    while True:
        await account.refresh()
        print(f"Balance: {account.balance}, Equity: {account.equity}")
        await asyncio.sleep(60)


bot = Bot()
bot.add_strategies(strategies)

# Runs in the same event loop
bot.add_coroutine(coroutine=log_account_status)

# Runs on a separate thread (for CPU-intensive or blocking tasks)
bot.add_coroutine(
    coroutine=some_blocking_task,
    on_separate_thread=True
)
```

### Adding Functions

For synchronous functions that should run in a thread pool:

```python
import time

def heartbeat(interval=30):
    while True:
        print("Bot is alive...")
        time.sleep(interval)


bot.add_function(function=heartbeat, interval=30)
```

### Async Entry Point

If you're already inside an async context, use `start()` instead of `execute()`:

```python
async def main():
    bot = Bot()
    bot.add_strategies(strategies)
    await bot.start()

asyncio.run(main())
```

### What Happens Inside

When you call `bot.execute()`:

1. **Terminal Start** — connects to the MT5 terminal and logs in
2. **Strategy Initialization** — each strategy's `initialize()` is called;
   strategies that fail are silently skipped
3. **Executor Start** — the `Executor` runs all strategies, coroutines, and
   functions concurrently using asyncio tasks and thread pools

---

## Position Tracking

aiomql provides a sophisticated position tracking system through the `contrib.trackers`
package. This allows you to monitor open positions and apply automated management rules.

### OpenPosition

The `OpenPosition` class wraps a trade position with tracking, hedging, and stacking
capabilities:

```python
from aiomql import OpenPosition, PositionTracker

# Create an OpenPosition from a trade result
pos = OpenPosition(
    ticket=123456,
    symbol="EURUSD",
    # ... other position details
)

# Modify stop-loss and take-profit
await pos.modify_stops(sl=1.0960, tp=1.1120)

# Close the position
success, result = await pos.close_position()

# Add custom trackers to the position
pos.add_tracker(tracker=my_tracker, name="trailing_stop")
```

### Position Tracking Functions

aiomql includes pre-built tracking functions:

- **`exit_at_profit`** — Close a position when profit reaches a target price
- **`extend_take_profit`** — Dynamically extend the take-profit as price moves favorably

### OpenPositionsTracker

The `OpenPositionsTracker` manages all open positions and runs their trackers
automatically:

```python
from aiomql import Bot, OpenPositionsTracker

bot = Bot()
bot.add_strategies(strategies)

# Track all open positions on a separate thread
bot.add_coroutine(
    coroutine=OpenPositionsTracker(autocommit=True).track,
    on_separate_thread=True
)

bot.execute()
```

This automatically:
- Discovers all open positions
- Runs any registered trackers on each position
- Handles position closure and cleanup
- Manages hedges, stacks, and pending orders

---

## Trade Result Recording

Every trade can be automatically recorded for analysis. The `Result` class supports
three storage formats:

### CSV

```python
# In your Config or aiomql.json
config = Config(trade_record_mode="csv")

# Trades are saved to: <root>/trade_records/<strategy_name>.csv
```

### JSON

```python
config = Config(trade_record_mode="json")

# Trades are saved to: <root>/trade_records/<strategy_name>.json
```

### SQLite

```python
config = Config(trade_record_mode="sql")

# Trades are saved to a SQLite database in your project root
```

### What Gets Recorded?

Each trade record includes:
- **Order result** — ticket, deal, volume, price, retcode
- **Strategy parameters** — all parameters from the strategy's `parameters` dict
- **Trade request** — the actual request sent to the broker
- **Extras** — timestamp, expected profit, strategy name

### Manual Recording

```python
from aiomql import Result
from aiomql.core.models import OrderSendResult

result = Result(
    result=order_send_result,
    parameters={"strategy": "EMA", "timeframe": "H1"},
    name="EMAXOver",
    expected_profit=25.0
)

await result.save(trade_record_mode="csv")
```

---

## Trade History

The `History` class lets you retrieve completed deals and orders from your account
history:

```python
from datetime import datetime, timedelta
from aiomql import History

# Get the last 7 days of history
history = History(
    date_from=datetime.now() - timedelta(days=7),
    date_to=datetime.now()
)

# Fetch deals and orders
await history.initialize()

# Access deals
print(f"Total deals: {history.total_deals}")
for deal in history.deals:
    print(f"  {deal.symbol}: {deal.profit}")

# Access orders
print(f"Total orders: {history.total_orders}")

# Filter by ticket
deals = history.filter_deals_by_ticket(ticket=123456)

# Filter by position ID
deals = history.filter_deals_by_position(position=789012)

# Filter by symbol group (e.g., only USD pairs)
history = History(
    date_from=datetime.now() - timedelta(days=30),
    date_to=datetime.now(),
    group="*USD*"
)
```

---

## Contributed Extensions

The `contrib` package contains community extensions that build on the core framework.

### Strategies

#### Chaos

A demo strategy that randomly buys or sells. Useful for testing your infrastructure:

```python
from aiomql import Chaos, ForexSymbol

strategy = Chaos(symbol=ForexSymbol(name="EURUSD"))
```

### Symbols

#### ForexSymbol

Specialized `Symbol` subclass with pip calculations and volume computation based on
stop-loss distance. [See the Symbols section above for details.](#forexsymbol--specialized-for-forex)

### Traders

#### SimpleTrader

Trades with a stop-loss, calculating volume from risk.
[See above.](#simpletrader)

#### ScalpTrader

Trades with minimum volume and no stops.
[See above.](#scalptrader)

### Trackers

#### Tracker (Strategy Tracker)

A lightweight state holder for tracking strategy signals and snooze timers.
[See the Strategy section.](#the-tracker)

#### PositionTracker

Wraps a tracking function to execute on an open position.

#### OpenPositionsTracker

Automatically discovers and manages all open positions.
[See the Position Tracking section.](#openpositionstracker)

---

## Multi-Process Execution

For running completely independent bots in parallel, use `Bot.process_pool()`:

```python
from aiomql import Bot, ForexSymbol
from strategies import ForexStrategy, CryptoStrategy


def run_forex():
    bot = Bot()
    symbols = [ForexSymbol(name=s) for s in ["EURUSD", "GBPUSD"]]
    strategies = [ForexStrategy(symbol=s) for s in symbols]
    bot.add_strategies(strategies)
    bot.execute()


def run_crypto():
    bot = Bot()
    symbols = [ForexSymbol(name=s) for s in ["BTCUSD", "ETHUSD"]]
    strategies = [CryptoStrategy(symbol=s) for s in symbols]
    bot.add_strategies(strategies)
    bot.execute()


# Run both bots in separate processes
Bot.process_pool(
    processes={
        run_forex: {},
        run_crypto: {}
    },
    num_workers=2
)
```

Each process gets its own event loop, MT5 connection, and strategy set. This is
useful when you want complete isolation between different trading systems.

---

## Synchronous API

Every async class in aiomql has a synchronous counterpart. This makes the library
usable in Jupyter notebooks, simple scripts, or anywhere you don't want to deal with
`asyncio`.

### Synchronous MetaTrader

```python
from aiomql.core.sync import MetaTrader as SyncMetaTrader

mt5 = SyncMetaTrader()
mt5.initialize_sync()
mt5.login_sync(login=12345678, password="your_password", server="YourBroker-Demo")

account = mt5._account_info()
print(f"Balance: {account.balance}")

mt5.shutdown()
```

### Synchronous Strategy Initialization

```python
# The Bot class handles sync initialization internally
bot = Bot()
bot.execute()  # Uses sync initialization under the hood
```

### Synchronous RAM

```python
ram = RAM(risk=2)
amount = ram.get_amount_sync()
can_trade = ram.check_open_positions_sync()
```

---

## Full Example: EMA Crossover Bot

Here's a complete, production-ready example that puts everything together:

### Project Structure

```
my_trading_bot/
├── aiomql.json
├── strategies/
│   ├── __init__.py
│   └── ema_crossover.py
└── bot.py
```

### aiomql.json

```json
{
  "login": 12345678,
  "password": "your_password",
  "server": "YourBroker-Demo",
  "trade_record_mode": "csv"
}
```

### strategies/ema_crossover.py

```python
from aiomql import (
    Strategy, ForexSymbol, TimeFrame, Tracker,
    OrderType, Sessions, ScalpTrader
)


class EMAXOver(Strategy):
    """EMA Crossover strategy.

    Buys when the fast EMA crosses above the slow EMA.
    Sells when the fast EMA crosses below the slow EMA.
    """

    ttf: TimeFrame
    tcc: int
    fast_ema: int
    slow_ema: int
    tracker: Tracker
    interval: TimeFrame
    timeout: int

    parameters = {
        "ttf": TimeFrame.H1,
        "tcc": 3000,
        "fast_ema": 34,
        "slow_ema": 55,
        "interval": TimeFrame.M15,
        "timeout": 3 * 60 * 60,  # 3 hours cooldown after a trade
    }

    def __init__(self, *, symbol: ForexSymbol, params: dict = None,
                 sessions: Sessions = None, name: str = "EMAXOver"):
        super().__init__(
            symbol=symbol, params=params,
            sessions=sessions, name=name
        )
        self.tracker = Tracker(snooze=self.interval.seconds)
        self.trader = ScalpTrader(symbol=self.symbol)

    async def find_entry(self):
        # Fetch candle data
        candles = await self.symbol.copy_rates_from_pos(
            timeframe=self.ttf, count=self.tcc
        )

        # Calculate EMAs
        candles.ta.ema(length=self.fast_ema, append=True)
        candles.ta.ema(length=self.slow_ema, append=True)
        candles.rename(
            **{f"EMA_{self.fast_ema}": "fast_ema",
               f"EMA_{self.slow_ema}": "slow_ema"},
            inplace=True,
        )

        # Check for crossover signals
        fast_above_slow = candles.ta_lib.above(
            candles.fast_ema, candles.slow_ema
        )
        fast_below_slow = candles.ta_lib.below(
            candles.fast_ema, candles.slow_ema
        )

        if fast_above_slow.iloc[-1]:
            self.tracker.update(
                order_type=OrderType.BUY,
                snooze=self.timeout
            )
        elif fast_below_slow.iloc[-1]:
            self.tracker.update(
                order_type=OrderType.SELL,
                snooze=self.timeout
            )
        else:
            self.tracker.update(
                order_type=None,
                snooze=self.interval.seconds
            )

    async def trade(self):
        await self.find_entry()

        if self.tracker.order_type is None:
            # No signal — sleep until next bar
            await self.sleep(secs=self.tracker.snooze)
        else:
            # Signal found — place trade and cooldown
            await self.trader.place_trade(
                order_type=self.tracker.order_type,
                parameters=self.parameters,
            )
            await self.delay(secs=self.tracker.snooze)
```

### bot.py

```python
import logging
from aiomql import Bot, ForexSymbol, OpenPositionsTracker
from strategies.ema_crossover import EMAXOver

logging.basicConfig(level=logging.INFO)


def main():
    # Define symbols to trade
    symbols = [
        ForexSymbol(name=s)
        for s in ["EURUSD", "GBPUSD", "USDJPY"]
    ]

    # Create a strategy instance for each symbol
    strategies = [EMAXOver(symbol=sym) for sym in symbols]

    # Create the bot
    bot = Bot()
    bot.add_strategies(strategies)

    # Track open positions on a separate thread
    bot.add_coroutine(
        coroutine=OpenPositionsTracker(autocommit=True).track,
        on_separate_thread=True
    )

    # Start trading
    bot.execute()


if __name__ == "__main__":
    main()
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                     Bot (Orchestrator)               │
│  ┌──────────────────────────────────────────────┐   │
│  │               Executor                        │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────────────┐│   │
│  │  │Strategy 1│ │Strategy 2│ │  Coroutines/    ││   │
│  │  │(EURUSD) │ │(GBPUSD) │ │  Functions       ││   │
│  │  └────┬────┘ └────┬────┘ └────────┬────────┘│   │
│  └───────┼───────────┼───────────────┼──────────┘   │
│          │           │               │               │
│  ┌───────▼───────────▼───────────────▼──────────┐   │
│  │                Shared Services                 │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐│   │
│  │  │ Config │ │MetaTrader│ │  RAM   │ │ Result ││   │
│  │  │(single)│ │(single) │ │        │ │        ││   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘│   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────┐
│  MetaTrader 5       │
│  Terminal           │
│  (asyncio.to_thread)│
└─────────────────────┘
```

### Design Principles

1. **Singletons** — `Config` and `MetaTrader` in some cases are singletons, ensuring consistent
   state across all components.
2. **Async-first** — Every MT5 call is wrapped with `asyncio.to_thread`, keeping
   the event loop responsive.
3. **Composition** — Components are designed to be composed. A `Strategy` uses a
   `Symbol`, `Trader`, `RAM`, and `Sessions`.
4. **Separation of concerns** — Market data (`Symbol`, `Candles`, `Ticks`), trade
   execution (`Order`, `Trader`), risk management (`RAM`), and orchestration (`Bot`,
   `Executor`) are all separate modules.

---

## Summary

| Feature | Module | Description |
|---|---|---|
| MT5 Connection | `MetaTrader` | Async MT5 interface with retry |
| Configuration | `Config` | Singleton JSON/programmatic config |
| Market Data | `Symbol`, `Candles`, `Ticks` | Symbols, OHLC bars, tick data |
| Technical Analysis | `ta_libs` | pandas-ta + optional TA-Lib |
| Orders | `Order` | Check, send, margin/profit calc |
| Trade Execution | `Trader`, `SimpleTrader`, `ScalpTrader` | High-level trade placement |
| Risk Management | `RAM` | Position sizing, trade limits |
| Strategy | `Strategy` | Base class for trading logic |
| Sessions | `Session`, `Sessions` | Time-window trading restrictions |
| Orchestration | `Bot`, `Executor` | Multi-strategy concurrent execution |
| Position Tracking | `OpenPositionsTracker`, `OpenPosition` | Trailing stops, hedging, stacking |
| Trade Recording | `Result` | CSV, JSON, SQLite persistence |
| History | `History` | Deal and order history queries |
| Forex Helpers | `ForexSymbol` | Pip calc, volume from SL |
| Positions | `Positions` | Open position management |
| Multi-Process | `Bot.process_pool()` | Run bots in parallel processes |
| Sync API | `core.sync`, `lib.sync` | Synchronous mirrors |

aiomql takes care of the infrastructure, the connection handling, the execution
loops, and the bookkeeping — so you can focus on what matters: **your trading
strategy**.

---

*For the full API reference, see the [documentation](docs/toc.md).*

*aiomql is MIT-licensed and maintained by [Ichinga Samuel](https://github.com/Ichinga-Samuel/aiomql).*
