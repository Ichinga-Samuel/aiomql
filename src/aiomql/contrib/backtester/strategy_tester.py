import asyncio

from .event_manager import EventManager
from .get_data import GetData
from .test_data import TestData
from .meta_tester import MetaTester

from ...core import Config

class StrategyTester:
    def __init__(self, *, strategies: list = None, test_data: TestData = None, test_data_file: str = ''):
        self.config = Config()
        self.mt5 = MetaTester()
        self.strategies = strategies or []
        self.test_data = test_data or self.get_test_data(name=test_data_file)
        self.config.test_data = self.test_data
        self.event_manager = EventManager(num_tasks=len(self.strategies))

    def get_test_data(self, name: str) -> TestData | None:
        name = f"{self.config.test_data_dir_name}/{name or self.config.test_data_file}"
        data = GetData.load_data(name=name, compressed=self.config.compress_test_data)
        return TestData(data) if data is not None else None

    async def start(self):
        acc = self.config.account_info()
        await self.mt5.initialize(**acc)
        await self.mt5.login(**acc)

    async def run(self):
        await self.start()
        tasks = [*[asyncio.create_task(strategy.test()) for strategy in self.strategies],
                 asyncio.create_task(self.event_manager.event_monitor())]
        self.event_manager.add_task(*tasks)
        await asyncio.gather(*tasks)
        await self.mt5.shutdown()
