## <a id="bot_builder"></a> Bot Builder

```python
class Bot()
```
The bot class. Create a bot instance to run your strategies.
### Attributes:
|Name|Type|Description|Default|
|---|---|---|---|
|**account**|**Account**|Account Object.|None|
|**executor**|**ThreadPoolExecutor**|The default thread executor.|None|
|**symbols**|**set[Symbols]**|A set of symbols for the trading session|set()|

### initialize
```python
async def initialize()
```
Prepares the bot by signing in to the trading account and initializing the symbols for the trading session.
#### Raises:
|Exception|Description|
|---|---|
|**SystemExit**|If sign in was not successful|

### execute
```python
def execute()
```
Execute the bot. This method calls start internally. To enable you run your bot outside of an async function.
### start
```python
async def start()
```
Starts the bot by calling the initialize method and running the strategies in the executor.

### add_coroutine
```python
def add_coroutine(coro: Coroutine, **kwargs)
```
#### Arguments:
|Name|Type|Description|
|---|---|---|
|**coro**|**Coroutine**|A coroutine to run in the executor|

### add_function
```python
def add_coroutine(func: Callable, **kwargs)
```
#### Arguments:
| Name     | Type         | Description                       |
|----------|--------------|-----------------------------------|
| **func** | **Callable** | A function to run in the executor |

### add_strategy
```python
def add_strategy(strategy: Strategy)
```
Add a strategy to the executor. An added strategy will only run if it's symbol was successfully initialized.
#### Arguments:
|Name|Type|Description|
|---|---|---|
|**strategy**|**Strategy**|A Strategy instance to run on bot|

### add_strategies
```python
def add_strategies(strategies: Iterable[Strategy])
```
Add multiple strategies at the same time
#### Arguments:
|Name|Type|Description|
|---|---|---|
|**strategies**|**Iterable[Strategy]**|An iterable of Strategy instances|

### add_strategy_all
```python
def add_strategy_all(*, strategy: Type[Strategy], params: dict | None = None)
```
Use this to run a single strategy on all available instruments in the market using the default parameters
i.e one set of parameters for all trading symbols
#### Arguments
|Name|Type|Description|
|---|---|---|
|**strategy**|**Type[Strategy]**|A Strategy class|
|**params**|**dict** or **None**|A dictionary of parameters for the strategy|

### init_symbols
```python
async def init_symbols()
```
Initialize the symbols for the current trading session. This method is called internally by the bot.

### init_symbol
```python
async def init_symbol(symbol: Symbol) -> Symbol
```
Initialize a symbol before the beginning of a trading session.
Removes it from the list of symbols if it was not successfully initialized or not available
for the account.
#### Arguments:
|Name|Type|Description|
|---|---|---|
|**symbol**|**Symbol**|A Symbol instance|
#### Returns:
|Type|Description|
|---|---|
|**Symbol**|A Symbol instance|
