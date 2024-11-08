# Bot

## Table of Contents
- [Bot](#bot.Bot)
- [\_\_init\_\_](#bot.init)
- [initialize](#bot.initialize)
- [execute](#bot.execute)
- [start](#bot.start)
- [add_coroutine](#bot.add_coroutine)
- [add_function](#bot.add_function)
- [add_strategy](#bot.add_strategy)
- [add_strategies](#bot.add_strategies)
- [add_strategy_all](#bot.add_strategy_all)
- [process_pool](#bot.run_bots)

<a id='bot.Bot'></a>
### Bot
```python
class Bot
```
"""The bot class. Create a bot instance to run strategies.

#### Attributes.
| Name         | Type               | Description                                | Default      |
|--------------|--------------------|--------------------------------------------|--------------|
| `account`    | `Account`          | Account Object.                            | None         |
| `executor`   | `Executor`         | The executor.                              | None         |
| `strategies` | `List[Strategies]` | A list of strategies to initialize and run | list()       |
| `mt5`        | `MetaTrader`       | `A MetaTrader Instance`                    | MetaTrader() |
| `config`     | `Config`           | A Config instance                          | Config()     |

<a id='bot.init'></a>
### \_\_init\_\_
```python
def __init__()
```
Initializes the Bot class.

<a id='bot.initialize'></a>
### initialize
```python
async def initialize(self)
```
Prepares the bot by signing in to the trading account and initializing the symbols for each strategy.
Only strategies with successfully initialized symbols will be added to the executor. Starts the global task queue.

Note: *initialize_sync* is a synchronous version of this method.

#### Raises:
| Exception    | Description                   |
|--------------|-------------------------------|
| `SystemExit` | If sign in was not successful |



<a id='bot.execute'></a>
### execute
```python
def execute()
```
Executes the bot. Use this method to run the bot in a synchronous manner.
This method is blocking and will not return until the bot is done running.

<a id='bot.start'></a>
### start
```python
async def start()
```
Initialize the bot and execute it. Similar to calling **execute** method but is asynchronous.

<a id='bot.add_coroutine'></a>
### add_coroutine
```python
def add_coroutine(self, coroutine: Coroutine, on_separate_thread=False, **kwargs)
```
Add a coroutine to the executor. By default, all coroutines added to the executor run on this same thread,
using _asyncio.gather_, but if _on_separate_thread_ is true then the coroutine is given it's own thread.

#### Parameters:
| Name                 | Type        | Description                                        |
|----------------------|-------------|----------------------------------------------------|
| `coroutine`          | `Coroutine` | A coroutine to run in the executor                 |
| `on_separate_thread` | `bool`      | Run coroutine on a separate thread in the executor |
| `kwargs`             | `Any`       | Keyword arguments to pass to the coroutine         |

<a id='bot.add_function'></a>
### add_function
```python
def add_function(self, function: Callable, **kwargs)
```
Add a function to the executor.
#### Parameters:
| Name       | Type       | Description                               |
|------------|------------|-------------------------------------------|
| `function` | `Callable` | A function to run in the executor         |
| `kwargs`   | `Any`      | Keyword arguments to pass to the function |

<a id='bot.add_strategy'></a>
### add_strategy
```python
def add_strategy(self, strategy: Strategy)
```
Add a strategy to the list of strategies.

#### Parameters:
| Name       | Type       | Description                       |
|------------|------------|-----------------------------------|
| `strategy` | `Strategy` | A Strategy instance to run on bot |

<a id='bot.add_strategies'></a>
### add_strategies
```python
def add_strategies(strategies: Iterable[Strategy])
```
Add multiple strategies at the same time
#### Parameters:
| Name         | Type                 | Description                       |
|--------------|----------------------|-----------------------------------|
| `strategies` | `Iterable[Strategy]` | An iterable of Strategy instances |

<a id='bot.add_strategy_all'></a>
### add_strategy_all
```python
def add_strategy_all(*, strategy: Type[Strategy], params: dict | None = None, symbols: list[Symbol] = None, **kwargs)
```
Use this to run a single strategy on multiple symbols with the same parameters and keyword arguments.
#### Parameters:
| Name       | Type             | Description                                 |
|------------|------------------|---------------------------------------------|
| `strategy` | `Type[Strategy]` | A Strategy class                            |
| `params`   | `dict` or `None` | A dictionary of parameters for the strategy |
| `symbols`  | `list[Symbol]`   | A list of symbols to run the strategy on    |
| `**kwargs` | `Any`            | Keyword arguments                           |


<a id='bot.process_pool'></a>
```python
@classmethod
def process_pool(cls, bots: dict[Callable: dict] = None, num_workers: int = None):
```
Run multiple functions (scripts, bots) at the same time in parallel with different accounts. 
Running multiple functions is useful when you want to run different strategies on different accounts.
The callable can for example be a bot instance that defines its own Config instance within the function scope.
The dictionary should contain the callable as the key and the dictionary of keyword arguments to pass to the callable as
the value. Use the path attribute of the config instance to specify the terminal path of each account.
The num_workers parameter specifies the number of workers to use. If not specified, the number of workers will be the
number of bots.

#### Parameters
| Name         | Type                   | Description                                                                     |
|--------------|------------------------|---------------------------------------------------------------------------------|
| `bots`       | `dict[Callable: dict]` | A dictionary of callables and their keyword arguments to run as bots            |
| `num_workers` | `int`                  | The number of workers to use. If not specified, the number of bots will be used |
