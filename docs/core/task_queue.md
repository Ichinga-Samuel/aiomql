# TaskQueue and QueueItem

## Table of Contents
- [QueueItem](#queue_item)
  - [run](#run)

- [TaskQueue](#task_queue)
  - [TaskQueue.add](#task_queue.add)
  - [TaskQueue.add_task](#task_queue.add_task)
  - [TaskQueue.worker](#task_queue.worker)
  - [TaskQueue.start](#task_queue.start)


<a id="queue_item"></a>
### QueueItem
```python
class QueueItem:
    def __init__(self, task: Callable | Awaitable, *args, **kwargs):
```
A task to be executed by the `TaskQueue`. The task can be a callable or an awaitable. The task is wrapped as a
`QueueItem` object, which is then added to the `TaskQueue` for execution. The arguments and keyword arguments are
passed to the task when it is executed. All parameters are created as attributes of the `QueueItem` object.

#### Parameters:
| Name     | Type                      | Description                                                       |
|----------|---------------------------|-------------------------------------------------------------------|
| `task`   | `Callable` \| `Awaitable` | A callable or awaitable task to be executed by the `TaskQueue`    |
| `args`   | `Any`                     | Positional arguments to be passed to the task when it is executed |
| `kwargs` | `Any`                     | Keyword arguments to be passed to the task when it is executed    |

<a id="run"></a>
### run
```python
def run(self) -> Any
```
Run the task. If the task is a coroutine, it is awaited. If the task is a callable, it is called.


### TaskQueue
```python
class TaskQueue:
    def __init__(self):
```
#### Attributes:
| Name          | Type            | Description                                                                     |
|---------------|-----------------|---------------------------------------------------------------------------------|
| `queue`       | `asyncio.Queue` | An asyncio.Queue queue of `QueueItem` objects to be executed by the `TaskQueue` |


<a id="task_queue.add"></a>
### add
```python
def add(self, item: QueueItem, *args, **kwargs) -> None
```
Add a `QueueItem` to the `TaskQueue` queue.

#### Parameters:
| Name   | Type        | Description                            |
|--------|-------------|----------------------------------------|
| `item` | `QueueItem` | A `QueueItem` to be added to the queue |


<a id="task_queue.add_task"></a>
### add_task
```python
def add_task(self, task: Callable | Awaitable, *args, **kwargs) -> None
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
async def worker(self) -> None
```
A worker that processes the `QueueItem` objects in the `TaskQueue` queue. The worker runs indefinitely, processing
`QueueItem` objects as they are added to the queue.

<a id="task_queue.start"></a>
### start
```python
def start(self) -> None
```
Start the worker that processes the `QueueItem` objects in the `TaskQueue` queue.
