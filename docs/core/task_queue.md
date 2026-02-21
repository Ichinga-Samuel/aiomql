# task_queue

`aiomql.core.task_queue` — Async priority task queue for managing concurrent execution.

## Overview

Provides `QueueItem` (a callable wrapper) and `TaskQueue` (an `asyncio.PriorityQueue`-based
executor). Supports priority-based scheduling, dynamic worker scaling, timeout handling, and
both **finite** (run until empty) and **infinite** (run until stopped) modes.

## Classes

### `QueueItem`

> Wraps a callable or coroutine for deferred, priority-aware execution.

| Attribute | Type | Description |
|-----------|------|-------------|
| `task` | `Callable \| Coroutine` | The wrapped callable |
| `args` | `tuple` | Positional arguments |
| `kwargs` | `dict` | Keyword arguments |
| `time` | `float` | Creation timestamp (used for ordering) |

#### `__call__()`

Executes the task. Coroutine functions are awaited directly; regular callables are run
in a thread executor. Handles `asyncio.CancelledError`.

Comparison operators (`<`, `<=`, `==`) are based on creation time.

---

### `TaskQueue`

> Priority-based async task queue with worker management.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `size` | `int` | `0` | Max queue size (0 = unlimited) |
| `max_workers` | `int \| None` | `None` | Max concurrent workers |
| `queue_timeout` | `int \| None` | `None` | Overall timeout in seconds |
| `on_exit` | `Literal["cancel","complete_priority"]` | `"complete_priority"` | Shutdown behaviour |
| `mode` | `Literal["finite","infinite"]` | `"finite"` | Queue mode |

#### Task Management

| Method | Description |
|--------|-------------|
| `add_task(task, *args, must_complete=False, priority=3, **kwargs)` | Wraps and enqueues a task |
| `add(*, item, priority=3, must_complete=False, with_new_workers=True)` | Enqueues a `QueueItem` |

#### Worker Management

| Method | Description |
|--------|-------------|
| `add_workers(no_of_workers=None)` | Creates worker coroutines |
| `remove_worker(wid)` | Removes a specific worker |
| `cancel_all_workers()` | Cancels all workers |
| `cancel()` | Cancels workers and stops the queue |

#### Execution

| Method | Description |
|--------|-------------|
| `run(queue_timeout=None)` | Starts workers and processes the queue |
| `worker(wid=None)` | Internal worker coroutine |
| `check_timeout()` | Checks and enforces queue timeout |
