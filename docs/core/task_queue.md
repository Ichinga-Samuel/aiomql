# TaskQueue and QueueItem

## Table of Contents
- [QueueItem](#queue_item.queue_item)
  - [\__init\__](#queue_item.__init__)
  - [run](#queue_item.run)

- [TaskQueue](#task_queue.task_queue)
  - [\__init\__](#task_queue.__init__)
  - [add](#task_queue.add)
  - [add_task](#task_queue.add_task)
  - [worker](#task_queue.worker)
  - [run](#task_queue.run)
  - [stop_queue](#task_queue.stop_queue)
  - [clean_up](#task_queue.clean_up)
  - [cancel](#task_queue.cancel)


<a id="queue_item.queue_item"></a>
### QueueItem
```python
class QueueItem
```
A task to be executed by the `TaskQueue`. The task can be any coroutine callable. The task is wrapped as a
`QueueItem` object, which is then added to the `TaskQueue` for execution. The arguments and keyword arguments are
passed to the task when it is executed. 

#### Attributes:
| Name            | Type                      | Description                                                           |
|-----------------|---------------------------|-----------------------------------------------------------------------|
| `task_item`     | `Callable` \| `Coroutine` | A coroutine function to be executed by the `TaskQueue`                |
| `args`          | `tuple[Any, ...]`         | Positional arguments to be passed to the task_item                    |
| `kwargs`        | `dict[str, Any]`          | Keyword arguments to be passed to the task_item                       |
| `must_complete` | `bool`                    | If True, the item must be completed even if the queue is stopped.     |
| `time`          | `float`                   | The time the item was added to the queue. For sorting priority queues |


<a id="queue_item.__init__"></a>
### \__init\__
```python
def __init__(self, task: Callable | Coroutine, *args, **kwargs):
```

#### Parameters:
| Name     | Type                      | Description                                                       |
|----------|---------------------------|-------------------------------------------------------------------|
| `task`   | `Callable` \| `Coroutine` | A coroutine to be executed by the `TaskQueue`                     |
| `args`   | `Any`                     | Positional arguments to be passed to the task when it is executed |
| `kwargs` | `Any`                     | Keyword arguments to be passed to the task when it is executed    |


<a id="queue.run"></a>
### run
```python
def run(self)
```
Run the task. If the task is a coroutine, it is awaited. If the task is a callable, it is called.


<a id="task_queue.task_queue"></a>
### TaskQueue
```python
class TaskQueue
```
A perpetual task queue that processes `QueueItem` objects. The `TaskQueue` runs indefinitely, processing `QueueItem`
objects as they are added to the queue. The `TaskQueue` is a wrapper around an `asyncio.Queue` that can be passed in as
an argument or defaults to an `asyncio.PriorityQueue`. It is added to the bot executor of the `Bot` class on a
separate thread.

#### Attributes:
| Name             | Type                                     | Description                                                                                                                                                                                                            |
|------------------|------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `queue`          | `asyncio.Queue`                          | An `asyncio.Queue` queue of `QueueItem` objects to be executed by the `TaskQueue`. If not provided during instantiation, an `asyncio.PriorityQueue` is used                                                            |
| `stop`           | `bool`                                   | A flag to stop the task_queue instance.                                                                                                                                                                                |
| `workers`        | `int`                                    | The number of workers to process the queue items. Defaults to 10.                                                                                                                                                      |
| `timeout`        | `int`                                    | The maximum time to wait for the queue to complete. Default is None. If timeout is provided the queue is joined using `asyncio.wait_for` with the timeout                                                              |
| `on_exit`        | `Literal["cancel", "complete_priority"]` | The action to take when the queue is stopped. If "cancel" the queue is cancelled and the remaining items are not processed. If "complete_priority" the queue is completed with the priority items. Default is "cancel" |
| `mode`           | `Literal["finite", "infinite"]`          | The mode of the queue. If `finite` the queue will stop when all tasks are completed. If `infinite` the queue will continue to run until stopped.                                                                       |
| `worker_timeout` | `int`                                    | The time to wait for a task to be added to the queue before stopping the worker or adding a dummy sleep task to the queue.                                                                                             |
| `tasks`          | `List[Task]`                             | A list of the worker tasks running concurrently, including the main task that joins the queue.                                                                                                                         |
| `priority_tasks` | `set[QueueItem]`                         | A set to store the `QueueItems` that must complete before the queue stops                                                                                                                                              |


<a id="task_queue.__init__"></a>
### \__init\__
```python
def __init__(self, queue: asyncio.Queue = None, workers: int = 10, timeout: int = None, size: int = None,
             on_exit: Literal["cancel", "complete_priority"] = "cancel",
             mode: Literal["finite", "infinite"] = "infinite", worker_timeout: int = 60)
```
Create a new `TaskQueue` instance.

#### Parameters:
| Name             | Type                                     | Description                                                                                                                | Default             |
|------------------|------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|---------------------|
| `queue`          | `asyncio.Queue`                          | An `asyncio.Queue` queue instance                                                                                          | None                |
| `workers`        | `int`                                    | The number of workers to process the queue items.                                                                          | 10                  |
| `timeout`        | `int`                                    | The maximum time to wait for the queue to complete.                                                                        | None                |
| `size`           | `int`                                    | The maximum size of the queue.                                                                                             | None                |
| `on_exit`        | `Literal["cancel", "complete_priority"]` | The action to take when the queue is stopped.                                                                              | "complete_priority" |
| `mode`           | `Literal["finite", "infinite"]`          | The mode of the queue.                                                                                                     | "infinite"          |
| `worker_timeout` | `int`                                    | The time to wait for a task to be added to the queue before stopping the worker or adding a dummy sleep task to the queue. | 60                  |


<a id="task_queue.add"></a>
### add
```python
def add(*, item: QueueItem, priority: int = 3, must_complete_false: bool = False) -> None
```
Add a `QueueItem` to the `TaskQueue` queue.

#### Parameters:
| Name                  | Type        | Description                                                                            |
|-----------------------|-------------|----------------------------------------------------------------------------------------|
| `item`                | `QueueItem` | A `QueueItem` to be added to the queue                                                 |
| `priority`            | `int`       | The priority of the item. The lower the number, the higher the priority. Default is 3. |
| `must_complete_false` | `bool`      | If True, the item must be completed even if the queue is stopped. Default is False.    |


<a id="task_queue.add_task"></a>
### add_task
```python
def add_task(self, task: Callable | Awaitable, *args, **kwargs)
```
Create a QueueItem from the task and add it to the `TaskQueue` queue. The task can be a callable or an awaitable.
The arguments and keyword arguments are passed to the QueueItem. 

#### Parameters:
| Name     | Type                      | Description                                                       |
|----------|---------------------------|-------------------------------------------------------------------|
| `task`   | `Callable` \| `Awaitable` | A callable or awaitable task to be executed by the `TaskQueue`    |
| `args`   | `Any`                     | Positional arguments to be passed to the task when it is executed |
| `kwargs` | `Any`                     | Keyword arguments to be passed to the task when it is executed    |

<a id="task_queue.worker"></a>
### worker
```python
async def worker()
```
A worker that processes the `QueueItem` objects in the `TaskQueue` queue.


<a id="task_queue.run"></a>
### run
```python
async def run(timeout: int = None)
```
Start the `TaskQueue` instance. If a timeout is provided, the queue is joined using `asyncio.wait_for` with the timeout.
This is the main entry point for the `TaskQueue` instance. It is added to the bot executor of the `Bot` class on a
separate thread.

#### Parameters:
| Name      | Type  | Description                                                          |
|-----------|-------|----------------------------------------------------------------------|
| `timeout` | `int` | The maximum time to wait for the queue to complete. Default is None. |


<a id="task_queue.stop_queue"></a>
### stop_queue
```python
def stop_queue()
```
Stop the `TaskQueue` instance. This sets the `stop` attribute to True, changes the `on_exit` attribute to "cancel",
and cancels the queue.


<a id="task_queue.clean_up"></a>
### clean_up
```python
async def clean_up()
```
Clean up the `TaskQueue` instance. This is called when the queue is stopped. It cancels the queue and processes the
remaining priority items based on the `on_exit` attribute.


<a id="task_queue.cancel"></a>
### cancel
```python
def cancel()
```
Cancel all remaining tasks.
