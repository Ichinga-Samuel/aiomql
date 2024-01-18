from logging import getLogger

from ..symbols import ForexSymbol
from ...ram import RAM
from ...core.models import OrderType
from ...positions import Positions
from ...trader import Trader

logger = getLogger(__name__)


class SimpleTrader(Trader):
    """A simple trader class. Limits the number of loosing trades per symbol"""
    def __init__(self, *, symbol: ForexSymbol, ram: RAM = None, loss_limit: int = 3):
        """Initializes the order object and RAM instance
        The default risk to reward ratio is 1:1.

        Args:
            symbol (Symbol): Financial instrument
            ram (RAM): Risk Assessment and Management instance
            loss_limit (int): Maximum number of losing trades allowed at a time.
        """
        ram = ram or RAM(risk_to_reward=1, points=100)
        super().__init__(symbol=symbol, ram=ram)
        self.loss_limit = loss_limit

    async def create_order(self, *, order_type: OrderType):
        """Complete the order object with the required values. Creates a simple order.

        Args:
            order_type (OrderType): Type of order
        """
        positions = await Positions().positions_get()
        loosing = [trade for trade in positions if trade.profit < 0]
        if (losses := len(loosing)) > self.loss_limit:
            raise RuntimeError(f"Last {losses} trades in a losing position")
        points = self.ram.points or self.symbol.trade_stops_level * 3
        amount = await self.ram.get_amount()
        self.order.volume = await self.symbol.compute_volume(amount=amount, points=points)
        self.order.type = order_type
        self.order.comment = self.parameters.get('name', '')
        await self.set_trade_stop_levels(points=points)

    async def place_trade(self, order_type: OrderType, parameters: dict = None):
        """Places a trade based on the order_type."""
        try:
            self.parameters |= parameters or {}
            await self.create_order(order_type=order_type)
            if not await self.check_order():
                return
            await self.send_order()
        except Exception as err:
            logger.error(f"{err} in {self.__class__.__name__}.place_trade for {self.symbol.name}")