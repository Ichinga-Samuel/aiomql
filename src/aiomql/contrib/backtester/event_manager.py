import asyncio
from asyncio import  Condition, Task
from typing import Self

from ...core import Config


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

    def add_task(self, *task: Task):
        self.tasks.extend(task)

    def sigint_handler(self, sig, frame):
        for task in self.tasks:
            task.cancel() if not task.done() else ...

    async def acquire(self):
        await self.condition.acquire()

    def notify_all(self):
        self.condition.notify_all()

    async def event_monitor(self):
        while True:
            async with self.condition:
                if self.task_tracker == self.num_main_tasks:
                    self.task_tracker = 0
                    await self.config.test_data.tracker()
                    self.config.test_data.next()
                    print(self.config.test_data.cursor.time)
                    self.condition.notify_all()
                    await asyncio.sleep(0)

    async def wait(self):
        self.task_tracker += 1
        await self.condition.wait()

    def release(self):
        self.condition.release()