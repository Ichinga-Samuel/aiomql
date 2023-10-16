## <a id="executor"></a> Executor

```python
class Executor
```
Executor class for running multiple strategies on multiple symbols concurrently.
### Attributes:
| Name           | Type                | Description                                    | Default |
|----------------|---------------------|------------------------------------------------|----|
| **executor**   |**ThreadPoolExecutor** | The default thread executor.                   |None|
| **workers**    |**list**             | List of strategies.                            |[]|
| **coroutines** |**dict**             | Dictionary of coroutines and keyword arguments | {} |
| **functions**  |**dict**             | Dictionary of functions and keyword arguments  | {} |

### add\_workers
```python
def add_workers(strategies: Sequence[type(Strategy)])
```
Add multiple strategies at once
#### Arguments:
|Name|Type|Description|
|---|---|---|
|**strategies**|**Sequence[type(Strategy)]**|A sequence of strategies.|

### remove\_workers
```python
def remove_workers(*symbols: Sequence[Symbol])
```
Removes any worker running on a symbol not successfully initialized.
#### Arguments:
|Name|Type|Description|
|---|---|---|
|**symbols**|**Sequence[Symbol]**|A sequence of symbols.|

### add\_worker
```python
def add_worker(strategy: type(Strategy))
```
Add a strategy instance to the list of workers
#### Arguments:
|Name|Type|Description|
|---|---|---|
|**strategy**|**type(Strategy)**|A strategy instance.|

### run
```python
@staticmethod
def run(func: Callable|Coroutine, kwargs: dict)
```
Wrap the input coroutine function with 'asyncio.run' so that it can be executed in a threadpool executor.
#### Arguments:
| Name       | Type       |Description|
|------------|------------|---|
| **func**   | **Callable |Coroutine**|A coroutine function.|
| **kwargs** | **Dict**   |Keyword arguments to pass to the function.|

### trade
```python
def trade(strategy: Strategy)
```
Wrap the input coroutine function trade method of each strategy with 'asyncio.run'.
#### Arguments:
|Name|Type|Description|
|---|---|---|
|**strategy**|**Strategy**|A strategy instance.|

### execute
```python
async def execute(workers: int = 0)
```
Run the strategies with a threadpool executor.
#### Arguments:
|Name|Type|Description|
|---|---|---|
|**workers**|**int**|Number of workers to use in executor pool. Defaults to zero which uses all workers.|
#### Notes:
No matter the number specified, the executor will always use a minimum of 5 workers.
