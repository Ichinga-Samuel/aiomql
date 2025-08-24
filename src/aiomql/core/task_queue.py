import asyncio
import time
import random
from typing import Coroutine, Callable, Literal
from logging import getLogger
from functools import partial

logger = getLogger(__name__)


class QueueItem:
    """A class to represent a task item in the queue.

        Attributes:
            - `task` (Callable | Coroutine): The task to run.

            - `args` (tuple): The arguments to pass to the task

            - `kwargs` (dict): The keyword arguments to pass to the task

            - `must_complete` (bool): A flag to indicate if the task must complete before the queue stops. Default is False.

            - `time` (int): The time the task was added to the queue.
    """
    must_complete: bool

    def __init__(self, task: Callable | Coroutine, /, *args, **kwargs):
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.time = time.time_ns()

    def __hash__(self):
        return self.time

    def __lt__(self, other):
        return self.time < other.time

    def __eq__(self, other):
        return self.time == other.time

    def __le__(self, other):
        return self.time <= other.time

    async def __call__(self):
        try:
            if asyncio.iscoroutinefunction(self.task):
                return await self.task(*self.args, **self.kwargs)

            elif not asyncio.iscoroutinefunction(self.task):
                loop = asyncio.get_running_loop()
                func = partial(self.task, *self.args, **self.kwargs)
                return await loop.run_in_executor(None, func)
        except asyncio.CancelledError:
            logger.debug("Task %s was cancelled", self.task.__name__)
        except Exception as err:
            logger.error("Error %s occurred in %s", err, self.task.__name__)


class TaskQueue:
    start_time: float
    """
    A wrapper around an asyncio Queue
        Attributes:
            queue (Queue): An asyncio Queue
            start_time (float): The time the task was started
            size (int): The size of the queue
            queue_timeout (float): The time to wait for the task to finish
            on_exit (Literal['cancel', 'complete_priority']: Action to take on unfinished tasks
            mode (Literal['finite', 'infinite'] = 'finite'): Run queue in finite or infinite mode
            queue_cancelled (bool): Whether the queue was cancelled
            max_workers (int): The maximum number of concurrent workers
    """

    def __init__(self, *, size: int = 0, max_workers: int = None, queue: asyncio.Queue = None, queue_timeout: int = 0,
                 on_exit: Literal['cancel', 'complete_priority'] = 'complete_priority',
                 mode: Literal['finite', 'infinite'] = 'finite'):
        self.queue = queue or asyncio.PriorityQueue(maxsize=size)
        self.max_workers = max_workers
        self.worker_tasks: dict[int | float, asyncio.Task] = {}
        self.queue_timeout = queue_timeout
        self.stop = False
        self.on_exit = on_exit
        self.mode = mode
        self.queue_cancelled = False

    def add_task(self, task: Callable | Coroutine, *args, must_complete=False, priority=3, **kwargs):
        """
        Args:
            task (Callable | Coroutine): task to execute
            *args (Any): args to pass to the task
            **kwargs (Any): kwargs to pass to the task
            must_complete: ensure task is completed, even when the queue is shut down
            priority (int): priority of the task in priority queue
        """
        try:
            task = QueueItem(task, *args, **kwargs)
            self.add(item=task, priority=priority, must_complete=must_complete)
        except Exception as e:
            logger.error("%s: Error occurred while adding task to queue", e)
            raise e

    def add(self, *, item: QueueItem, priority=3, must_complete=False, with_new_workers=True):
        """Add a task to the queue.
        Args:
            item (QueueItem): The task to add to the queue.
            priority (int): The priority of the task. Default is 3.
            must_complete (bool): A flag to indicate if the task must complete before the queue stops. Default is False.
            with_new_workers (bool): If True, new workers will be added if needed. Default is True.
        """
        try:
            if self.stop:
                return
            item.must_complete = must_complete
            if isinstance(self.queue, asyncio.PriorityQueue):
                item = (priority, item)
            self.queue.put_nowait(item)
            if self.max_workers is None and with_new_workers:
                self.add_workers()
        except asyncio.QueueFull:
            logger.error("Cannot add task: Queue is full")
        except Exception as exe:
            logger.error("Cannot add task: %s", exe)

    async def worker(self, wid: int = None):
        """Worker function to run tasks in the queue.
        Args:
            wid (int): The worker id
        """
        while True:
            try:
                self.check_timeout()

                if self.stop and (self.on_exit == 'cancel') and not self.queue_cancelled:
                    self.cancel()

                if not self.stop and self.mode == 'infinite' and self.queue.qsize() <= 1:
                    self.add_dummy_task()

                if isinstance(self.queue, asyncio.PriorityQueue):
                    _, item = self.queue.get_nowait()

                else:
                    item = self.queue.get_nowait()

                if self.stop is False or (self.on_exit == 'complete_priority' and item.must_complete):
                    await item()
                    self.queue.task_done()
                else:
                    self.queue.task_done()

                if self.max_workers is None:
                    self.add_workers()

            except asyncio.QueueEmpty:
                if self.stop or self.mode == 'finite':
                    self.remove_worker(wid=wid)
                    break

                if self.mode == 'infinite':
                    await asyncio.sleep(1)
                    continue

            except asyncio.CancelledError:
                self.remove_worker(wid=wid)
                break

            except Exception as err:
                logger.error("%s: Error occurred in worker", err)
                self.remove_worker(wid)
                break

    def check_timeout(self):
        """Check for timeout, and stop queue"""
        if self.queue_timeout and (time.perf_counter() - self.start_time) > self.queue_timeout:
            if self.on_exit == 'cancel':
                self.queue_timeout = None
                self.cancel()
            else:
                self.stop = True
                self.queue_timeout = None

    @staticmethod
    async def dummy_task():
        """A dummy task to make sure the queue keeps running when in infinite mode."""
        await asyncio.sleep(1)

    def add_dummy_task(self):
        dt = QueueItem(self.dummy_task)
        self.add(item=dt, with_new_workers=False)

    def remove_worker(self, wid: int):
        """Remove a worker task.
        Args:
            wid (int): The worker id
        """
        try:
            task = self.worker_tasks.pop(wid, None)
            if task is not None:
                task.cancel()
        except Exception as err:
            logger.debug("%s: Error occurred in removing worker %d", err, wid)
        except asyncio.CancelledError as _:
            ...

    def add_workers(self, no_of_workers: int = None):
        """Create workers for running queue tasks.
        Args:
            no_of_workers (int): Number of workers to create
        """
        if no_of_workers is None:
            qs = self.queue.qsize()
            req_workers = qs - len(self.worker_tasks)
            if req_workers >= 1:
                no_of_workers = req_workers + 2
            else:
                return
        ri = lambda: random.randint(999, 999_999_999)  # random id
        ct = lambda ti: asyncio.create_task(self.worker(wid=ti), name=ti)  # create task
        wr = range(no_of_workers)
        [self.worker_tasks.setdefault(wi := ri(), ct(wi)) for _ in wr]

    async def watch(self):
        """If queue timeout is specified, monitors,the queue to shut down at timeout"""
        while True:
            await asyncio.sleep(1)
            if self.queue_timeout and ((time.perf_counter() - self.start_time) > self.queue_timeout):
                if self.on_exit == 'cancel':
                    self.queue_timeout = None
                    break
                else:
                    self.stop = True
                    self.queue_timeout = None
                    return
            else:
                return
        self.cancel()

    async def run(self, queue_timeout: int = None):
        """Run the queue until all tasks are completed or the timeout is reached.
        Args:
            queue_timeout (int): The time to wait for the task to finish
        """
        try:
            self.queue_timeout = queue_timeout or self.queue_timeout
            self.start_time = time.perf_counter()

            if self.queue_timeout:
                asyncio.create_task(self.watch())

            if self.mode == 'infinite' and (len(self.worker_tasks) < 1 or self.queue.qsize() < 1):
                self.add_dummy_task()
                workers = self.max_workers or 1
                self.add_workers(no_of_workers=workers)
            await self.queue.join()

        except asyncio.CancelledError:
            logger.warning("Task Queue Cancelled after %d seconds, %d tasks remaining",
                           time.perf_counter() - self.start_time, self.queue.qsize())

        except Exception as err:
            logger.warning("%s occurred after %d seconds, %d tasks remaining",
                           err, time.perf_counter() - self.start_time, self.queue.qsize())
        finally:
            logger.info("Tasks completed after %d seconds, %d tasks remaining",
                        time.perf_counter() - self.start_time, self.queue.qsize())

    def cancel_all_workers(self):
        """Cancel all workers."""
        try:
            wids = list(self.worker_tasks.keys())
            [self.remove_worker(wid) for wid in wids]
        except Exception as err:
            logger.error("%s: Error occurred in cancelling workers", err)

    def cancel(self):
        """Cancel all workers and stop queue."""
        try:
            self.stop = True
            self.queue.shutdown(immediate=True)
            self.queue_cancelled = True
            self.cancel_all_workers()
        except asyncio.CancelledError as _:
            ...
        except Exception as err:
            logger.error("%s: Error occurred in cancelling queue", err)

