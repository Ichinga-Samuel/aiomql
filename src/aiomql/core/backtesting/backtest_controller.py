from logging import getLogger
from asyncio import Task
from signal import signal, SIGINT
from threading import Barrier, BrokenBarrierError
from typing import Self
from datetime import datetime

from ..config import Config
from ..exceptions import StopTrading

logger = getLogger(__name__)


class BackTestController:
    _instance: Self
    task_tracker: int
    config: Config
    tasks: list[Task]

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance.config = Config()
            cls._instance.barrier = Barrier(1)
            cls._instance.task_tracker = 0
            cls._instance.tasks = []
        return cls._instance

    def __init__(self):
        signal(SIGINT, self.sigint_handler)

    @property
    def backtest_engine(self):
        return self.config.backtest_engine

    def add_tasks(self, *tasks: Task):
        self.tasks.extend(tasks)

    def set_parties(self, *, parties: int):
        self.barrier._parties = parties

    @property
    def parties(self):
        return self.barrier.parties

    def sigint_handler(self, sig, frame):
        logger.warning("SIGINT received. Stopping the controller.")
        self.backtest_engine.stop_testing = True

    async def control(self):
        try:
            self.backtest_engine.next()
            while True:
                pending = self.wait()
                if (
                    pending == 0
                ):  # all main tasks have been completed in the current cycle
                    await self.backtest_engine.tracker()
                    self.backtest_engine.next()
                    if self.backtest_engine.cursor.time % 3600 == 0:
                        logger.info(
                            datetime.strftime(
                                datetime.fromtimestamp(
                                    self.backtest_engine.cursor.time
                                ),
                                "%Y-%m-%d %H:%M:%S",
                            )
                        )
                if self.backtest_engine.stop_testing:
                    logger.info(
                        "Stop trading called in control at %s",
                        datetime.fromtimestamp(self.backtest_engine.cursor.time).strftime("%Y-%m-%d %H:%M:%S"),
                    )
                    break
            await self.backtest_engine.wrap_up()
            self.stop_backtesting()
        except BrokenBarrierError:
            return

        except Exception as err:
            logger.error("Error: %s in controller", err)
            await self.backtest_engine.wrap_up()
            self.stop_backtesting()
            return

    def stop_backtesting(self):
        self.abort()
        self.config.shutdown = True

    def wait(self):
        try:
            pending = self.barrier.wait()
            return pending
        except BrokenBarrierError:
            raise StopTrading
        except Exception as err:
            logger.error("Error: %s in wait", err)

    def abort(self):
        self.barrier.abort()
