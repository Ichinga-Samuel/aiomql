import random
from logging import getLogger

from ...lib.strategy import Strategy
from ..symbols import ForexSymbol
from ..utils import Tracker
from ...core.constants import TimeFrame, OrderType
from ..traders.scalp_trader import ScalpTrader

logger = getLogger(__name__)


class Chaos(Strategy):
    """A chaotic strategy that buys and sells randomly."""

    ltf: TimeFrame
    htf: TimeFrame
    lcc: int
    hcc: int
    fast_ema: int
    slow_ema: int
    tracker: Tracker
    parameters = {
        "fast_ema": 8,
        "slow_ema": 20,
        "ltf": TimeFrame.M1,
        "htf": TimeFrame.M2,
        "lcc": 100,
        "hcc": 100,
    }

    def __init__(
        self, *, symbol: ForexSymbol, params: dict = None, sessions=None, name="Chaos"
    ):
        super().__init__(symbol=symbol, params=params, sessions=sessions, name=name)
        self.tracker = Tracker(snooze=self.ltf.seconds)
        self.trader = ScalpTrader(symbol=self.symbol)

    async def check_trend(self):
        try:
            candles = await self.symbol.copy_rates_from_pos(
                timeframe=self.htf, count=self.hcc
            )
            if (
                (current := candles[-1])
                and current.time < self.tracker.trend_time
                and current.close == self.tracker.last_trend_price
            ):
                self.tracker.update(new=False, order_type=None, snooze=5)
                return
            self.tracker.update(
                new=True, trend_time=current.time, last_trend_price=current.close
            )
            candles.ta.ema(length=self.slow_ema, append=True, fillna=0)
            candles.ta.ema(length=self.fast_ema, append=True, fillna=0)
            candles.rename(
                inplace=True,
                **{f"EMA_{self.fast_ema}": "fast", f"EMA_{self.slow_ema}": "slow"},
            )
            order_type = random.choice([OrderType.BUY, OrderType.SELL])
            if order_type == OrderType.BUY:
                self.tracker.update(
                    trend="bullish", snooze=self.htf.seconds, order_type=OrderType.BUY
                )
            else:
                self.tracker.update(
                    trend="bearish", snooze=self.htf.seconds, order_type=OrderType.SELL
                )
        except Exception as err:
            logger.error(f"{err}. Failed to check trend")
            self.tracker.update(
                trend="ranging", snooze=self.ltf.seconds, order_type=None
            )

    async def trade(self):
        try:
            await self.check_trend()
            if self.tracker.order_type is not None:
                await self.trader.place_trade(
                    order_type=self.tracker.order_type, parameters=self.parameters
                )
                self.tracker.update(order_type=None)
                await self.sleep(secs=self.tracker.snooze)
            else:
                await self.sleep(secs=self.tracker.snooze)
        except Exception as err:
            logger.error(
                f"{err}. Failed to trade {self.symbol.name} with {self.__class__.__name__}"
            )
