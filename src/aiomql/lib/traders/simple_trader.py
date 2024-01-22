from logging import getLogger

from ..symbols import ForexSymbol
from ...ram import RAM
from ...core.models import OrderType
from ...trader import Trader

logger = getLogger(__name__)


class SimpleTrader(Trader):
    """A simple trader class"""
    def __init__(self, *, symbol: ForexSymbol, ram: RAM = None):
        """Initializes the order object and RAM instance

        Args:
            symbol (Symbol): Financial instrument
            ram (RAM): Risk Assessment and Management instance
        """
        ram = ram or RAM(risk_to_reward=2)
        super().__init__(symbol=symbol, ram=ram)

    async def create_order(self, *, order_type: OrderType):
        """Complete the order object with the required values. Creates a simple order.

        Args:
            order_type (OrderType): Type of order
        """
        losing = await self.ram.check_losing_positions()
        if losing:
            raise RuntimeError(f"More than {self.ram.loss_limit} losing positions")
        amount = await self.ram.get_amount()
        points = self.symbol.compute_points(amount=amount, volume=self.symbol.volume_min)
        self.order.volume = self.symbol.volume_min
        self.order.type = order_type
        self.order.comment = self.parameters.get('name', 'SimpleTrader')
        tick = await self.symbol.info_tick()
        self.set_trade_stop_levels(points=points, tick=tick)

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