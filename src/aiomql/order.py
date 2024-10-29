import asyncio
from logging import getLogger

from .core.models import TradeRequest, OrderSendResult, OrderCheckResult, TradeOrder
from .core.constants import TradeAction, OrderTime, OrderFilling
from .core.exceptions import OrderError
logger = getLogger(__name__)


class Order(TradeRequest):
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
        if 'symbol' in kwargs:
            kwargs['symbol'] = str(kwargs['symbol'])
        self.action = kwargs.pop('action', TradeAction.DEAL)
        self.type_time = kwargs.pop('type_time', OrderTime.DAY)
        self.type_filling = kwargs.pop('type_filling', OrderFilling.FOK)
        super().__init__(**kwargs)

    async def orders_total(self):
        """Get the number of active orders.

        Returns:
            (int): total number of active orders
        """
        return await self.mt5.orders_total()

    async def get_order(self, *, ticket: int, retries: int = 3) -> TradeOrder | None:
        """
        Get the order by ticket number.
        Args:
            ticket (int): Order ticket number
            retries (int): Number of retries
        Returns:
        """
        if retries < 1:
            return None
        orders = await self.mt5.orders_get(ticket=ticket)
        if orders and (order := orders[0]).ticket == ticket:
            return TradeOrder(**order._asdict())
        if self.mt5.error.is_connection_error():
            await asyncio.sleep(retries)
            return await self.get_order(ticket=ticket, retries=retries-1)
        return None

    async def get_orders(self, *, ticket: int = 0, symbol: str = '', group: str = '', retries=3)\
            -> tuple[TradeOrder, ...]:
        """Get the list of active orders for the current symbol.
        Keyword Args:
            ticket (int): Order ticket number
            symbol (str): Symbol name
            group (str): Group name
        Returns:
            tuple[TradeOrder]: A Tuple of active trade orders as TradeOrder objects
        """
        if retries < 1:
            return tuple()
        symbol = getattr(self, 'symbol', symbol)
        orders = await self.mt5.orders_get(symbol=symbol, ticket=ticket, group=group)
        if orders is not None:
            orders = (TradeOrder(**order._asdict()) for order in orders)
            return tuple(orders)
        if self.mt5.error.is_connection_error():
            await asyncio.sleep(retries)
            return await self.get_orders(ticket=ticket, symbol=symbol, group=group, retries=retries-1)
        return tuple()

    async def check(self, **kwargs) -> OrderCheckResult:
        """Check funds sufficiency for performing a required trading operation and the possibility of executing it.

        Returns:
            OrderCheckResult: An OrderCheckResult object

        Raises:
            OrderError: If not successful
        """
        req = self.dict | kwargs
        res = await self.mt5.order_check(req)
        if res is None:
            raise OrderError(f'Failed to check order due to {self.mt5.error.description}')
        return OrderCheckResult(**res._asdict())

    async def send(self) -> OrderSendResult:
        """Send a request to perform a trading operation from the terminal to the trade server.

        Returns:
             OrderSendResult: An OrderSendResult object

        Raises:
            OrderError: If not successful
        """
        res = await self.mt5.order_send(self.dict)
        if res is None:
            raise OrderError(f'Failed to send order {self.symbol} due to {self.mt5.error.description}')
        res = OrderSendResult(**res._asdict())
        try:
            profit = await self.calc_profit()
            loss = await self.calc_profit(tp=self.sl)
            res.loss = loss
            res.profit = profit
        except Exception as exe:
            logger.error(f'Failed to calculate profit and loss for this order due to {exe}')
        return res

    async def calc_margin(self) -> float:
        """Return the required margin in the account currency to perform a specified trading operation.

        Returns:
            float: Returns float value if successful

        Raises:
            OrderError: If not successful
        """
        res = await self.mt5.order_calc_margin(self.type, self.symbol, self.volume, self.price)
        if res is None:
            raise OrderError(f'Failed to calculate margin for {self.symbol} due to {self.mt5.error.description}')
        return res

    async def calc_profit(self, **kwargs) -> float:
        """Return profit in the account currency for a specified trading operation.

        Returns:
            float: Returns float value if successful

        Raises:
            OrderError: If not successful
        """
        args = self.get_dict(include={'tp', 'price', 'symbol', 'volume', 'type'})
        args |= kwargs
        res = await self.mt5.order_calc_profit(args['type'], args['symbol'], args['volume'], args['price'], args['tp'])
        if res is None:
            raise OrderError(f'Failed to calculate profit for {self.symbol} due to {self.mt5.error.description}')
        return res
