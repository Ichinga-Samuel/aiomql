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
