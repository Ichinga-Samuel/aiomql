<a id="aiomql.strategy"></a>

# aiomql.strategy

The base class for creating strategies.

<a id="aiomql.strategy.Strategy"></a>

## Strategy Objects

```python
class Strategy(ABC)
```

The base class for creating strategies.

**Attributes**:

- `symbol` _Symbol_ - The Financial Instrument as a Symbol Object
- `parameters` _Dict_ - A dictionary of parameters for the strategy.
  
  Class Attributes:
- `name` _str_ - A name for the strategy.
- `account` _Account_ - Account instance.
- `mt5` _MetaTrader_ - MetaTrader instance.
- `config` _Config_ - Config instance.
  

**Notes**:

  Define the name of a strategy as a class attribute. If not provided, the class name will be used as the name.

<a id="aiomql.strategy.Strategy.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*, symbol: Symbol, params: dict = None)
```

Initiate the parameters dict and add name and symbol fields.
Use class name as strategy name if name is not provided

**Arguments**:

- `symbol` _Symbol_ - The Financial instrument
- `params` _Dict_ - Trading strategy parameters

<a id="aiomql.strategy.Strategy.sleep"></a>

#### sleep

```python
@staticmethod
async def sleep(secs: float)
```

Sleep for the needed amount of seconds in between requests to the terminal.
computes the accurate amount of time needed to sleep ensuring that the next request is made at the start of
a new bar and making cooperative multitasking possible.

**Arguments**:

- `secs` _float_ - The time in seconds. Usually the timeframe you are trading on.

<a id="aiomql.strategy.Strategy.trade"></a>

#### trade

```python
@abstractmethod
async def trade()
```

Place trades using this method. This is the main method of the strategy.
It will be called by the strategy runner.

