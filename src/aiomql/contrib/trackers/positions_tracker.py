import asyncio
from logging import getLogger
from typing import ClassVar

from ...core import Config, State, Store, sleep
from ...lib import Positions


logger = getLogger(__name__)


class OpenPositionsTracker:
    state: ClassVar[State]
    store: ClassVar[Store]
    config: ClassVar[Config]

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "config"):
            cls.config = Config()
        if not hasattr(cls, "state"):
            cls.state = cls.config.state
        if not hasattr(cls, "positions"):
            cls.positions = Positions()
        if not hasattr(cls, "store"):
            cls.store = cls.config.store
        return super().__new__(cls)

    def __init__(self, interval: int = 10, state_key: str = "tracked_positions", autocommit=False):
        self.interval = interval
        self.state_key = state_key
        self.autocommit = autocommit

    async def track(self):
        conn = self.config.state.conn
        while self.config.shutdown is False:
            try:
                await sleep(self.interval)
                tracked_positions = self.state.get("tracked_positions", {})
                await asyncio.gather(*(pos.track() for pos in tracked_positions.values()))
                await self.remove_closed_positions(tracked_positions)
                if self.autocommit:
                    await self.state.acommit(conn=conn, close=False)
            except Exception as exe:
                logger.error("%s: Error occurred in main position tracker", exe)
        conn.close()

    async def remove_closed_positions(self, tracked_positions):
        all_pos = await self.positions.get_positions()
        all_pos = {pos.ticket for pos in all_pos}
        self.state[self.state_key] = {pos.ticket: pos for pos in tracked_positions.values() if pos.ticket in all_pos}
