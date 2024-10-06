import asyncio
import signal
from logging import getLogger

from ..core.event_manager import EventManager
from ..contrib.backtesting.backtest_engine import BackTestEngine
from .strategy import Strategy
from ..core.meta_backtester import MetaBackTester

logger = getLogger(__name__)


class BackTestRunner:
    def __init__(self, *, strategies: list[Strategy] = None, backtest_engine: BackTestEngine = None):
        self.strategies = strategies or []
        self.event_manager = EventManager()
        self.mt5 = MetaBackTester(backtest_engine=backtest_engine)
        signal.signal(signal.SIGINT, self.event_manager.sigint_handler)

    async def run(self):
        try:
            await self.mt5.initialize()
            await self.mt5.login()
            strategies = [strategy for strategy in self.strategies if await strategy.symbol.init()]
            self.event_manager.num_main_tasks = len(strategies)
            tasks = [*[asyncio.create_task(strategy.run_strategy()) for strategy in strategies],
                     asyncio.create_task(self.event_manager.event_monitor())]
            self.event_manager.add_tasks(*tasks)
            await asyncio.gather(*tasks, return_exceptions=True) if strategies else ...
        except Exception as err:
            logger.error(f"Error {err} occurred in StrategyTester")
