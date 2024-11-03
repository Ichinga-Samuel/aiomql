from logging import getLogger

from ...core.models import OrderType
from ...lib.trader import Trader

logger = getLogger(__name__)


class SimpleTrader(Trader):
    async def place_trade(
        self, *, order_type: OrderType, sl: float, parameters: dict = None
    ):
        """Places a trade based on the order_type and a given stop_loss

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
        except Exception as err:
            logger.error(
                f"{err} in {self.__class__.__name__}.place_trade for {self.symbol.name}"
            )
