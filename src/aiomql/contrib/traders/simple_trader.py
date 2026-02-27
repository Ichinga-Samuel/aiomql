"""Simple trader for placing trades with a stop loss level.

This module provides the ``SimpleTrader`` class, a concrete implementation
of the ``Trader`` base class that places trades using a specified stop loss
and volume calculated from the risk amount via the RAM instance.
"""

from logging import getLogger

from ...core.models import OrderType
from ...lib.trader import Trader

logger = getLogger(__name__)


class SimpleTrader(Trader):
    """Trader that places trades with a given stop loss.

    Extends the ``Trader`` base class to implement a straightforward
    strategy where the trade volume is calculated based on the risk
    amount and the distance to the stop loss.
    """
    async def place_trade(self, *, order_type: OrderType, sl: float, parameters: dict = None):
        """Places a trade based on the order_type and a given stop_loss. The volume is based on the amount to risk which is
           calculated using the Risk Assessment Management instance.

        Args:
            order_type (OrderType): The order_type
            sl (float): The stop_loss
            parameters (dict): Parameters associated with the trade
        """
        try:
            self.parameters |= parameters or {}
            await self.create_order_with_sl(order_type=order_type, sl=sl)
            if not await self.check_order():
                return
            self.order.comment = self.parameters.get("name", self.__class__.__name__)
            await self.send_order()
            self.reset_order()
        except Exception as err:
            logger.error(f"{err} in {self.__class__.__name__}.place_trade for {self.symbol.name}")
