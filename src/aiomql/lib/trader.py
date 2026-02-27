"""Trader module for order creation and trade execution.

This module provides the Trader base class for creating and managing
trade orders. It includes methods for setting stop levels, calculating
volumes based on risk, and recording trades.

Example:
    Creating a custom trader::

        class MyTrader(Trader):
            async def place_trade(self, order_type, sl, tp):
                await self.create_order_with_stops(
                    order_type=order_type, sl=sl, tp=tp
                )
                result = await self.send_order()
                return result
"""

from abc import ABC, abstractmethod
from typing import TypeVar
from logging import getLogger

from ..core.models import OrderType, OrderSendResult, OrderCheckResult
from ..core.config import Config
from ..core.task_queue import QueueItem
from .result import Result
from .order import Order
from .symbol import Symbol as _Symbol
from .ram import RAM
from ..utils import error_handler

logger = getLogger(__name__)
Symbol = TypeVar("Symbol", bound=_Symbol)


class Trader(ABC):
    """Base class for creating and managing orders.
    Handles the creation and placing of an order.
    It is an abstract class and must be subclassed to implement the place_trade method.

    Attributes:
        symbol (Symbol): The financial instrument.
        ram (RAM): RAM instance
        order (Order): Trade order
        parameters (dict): Parameters of the trading strategy used to place the trade
        config (Config): The Config instance.
    """

    config: Config
    ram: RAM
    parameters: dict

    def __init__(self, *, symbol: Symbol, ram: RAM = None):
        """Initializes the order object and RAM instance

        Args:
            symbol (Symbol): Financial instrument
            ram (RAM): Risk Assessment and Management instance
        """
        self.config = Config()
        self.symbol = symbol
        self.ram = ram or RAM()
        self.order = Order(symbol=symbol.name)
        self.parameters = {}

    def set_trade_stop_levels_pips(self, *, pips: float, risk_to_reward: float = None):
        """Sets the stop loss and take profit for the order.

        This method uses pips as defined for forex instruments. It is assumed
        that order_type and price are already set before calling this method.

        Args:
            pips: Target pips for stop loss distance.
            risk_to_reward: Optional risk to reward ratio. If not provided,
                uses the ratio from the RAM instance.
        """
        pips = pips * self.symbol.pip
        sl, tp = pips, pips * (risk_to_reward or self.ram.risk_to_reward)
        price = self.order.price
        if self.order.type.is_long:
            self.order.sl, self.order.tp = round(price - sl, self.symbol.digits), round(price + tp, self.symbol.digits)
        elif self.order.type.is_short:
            self.order.sl, self.order.tp = round(price + sl, self.symbol.digits), round(price - tp, self.symbol.digits)

    def set_trade_stop_levels_points(self, *, points: float, risk_to_reward: float = None):
        """Set the stop loss and take profit based on points and risk to reward.

        It is assumed that order_type and price are already set before calling
        this method.

        Args:
            points: Target points for stop loss distance.
            risk_to_reward: Risk to reward ratio. If not provided, uses the
                ratio from the RAM instance.
        """
        points = points * self.symbol.point
        sl, tp = points, points * (risk_to_reward or self.ram.risk_to_reward)
        price, digits = self.order.price, self.symbol.digits

        if self.order.type.is_long:
            self.order.sl, self.order.tp = round(price - sl, self.symbol.digits), round(price + tp, digits)

        elif self.order.type.is_short == OrderType.SELL:
            self.order.sl, self.order.tp = round(price + sl, self.symbol.digits), round(price - tp, digits)

    async def create_order_with_stops(
        self, *, order_type: OrderType, sl: float, tp: float, amount_to_risk: float = None
    ):
        """Create an order with stop loss and take profit levels.

        Uses the amount to risk per trade to calculate the volume.

        Args:
            order_type: Order type (BUY or SELL).
            sl: Stop loss price level.
            tp: Take profit price level.
            amount_to_risk: Amount to risk per trade in account currency.
                If not provided, uses the amount from the RAM instance.
        """
        amount = amount_to_risk or await self.ram.get_amount()
        amount = await self.symbol.amount_in_quote_currency(amount=amount)
        tick = await self.symbol.info_tick()
        price = tick.ask if order_type.is_long else tick.bid
        volume = self.symbol.compute_volume_sl(amount=amount, price=price, sl=sl)
        self.order.set_attributes(sl=sl, tp=tp, volume=volume, price=price, type=order_type)

    async def create_order_with_sl(
        self, *, order_type: OrderType, sl: float, amount_to_risk: float = None, risk_to_reward: float = None
    ):
        """
        Create an order with a given stop_loss level. Use the amount to risk per trade to calculate the volume.

        Args:
            order_type (OrderType): Order type
            sl (float): Stop loss in price
            amount_to_risk (float): Amount to risk per trade in terms of the account currency. Optional parameter,
                default is the amount as computed by the RAM instance.
            risk_to_reward (float): Risk to reward ratio. Optional parameter, default is the risk to reward ratio as
                defined in the RAM instance.
        """
        amount = amount_to_risk or await self.ram.get_amount()
        amount = await self.symbol.amount_in_quote_currency(amount=amount)
        tick = await self.symbol.info_tick()
        price = tick.ask if order_type == OrderType.BUY else tick.bid
        dsl = abs(price - sl)
        dtp = dsl * (risk_to_reward or self.ram.risk_to_reward)
        tp = price + dtp if order_type == OrderType.BUY else price - dtp
        volume = await self.symbol.compute_volume_sl(amount=amount, price=price, sl=sl)
        self.order.set_attributes(sl=sl, tp=tp, volume=volume, price=price, type=order_type)

    async def create_order_with_points(
        self, *, order_type: OrderType, points: float, amount_to_risk: float = None, risk_to_reward: float = None
    ):
        """Create an order with specific points to risk. Use the amount to risk per trade to calculate the volume.

        Args:
            order_type (OrderType): Order type
            points (float): Points to risk
            amount_to_risk (float): Amount to risk per trade in terms of the account currency. Optional parameter,
                default is the amount as computed by the RAM instance.
            risk_to_reward (float): Risk to reward ratio. Optional parameter, default is the risk to reward ratio as
                defined in the RAM instance.
        """
        self.order.type = order_type
        amount = amount_to_risk or await self.ram.get_amount()
        amount = await self.symbol.amount_in_quote_currency(amount=amount)
        tick = await self.symbol.info_tick()
        self.order.price = tick.ask if order_type == OrderType.BUY else tick.bid
        volume = await self.symbol.compute_volume_points(amount=amount, points=points)
        self.order.volume = volume
        self.set_trade_stop_levels_points(points=points, risk_to_reward=risk_to_reward)

    async def create_order_no_stops(self, *, order_type: OrderType, volume: float = None):
        """Create an order without setting stop loss and take profit. Using minimum lot size.

        Args:
            order_type (OrderType): Order type
            volume (float): Volume to trade with. Optional parameter, default is the minimum lot size.
        """
        tick = await self.symbol.info_tick()
        self.order.volume = volume or self.symbol.volume_min
        self.order.price = tick.ask if order_type == OrderType.BUY else tick.bid
        self.order.type = order_type

    async def check_order(self) -> OrderCheckResult | None:
        """Check order before sending it to the broker.

        Returns:
            bool: True if order can go through else false
        """
        check = await self.order.check()

        if check is None:
            logger.warning(f"{self.order.mt5.error}: Order check failed")
            return check

        if check.retcode != 0:
            logger.warning("Invalid order %s, for due to %s", self.symbol, check.comment)
        return check

    async def send_order(self) -> OrderSendResult | None:
        """Send the order to the broker."""
        result = await self.order.send()
        if result is None:
            logger.warning("%s: Failed to place order.", self.order.mt5.error)
            return result

        if result.retcode != 10009:
            logger.warning("Unable to place order for %s due to %s", self.symbol, result.comment)
            return result
        return result

    @error_handler
    async def record_trade(self, *, result: OrderSendResult, parameters: dict = None, name: str = "",
                           expected_profit: float = None, use_task_queue=True):
        """Record the trade in csv, json, or sql database.

        Args:
            result: Result of the order send operation.
            parameters: Parameters of the trading strategy used to place the trade.
            name: Name of the trading strategy.
            expected_profit: Expected profit for the trade. If not provided,
                calculates using order.calc_profit().
            use_task_queue: If True, adds save operation to task queue.
                If False, saves immediately. Defaults to True.
        """
        if self.config.record_trades is False or result.retcode != 10009:
            return
        params = {**parameters} if isinstance(parameters, dict) else {}
        expected_profit = expected_profit or await self.order.calc_profit() or 0
        order = await self.order.get_history_order_by_ticket(ticket=result.order)
        result.request.sl = order.sl
        result.request.tp = order.tp
        res = Result(result=result, parameters=params, name=name, time=order.time_setup_msc, expected_profit=expected_profit)
        if use_task_queue:
            self.config.task_queue.add(item=QueueItem(res.save), must_complete=True)
        else:
            await res.save()

    def reset_order(self):
        self.order = Order(symbol=self.symbol)

    @abstractmethod
    async def place_trade(self, *args, **kwargs):
        """Places a trade based on the order_type."""
