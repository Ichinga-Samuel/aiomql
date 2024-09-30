from .event_manager import EventManager
from ...core.config import Config


class StrategyTester:
    event_manager: EventManager
    config: Config

    def set_up(self):
        self.event_manager = EventManager()

    async def sleep(self, secs: float):
        time = self.config.backtest_engine.cursor.time
        mod = time % secs
        secs = secs - mod if mod != 0 else mod
        if self.event_manager.num_main_tasks == 1:
            self.config.backtest_engine.fast_forward(secs)
            await self.event_manager.wait()
        elif self.event_manager.num_main_tasks > 1:
            time = self.config.backtest_engine.cursor.time + secs
            while time > self.config.backtest_engine.cursor.time:
                await self.event_manager.wait()
        else:
            ...

    def test(self):
        raise NotImplementedError("Implement this method in your subclass")
