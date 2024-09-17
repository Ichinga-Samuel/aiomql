from typing import TypeVar

from .event_manager import EventManager
from ...core.config import Config

Symbol = TypeVar("Symbol")


class TestStrategy:
    event_manager: EventManager
    config: Config
    symbol: Symbol

    def set_up(self):
        self.event_manager = EventManager()

    async def sleep(self, secs: float):
        time = self.config.test_data.cursor.time
        mod = time % secs
        secs = secs - mod if mod != 0 else mod
        time = self.config.test_data.cursor.time + secs
        while time > self.config.test_data.cursor.time:
          await self.event_manager.wait()

    def test(self):
        raise NotImplementedError("Implement this method in your subclass")


class TestSingleStrategy:
    config: Config
    symbol: Symbol

    async def sleep(self, secs: float):
        time = self.config.test_data.cursor.time
        mod = time % secs
        secs = secs - mod if mod != 0 else mod
        self.config.test_data.fast_forward(secs)

    def test(self):
        raise NotImplementedError("Implement this method in your subclass")
