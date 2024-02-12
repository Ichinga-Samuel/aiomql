"""Trader class module. Handles the creation of an order and the placing of trades"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypeVar
from logging import getLogger
from zoneinfo import ZoneInfo

from .order import Order
from .symbol import Symbol as _Symbol
from .ticks import Tick
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
    config: Config

    def __init__(self, *, symbol: Symbol, ram: RAM = None):
        """Initializes the order object and RAM instance

        Args:
            symbol (Symbol): Financial instrument
            ram (RAM): Risk Assessment and Management instance
        """
        self.config = Config()
        self.symbol = symbol
        self.order = Order(symbol=symbol.name)
        self.ram = ram or RAM()
        self.parameters = {}

    def set_order_limits(self, *, pips: float, tick: Tick):
        """Sets the stop loss and take profit for the order. This method uses pips as defined for forex instruments.

        Args:
            pips: Target pips
            tick: Tick object
        """
        pips = pips * self.symbol.pip
        sl, tp = pips, pips * self.ram.risk_to_reward
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

    def set_trade_stop_levels(self, *, points: float, tick: Tick):
        """Set the stop loss and take profit levels of the order based on the points and price tick.

        Args:
            points: Target points
            tick: Tick object
        """
        points = points * self.symbol.point
        sl, tp = points, points * self.ram.risk_to_reward
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
            req = check.request._asdict() | check.get_dict(include={'comment', 'retcode'})
            logger.warning(f"Invalid order for {self.symbol}: {dict_to_string(req)}")
            return False
        return True

    async def send_order(self) -> OrderSendResult:
        """Send the order to the broker."""
        result = await self.order.send()
        if result.retcode != 10009:
            req = result.request._asdict() | result.get_dict(include={'comment', 'retcode'})
            logger.warning(f"Unable to place order for {self.symbol}: {dict_to_string(req)}")
            return result
        res = result.get_dict(exclude={'request', 'retcode_external', 'retcode', 'request_id'})
        logger.info(f"Placed Trade for {self.symbol}: {dict_to_string(res)}")
        await self.record_trade(result, parameters=self.parameters.copy())
        return result

    async def record_trade(self, result: OrderSendResult, parameters: dict = None, name: str = ''):
        """Record the trade in a csv file.

        Args:
            result (OrderSendResult): Result of the order send
            parameters: parameters of the trading strategy used to place the trade
            name: Name of the trading strategy
        """
        if result.retcode != 10009 or not self.config.record_trades:
            return
        params = parameters or self.parameters.copy()
        profit = await self.order.calc_profit()
        params["expected_profit"] = profit
        date = datetime.utcnow()
        date = date.replace(tzinfo=ZoneInfo("UTC"))
        params["date"] = str(date.date())
        params["time"] = str(date.time())
        res = Result(result=result, parameters=params, name=name)
        self.config.task_queue.add_task(res.to_csv)

    @abstractmethod
    async def place_trade(self, *args, **kwargs):
        """Places a trade based on the order_type."""
