from .event_manager import EventManager

from ...core.config import Config


class TestStrategy:
    event_manager: EventManager
    config: Config

    def set_up(self):
        self.config = Config()
        self.event_manager = EventManager()

    async def sleep(self, secs: float):
        time = self.config.test_data.cursor.time
        mod = time % secs
        secs = secs - mod if mod != 0 else mod
        time = self.config.test_data.cursor.time + secs
        while time > self.config.test_data.cursor.time:
          await self.event_manager.wait()
