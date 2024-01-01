"""Trader class module. Handles the creation of an order and the placing of trades"""

from logging import getLogger

from ..symbols import ForexSymbol
from ...ram import RAM
from ...core.models import OrderType
from ...positions import Positions
from ...trader import Trader

logger = getLogger(__name__)


class SimpleTrader(Trader):
    """A simple trader class. Limits the number of loosing trades per symbol"""
    def __init__(self, *, symbol: ForexSymbol, ram: RAM = None, num_trades: int = 1):
        """Initializes the order object and RAM instance

        Args:
            symbol (Symbol): Financial instrument
            ram (RAM): Risk Assessment and Management instance
            num_trades (int): Number of open trades in loosing positions to allow per symbol
        """
        super().__init__(symbol=symbol, ram=ram)
        self.positions = Positions(symbol=symbol.name)
        self.num_trades = num_trades

    async def create_order(self, *, order_type: OrderType, points: float = 0):
        """Complete the order object with the required values. Creates a simple order.

        Args:
            order_type (OrderType): Type of order
            points (float): Target points
        """
        positions = await self.positions.positions_get()
        positions.sort(key=lambda pos: pos.time_msc)
        loosing = [trade for trade in positions if trade.profit < 0]
        if (losses := len(loosing)) > self.num_trades:
            raise RuntimeError(f"Last {losses} trades in a losing position")
        points = points or self.symbol.trade_stops_level * 2
        amount = self.ram.amount or await self.ram.get_amount()
        self.order.volume = await self.symbol.compute_volume(amount=amount, points=points)
        self.order.type = order_type
        await self.set_trade_stop_levels(points=points)

    async def place_trade(self, order_type: OrderType, parameters: dict = None, points: float = 0):
        """Places a trade based on the order_type.

        Args:
            order_type (OrderType): Type of order
            parameters: parameters of the trading strategy used to place the trade
            points (float): Target points
        """
        try:
            self.parameters |= parameters or {}
            await self.create_order(order_type=order_type, points=points)
            if not await self.check_order():
                return
            await self.send_order()
        except Exception as err:
            logger.error(f"{err}. Symbol: {self.order.symbol}\n {self.__class__.__name__}.place_trade")