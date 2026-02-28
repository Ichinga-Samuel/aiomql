from aiomql import Strategy, ForexSymbol, TimeFrame, OrderType, Tracker, Trader
from ..traders.rs_trader import RSTrader

class RibbonScalper(Strategy):
    """
    Entry Strategy (Long): When the 5 and 8 EMA cross above the 13 EMA and the EMAs start spreading out (indicating a trend).
    Entry Strategy (Short): When the 5 and 8 EMA cross below the 13 EMA and spread out.
    Exit Strategy (Take Profit): Set a small, fixed profit target (e.g., 5-10 pips) or exit when the EMA ribbon starts to flatten or twist.
    Exit Strategy (Stop Loss): Tight stop-loss the previous candle high/low to limit risk.
    """
    fast_ema: int # fast moving average
    medium_ema: int  # medium moving average
    slow_ema: int   # slow moving average
    time_frame: TimeFrame # time frame
    candles_count: int # lookback period
    tracker: Tracker # a tracker class
    pips_target: int  # number of pips to target
    interval: int # interval between successive runs in seconds

    parameters = {"fast_ema": 5, "medium_ema": 8, "slow_ema": 13, "time_frame": TimeFrame.M1,
                  "candles_count": 120, "pips_target": 10, "interval": 30}

    def __init__(self, *, symbol: ForexSymbol, params: dict = None, trader: Trader = None, name="RibbonScalper"):
        super().__init__(symbol=symbol, params=params, name=name)
        self.tracker = Tracker()
        self.trader = trader or RSTrader(symbol=symbol)
        self.interval = self.time_frame.seconds

    async def find_entry(self):
        rates = await self.symbol.copy_rates_from_pos(count=self.candles_count, timeframe=self.time_frame)
        rates.ta.ema(length=self.fast_ema, append=True)
        rates.ta.ema(length=self.medium_ema, append=True)
        rates.ta.ema(length=self.slow_ema, append=True)
        rates.rename(**{f"EMA_{self.fast_ema}": "fast", f"EMA_{self.medium_ema}": "medium", f"EMA_{self.slow_ema}": "slow"})
        find_long_fast = rates.ta_lib.cross(rates.fast, rates.slow)
        find_long_medium = rates.ta_lib.cross(rates.medium, rates.slow)

        if find_long_fast.iloc[-1]  and find_long_medium.iloc[-1]:
            self.tracker.update(order_type=OrderType.BUY, trend="bullish", sl=rates[-2].low, snooze=300)
            return

        find_short_fast = rates.ta_lib.cross(rates.fast, rates.slow, above=False)
        find_short_medium = rates.ta_lib.cross(rates.medium, rates.slow, above=False)

        if find_short_fast.iloc[-1] and find_short_medium.iloc[-1]:
            self.tracker.update(order_type=OrderType.SELL, trend="bearish", sl=rates[-2].high, snooze=300)
            return

        self.tracker.update(order_type=None, trend="ranging", snooze=self.interval)

    async def trade(self):
        await self.find_entry()
        if self.tracker.order_type is not None:
            await self.trader.place_trade(parameters=self.parameters, order_type=self.tracker.order_type,
                                          sl=self.tracker.sl, pips_target=self.pips_target)
            await self.sleep(secs=self.tracker.snooze)
            return
        else:
            await self.sleep(secs=self.tracker.snooze)