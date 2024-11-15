# MetaBackTester

## Table of Contents
- [MetaBackTester](#metabacktester)
- [\__init\__](#metabacktester.__init__)
- [backtest_engine](#metabacktester.backtest_engine)
- [backtest_engine.setter](#metabacktester.backtest_engine.setter)


<a id="metabacktester.meta_back_tester"></a>
### MetaBackTester
```python
class MetaBackTester(MetaTrader)
```
A class for testing trading strategies in the MetaTrader 5 terminal. A subclass of MetaTrader.
    
#### Attributes:
| Name              | Type             | Description                                                   |
|-------------------|------------------|---------------------------------------------------------------|
| `backtest_engine` | `BackTestEngine` | The backtesting engine to use for testing trading strategies. |


<a id="metabacktester.__init__"></a>
### \__init\__
```python
def __init__(self, *, backtest_engine: BackTestEngine = None)
```

#### Parameters:
| Name              | Type             | Description                                      |
|-------------------|------------------|--------------------------------------------------|
| `backtest_engine` | `BackTestEngine` | The backtesting engine to use for testing trades |

<a id="metabacktester.backtest_engine"></a>
```python
@property
def backtest_engine(self) -> BackTestEngine
```
Returns the backtest engine object.


<a id="metabacktester.backtest_engine.setter"></a>
```python
@backtest_engine.setter
def backtest_engine(self, value: BackTestEngine):
```
Sets the backtest engine object.
