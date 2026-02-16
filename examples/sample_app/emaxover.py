from aiomql import Strategy, ForexSymbol, TimeFrame, Tracker, OrderType, Sessions, Trader, ScalpTrader

from .traders import TestTrader

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
    parameters = {'ttf': TimeFrame.M10, 'tcc': 3000, 'fast_ema': 34, 'slow_ema': 55, 'interval': TimeFrame.M5,
                  'timeout': 120, "macd": 87, "sma": 90}

    def __init__(self, *, symbol: ForexSymbol, params: dict | None = None, trader: Trader = None,
                 sessions: Sessions = None, name: str = "EMAXOver"):
        super().__init__(symbol=symbol, params=params, sessions=sessions, name=name)
        self.tracker = Tracker(snooze=self.interval.seconds)
        self.trader = trader or TestTrader(symbol=self.symbol)

    async def find_entry(self):
        # get the candles
        candles = await self.symbol.copy_rates_from_pos(timeframe=self.ttf, count=self.tcc)

        # get the fast moving average
        candles.ta.ema(length=self.fast_ema, append=True)
        # get the slow moving average
        candles.ta.ema(length=self.slow_ema, append=True)
        # rename the columns
        candles.rename(**{f"EMA_{self.fast_ema}": "fast_ema", f"EMA_{self.slow_ema}": "slow_ema"}, inplace=True)

        # check for crossovers
        # fast above slow
        fas = candles.ta_lib.above(candles.fast_ema, candles.slow_ema)
        # fast below slow
        fbs = candles.ta_lib.below(candles.fast_ema, candles.slow_ema)

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
