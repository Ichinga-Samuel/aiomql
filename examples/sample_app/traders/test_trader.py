from logging import getLogger
from datetime import datetime
from aiomql import Trader, OrderType, OpenPosition, Positions, PositionTracker, Store

from ..trackers import close_after

logger = getLogger(__name__)


class TestTrader(Trader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.positions = Positions()
        self.store = Store()

    async def place_trade(self, *, order_type: OrderType, volume: float = None, parameters: dict = None):
            """Places a trade based on the order_type and volume. The volume is optional. If not provided, the minimum volume
            for the symbol will be used. This trade is placed without a stop_loss or take_profit. The trade is recorded in the
            trade_record file.

            Args:
                order_type (OrderType): The order_type
                volume (float): The volume to trade
                parameters (dict): Parameters associated with the trade
            """
            try:
                self.parameters |= parameters or {}
                volume = volume or self.symbol.volume_min
                await self.create_order_no_stops(order_type=order_type, volume=volume)
                if not await self.check_order():
                    return
                self.order.comment = self.parameters.get("name", self.__class__.__name__)
                res = await self.send_order()
                if res is not None and res.retcode == 10009:
                    position = await self.positions.get_position_by_ticket(ticket=res.order)
                    open_position = OpenPosition(ticket=res.order, symbol=self.symbol, position=position)
                    kwargs = {"duration": 40, "start": datetime.now().timestamp()}
                    ca = PositionTracker(close_after, **kwargs)
                    open_position.add_tracker(tracker=ca)
                    await self.record_trade(result=res, parameters=self.parameters)
            except Exception as err:
                logger.error(f"{err} in {self.__class__.__name__}.place_trade for {self.symbol.name}")
