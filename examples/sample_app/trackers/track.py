import asyncio
from logging import getLogger
from datetime import datetime

from aiomql import OpenPosition

logger = getLogger(__name__)


async def close_after(open_pos: OpenPosition, /, *, duration: int, start: float = 0):
    if not await open_pos.update_position():
        return
    pos = open_pos.position
    start = start or pos.time
    diff = datetime.now().timestamp() - start
    if diff > duration:
        _, res = await open_pos.close_position()
        if res.retcode == 10009:
            logger.info("%s, %d closed", pos.symbol, pos.ticket)


async def hedge_position(pos: OpenPosition, /, *, hedge_amount: float = -2, close_hedge_amount: float = 0,
                         order_params: dict = None):
    is_open = await pos.update_position()
    position = pos.position
    if not (is_open and pos.is_hedged is False and position.profit < 0):
        return

    if position.profit <= hedge_amount:
        ok, order = await pos.hedge_position(order_params=order_params)
        if not ok:
            logger.error("Could not hedge %s:%d", pos.symbol, pos.ticket)


async def track_hedges(pos: OpenPosition, close_hedge_amount: float = -10):
    res = await pos.update_position()
    if not res:
        return
    hedges = list(pos.hedges.values())
    await asyncio.gather(*[hedge.update_position() for hedge in hedges], return_exceptions=True)
    hedges = [hedge for hedge in hedges if hedge.is_open]
    await asyncio.gather(*[hedge.close_position() for hedge in hedges if hedge.position.profit <= close_hedge_amount],
                         return_exceptions=True)