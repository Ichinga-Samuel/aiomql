# Executor

## Table of Contents
- [Executor](#executor.Executor)
- [__init__](#executor.__init__)
- [add_workers](#executor.add_workers)
- [remove_workers](#executor.remove_workers)
- [add_worker](#executor.add_worker)
- [run](#executor.run)
- [trade](#executor.trade)
- [execute](#executor.execute)

<a id='executor.Executor'></a>
### Executor
```python
class Executor
```
Executor class for running multiple strategies on multiple symbols concurrently.
#### Attributes:
| Name         | Type                 | Description                                    | Default |
|--------------|----------------------|------------------------------------------------|---------|
| `executor`   | `ThreadPoolExecutor` | The default thread executor.                   | None    |
| `workers`    | `list`               | List of strategies.                            | []      |
| `coroutines` | `dict`               | Dictionary of coroutines and keyword arguments | {}      |
| `functions`  | `dict`               | Dictionary of functions and keyword arguments  | {}      |

<a id="executor.__init__"></a>
#### \_\_init\_\_
```python
def __init__(self):
```
Initialize the executor class.

<a id="executor.add_workers"></a>
### add\_workers
```python
def add_workers(strategies: Sequence[type(Strategy)])
```
Add multiple strategies at once
#### Arguments:
| Name         | Type                       | Description               |
|--------------|----------------------------|---------------------------|
| `strategies` | `Sequence[type(Strategy)]` | A sequence of strategies. |

<a id="executor.remove_workers"></a>
### remove\_workers
```python
def remove_workers(*symbols: Sequence[Symbol])
```
Removes any worker running on a symbol not successfully initialized.
#### Arguments:
| Name      | Type               | Description            |
|-----------|--------------------|------------------------|
| `symbols` | `Sequence[Symbol]` | A sequence of symbols. |

<a id="executor.add_worker"></a>
### add\_worker
```python
def add_worker(strategy: type(Strategy))
```
Add a strategy instance to the list of workers
#### Arguments:
| Name       | Type             | Description          |
|------------|------------------|----------------------|
| `strategy` | `type(Strategy)` | A strategy instance. |

<a id="executor.run"></a>
### run
```python
@staticmethod
def run(func: Callable|Coroutine, kwargs: dict)
```
Wrap the input coroutine function with 'asyncio.run' so that it can be executed in a threadpool executor.
#### Arguments:
| Name     | Type      | Description                                |
|----------|-----------|--------------------------------------------|
| `func`   | `Callable | Coroutine`                                 |A coroutine function.|
| `kwargs` | `Dict`    | Keyword arguments to pass to the function. |

<a id="executor.trade"></a>
### trade
```python
def trade(strategy: Strategy)
```
Wrap coroutine trade method of each strategy with 'asyncio.run'.
#### Arguments:
| Name       | Type       | Description          |
|------------|------------|----------------------|
| `strategy` | `Strategy` | A strategy instance. |

<a id="executor.execute"></a>
### execute
```python
async def execute(workers: int = 5)
```
Run the strategies with a threadpool executor.
#### Arguments:
| Name      | Type  | Description                                               |
|-----------|-------|-----------------------------------------------------------|
| `workers` | `int` | Number of workers to use in executor pool. Defaults to 5. |
#### Notes:
No matter the number specified, the executor will always use a minimum of 5 workers.
