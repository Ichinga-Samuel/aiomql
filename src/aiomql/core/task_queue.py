import asyncio
import time
from typing import Coroutine, Callable, Literal
from logging import getLogger
from signal import SIGINT, signal

logger = getLogger(__name__)


class QueueItem:
    """A class to represent a task item in the queue.

    Attributes:
        - `task_item` (Callable | Coroutine): The task to run.

        - `args` (tuple): The arguments to pass to the task

        - `kwargs` (dict): The keyword arguments to pass to the task

        - `must_complete` (bool): A flag to indicate if the task must complete before the queue stops. Default is False.

        - `time` (int): The time the task was added to the queue.
    """

    def __init__(self, task_item: Callable | Coroutine, *args, **kwargs):
        self.task_item = task_item
        self.args = args
        self.kwargs = kwargs
        self.must_complete = False
        self.time = time.monotonic_ns()

    def __hash__(self):
        return id(self)

    def __lt__(self, other):
        return self.time < other.time

    async def run(self):
        try:
            if asyncio.iscoroutinefunction(self.task_item):
                await self.task_item(*self.args, **self.kwargs)
            else:
                await asyncio.to_thread(self.task_item, *self.args, **self.kwargs)
        except Exception as err:
            logger.error("Error %s occurred in %s with args %s and %s",
                         err, self.task_item.__name__, self.args, self.kwargs)


class TaskQueue:
    queue_task: asyncio.Task

    def __init__(self, size: int = 0, workers: int = 500, timeout: int = None, queue: asyncio.Queue = None,
                 on_exit: Literal['cancel', 'complete_priority'] = 'complete_priority',
                 mode: Literal['finite', 'infinite'] = 'finite', worker_timeout: int = 60):

        self.queue = queue or asyncio.PriorityQueue(maxsize=size)
        self.workers = workers
        self.worker_tasks = []
        self.priority_tasks = set()  # tasks that must complete
        self.timeout = timeout
        self.stop = False
        self.on_exit = on_exit
        self.mode = mode
        self.worker_timeout = worker_timeout
        signal(SIGINT, self.sigint_handle)

    def add(self, *, item: QueueItem, priority=3, must_complete=False):
        """Add a task to the queue.

        Args:
            item (QueueItem): The task to add to the queue.
            priority (int): The priority of the task. Default is 3.
            must_complete (bool): A flag to indicate if the task must complete before the queue stops. Default is False.
        """
        try:
            if self.stop:
                return
            item.must_complete = must_complete
            self.priority_tasks.add(item) if item.must_complete else ...
            if isinstance(self.queue, asyncio.PriorityQueue):
                item = (priority, item)
            self.queue.put_nowait(item)
        except asyncio.QueueFull:
            logger.error("Queue is full")

    async def worker(self):
        """Worker function to run tasks in the queue."""
        while True:
            try:
                if isinstance(self.queue, asyncio.PriorityQueue):
                    _, item = self.queue.get_nowait()
                else:
                    item = self.queue.get_nowait()

                if self.stop is False or item.must_complete:
                    await item.run()

                self.queue.task_done()
                self.priority_tasks.discard(item)

                if self.stop and (self.on_exit == 'cancel' or len(self.priority_tasks) == 0):
                    self.cancel()
                    break

            except asyncio.QueueEmpty:
                if self.stop:
                    break

                if self.mode == 'finite':
                    break

                # add dummy task to prevent worker from exiting
                sleep = QueueItem(asyncio.sleep, 1)
                self.add(item=sleep)
                await asyncio.sleep(self.worker_timeout)
            except Exception as err:
                logger.error("%s: Error occurred in worker", err)
                break

    async def run(self, timeout: int = 0):
        """Run the queue until all tasks are completed or the timeout is reached.

        Args:
            timeout (int): The maximum time to wait for the queue to complete. Default is 0. If timeout is provided
                the queue is joined using `asyncio.wait_for` with the timeout. If the timeout is reached, the queue is
                stopped and the remaining tasks are handled based on the `on_exit` attribute.
                If the timeout is 0, the queue will run until all tasks are completed or the queue is stopped.
        """
        start = time.perf_counter()
        try:
            self.worker_tasks.extend([asyncio.create_task(self.worker()) for _ in range(self.workers)])
            timeout = timeout or self.timeout
            self.queue_task = asyncio.create_task(self.queue.join())

            if timeout:
                await asyncio.wait_for(self.queue_task, timeout=timeout)
                self.stop = True
            else:
                await self.queue_task

        except TimeoutError:
            logger.warning("Timed out after %d seconds, %d tasks remaining",
                           time.perf_counter() - start, self.queue.qsize())
            self.stop = True

        except asyncio.CancelledError:
            self.stop = True

        except Exception as err:
            logger.warning("%s: An error occurred in %s.run", err, self.__class__.__name__)
            self.stop = True

        finally:
            await self.clean_up()

    async def clean_up(self):
        """Clean up tasks in the queue, completing priority tasks if `on_exit` is `complete_priority`"""
        try:
            logger.info('cleaning up tasks...')

            if self.on_exit == 'complete_priority' and (pt := len(self.priority_tasks)) > 0:
                logger.info('Completing %d priority tasks...', pt)
                self.queue_task = asyncio.create_task(self.queue.join())
                await self.queue_task
            logger.info('Cleaning up tasks done...')
            self.cancel()

        except asyncio.CancelledError:
            self.stop = True

        except Exception as err:
            logger.error(f"%s: Error occurred in %s", err, self.__class__.__name__)

        finally:
            self.cancel()

    def cancel(self):
        """Cancel all tasks in the queue"""
        try:

           self.queue_task.cancel()

        except asyncio.CancelledError:
            ...

        except Exception as err:
            logger.error("%s: occurred in canceling all tasks", err)

    def sigint_handle(self, sig, frame):
        logger.info('SIGINT received, cleaning up...')
        self.stop = True
        self.cancel()


TaskQueue.__doc__ = """TaskQueue is a class that allows you to queue tasks and run them concurrently with a specified number of workers.

    Attributes:
        - `workers` (int): The number of workers to run concurrently. Default is 10.

        - `timeout` (int): The maximum time to wait for the queue to complete. Default is None. If timeout is provided
            the queue is joined using `asyncio.wait_for` with the timeout.

        - `queue` (asyncio.Queue): The queue to store the tasks. Default is `asyncio.PriorityQueue` with no size limit.

        - `on_exit` (Literal["cancel", "complete_priority"]): The action to take when the queue is stopped.

        - `mode` (Literal["finite", "infinite"]): The mode of the queue. If `finite` the queue will stop when all tasks
            are completed. If `infinite` the queue will continue to run until stopped.

        - `worker_timeout` (int): The time to wait for a task to be added to the queue before stopping the worker or
            adding a dummy sleep task to the queue.

        - `stop` (bool): A flag to stop the queue instance.

        - `tasks` (list): A list of the worker tasks running concurrently, including the main task that joins the queue.

        - `priority_tasks` (set): A set to store the QueueItems that must complete before the queue stops.
    """
