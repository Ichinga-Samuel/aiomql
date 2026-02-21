# process_pool

`aiomql.utils.process_pool` — Multi-process parallel execution.

## Overview

Provides a simple wrapper around `ProcessPoolExecutor` for running CPU-bound
functions in parallel across multiple processes.

## Functions

### `process_pool(*functions)`

> Runs multiple callables in parallel using a process pool.

Accepts one or more callables (no arguments) and submits them to a
`ProcessPoolExecutor`. Returns when all processes complete.

**Args:**
- `*functions` (`Callable`) — Callables to execute in parallel.

**Example:**
```python
from aiomql.utils import process_pool

def run_strategy_a():
    ...

def run_strategy_b():
    ...

process_pool(run_strategy_a, run_strategy_b)
```
