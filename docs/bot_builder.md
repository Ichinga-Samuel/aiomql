# Bot

## Table of Contents
- [Bot](#bb.Bot)
- [\_\_init\_\_](#bb.__init__)
- [initialize](#bb.initialize)
- [execute](#bb.execute)
- [start](#bb.start)
- [add_coroutine](#bb.add_coroutine)
- [add_function](#bb.add_function)
- [add_strategy](#bb.add_strategy)
- [add_strategies](#bb.add_strategies)
- [add_strategy_all](#bb.add_strategy_all)
- [init_symbols](#bb.init_symbols)
- [init_symbol](#bb.init_symbol]())
- [run_bots](#bb.run_bots)

<a id='bb.Bot'></a>
### Bot
```python
class Bot
```
The bot class. Create a bot instance to run your strategies.
#### Attributes:
| Name       | Type                 | Description                              | Default  |
|------------|----------------------|------------------------------------------|----------|
| `account`  | `Account`            | Account Object.                          | None     |
| `executor` | `ThreadPoolExecutor` | The default thread executor.             | None     |
| `symbols`  | `set[Symbols]`       | A set of symbols for the trading session | set()    |
| `config`   | `Config`             | A Config instance                        | Config() |

<a id='bb.__init__'></a>
### \_\_init\_\_
```python
def __init__()
```
Initializes the Bot class.

<a id='bb.initialize'></a>
### initialize
```python
async def initialize()
```
Prepares the bot by signing in to the trading account and initializing the symbols for the trading session.
#### Raises:
| Exception    | Description                   |
|--------------|-------------------------------|
| `SystemExit` | If sign in was not successful |

<a id='bb.execute'></a>
### execute
```python
def execute()
```
Execute the bot. Use this method to run the bot.

<a id='bb.start'></a>
### start
```python
async def start()
```
Initialize the bot and execute it. Similar to calling **execute** method but is asynchronous.

<a id='bb.add_coroutine'></a>
### add_coroutine
```python
def add_coroutine(coro: Coroutine, **kwargs)
```
Add a coroutine to the executor.
#### Parameters:
| Name     | Type        | Description                                |
|----------|-------------|--------------------------------------------|
| `coro`   | `Coroutine` | A coroutine to run in the executor         |
| `kwargs` | `Any`       | Keyword arguments to pass to the coroutine |

<a id='bb.add_function'></a>
### add_function
```python
def add_function(func: Callable, **kwargs)
```
Add a function to the executor.
#### Parameters:
| Name     | Type       | Description                               |
|----------|------------|-------------------------------------------|
| `func`   | `Callable` | A function to run in the executor         |
| `kwargs` | `Any`      | Keyword arguments to pass to the function |

<a id='bb.add_strategy'></a>
### add_strategy
```python
def add_strategy(strategy: Strategy)
```
Add a strategy to the executor. An added strategy will only run if it's symbol was successfully initialized.
#### Parameters:
| Name       | Type       | Description                       |
|------------|------------|-----------------------------------|
| `strategy` | `Strategy` | A Strategy instance to run on bot |

<a id='bb.add_strategies'></a>
### add_strategies
```python
def add_strategies(strategies: Iterable[Strategy])
```
Add multiple strategies at the same time
#### Parameters:
| Name         | Type                 | Description                       |
|--------------|----------------------|-----------------------------------|
| `strategies` | `Iterable[Strategy]` | An iterable of Strategy instances |

<a id='bb.add_strategy_all'></a>
### add_strategy_all
```python
def add_strategy_all(*, strategy: Type[Strategy], params: dict | None = None)
```
Use this to run a single strategy on all available instruments in the market using the default parameters
i.e. one set of parameters for all trading symbols
#### Parameters:
| Name       | Type             | Description                                 |
|------------|------------------|---------------------------------------------|
| `strategy` | `Type[Strategy]` | A Strategy class                            |
| `params`   | `dict` or `None` | A dictionary of parameters for the strategy |

<a id='bb.init_symbols'></a>
### init_symbols
```python
async def init_symbols()
```
Initialize the symbols for the current trading session. This method is called internally by the bot.

<a id='bb.init_symbol'></a>
### init_symbol
```python
async def init_symbol(symbol: Symbol) -> Symbol
```
Initialize a symbol before the beginning of a trading session.
Removes it from the list of symbols if it was not successfully initialized or not available for the account.
#### Parameters:
| Name     | Type     | Description       |
|----------|----------|-------------------|
| `symbol` | `Symbol` | A Symbol instance |
#### Returns:
| Type     | Description       |
|----------|-------------------|
| `Symbol` | A Symbol instance |

<a id='bb.run_bots'></a>
```python
@classmethod
def run_bots(cls, funcs: dict[Callable: dict] = None, num_workers: int = None):
```
Run multiple functions (scripts, bots) at the same time in parallel with different accounts. 
Running multiple functions is useful when you want to run different strategies on different accounts.
The callable can for example be a bot instance that defines its own Config instance within the function scope.
The dictionary should contain the callable as the key and the dictionary of keyword arguments to pass to the callable as
the value. Use the path attribute of the config instance to specify the terminal path of each account.
The num_workers parameter specifies the number of workers to use. If not specified, the number of workers will be the
number of bots.
#### Parameters
| Name          | Type                   | Description                                                                     |
|---------------|------------------------|---------------------------------------------------------------------------------|
| `funcs`       | `dict[Callable: dict]` | A dictionary of callables and their keyword arguments to run as bots            |
| `num_workers` | `int`                  | The number of workers to use. If not specified, the number of bots will be used |
