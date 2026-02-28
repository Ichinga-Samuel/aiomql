from logging import getLogger

from aiomql import Trader, OrderType

logger = getLogger(__name__)

class RSTrader(Trader):
    async def create_order(self, sl: float, pips_target: int = 5):
        try:
            amount = await self.ram.get_amount()
            tick = await self.symbol.info_tick()
            price = tick.ask if self.order.type.is_long else tick.bid
            volume = await self.symbol.compute_volume_sl(sl=sl, amount=amount, price=price)
            tp = price + (self.symbol.point * 10 * pips_target)
            self.order.set_attributes(sl=sl, tp=tp, volume=volume, price=price)
        except Exception as exe:
            logger.error("%s: unable to create order", exe)

    async def place_trade(self, sl: float, order_type: OrderType, pips_target: int = 10, parameters: dict = None):
        try:
            self.order.type = order_type
            await self.create_order(sl=sl, pips_target=pips_target)
            parameters = parameters or {}
            self.order.set_attributes(comment=comment) if (comment := parameters.get("name")) else ...
            res = await self.send_order()
            if res and res.retcode  == 10009:
                await self.record_trade(result=res, parameters=parameters)
            self.reset_order()
        except Exception as exe:
            logger.error("%s: unable to place trade", exe)
