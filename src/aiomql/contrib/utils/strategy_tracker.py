from datetime import datetime
from dataclasses import dataclass
from typing import Literal

from ...core.constants import OrderType


@dataclass
class StrategyTracker:
    """Keeps track of a strategy's data and state"""
    trend: Literal["ranging", "bullish", "bearish"] = "ranging"
    bullish: bool = False
    bearish: bool = False
    ranging: bool = True
    snooze: float = 0
    trend_time: float = 0
    entry_time: float = 0
    last_trend_price: float = 0
    last_entry_price: float = 0
    new: bool = True
    order_type: OrderType = None
    sl: float = 0
    tp: float = 0

    @property
    def time(self):
        return datetime.now()

    @property
    def timestamp(self):
        return self.time.timestamp()

    def update(self, **kwargs):
        """Updates the tracker with the given kwargs"""
        fields = self.__dict__
        for key in kwargs:
            if key in fields:
                setattr(self, key, kwargs[key])
        if "trend" in kwargs:
            match self.trend:
                case "ranging":
                    self.ranging = True
                    self.bullish = self.bearish = False
                case "bullish":
                    self.ranging = self.bearish = False
                    self.bullish = True
                case "bearish":
                    self.ranging = self.bullish = False
                    self.bearish = True
