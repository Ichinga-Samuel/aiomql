import asyncio
from typing import Coroutine, Callable, Literal
from signal import signal, SIGINT
from logging import getLogger

logger = getLogger(__name__)


class QueueItem:
    must_complete: bool
    
    def __init__(self, task_item: Callable | Coroutine, *args, **kwargs):
        self.task_item = task_item
        self.args = args
        self.kwargs = kwargs
        self.time = asyncio.get_event_loop().time()

    def __hash__(self):
        return id(self)

    def __lt__(self, other):
        return self.time < other.time

    async def run(self):
        try:
            if asyncio.iscoroutinefunction(self.task_item):
                await self.task_item(*self.args, **self.kwargs)

            else:
                self.task_item(*self.args, **self.kwargs)
            
        except Exception as err:
            logger.error(f"Error {err} occurred in {self.task_item.__name__} with args {self.args} and kwargs {self.kwargs}")


class TaskQueue:
    def __init__(self, size: int = 0, workers: int = 50, timeout: int = None, queue: asyncio.Queue = None,
                  on_exit: Literal['cancel', 'complete_priority'] = 'complete_priority'):
        
        self.queue = queue or asyncio.PriorityQueue(maxsize=size)
        self.workers = workers
        self.tasks = []
        self.priority_tasks = set()  # tasks that must complete
        self.timeout = timeout
        self.stop = False
        self.on_exit = on_exit

    def add(self, *, item: QueueItem, priority=3, must_complete=False):
        try:
            if not self.stop:
                item.must_complete = must_complete
                if isinstance(self.queue, asyncio.PriorityQueue):
                    item = (priority, item)
                self.priority_tasks.add(item) if item.must_complete else ...
                self.queue.put_nowait(item)

        except asyncio.QueueFull:
            logger.error(f"Queue is full, could not add {item}")

    async def worker(self):
        while True:
            if isinstance(self.queue, asyncio.PriorityQueue):
                _, item = await self.queue.get()

            else:
                item = await self.queue.get()
                
            if not self.stop or item.must_complete:
                await item.run()

            self.queue.task_done()
            self.priority_tasks.discard(item)

            if self.stop and len(self.priority_tasks) == 0:
                print('All priority tasks completed')
                self.cancel()
                break

    def sigint_handle(self, sig, frame):
        print('SIGINT received, cleaning up...')

        if self.on_exit == 'complete_priority' and self.priority_tasks:
            print(f'Completing {len(self.priority_tasks)} priority tasks...')
            self.stop = True
        else:
            self.cancel()

        self.on_exit = 'cancel'  # force cancel on exit if SIGINT is received again
                
    async def run(self, timeout: int = 0):
        signal(SIGINT, self.sigint_handle)
        loop = asyncio.get_running_loop()
        start = loop.time()

        try:
            self.tasks.extend(asyncio.create_task(self.worker()) for _ in range(self.workers))
            task = asyncio.create_task(self.queue.join())
            self.tasks.append(task)
            await asyncio.wait_for(task, timeout = timeout or self.timeout)

        except TimeoutError:
            print(f"Timed out after {loop.time() - start} seconds. {self.queue.qsize()} tasks remaining")

            if self.on_exit == 'complete_priority' and self.priority_tasks:
                print(f'Completing {len(self.priority_tasks)} priority tasks...')
                self.stop = True
                await self.queue.join()

            else:
                self.cancel()

        except asyncio.CancelledError:
            print('Tasks cancelled')

        finally:
            print(f'Exiting queue after {(loop.time() - start)} seconds.'
                  f'{self.queue.qsize()} tasks remaining, {len(self.priority_tasks)} are priority tasks')

        self.cancel()

    def cancel(self):
        cancelled = [task.cancel() for task in self.tasks if not task.done()]
        print(f'Cancelled {len(cancelled)} worker tasks') if cancelled else ...
        self.tasks.clear()
