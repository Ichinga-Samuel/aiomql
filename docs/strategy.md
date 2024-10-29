## <a id="strategy"></a> Strategy
The base class for creating strategies.
```python
class Strategy(ABC)
```
The base class for creating strategies.
### Attributes:
|Name|Type|Description|Default|
|---|---|---|---|
|**name**|**str**|A name for the strategy.|None|
|**account**|**Account**|Account instance.|None|
|**mt5**|**MetaTrader**|MetaTrader instance.|None|
|**config**|**Config**|Config instance.|None|
|**symbol**|**Symbol**|The Financial Instrument as a Symbol Object|None|
|**parameters**|**Dict**|A dictionary of parameters for the strategy.|None|

### Notes:
Define the name of a strategy as a class attribute. If not provided, the class name will be used as the name.

### \_\_init\_\_
```python
def __init__(*, symbol: Symbol, params: dict = None, sessions: Sessions)
```
Initiate the parameters dict and add name and symbol fields. Use class name as strategy name if name is not provided.
### Arguments:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**symbol**| **Symbol** | The Financial instrument | None |
|**params**| **Dict** | Trading strategy parameters | None |
|**sessions**| **Sessions** | Trading sessions | None |

### sleep
```python
@staticmethod
async def sleep(secs: float)
```
Sleep for the needed amount of seconds in between requests to the terminal.
computes the accurate amount of time needed to sleep ensuring that the next request is made at the start of
a new bar and making cooperative multitasking possible.

### Arguments:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**secs**| **float** | The time in seconds. Usually the timeframe you are trading on. | None |

### trade
```python
@abstractmethod
async def trade()
```
Place trades using this method. This is the main method of the strategy.
It will be called by the strategy runner.
