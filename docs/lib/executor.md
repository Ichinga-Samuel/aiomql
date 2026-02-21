# executor

`aiomql.lib.executor` — Strategy and task executor.

## Overview

The `Executor` manages the lifecycle of trading strategies and background tasks. It collects
functions, coroutines, and `Strategy` instances, then runs them via a `TaskQueue`.

## Classes

### `Executor`

> Executes strategies and tasks using a `TaskQueue`.

| Attribute | Type | Description |
|-----------|------|-------------|
| `config` | `Config` | Global configuration |
| `task_queue` | `TaskQueue` | The underlying task queue |

#### Adding Tasks

| Method | Description |
|--------|-------------|
| `add_function(func, *args, **kwargs)` | Registers a regular callable |
| `add_coroutine(coro, *args, **kwargs)` | Registers an async coroutine |
| `add_strategy(strategy)` | Registers a `Strategy` instance |

#### Execution

| Method | Description |
|--------|-------------|
| `execute()` | Starts all registered tasks and strategies via the queue |
| `run_coroutine_task(coro, *args, **kwargs)` | Runs a single coroutine task |

#### Shutdown

| Method | Description |
|--------|-------------|
| `sigint_handle(sig, frame)` | Handles SIGINT for graceful shutdown |
| `exit()` | Sets the shutdown flag and stops the queue |
