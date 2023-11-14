import asyncio
import logging
from typing import Literal
from dataclasses import dataclass

from ...symbol import Symbol
from ...trader import Trader
from ...candle import Candles
from ...strategy import Strategy
from ...core import TimeFrame, OrderType
from ...sessions import Sessions

logger = logging.getLogger(__name__)


@dataclass
class Entry:
    """
    Entry class for FingerTrap strategy. Will be used to store entry conditions and other entry related data.

    Attributes:
        bearish (bool): True if the market is bearish
        bullish (bool): True if the market is bullish
        ranging (bool): True if the market is ranging
        snooze (float): Time to wait before checking for entry conditions
        trend (str): The current trend of the market
        new (bool): True if the last candle is new
        order_type (OrderType): The type of order to place
    """

    bearish: bool = False
    bullish: bool = False
    ranging: bool = True
    trending: bool = False
    trend: Literal["ranging", "bullish", "bearish"] = "ranging"
    snooze: float = 0
    last_trend_time: float = 0
    last_entry_time: float = 0
    new: bool = True
    order_type: OrderType | None = None

    def update(self, **kwargs):
        fields = self.__dict__
        for key in kwargs:
            if key in fields:
                setattr(self, key, kwargs[key])
        match self.trend:
            case "ranging":
                self.ranging = True
                self.trending = self.bullish = self.bearish = False
            case "bullish":
                self.ranging = self.bearish = False
                self.bullish = self.trending = True
            case "bearish":
                self.ranging = self.bullish = False
                self.bearish = self.trending = True


class FingerTrap(Strategy):
    trend_time_frame: TimeFrame
    entry_time_frame: TimeFrame
    trend: int
    fast_period: int
    slow_period: int
    entry_period: int
    parameters: dict
    prices: Candles
    name = "FingerTrap"
    interval: TimeFrame
    entry_candles_count: int
    trend_candles_count: int

    def __init__(
        self,
        *,
        symbol: Symbol,
        params: dict | None = None,
        trader: Trader = None,
        sessions: Sessions = None,
    ):
        super().__init__(symbol=symbol, params=params, sessions=sessions)
        self.trend = self.parameters.get("trend", 3)
        self.fast_period = self.parameters.setdefault("fast_period", 8)
        self.slow_period = self.parameters.setdefault("slow_period", 34)
        self.entry_time_frame = self.parameters.setdefault(
            "entry_time_frame", TimeFrame.M5
        )
        self.trend_time_frame = self.parameters.setdefault(
            "trend_time_frame", TimeFrame.H1
        )
        self.trader = trader or Trader(symbol=self.symbol)
        self.entry: Entry = Entry(snooze=self.trend_time_frame.time)
        self.entry_period = self.parameters.setdefault("entry_period", 8)

        self.trend_candles_count = self.parameters.setdefault(
            "trend_candles_count", 86400 // self.trend_time_frame.time
        )
        self.trend_candles_count = max(self.trend_candles_count, self.slow_period)
        self.entry_candles_count = self.trend_candles_count * (
            self.trend_time_frame.time // self.entry_time_frame.time
        )
        self.entry_candles_count = max(self.entry_candles_count, self.entry_period)

    async def check_trend(self):
        try:
            candles = await self.symbol.copy_rates_from_pos(
                timeframe=self.trend_time_frame, count=self.trend_candles_count
            )
            current = candles[-1]
            if current.time > self.entry.last_trend_time:
                self.entry.update(new=True, last_trend_time=current.time)
            else:
                self.entry.update(new=False)
                return

            candles.ta.ema(length=self.slow_period, append=True, fillna=0)
            candles.ta.ema(length=self.fast_period, append=True, fillna=0)
            candles.rename(
                inplace=True,
                **{
                    f"EMA_{self.fast_period}": "fast",
                    f"EMA_{self.slow_period}": "slow",
                },
            )

            # Compute
            candles["fast_A_slow"] = candles.ta_lib.above(candles.fast, candles.slow)
            candles["fast_B_slow"] = candles.ta_lib.below(candles.fast, candles.slow)
            candles["close_A_fast"] = candles.ta_lib.above(candles.close, candles.fast)
            candles["close_B_fast"] = candles.ta_lib.below(candles.close, candles.fast)

            trend = candles[-self.trend : -1]
            if all(
                (c.is_bullish() and c.fast_A_slow and c.close_A_fast) for c in trend
            ):
                self.entry.update(trend="bullish")

            elif all(
                c.is_bearish() and c.fast_B_slow and c.close_B_fast for c in trend
            ):
                self.entry.update(trend="bearish")

            else:
                self.entry.update(trend="ranging", snooze=self.trend_time_frame.time)
        except Exception as exe:
            logger.error(f"{exe}. Error in {self.__class__.__name__}.check_trend")

    async def confirm_trend(self):
        try:
            candles = await self.symbol.copy_rates_from_pos(
                timeframe=self.entry_time_frame, count=self.entry_candles_count
            )
            current = candles[-1]
            if current.time > self.entry.last_entry_time:
                self.entry.update(new=True, last_entry_time=current.time)
            else:
                self.entry.update(new=False)
                return

            candles.ta.ema(length=self.entry_period, append=True, fillna=0)
            candles.rename(**{f"EMA_{self.entry_period}": "ema"})
            candles["close_A_ema"] = candles.ta_lib.above(candles.close, candles.ema)
            candles["close_B_ema"] = candles.ta_lib.below(candles.close, candles.ema)
            candles["close_XA_ema"] = candles.ta_lib.cross(candles.close, candles.ema)
            candles["close_XB_ema"] = candles.ta_lib.cross(
                candles.close, candles.ema, above=False
            )
            if self.entry.bullish and current.close_XA_ema:
                self.entry.update(
                    snooze=self.entry_time_frame.time, order_type=OrderType.BUY
                )
            elif self.entry.bearish and current.close_XB_ema:
                self.entry.update(
                    snooze=self.entry_time_frame.time, order_type=OrderType.SELL
                )
            else:
                self.entry.update(snooze=self.entry_time_frame.time, order_type=None)
        except Exception as exe:
            logger.error(f"{exe} Error in {self.__class__.__name__}.confirm_trend")

    async def watch_market(self):
        await self.check_trend()
        if not self.entry.ranging:
            await self.confirm_trend()

    async def trade(self):
        logger.info(f"Trading {self.symbol}")
        async with self.sessions as sess:
            while True:
                await sess.check()
                try:
                    await self.watch_market()
                    if not self.entry.new:
                        await asyncio.sleep(2)
                        continue
                    if self.entry.order_type is None:
                        await self.sleep(self.entry.snooze)
                        continue

                    await self.trader.place_trade(
                        order_type=self.entry.order_type, params=self.parameters
                    )
                    await self.sleep(self.entry.snooze)
                except Exception as err:
                    logger.error(
                        f"Error: {err}\t Symbol: {self.symbol} in {self.__class__.__name__}.trade"
                    )
                    await self.sleep(self.trend_time_frame.time)
                    continue

