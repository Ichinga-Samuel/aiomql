# aiomql

![aiomql](docs/images/cover.png)

**Asynchronous MetaTrader 5 Library & Algorithmic Trading Framework**

![PyPI Version](https://img.shields.io/pypi/v/aiomql)
![Python](https://img.shields.io/pypi/pyversions/aiomql)
![License](https://img.shields.io/github/license/ichinga-samuel/aiomql?style=plastic)
![GitHub Issues](https://img.shields.io/github/issues/ichinga-samuel/aiomql?style=plastic)

---

## Overview

**aiomql** is a Python framework for building algorithmic trading bots on top of MetaTrader 5.
It wraps every MT5 API call in an async-friendly interface and provides high-level abstractions
for strategies, risk management, trade execution, session management, and position tracking —
so you can focus on your trading logic instead of boilerplate.

---

## Key Features

- **Async-first MT5 interface** — every MT5 function wrapped with `asyncio.to_thread` and automatic reconnection
- **Full synchronous API** — every async class has a sync counterpart for scripts and notebooks
- **Bot orchestrator** — run multiple strategies on multiple instruments concurrently via thread-pool executors
- **Strategy base class** — define `trade()`, set parameters, and let the framework handle the execution loop
- **Session management** — restrict trading to specific time windows (London, New York, Tokyo, etc.)
- **Risk & money management** — built-in `RAM` (Risk Assessment & Money) manager
- **Trade recording** — persist results to CSV, JSON, or SQLite
- **Position tracking** — monitor open positions with trailing stops, extending take-profits, and custom tracking functions
- **Technical analysis** — built-in pandas-ta integration plus optional TA-Lib support
- **Multi-process execution** — run independent bots in parallel with `Bot.process_pool()`
- **JSON configuration** — centralise credentials and settings in `aiomql.json`
- **Contributed extensions** — pre-built traders (`SimpleTrader`, `ScalpTrader`), strategies (`Chaos`), and specialised symbols (`ForexSymbol`)

---

## Requirements

- **Python ≥ 3.13**
- **Windows** (MetaTrader 5 terminal requirement)
- A MetaTrader 5 trading account

---

## Installation

```bash
pip install aiomql
```

**Optional extras:**

```bash
# TA-Lib technical indicators
pip install aiomql[talib]

# Optional (Cython, Numba, tqdm)
pip install aiomql[optional]

# Both
pip install aiomql[all]
```

---

## Quick Start

### Configuration

Create an `aiomql.json` file in your project root:

```json
{
  "login": 12345678,
  "password": "your_password",
  "server": "YourBroker-Demo"
}
```

All settings can also be set programmatically via the singleton `Config` class:

```python
from aiomql import Config

config = Config(login=12345678, password="your_password", server="YourBroker-Demo")
```

### Using the MetaTrader Interface

```python
import asyncio
from aiomql import MetaTrader


async def main():
    async with MetaTrader() as mt5:
        # Account information
        account = await mt5.account_info()
        print(account)

        # Available symbols
        symbols = await mt5.symbols_get()
        print(f"{len(symbols)} symbols available")


asyncio.run(main())
```

---

## Building a Trading Bot

### 1. Define a Strategy

Subclass `Strategy` and implement the `trade()` method. Parameters declared in the
`parameters` dict become instance attributes and can be overridden at construction time.

```python
# strategies/ema_crossover.py
from aiomql import Strategy, ForexSymbol, TimeFrame, Tracker, OrderType, Sessions, Trader, ScalpTrader


class EMAXOver(Strategy):
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
        "timeout": 3 * 60 * 60,
    }

    def __init__(self, *, symbol: ForexSymbol, params: dict | None = None,
                 trader: Trader = None, sessions: Sessions = None,
                 name: str = "EMAXOver"):
        super().__init__(symbol=symbol, params=params, sessions=sessions, name=name)
        self.tracker = Tracker(snooze=self.interval.seconds)
        self.trader = trader or ScalpTrader(symbol=self.symbol)

    async def find_entry(self):
        candles = await self.symbol.copy_rates_from_pos(
            timeframe=self.ttf, count=self.tcc
        )
        candles.ta.ema(length=self.fast_ema, append=True)
        candles.ta.ema(length=self.slow_ema, append=True)
        candles.rename(
            **{f"EMA_{self.fast_ema}": "fast_ema",
               f"EMA_{self.slow_ema}": "slow_ema"},
            inplace=True,
        )

        fas = candles.ta_lib.above(candles.fast_ema, candles.slow_ema)
        fbs = candles.ta_lib.below(candles.fast_ema, candles.slow_ema)

        if fas.iloc[-1]:
            self.tracker.update(order_type=OrderType.BUY, snooze=self.timeout)
        elif fbs.iloc[-1]:
            self.tracker.update(order_type=OrderType.SELL, snooze=self.timeout)
        else:
            self.tracker.update(order_type=None, snooze=self.interval.seconds)

    async def trade(self):
        await self.find_entry()
        if self.tracker.order_type is None:
            await self.sleep(secs=self.tracker.snooze)
        else:
            await self.trader.place_trade(
                order_type=self.tracker.order_type, parameters=self.parameters
            )
            await self.delay(secs=self.tracker.snooze)
```

### 2. Wire It Up with a Bot

```python
import logging
from aiomql import Bot, ForexSymbol, OpenPositionsTracker
from strategies.ema_crossover import EMAXOver

logging.basicConfig(level=logging.INFO)


def main():
    symbols = [ForexSymbol(name=s) for s in ["EURUSD", "GBPUSD", "USDJPY"]]
    strategies = [EMAXOver(symbol=sym) for sym in symbols]

    bot = Bot()
    bot.add_strategies(strategies)

    # Optionally track open positions on a separate thread
    bot.add_coroutine(
        coroutine=OpenPositionsTracker(autocommit=True).track,
        on_separate_thread=True,
    )

    bot.execute()  # synchronous entry point (blocks until shutdown)


if __name__ == "__main__":
    main()
```

> **Tip:** Use `await bot.start()` instead of `bot.execute()` if you're already inside an async context.

### 3. Trading Sessions

Restrict when a strategy trades by passing `Sessions`:

```python
from datetime import time
from aiomql import Session, Sessions, ForexSymbol, Chaos

london = Session(name="London", start=time(8, 0), end=time(16, 0))
new_york = Session(name="New York", start=time(13, 0), end=time(21, 0))

sessions = Sessions(sessions=[london, new_york])
strategy = Chaos(symbol=ForexSymbol(name="USDJPY"), sessions=sessions)
```

### 4. Multi-Process Execution

Run completely independent bots in separate processes:

```python
from aiomql import Bot


def run_forex():
    bot = Bot()
    # ... add forex strategies ...
    bot.execute()


def run_crypto():
    bot = Bot()
    # ... add crypto strategies ...
    bot.execute()


Bot.process_pool(processes={run_forex: {}, run_crypto: {}}, num_workers=2)
```

---

## Project Structure

```
src/aiomql/
├── core/               # Low-level infrastructure
│   ├── _core.py        #   MT5 function definitions & async wrappers
│   ├── meta_trader.py  #   MetaTrader singleton (init, login, symbol/order calls)
│   ├── config.py       #   Singleton Config (JSON + programmatic settings)
│   ├── constants.py    #   Enums (TimeFrame, OrderType, TradeAction, …)
│   ├── models.py       #   Data models (SymbolInfo, AccountInfo, TradeRequest, …)
│   ├── base.py         #   _Base metaclass (attribute helpers, MT5 access)
│   ├── db.py           #   SQLite trade-results database
│   ├── store.py        #   In-memory shared state store
│   ├── state.py        #   State management
│   ├── task_queue.py   #   Async task queue for scheduled work
│   ├── errors.py       #   Error definitions
│   ├── exceptions.py   #   Custom exceptions (OrderError, LoginError, …)
│   └── sync/           #   Synchronous MetaTrader wrapper
│
├── lib/                # High-level trading components
│   ├── bot.py          #   Bot orchestrator (strategy runner, process pool)
│   ├── executor.py     #   Thread/task executor for strategies
│   ├── strategy.py     #   Strategy base class (trade loop, sessions)
│   ├── symbol.py       #   Symbol (market data, ticks, rates)
│   ├── order.py        #   Order (check, send, margin, profit)
│   ├── trader.py       #   Trader (place_trade, SL/TP management)
│   ├── account.py      #   Account singleton
│   ├── candle.py       #   Candles collection (DataFrame + TA)
│   ├── ticks.py        #   Tick & Ticks (tick data collections)
│   ├── positions.py    #   Position querying & management
│   ├── history.py      #   Trade & order history
│   ├── ram.py          #   RAM (Risk Assessment & Money) manager
│   ├── sessions.py     #   Session & Sessions (time-window trading)
│   ├── terminal.py     #   Terminal info wrapper
│   ├── result.py       #   Trade result recording (CSV/JSON)
│   ├── result_db.py    #   Trade result recording (SQLite)
│   ├── trade_records.py#   Trade records management
│   └── sync/           #   Synchronous mirrors of lib modules
│
├── contrib/            # Community extensions
│   ├── strategies/     #   Chaos (random buy/sell demo)
│   ├── symbols/        #   ForexSymbol (pip & volume calculations)
│   ├── trackers/       #   Position & open-positions trackers
│   ├── traders/        #   SimpleTrader, ScalpTrader
│   └── utils/          #   StrategyTracker (Tracker)
│
├── ta_libs/            # Technical analysis (pandas-ta classic)
└── utils/              # Decorators, price helpers, process pool
```

---

## API Documentation

See the full [API Reference](docs/toc.md) for detailed documentation of every module.

---

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run the test suite
pytest tests
```

---

## Contributing

Pull requests are welcome. For major changes, please open an [issue](https://github.com/Ichinga-Samuel/aiomql/issues) first
to discuss what you would like to change.

---

## License

[MIT](LICENSE)

---

## Support

If you find this project useful, consider supporting its development:

- [❤️ Sponsor on GitHub](https://github.com/sponsors/Ichinga-Samuel)
- [☕ Buy Me a Coffee](https://buymeacoffee.com/ichingasamuel)