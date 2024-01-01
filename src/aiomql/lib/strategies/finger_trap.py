import asyncio
import logging

from .tracker import Tracker
from ..traders import SimpleTrader
from ...symbol import Symbol
from ...trader import Trader
from ...candle import Candles
from ...strategy import Strategy
from ...core import TimeFrame, OrderType
from ...sessions import Sessions

logger = logging.getLogger(__name__)


class FingerTrap(Strategy):
    trend_time_frame: TimeFrame
    entry_time_frame: TimeFrame
    trend: int
    fast_period: int
    slow_period: int
    entry_period: int
    parameters: dict
    entry_candles_count: int
    trend_candles_count: int
    trader: Trader
    tracker: Tracker
    _parameters = {"trend": 3, "fast_period": 8, "slow_period": 34, "entry_time_frame": TimeFrame.M5,
                   "trend_time_frame": TimeFrame.H1, "entry_period": 8,
                   "trend_candles_count": 48, "entry_candles_count": 50}

    def __init__(self, *, symbol: Symbol, params: dict | None = None, trader: Trader = None, sessions: Sessions = None,
                 name: str = 'FingerTrap'):
        super().__init__(symbol=symbol, params=params, sessions=sessions, name=name)
        self.trader = trader or SimpleTrader(symbol=self.symbol)
        self.tracker: Tracker = Tracker(snooze=self.trend_time_frame.time)

    async def check_trend(self):
        try:
            candles: Candles = await self.symbol.copy_rates_from_pos(timeframe=self.trend_time_frame,
                                                            count=self.trend_candles_count)
            if not ((current := candles[-1].time) >= self.tracker.trend_time):
                self.tracker.new = False
                return
            self.tracker.update(new=True, trend_time=current)
            candles.ta.ema(length=self.slow_period, append=True, fillna=0)
            candles.ta.ema(length=self.fast_period, append=True, fillna=0)
            candles.rename(inplace=True, **{f"EMA_{self.fast_period}": "fast", f"EMA_{self.slow_period}": "slow"})
            # Compute
            candles["fast_A_slow"] = candles.ta_lib.above(candles.fast, candles.slow)
            candles["fast_B_slow"] = candles.ta_lib.below(candles.fast, candles.slow)
            candles["close_A_fast"] = candles.ta_lib.above(candles.close, candles.fast)
            candles["close_B_fast"] = candles.ta_lib.below(candles.close, candles.fast)

            trend = candles[-self.trend: -1]
            if all((c.is_bullish() and c.fast_A_slow and c.close_A_fast) for c in trend):
                self.tracker.update(trend="bullish")

            elif all(c.is_bearish() and c.fast_B_slow and c.close_B_fast for c in trend):
                self.tracker.update(trend="bearish")
            else:
                self.tracker.update(trend="ranging", snooze=self.trend_time_frame.time)
        except Exception as exe:
            logger.error(f"{exe}. Error in {self.__class__.__name__}.check_trend")

    async def confirm_trend(self):
        try:
            candles = await self.symbol.copy_rates_from_pos(timeframe=self.entry_time_frame,
                                                            count=self.entry_candles_count)
            if not ((current := candles[-1].time) >= self.tracker.entry_time):
                self.tracker.new = False
                return
            self.tracker.update(new=True, entry_time=current)
            candles.ta.ema(length=self.entry_period, append=True, fillna=0)
            candles.rename(**{f"EMA_{self.entry_period}": "ema"})
            candles["close_A_ema"] = candles.ta_lib.above(candles.close, candles.ema)
            candles["close_B_ema"] = candles.ta_lib.below(candles.close, candles.ema)
            candles["close_XA_ema"] = candles.ta_lib.cross(candles.close, candles.ema)
            candles["close_XB_ema"] = candles.ta_lib.cross(candles.close, candles.ema, above=False)
            current = candles[-2]
            if self.tracker.bullish and current.close_XA_ema:
                self.tracker.update(snooze=self.entry_time_frame.time, order_type=OrderType.BUY)
            elif self.tracker.bearish and current.close_XB_ema:
                self.tracker.update(snooze=self.entry_time_frame.time, order_type=OrderType.SELL)
            else:
                self.tracker.update(snooze=self.entry_time_frame.time, order_type=None)
        except Exception as exe:
            logger.error(f"{exe} Error in {self.name}.confirm_trend")

    async def watch_market(self):
        await self.check_trend()
        if not self.tracker.ranging:
            await self.confirm_trend()

    async def trade(self):
        logger.info(f"Trading {self.symbol}")
        async with self.sessions as sess:
            while True:
                await sess.check()
                try:
                    await self.watch_market()
                    if not self.tracker.new:
                        await asyncio.sleep(2)
                        continue
                    if self.tracker.order_type is None:
                        await self.sleep(self.tracker.snooze)
                        continue
                    await self.trader.place_trade(order_type=self.tracker.order_type, parameters=self.parameters)
                    await self.sleep(self.tracker.snooze)
                except Exception as err:
                    logger.error(f"Error: {err}\t Symbol: {self.symbol} in {self.__class__.__name__}.trade")
                    await self.sleep(self.trend_time_frame.time)
                    continue