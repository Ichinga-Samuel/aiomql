"""Task queue module for managing asynchronous task execution.

This module provides classes for creating and managing asynchronous task queues.
It supports priority-based task scheduling, worker management, and both finite
and infinite queue modes.

Classes:
    QueueItem: Represents a task item in the queue.
    TaskQueue: A wrapper around asyncio Queue for managing task execution.

Example:
    Basic usage::

        from aiomql.core.task_queue import TaskQueue

        async def my_task(x):
            print(f"Processing {x}")

        queue = TaskQueue()
        queue.add_task(my_task, 42, priority=1)
        await queue.run()
"""

import asyncio
import time
import random
from typing import Coroutine, Callable, Literal
from logging import getLogger
from functools import partial

logger = getLogger(__name__)

class QueueItem:
    """Represents a task item in the queue.

    Wraps a callable or coroutine with its arguments for deferred execution.
    Supports comparison operations for priority queue ordering.

    Attributes:
        task (Callable | Coroutine): The task to execute.
        args (tuple): Positional arguments for the task.
        kwargs (dict): Keyword arguments for the task.
        time (int): Timestamp when the task was created (nanoseconds).
        must_complete (bool): If True, task must complete even when queue stops.

    Example:
        >>> async def my_task(x): return x * 2
        >>> item = QueueItem(my_task, 5)
        >>> await item()  # Returns 10
    """

    must_complete: bool

    def __init__(self, task: Callable | Coroutine, /, *args, **kwargs):
        """Initializes a QueueItem.

        Args:
            task: The callable or coroutine to execute.
            *args: Positional arguments to pass to the task.
            **kwargs: Keyword arguments to pass to the task.
        """
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.time = time.time_ns()

    def __hash__(self):
        """Returns the hash of the item based on creation time.

        Returns:
            int: The creation timestamp as hash.
        """
        return self.time

    def __lt__(self, other):
        """Compares items by creation time (less than).

        Args:
            other: Another QueueItem to compare.

        Returns:
            bool: True if this item was created before other.
        """
        return self.time < other.time

    def __eq__(self, other):
        """Compares items by creation time (equality).

        Args:
            other: Another QueueItem to compare.

        Returns:
            bool: True if items were created at the same time.
        """
        return self.time == other.time

    def __le__(self, other):
        """Compares items by creation time (less than or equal).

        Args:
            other: Another QueueItem to compare.

        Returns:
            bool: True if this item was created before or at same time.
        """
        return self.time <= other.time

    async def __call__(self):
        """Executes the wrapped task.

        Handles both coroutine functions and regular callables.
        Regular callables are run in a thread executor.

        Returns:
            The result of the task execution.

        Raises:
            asyncio.CancelledError: If the task was cancelled.
            Exception: Any exception raised by the task.
        """
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
    """A wrapper around asyncio Queue for managing asynchronous task execution.

    Provides priority-based task scheduling, worker management, timeout handling,
    and support for both finite and infinite queue modes.

    Attributes:
        queue (asyncio.Queue): The underlying asyncio queue.
        start_time (float): Timestamp when the queue started running.
        max_workers (int | None): Maximum concurrent workers. None for dynamic.
        worker_tasks (dict): Dictionary mapping worker IDs to their tasks.
        queue_timeout (int): Timeout in seconds for queue execution.
        stop (bool): Flag to signal queue shutdown.
        on_exit (str): Action on exit - 'cancel' or 'complete_priority'.
        mode (str): Queue mode - 'finite' or 'infinite'.
        queue_cancelled (bool): Whether the queue was cancelled.

    Example:
        >>> queue = TaskQueue(mode='finite')
        >>> queue.add_task(my_async_func, arg1, priority=1)
        >>> await queue.run(queue_timeout=60)
    """

    start_time: float

    def __init__(self, *, size: int = 0, max_workers: int = None, queue: asyncio.Queue = None, queue_timeout: int = 0,
                 on_exit: Literal['cancel', 'complete_priority'] = 'complete_priority',
                 mode: Literal['finite', 'infinite'] = 'finite'):
        """Initializes the TaskQueue.

        Args:
            size: Maximum queue size. 0 for unlimited. Defaults to 0.
            max_workers: Maximum concurrent workers. None for dynamic scaling.
            queue: Custom asyncio queue to use. Defaults to PriorityQueue.
            queue_timeout: Timeout in seconds. 0 for no timeout.
            on_exit: Action for unfinished tasks on exit.
                'cancel': Cancel all remaining tasks.
                'complete_priority': Complete tasks marked as must_complete.
            mode: Queue operation mode.
                'finite': Stop when queue is empty.
                'infinite': Keep running until explicitly stopped.
        """
        self.queue = queue or asyncio.PriorityQueue(maxsize=size)
        self.max_workers = max_workers
        self.worker_tasks: dict[int | float, asyncio.Task] = {}
        self.queue_timeout = queue_timeout
        self.stop = False
        self.on_exit = on_exit
        self.mode = mode
        self.queue_cancelled = False

    def add_task(self, task: Callable | Coroutine, *args, must_complete=False, priority=3, **kwargs):
        """Adds a task to the queue.

        Convenience method that wraps the task in a QueueItem and adds it.

        Args:
            task: The callable or coroutine to execute.
            *args: Positional arguments for the task.
            must_complete: If True, task completes even during shutdown.
            priority: Task priority (lower = higher priority). Defaults to 3.
            **kwargs: Keyword arguments for the task.

        Raises:
            Exception: If an error occurs while adding the task.
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
        """Worker coroutine that processes tasks from the queue.

        Continuously pulls and executes tasks until the queue is empty
        (finite mode) or stopped (infinite mode).

        Args:
            wid: Unique worker identifier for tracking and removal.
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
        """Checks if queue timeout has been exceeded and stops if needed."""
        if self.queue_timeout and (time.perf_counter() - self.start_time) > self.queue_timeout:
            if self.on_exit == 'cancel':
                self.queue_timeout = None
                self.cancel()
            else:
                self.stop = True
                self.queue_timeout = None

    @staticmethod
    async def dummy_task():
        """A placeholder task to keep infinite mode queues active."""
        await asyncio.sleep(1)

    def add_dummy_task(self):
        """Adds a dummy task to prevent infinite mode queue from becoming empty."""
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
        """Monitors the queue for timeout and triggers shutdown if exceeded."""
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
        """Runs the queue until all tasks complete or timeout is reached.

        Args:
            queue_timeout: Optional timeout in seconds. Overrides init value.
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

