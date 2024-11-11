# Strategy
The base class for creating strategies.

## Table of Contents
- [Strategy](#strategy.strategy)
- [\_\_init\_\_](#strategy.__init__)
- [sleep](#strategy.sleep)
- [live_sleep](#strategy.live_sleep)
- [backtest_sleep](#strategy.backtest_sleep)
- [run_strategy](#strategy.run_strategy)
- [live_strategy](#strategy.live_strategy)
- [backtest_strategy](#strategy.backtest_strategy)
- [trade](#strategy.trade)
- [test](#strategy.test)


<a id="strategy.strategy"></a>
### Strategy
```python
class Strategy(ABC)
```
The base class for creating strategies.

#### Attributes:
| Name                  | Type                           | Description                                    | Default |
|-----------------------|--------------------------------|------------------------------------------------|---------|
| `name`                | `str`                          | A name for the strategy.                       | None    |
| `symbol`              | `Symbol`                       | The Financial Instrument as a Symbol Object    | None    |
| `sessions`            | `Sessions`                     | Trading sessions.                              | None    |
| `mt5`                 | `MetaTrader \| MetaBackTester` | MetaTrader instance.                           | None    |
| `config`              | `Config`                       | Config instance.                               | None    |
| `parameters`          | `dict`                         | A dictionary of parameters for the strategy.   | None    |
| `backtest_controller` | `BackTesterController`         | A controller for the backtester.               |
| `current_session`     | `Session`                      | The current trading session                    |
| `running`             | `bool`                         | A flag to indicate if the strategy is running. | True    |


<a id="strategy.__init__"></a>
### \__init\__
```python
def __init__(*, symbol: Symbol, params: dict = None, sessions: Sessions, name: str = "")
```
Initiate the parameters dict and add name and symbol fields. Use class name as strategy name if name is not provided.

#### Parameters:
| Name       | Type       | Description                 | Default |
|------------|------------|-----------------------------|---------|
| `symbol`   | `Symbol`   | The Financial instrument    |         |
| `params`   | `Dict`     | Trading strategy parameters | None    |
| `sessions` | `Sessions` | Trading sessions            | None    |
| `name`     | `str`      | The name of the strategy    | ""      |


<a id="strategy.sleep"></a>
### sleep
```python
@staticmethod
async def sleep(secs: float)
```
Sleep for the needed amount of seconds in between requests to the terminal.
computes the accurate amount of time needed to sleep ensuring that the next request is made at the start of
a new bar and making cooperative multitasking possible.
This method calls the `live_sleep` method during live trading or `backtest_sleep`.

#### Parameters:
| Name   | Type    | Description                                                    | Default |
|--------|---------|----------------------------------------------------------------|---------|
| `secs` | `float` | The time in seconds. Usually the timeframe you are trading on. | None    |


<a id="strategy.live_sleep"></a>
### live_sleep
```python
async def live_sleep(*, secs: float)
```
Sleep method for live trading


<a id="strategy.backtest_sleep"></a>
### backtest_sleep
```python
async def backtest_sleep(*, secs: float)
```
Sleep method for backtesting


<a id="strategy.trade"></a>
### trade
```python
@abstractmethod
async def trade()
```
Place trades using this method.
Implement this method in your own strategy as you wish.


<a id="strategy.test"></a>
### test
```python
@abstractmethod
async def test()
```
Use for backtesting. If not implemented use the trade method.


<a id="strategy.run_strategy"></a>
### run_strategy
```python
async def run_strategy()
```
Run the strategy by calling the trade or test method repeatedly in a while loop.
This method actually calls the `live_strategy` or `backtest_strategy` depending on the mode.


<a id="strategy.live_strategy"></a>
### live_strategy
```python
async def live_strategy()
```
Runs the strategy in live mode.


<a id="strategy.backtest_strategy"></a>
### backtest_strategy
```python
async def live_strategy()
```
Runs the strategy in backtest mode.
