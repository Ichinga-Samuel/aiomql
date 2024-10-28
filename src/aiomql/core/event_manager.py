import asyncio
from asyncio import  Condition, Task
from typing import Self
from datetime import datetime
from .config import Config


class EventManager:
    _instance: Self
    task_tracker: int
    config: Config
    tasks: list[Task]
    num_main_tasks: int  # main tasks that are directly controlled by the Condition Synchronization primitives

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance.config = Config()
            cls._instance.condition = Condition()
            cls._instance.num_main_tasks = 0
            cls._instance.task_tracker = 0
            cls._instance.tasks = []
        return cls._instance

    def __init__(self, *, num_tasks: int = 0):
        self.num_main_tasks = num_tasks or self.num_main_tasks

    @property
    def backtest_engine(self):
        return self.config.backtest_engine

    def add_tasks(self, *tasks: Task):
        self.tasks.extend(tasks)

    def sigint_handler(self, sig, frame):
        for task in self.tasks:
            task.cancel()
        self.backtest_engine.wrap_up()

    async def acquire(self):
        await self.condition.acquire()

    def notify_all(self):
        self.condition.notify_all()

    async def event_monitor(self):
        self.backtest_engine.next()
        while True:
            async with self.condition:
                if self.task_tracker == self.num_main_tasks: # all main tasks have been completed in the current cycle
                    self.task_tracker = 0
                    await self.backtest_engine.tracker()
                    self.backtest_engine.next()
                    self.condition.notify_all()
                    # print(f"Time: {self.backtest_engine.cursor.time}")
                    if self.backtest_engine.cursor.time % 3600 == 0:
                        print(datetime.strftime(self.backtest_engine.cursor.time, "%Y-%m-%d %H:%M:%S"))
                if self.backtest_engine.stop_testing:
                    break
                await asyncio.sleep(0)
        self.backtest_engine.wrap_up()

    async def wait(self):
        self.task_tracker += 1
        await self.condition.wait()

    def release(self):
        self.condition.release()
