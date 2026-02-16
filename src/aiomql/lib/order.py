"""Order module for trade order operations.

This module provides the Order class for creating, checking, and sending
trade orders to the MetaTrader 5 terminal. It includes functionality for
margin calculations, profit projections, and pending order management.

Example:
    Sending a market order::

        from aiomql import Order, OrderType

        order = Order(symbol='EURUSD', type=OrderType.BUY, volume=0.1, price=1.1000)
        result = await order.send()
"""
import asyncio
from logging import getLogger

from ..core.models import TradeRequest, TradeOrder, OrderCheckResult, OrderSendResult
from ..core.constants import TradeAction, OrderTime, OrderFilling, OrderType
from ..core.exceptions import OrderError
from ..core.base import _Base
from ..utils import error_handler, decrease_value_by_pct, increase_value_by_pct

logger = getLogger(__name__)


class Order(_Base, TradeRequest):
    """Trade order related functions and properties. Subclass of TradeRequest."""
    def __init__(self, **kwargs):
        """Initialize the order object with keyword arguments, symbol must be provided.
        Provide default values for action, type_time and type_filling if not provided.

        Args:
            **kwargs: Keyword arguments must match the attributes of TradeRequest as well as the attributes of
             Order class as specified in the annotations in the class definition.

        Default Values:
            action (TradeAction.DEAL): Trade action
            type_time (OrderTime.DAY): Order time
            type_filling (OrderFilling.FOK): Order filling
        """
        kwargs = {"action": TradeAction.DEAL, "type_time": OrderTime.DAY, "type_filling": OrderFilling.FOK, **kwargs}
        super().__init__(**kwargs)

    def modify(self, **kwargs):
        """Modify the order object with keyword arguments.

        Args:
            **kwargs: Keyword arguments must match the attributes of TradeRequest as well as the attributes of
             Order class as specified in the annotations in the class definition.
        """
        self.set_attributes(**kwargs)

    @classmethod
    async def orders_total(cls):
        """Get the number of active pending orders.

        Returns:
            (int): total number of active pending orders
        """
        return await cls.mt5.orders_total()

    @classmethod
    async def get_pending_order(cls, *, ticket: int) -> TradeOrder | None:
        """
        Get a pending order by ticket number.

        Args:
            ticket (int): Order ticket number

        Returns:
        """
        orders = await cls.mt5.orders_get(ticket=ticket)
        for order_ in orders:
            if order_.ticket == ticket:
                return TradeOrder(**order_._asdict())
        return None

    @classmethod
    async def get_pending_orders(cls, *, ticket: int = 0, symbol: str = "", group: str = "") -> tuple[TradeOrder, ...]:
        """Get the list of active pending orders for the current symbol.

        Args:
            ticket (int): Order ticket number
            symbol (str): Symbol name
            group (str): Group name

        Returns:
            tuple[TradeOrder, ...]: A Tuple of active pending trade orders as TradeOrder objects
        """
        orders = await cls.mt5.orders_get(symbol=symbol, ticket=ticket, group=group)
        if orders is not None:
            return tuple(TradeOrder(**order._asdict()) for order in orders)
        return tuple()

    @classmethod
    async def cancel_order(cls, *, order: int, symbol: str = "") -> OrderSendResult:
        """Cancel an active pending order by ticket number."""
        res = await cls.send_order(request={"order": order, "action": TradeAction.REMOVE, "symbol": symbol})
        if res is None:
            raise OrderError("Unable to cancel order %d:%s" % (order, symbol))
        return res

    async def check(self, **kwargs) -> OrderCheckResult:
        """Check funds sufficiency for performing a required trading operation and the possibility of executing it.

        Returns:
            OrderCheckResult: An OrderCheckResult object

        Raises:
            OrderError: If not successful
        """
        req = self.request | kwargs
        res = await self.mt5.order_check(req)
        if res is None:
            raise OrderError(f"Order check failed for {self.symbol}")
        return OrderCheckResult(**res._asdict())

    async def send(self):
        return await self.send_order(request=self.request)

    @classmethod
    async def send_order(cls, *, request: dict, connection_retries=0) -> OrderSendResult:
        """Send a request to perform a trading operation from the terminal to the trade server.

        Returns:
             OrderSendResult: An OrderSendResult object

        Raises:
            OrderError: If not successful
        """
        res = await cls.mt5.order_send(request)
        if res is None:
            raise OrderError("Failed to send order %s" % request.get("symbol", ""))
        if res.retcode == 10031 and connection_retries < 3:
            await asyncio.sleep(3**connection_retries)
            return await cls.send_order(request=request, connection_retries= connection_retries + 1)
        return OrderSendResult(**res._asdict())

    @error_handler(log_error_msg=False)
    async def calc_margin(self) -> float | None:
        """Return the required margin in the account currency to perform a specified trading operation.

        Returns:
            float: Returns float value if successful
        """
        res = await self.mt5.order_calc_margin(self.type, self.symbol, self.volume, self.price)
        return res

    @error_handler(log_error_msg=False)
    async def calc_profit(self) -> float:
        """Return profit in the account currency for a specified trading operation.

        Returns:
            float: Returns float value if successful
            None: If not successful
        """
        action, symbol, volume, price_open, price_close = (self.type, self.symbol, self.volume, self.price, self.tp)
        res = await self.mt5.order_calc_profit(action, symbol, volume, price_open, price_close)
        return res

    @error_handler(log_error_msg=False)
    async def calc_loss(self) -> float:
        """Return profit in the account currency for a specified trading operation.

        Returns:
            float: Returns float value if successful
            None: If not successful
        """
        action, symbol, volume, price_open, price_close = (self.type, self.symbol, self.volume, self.price, self.sl)
        res = await self.mt5.order_calc_profit(action, symbol, volume, price_open, price_close)
        return res

    @property
    def request(self) -> dict:
        """Return the order request as a dictionary."""
        return {key: value for key, value in self.dict.items() if key in self.mt5.TradeRequest.__match_args__}

    @classmethod
    async def profit_to_price(cls, *, profit: float, order_type: OrderType, volume: float, symbol: str, price_open: float):
        price_close = increase_value_by_pct(price_open, 50) if order_type == 0 else decrease_value_by_pct(price_open, 50)
        half_profit = await cls.mt5.order_calc_profit(symbol=symbol, action=order_type, volume=volume,
                                             price_open=price_open, price_close=price_close)
        rate = profit / half_profit * 50
        rate = increase_value_by_pct(price_open, rate) if order_type == 0 else decrease_value_by_pct(price_open, rate)
        return rate

    @classmethod
    async def get_history_order_by_ticket(cls, *, ticket: int) -> TradeOrder | None:
        res = await cls.mt5.history_orders_get(ticket=ticket)
        if res is not None and len(res) > 0 and res[0].ticket == ticket:
            return TradeOrder(**res[0]._asdict())
        return None
