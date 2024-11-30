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
    """The controller for the backtesting engine.
    It also acts as a synchronizer for running multiple strategies (tasks) using a threading.Barrier primitive.
    It handles the updating of open positions and close them when necessary.
    It handles the iterator for the backtesting engine and handles it movement in time by moving it to the next time step.

    Attributes:
        _instance (Self): The instance of the controller
        config (Config): The configuration for the backtesting engine
        tasks (list[Task]): The tasks that are being run
        barrier (Barrier): The barrier for synchronizing the tasks
    """

    _instance: Self
    config: Config
    tasks: list[Task]
    barrier: Barrier

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance.config = Config()
            cls._instance.config.backtest_controller = cls._instance
            cls._instance.barrier = Barrier(1)
            cls._instance.tasks = []
        return cls._instance

    def __init__(self):
        signal(SIGINT, self.sigint_handler)

    @property
    def backtest_engine(self):
        """Returns the backtest engine"""
        return self.config.backtest_engine

    def add_tasks(self, *tasks: Task):
        """Adds tasks to the tasks list"""
        self.tasks.extend(tasks)

    def set_parties(self, *, parties: int):
        """Sets the number of parties for the barrier. The barrier will wait for the number of parties to reach the barrier.
        This has to be done here as it can be impossible to know the eventual number of parties to set the barrier to during initialization.

        Args:
            parties (int): The number of parties to set the barrier to
        """
        self.barrier._parties = parties

    @property
    def parties(self):
        """Returns the number of parties for the barrier"""
        return self.barrier.parties

    def sigint_handler(self, sig, frame):
        logger.warning("SIGINT received. Stopping the controller.")
        self.backtest_engine.stop_testing = True

    async def control(self):
        """The backtest controller. It controls the backtesting engine and the tasks that are being run.
        It acts as a synchronizer for the tasks and the backtesting engine.
        """
        try:
            self.backtest_engine.next()
            while True:
                pending = self.wait()
                # all main tasks have been completed in the current cycle
                if pending == 0:
                    await self.backtest_engine.tracker()
                    self.backtest_engine.next()
                    # gives an output every 6 hours
                    if self.backtest_engine.cursor.time % (3600 * 6) == 0:
                        logger.info(
                            datetime.strftime(
                                datetime.fromtimestamp(self.backtest_engine.cursor.time), "%Y-%m-%d %H:%M:%S"
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
        """Stop the backtester, and shutdown the executor"""
        self.abort()
        self.config.shutdown = True

    def wait(self):
        """Called by individual tasks to indicate completion of their cycle"""
        try:
            pending = self.barrier.wait()
            return pending
        except BrokenBarrierError:
            raise StopTrading
        except Exception as err:
            logger.error("Error: %s in wait", err)

    def abort(self):
        """Aborts the barrier"""
        self.barrier.abort()
