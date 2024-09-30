import asyncio
import signal
from logging import getLogger

from .event_manager import EventManager
from .meta_tester import MetaTester
from .backtest_engine import BackTestEngine
from .strategy_tester import StrategyTester
from ...core import Config

logger = getLogger(__name__)


class BackTester:
    def __init__(self, *, strategies: list[StrategyTester] = None, backtest_engine: BackTestEngine = None):
        self.strategies = strategies or []
        self.event_manager = EventManager()
        self.mt5 = MetaTester(backtest_engine=backtest_engine)
        signal.signal(signal.SIGINT, self.event_manager.sigint_handler)

    async def run(self):
        try:
            await self.mt5.initialize()
            strategies = [strategy for strategy in self.strategies if await strategy.symbol.init()]
            print(f"Number of strategies: {len(strategies)}")
            self.event_manager.num_main_tasks = len(strategies)
            tasks = [*[asyncio.create_task(strategy.test()) for strategy in strategies],
                     asyncio.create_task(self.event_manager.event_monitor())]
            self.event_manager.add_tasks(*tasks)
            await asyncio.gather(*tasks, return_exceptions=True) if strategies else ...
        except Exception as err:
            logger.error(f"Error {err} occurred in StrategyTester")
