# Executor

## Table of Contents
- [Executor](#executor.Executor)
- [__init__](#executor.__init__)
- [add_function](#executor.add_function)
- [add_coroutine](#executor.add_coroutine)
- [run_function](#executor.run_function)
- [execute](#executor.execute)

<a id='executor.Executor'></a>
### Executor
```python
class Executor
```
Executor class for running multiple strategies on multiple symbols concurrently.
#### Attributes:
| Name               | Type                 | Description                                    | Default |
|--------------------|----------------------|------------------------------------------------|---------|
| `executor`         | `ThreadPoolExecutor` | The default thread executor.                   | None    |
| `strategy_runners` | `list[Strategy]`     | List of strategies.                            | []      |
| `coroutines`       | `dict`               | Dictionary of coroutines and keyword arguments | {}      |
| `functions`        | `dict`               | Dictionary of functions and keyword arguments  | {}      |

<a id="executor.__init__"></a>
#### \_\_init\_\_
```python
def __init__(self):
```
Initialize the executor class.

<a id="executor.add_coroutine"></a>
### add_coroutine
```python
def add_coroutine(self,*,coroutine: Callable | Coroutine,kwargs: dict = None,on_separate_thread=False):
```
Submit a coroutine to the executor. The coroutines are run in parallel using *asyncio.gather* except when the
on_spate_thread flag is set to True. In that case, the coroutine is run in a separate thread.

#### Arguments:
| Name                 | Type       | Description                                     |
|----------------------|------------|-------------------------------------------------|
| `coroutine`          | `Callable` | The coroutine                                   |
| `kwargs`             | `Dict`     | The keyword arguments to pass to the coroutine. |
| `on_separate_thread` | `bool`     | If True run the coroutine on a separate thread  |

<a id="executor.add_function"></a>
### add_function
```python
def add_function(self, *, function: Callable, kwargs: dict = None)
```
Submit a function to the executor. Each functions runs on a separate thread.

#### Arguments:
| Name       | Type       | Description                                |
|------------|------------|--------------------------------------------|
| `function` | `Callable` | The function to run in the executor        |
| `kwargs`   | `Dict`     | Keyword arguments to pass to the function. |

<a id="executor.run_function"></a>
### run_function
```python
@staticmethod
def run_function(function: Callable, kwargs: dict)
```
Wrap the input coroutine function with 'asyncio.run' so that it can be executed in a threadpool executor.
#### Arguments:
| Name       | Type       | Description                                |
|------------|------------|--------------------------------------------|
| `function` | `Callable` | Run a function in the executor             |
| `kwargs`   | `Dict`     | Keyword arguments to pass to the function. |

<a id="executor.exit"></a>
### exit
```python
async def exit()
```
Shutdowns the executor. Due to the nature of threadpool executors, shutdown is not usually an immediate process.
This exit function is added as a coroutine function to the bot or backtester during initialization.

<a id="executor.execute"></a>
### execute
```python
def execute(workers: int = 5)
```
Run the strategies with a threadpool executor.
#### Arguments:
| Name      | Type  | Description                                               |
|-----------|-------|-----------------------------------------------------------|
| `workers` | `int` | Number of workers to use in executor pool. Defaults to 5. |

#### Notes:
No matter the number specified, the number of workers will always be greater than equal to the minimum number of
workers required to run all functions, coroutines and strategies added to the executor.
