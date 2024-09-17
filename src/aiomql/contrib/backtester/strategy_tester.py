import asyncio
import signal
from logging import getLogger

from .event_manager import EventManager
from .test_data import TestData
from .meta_tester import MetaTester
from .test_strategy import TestStrategy, TestSingleStrategy
from ...core import Config

logger = getLogger(__name__)


class StrategyTester:
    def __init__(self, *, strategies: list[TestStrategy] = None):
        self.strategies = strategies or []
        self.event_manager = EventManager(num_tasks=len(self.strategies))
        signal.signal(signal.SIGINT, self.event_manager.sigint_handler)

    async def run(self, test_data: TestData):
        try:
            config = Config()
            config.test_data = test_data
            mt5 = MetaTester()
            acc = config.account_info()
            await mt5.initialize(**acc)
            await mt5.login(**acc)
            strategies = [strategy for strategy in self.strategies if await strategy.symbol.init()]
            print(f"Number of strategies: {len(strategies)}")
            self.event_manager.num_main_tasks = len(strategies)
            tasks = [*[asyncio.create_task(strategy.test()) for strategy in strategies],
                     asyncio.create_task(self.event_manager.event_monitor())]
            self.event_manager.add_task(*tasks)
            await asyncio.gather(*tasks, return_exceptions=True) if strategies else ...
        except Exception as err:
            logger.error(f"Error {err} occurred in StrategyTester")


class SingleStrategyTester:
    def __init__(self, *, strategy: TestSingleStrategy):
        self.strategy = strategy

    async def run(self, test_data: TestData):
        try:
            config = Config()
            config.test_data = test_data
            mt5 = MetaTester()
            acc = config.account_info()
            await mt5.initialize(**acc)
            await mt5.login(**acc)
            sym = self.strategy.symbol
            res = await sym.init()
            await self.strategy.test() if res else ...
        except Exception as err:
            logger.error(f"Error {err} occurred in SingleStrategyTester")
