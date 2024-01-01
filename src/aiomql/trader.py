"""Trader class module. Handles the creation of an order and the placing of trades"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypeVar
from logging import getLogger
from zoneinfo import ZoneInfo

from .order import Order
from .symbol import Symbol as _Symbol
from .ram import RAM
from .core.models import OrderType, OrderSendResult
from .core.config import Config
from .utils import dict_to_string
from .result import Result

logger = getLogger(__name__)
Symbol = TypeVar("Symbol", bound=_Symbol)


class Trader(ABC):
    """Base class for creating a Trader object. Handles the creation of an order and the placing of trades.

    Attributes:
        symbol (Symbol): The financial instrument.
        ram (RAM): RAM instance
        order (Order): Trade order

    Class Attributes:
        config (Config): Config instance.
    """
    config = Config()

    def __init__(self, *, symbol: Symbol, ram: RAM = None):
        """Initializes the order object and RAM instance

        Args:
            symbol (Symbol): Financial instrument
            ram (RAM): Risk Assessment and Management instance
        """
        self.symbol = symbol
        self.order = Order(symbol=symbol.name)
        self.ram = ram or RAM()
        self.parameters = {}

    @abstractmethod
    async def create_order(self, *args, **kwargs):
        """Complete the order object with the required values. Creates a simple order."""

    async def set_order_limits(self, *, pips: float):
        """Sets the stop loss and take profit for the order. This method uses pips as defined for forex instruments.

        Args:
            pips: Target pips
        """
        pips = pips * self.symbol.pip
        sl, tp = pips, pips * self.ram.risk_to_reward
        tick = await self.symbol.info_tick()
        if self.order.type == OrderType.BUY:
            self.order.sl, self.order.tp = round(tick.ask - sl, self.symbol.digits), round(tick.ask + tp,
                                                                                           self.symbol.digits)
            self.order.price = tick.ask
        elif self.order.type == OrderType.SELL:
            self.order.sl, self.order.tp = round(tick.bid + sl, self.symbol.digits), round(tick.bid - tp,
                                                                                           self.symbol.digits)
            self.order.price = tick.bid
        else:
            raise ValueError(f"Invalid order type: {self.order.type}")

    async def set_trade_stop_levels(self, *, points):
        """Set the stop loss and take profit levels of the order based on the points.

        Args:
            points: Target points
        """
        points = points * self.symbol.point
        sl, tp = points, points * self.ram.risk_to_reward
        tick = await self.symbol.info_tick()
        if self.order.type == OrderType.BUY:
            self.order.sl, self.order.tp = round(tick.ask - sl, self.symbol.digits), round(tick.ask + tp,
                                                                                           self.symbol.digits)
            self.order.price = tick.ask
        else:
            self.order.sl, self.order.tp = round(tick.bid + sl, self.symbol.digits), round(tick.bid - tp,
                                                                                           self.symbol.digits)
            self.order.price = tick.bid

    async def check_order(self) -> bool:
        """Check order before sending it to the broker.

        Returns:
            bool: True if order can go through else false
        """
        check = await self.order.check()
        if check.retcode != 0:
            logger.warning(f"Symbol: {self.order.symbol}\nResult:\n"
                           f"{dict_to_string(check.get_dict(include={'comment', 'retcode'}), multi=True)}")
            return False
        return True

    async def send_order(self):
        """Send the order to the broker."""
        parameters = self.parameters.copy()
        result = await self.order.send()
        if result.retcode != 10009:
            logger.warning(f"Symbol: {self.order.symbol}\nResult:\n"
                           f"{dict_to_string(result.get_dict(include={'comment', 'retcode'}), multi=True)}")
            return
        logger.info(f"Symbol: {self.order.symbol}\nOrder: {dict_to_string(result.dict, multi=True)}\n")
        await self.record_trade(result, parameters)

    async def record_trade(self, result: OrderSendResult, parameters: dict):
        """Record the trade in a csv file.

        Args:
            result (OrderSendResult): Result of the order send
            parameters: parameters of the trading strategy used to place the trade
        """
        if result.retcode != 10009 or not self.config.record_trades:
            return
        params = parameters
        profit = await self.order.calc_profit()
        params["expected_profit"] = profit
        date = datetime.utcnow()
        date = date.replace(tzinfo=ZoneInfo("UTC"))
        params["date"] = date
        params["time"] = date.timestamp()
        res = Result(result=result, parameters=params)
        await res.save_csv()

    @abstractmethod
    async def place_trade(self, *args, **kwargs):
        """Places a trade based on the order_type."""