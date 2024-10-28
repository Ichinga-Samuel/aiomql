import asyncio
import signal
from logging import getLogger

from ..core.event_manager import EventManager
from ..core.task_queue import TaskQueue
from ..contrib.backtesting.backtest_engine import BackTestEngine
from .strategy import Strategy
from ..core.meta_backtester import MetaBackTester

logger = getLogger(__name__)


class BackTestRunner:
    def __init__(self, *, strategies: list[Strategy], backtest_engine: BackTestEngine):
        self.backtest_engine = backtest_engine
        self.strategies = strategies or []
        self.event_manager = EventManager()
        self.mt5 = MetaBackTester()
        signal.signal(signal.SIGINT, self.event_manager.sigint_handler)
        self.mt5.config.task_queue.worker_timeout = 5

    async def run(self):
        try:
            await self.mt5.initialize()
            await self.mt5.login()
            strategies = [strategy for strategy in self.strategies if await strategy.symbol.initialize()]
            self.event_manager.num_main_tasks = len(strategies)
            tasks = [*[asyncio.create_task(strategy.run_strategy()) for strategy in strategies],
                     asyncio.create_task(self.event_manager.event_monitor())]
            self.event_manager.add_tasks(*tasks)
            tasks.append(asyncio.create_task(self.mt5.config.task_queue.run()))
            await asyncio.gather(*tasks, return_exceptions=True) if len(strategies) else ...
        except Exception as err:
            logger.error(f"Error {err} occurred in StrategyTester")
