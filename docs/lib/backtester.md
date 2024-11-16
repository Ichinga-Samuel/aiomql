<a id="backtester"></a>

# backtester

<a id="backtester.BackTester"></a>

## BackTester Objects

```python
class BackTester()
```

The bot class. Create a bot instance to run your strategies.

**Attributes**:

- `executor` - The default thread executor.
- `config` _Config_ - Config instance
- `mt` _MetaBackTester_ - MetaTrader instance

<a id="backtester.BackTester.initialize_sync"></a>

#### initialize\_sync

```python
def initialize_sync()
```

Prepares the bot by signing in to the trading account and initializing the symbols for the trading session.
Starts the global task queue.

**Raises**:

  SystemExit if sign in was not successful

<a id="backtester.BackTester.initialize"></a>

#### initialize

```python
async def initialize()
```

Prepares the bot by signing in to the trading account and initializing the symbols for the trading session.
Starts the global task queue.

**Raises**:

  SystemExit if sign in was not successful

<a id="backtester.BackTester.add_coroutine"></a>

#### add\_coroutine

```python
def add_coroutine(*,
                  coroutine: Callable[..., ...] | Coroutine,
                  on_separate_thread=False,
                  **kwargs)
```

Add a coroutine to the executor.

**Arguments**:

- `coroutine` _Coroutine_ - A coroutine to be executed
- `on_separate_thread` _bool_ - Run the coroutine
- `**kwargs` _dict_ - keyword arguments for the coroutine
  

<a id="backtester.BackTester.execute"></a>

#### execute

```python
def execute()
```

Execute the bot.

<a id="backtester.BackTester.start"></a>

#### start

```python
async def start()
```

Initialize the bot and execute it. Similar to calling `execute` method but is a coroutine.

<a id="backtester.BackTester.add_strategy"></a>

#### add\_strategy

```python
def add_strategy(*, strategy: Strategy)
```

Add a strategy to the list of strategies.
An added strategy will only run if it's symbol was successfully initialized and it is added to the executor.

**Arguments**:

- `strategy` _Strategy_ - A Strategy instance to run on bot
  

**Notes**:

  Make sure the symbol has been added to the market

<a id="backtester.BackTester.add_strategies"></a>

#### add\_strategies

```python
def add_strategies(*, strategies: Iterable[Strategy])
```

Add multiple strategies at the same time

**Arguments**:

- `strategies` - A list of strategies

<a id="backtester.BackTester.add_strategy_all"></a>

#### add\_strategy\_all

```python
def add_strategy_all(*,
                     strategy: Type[Strategy],
                     params: dict | None = None,
                     symbols: list[Symbol] = None,
                     **kwargs)
```

Use this to run a single strategy on multiple symbols with the same parameters and keyword arguments.

**Arguments**:

- `strategy` _Strategy_ - Strategy class
- `params` _dict_ - A dictionary of parameters for the strategy
- `symbols` _list_ - A list of symbols to run the strategy on
- `**kwargs` - Additional keyword arguments for the strategy

<a id="backtester.BackTester.init_strategy"></a>

#### init\_strategy

```python
async def init_strategy(*, strategy: Strategy) -> bool
```

Initialize a single strategy. This method is called internally by the bot.

<a id="backtester.BackTester.init_strategy_sync"></a>

#### init\_strategy\_sync

```python
def init_strategy_sync(*, strategy: Strategy) -> bool
```

Initialize a single strategy. This method is called internally by the bot.

<a id="backtester.BackTester.init_strategies"></a>

#### init\_strategies

```python
async def init_strategies()
```

Initialize the symbols for the current trading session. This method is called internally by the bot.

<a id="backtester.BackTester.init_strategies_sync"></a>

#### init\_strategies\_sync

```python
def init_strategies_sync()
```

Initialize the symbols for the current trading session. This method is called internally by the bot.

