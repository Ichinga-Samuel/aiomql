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

    async def create_order(self, *, order_type: OrderType, sl: float):
        amount = await self.ram.get_amount()
        await self.symbol.info()
        tick = await self.symbol.info_tick()
        min_points = self.symbol.trade_stops_level + (self.symbol.spread * 1.5)
        points = (tick.ask - sl) / self.symbol.point if order_type == OrderType.BUY else\
            (abs(tick.bid - sl) / self.symbol.point)
        points = max(points, min_points)
        self.order.type = order_type
        volume, points = await self.symbol.compute_volume_points(amount=amount, points=points)
        self.order.volume = volume
        self.order.comment = self.parameters.get('name', self.__class__.__name__)
        tick = await self.symbol.info_tick()
        self.set_trade_stop_levels(points=points, tick=tick)

    async def place_trade(self, order_type: OrderType, sl: float, parameters: dict = None):
        """Places a trade based on the order_type."""
        try:
            self.parameters |= parameters or {}
            await self.create_order(order_type=order_type, sl=sl)
            if not await self.check_order():
                return
            await self.send_order()
        except Exception as err:
            logger.error(f"{err} in {self.__class__.__name__}.place_trade for {self.symbol.name}")
