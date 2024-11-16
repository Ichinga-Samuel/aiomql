# Aiomql - Bot Building Framework and Asynchronous MetaTrader5 Library
![GitHub](https://img.shields.io/github/license/ichinga-samuel/aiomql?style=plastic)
![GitHub issues](https://img.shields.io/github/issues/ichinga-samuel/aiomql?style=plastic)
![PyPI](https://img.shields.io/pypi/v/aiomql)


### Installation
```bash
pip install aiomql
```

### Key Features
- Asynchronous Python Library For MetaTrader5
- Asynchronous Bot Building Framework
- Build bots for trading in different financial markets.
- Use threadpool executors to run multiple strategies on multiple instruments concurrently
- Records and keep track of trades and strategies in csv files.
- Helper classes for Bot Building. Easy to use and extend.
- Compatible with pandas-ta.
- Sample Pre-Built strategies
- Specify and Manage Trading Sessions
- Risk Management
- Backtesting Engine
- Run multiple bots concurrently with different accounts from the same broker or different brokers
- Easy to use and very accurate backtesting engine

### As an asynchronous MetaTrader5 Libray
```python
import asyncio

from aiomql import MetaTrader


async def main():
    mt5 = MetaTrader()
    res = await mt5.initialize(login=31288540, password='nwa0#anaEze', server='Deriv-Demo')
    if not res:
        print('Unable to login and initialize')
        return 
    # get account information
    acc = await mt5.account_info()
    print(acc)
    # get symbols
    symbols = await mt5.symbols_get()
    print(symbols)
    
asyncio.run(main())
```

### As a Bot Building FrameWork using a Sample Strategy
Aiomql allows you to focus on building trading strategies and not worry about the underlying infrastructure.
It provides a simple and easy to use framework for building bots with rich features and functionalities.


```python
from datetime import time
import logging

from aiomql import Bot, ForexSymbol, FingerTrap, Session, Sessions, RAM, SimpleTrader, TimeFrame, Chaos

logging.basicConfig(level=logging.INFO)


def build_bot():
    bot = Bot()
    # configure the parameters and the trader for a strategy
    params = {'fast_period': 8, 'slow_period': 34, 'etf': TimeFrame.M5}
    symbols = ['GBPUSD', 'AUDUSD', 'USDCAD', 'EURGBP', 'EURUSD']
    symbols = [ForexSymbol(name=sym) for sym in symbols]
    strategies = [FingerTrap(symbol=sym, params=params)for sym in symbols]
    bot.add_strategies(strategies)
    
    # create a strategy that uses sessions
    # sessions are used to specify the trading hours for a particular market
    # the strategy will only trade during the specified sessions
    london = Session(name='London', start=time(8, 0), end=time(16, 0))
    new_york = Session(name='New York', start=time(13, 0), end=time(21, 0))
    tokyo = Session(name='Tokyo', start=time(0, 0), end=time(8, 0))
    
    sessions = Sessions(sessions=[london, new_york, tokyo])  
    jpy_strategy = Chaos(symbol=ForexSymbol(name='USDJPY'), sessions=sessions)
    bot.add_strategy(strategy=jpy_strategy)
    bot.execute()

# run the bot
build_bot()
```

### Backtesting
Aiomql provides a very accurate backtesting engine that allows you to test your trading strategies before deploying
them in the market. The backtest engine prioritizes accuracy over speed, but allows you to increase the speed
as desired. It is very easy to use and provides a lot of flexibility. The backtester is designed to run strategies
seamlessly without need for modification of the strategy code. When running in backtest mode all the classes that
needs to know if they are running in backtest mode will be able to do so and adjust their behavior accordingly.

```python
from aiomql import MetaBackTester, BackTestEngine, MetaTrader
import logging
from datetime import datetime, UTC

from aiomql.lib.backtester import BackTester
from aiomql.core import Config
from aiomql.contrib.strategies import FingerTrap
from aiomql.contrib.symbols import ForexSymbol
from aiomql.core.backtesting import BackTestEngine


def back_tester():
    config = Config(mode="backtest")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    syms = ["Volatility 75 Index", "Volatility 100 Index", "Volatility 25 Index", "Volatility 10 Index"]
    symbols = [ForexSymbol(name=sym) for sym in syms]
    strategies = [FingerTrap(symbol=symbol) for symbol in symbols]
    
    # create start time and end time for the backtest
    start = datetime(2024, 5, 1, tzinfo=UTC)
    stop_time = datetime(2024, 5, 2, tzinfo=UTC)
    end = datetime(2024, 5, 7, tzinfo=UTC)
    
    # create a backtest engine
    back_test_engine = BackTestEngine(start=start, end=end, speed=3600, stop_time=stop_time,
                                      close_open_positions_on_exit=True, assign_to_config=True, preload=True,
                                      account_info={"balance": 350})
    # add it to the backtester
    backtester = BackTester(backtest_engine=back_test_engine)
    # add strategies to the backtester
    backtester.add_strategies(strategies=strategies)
    backtester.execute()


back_tester()
```

### Writing a Custom Strategy
Aiomql provides a simple and easy to use framework for building trading strategies. You can easily extend the
framework to build your own custom strategies. Below is an example of a simple strategy that buys when the fast
moving average crosses above the slow moving average and sells when the fast moving average crosses below the slow
moving average.

```python
# emaxover.py
from aiomql import Strategy, ForexSymbol, TimeFrame, Tracker, OrderType, Sessions, Trader, ScalpTrader


class EMAXOver(Strategy):
    ttf: TimeFrame  # time frame for the strategy
    tcc: int  # how many candles to consider
    fast_ema: int  # fast moving average period
    slow_ema: int  # slow moving average period
    tracker: Tracker  # tracker to keep track of strategy state
    interval: TimeFrame  # intervals to check for entry and exit signals
    timeout: int  # timeout after placing an order in seconds

    # default parameters for the strategy
    # they are set as attributes. You can override them in the constructor via the params argument.
    parameters = {'ttf': TimeFrame.H1, 'tcc': 3000, 'fast_ema': 34, 'slow_ema': 55, 'interval': TimeFrame.M15,
                  'timeout': 3 * 60 * 60}

    def __init__(self, *, symbol: ForexSymbol, params: dict | None = None, trader: Trader = None,
                 sessions: Sessions = None, name: str = "EMAXOver"):
        super().__init__(symbol=symbol, params=params, sessions=sessions, name=name)
        self.tracker = Tracker(snooze=self.interval.seconds)
        self.trader = trader or ScalpTrader(symbol=self.symbol)

    async def find_entry(self):
        # get the candles
        candles = await self.symbol.copy_rates_from_pos(timeframe=self.ttf, start_position=0, count=self.tcc)

        # get the fast moving average
        candles.ta.ema(length=self.fast_ema, append=True)
        # get the slow moving average
        candles.ta.ema(length=self.slow_ema, append=True)
        # rename the columns
        candles.rename(**{f"EMA_{self.fast_ema}": "fast_ema", f"EMA_{self.slow_ema}": "slow_ema"}, inplace=True)

        # check for crossovers
        # fast above slow
        fas = candles.ta_lib.cross(candles.fast_ema, candles.slow_ema, above=True)
        # fast below slow
        fbs = candles.ta_lib.cross(candles.fast_ema, candles.slow_ema, above=False)

        ## check for entry signals in the current candle
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
            await self.trader.place_trade(order_type=self.tracker.order_type, parameters=self.parameters)
            await self.delay(secs=self.tracker.snooze)
```

### Testing

Run the tests with pytest

```bash
pytest test 
```

### API Documentation
see [API Documentation](docs) for more details

### Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

### Support
Feeling generous, like the package or want to see it become a more mature package?

Consider supporting the project by buying me a coffee.


[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/ichingasamuel)
