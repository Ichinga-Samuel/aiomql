import asyncio
from typing import Coroutine, Callable, Awaitable
from logging import getLogger

logger = getLogger(__name__)


class QueueItem:
    def __init__(self, task: Callable | Awaitable | Coroutine, *args, **kwargs):
        self.task = task
        self.args = args
        self.kwargs = kwargs

    async def run(self):
        try:
            if asyncio.iscoroutinefunction(self.task):
                return await self.task(*self.args, **self.kwargs)
            else:
                return self.task(*self.args, **self.kwargs)
        except Exception as err:
            logger.error(f"Error in running {getattr(self.task, '__name__', str(self.task))}"
                         f" with {str(self.args)}, {self.kwargs}: {err}")


class TaskQueue:
    def __init__(self):
        self.queue = asyncio.Queue()

    def add(self, item: QueueItem):
        try:
            self.queue.put_nowait(item)
        except asyncio.QueueFull:
            return

    async def worker(self):
        while True:
            try:
                item: QueueItem = self.queue.get_nowait()
                await item.run()
                self.queue.task_done()
            except asyncio.QueueEmpty:
                return

    def add_task(self, item: Callable | Awaitable | Coroutine, *args, **kwargs):
        self.add(QueueItem(item, *args, **kwargs))
        asyncio.create_task(self.worker())

    async def start(self):
        await self.queue.join()
