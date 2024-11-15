# Get Data

## Table of Contents

- [Cursor](#get_data.cursor)
- [BackTestData](#get_data.back_test_data)
  - [set_attrs](#get_data.back_test_data.set_attrs)
  - [fields](#get_data.back_test_data.fields)
- [GetData](#get_data.getdata)
  - [\__init\__](#get_data.get_data.__init__)
  - [pickle_data](#get_data.pickle_data)
  - [load_data](#get_data.load_data)
  - [save_data](#get_data.save_data)
  - [get_data](#get_data.get_data)


<a id="get_data.cursor"></a>
### Cursor 
```python
class Cursor(NamedTuple)
```
A cursor to iterate over the data. Marks the current position in time.


<a id="get_data.back_test_data"></a>
### BackTestData
```python
@dataclass
class BackTestData
```
The data class to store the backtesting data.

#### Attributes:
| Name             | Type     | Description                                    |
|------------------|----------|------------------------------------------------|
| `name`           | `str`    | The name of the backtest data                  |
| `terminal`       | `dict`   | The terminal information                       |
| `version`        | `tuple`  | The version of the terminal                    |
| `account`        | `dict`   | The account information                        |
| `symbols`        | `dict`   | The symbols information                        |
| `ticks`          | `dict`   | The ticks data                                 |
| `rates`          | `dict`   | The rates data                                 |
| `span`           | `range`  | The range of the data                          |
| `range`          | `range`  | The range of the data                          |
| `orders`         | `dict`   | The orders data                                |
| `deals`          | `dict`   | The deals data                                 |
| `positions`      | `dict`   | The positions data                             |
| `open_positions` | `set`    | The open positions                             |
| `cursor`         | `Cursor` | The cursor to iterate over the data            |
| `margins`        | `dict`   | The margins data                               |
| `fully_loaded`   | `bool`   | A flag to indicate if the data is fully loaded |


<a id="get_data.set_attrs"></a>
#### set_attrs
```python
def set_attrs(**kwargs)
```
Set the attributes of the class on the instance.


<a id="get_data.fields"></a>
#### fields
```python
@property
def fields()
```
A list of the fields of the class.


<a id="get_data.getdata"></a>
### GetData
```python
class GetData
```
A class to get the backtesting data from the MetaTrader5 terminal.

#### Attributes:
| Name         | Type                  | Description                           |
|--------------|-----------------------|---------------------------------------|
| `start`      | `datetime`            | The start date of the data            |
| `end`        | `datetime`            | The end date of the data              |
| `symbols`    | `Iterable[str]`       | The symbols to get the data for       |
| `timeframes` | `Iterable[TimeFrame]` | The timeframes to get the data for    |
| `name`       | `str`                 | The name of the backtest data         |
| `range`      | `range`               | The range of the data                 |
| `span`       | `range`               | The span of the data                  |
| `data`       | `BackTestData`        | The backtesting data                  |
| `mt5`        | `MetaTrader`          | The MetaTrader5 instance              |
| `task_queue` | `TaskQueue`           | The task queue to handle the requests |


<a id="get_data.__init__"></a>
#### \__init\__
```python
def __init__(*, start: datetime, end: datetime, symbols: Sequence[str],
             timeframes: Sequence[TimeFrame], name: str = "")
```
Get the backtesting data from the MetaTrader5 terminal.

#### Parameters:
| Name         | Type                  | Description                                    |
|--------------|-----------------------|------------------------------------------------|
| `start`      | `datetime`            | The start date of the data                     |
| `end`        | `datetime`            | The end date of the data                       |
| `symbols`    | `Sequence[str]`       | The symbols to get the data for                |
| `timeframes` | `Sequence[TimeFrame]` | The timeframes to get the data for             |
| `name`       | `str`                 | The name of the backtest data                  |


<a id="get_data.pickle_data"></a>
#### pickle_data
```python
@classmethod
def pickle_data(cls, *, data: BackTestData, name: str | Path)
```
Pickle the data to a file.

#### Parameters:
| Name   | Type                    | Description          |
|--------|-------------------------|----------------------|
| `data` | `BackTestData`          | The data to pickle   |
| `name` | `str           \| Path` | The name of the file |


<a id="get_data.load_data"></a>
#### load_data
```python
@classmethod
def load_data(cls, *, name: str | Path) -> BackTestData
```
Load the data from a file.

#### Parameters:
| Name   | Type                    | Description          |
|--------|-------------------------|----------------------|
| `name` | `str           \| Path` | The name of the file |


<a id="get_data.save_data"></a>
#### save_data
```python
def save_data(*, name: str | Path = "")
```
Save the data to a file.

#### Parameters:
| Name   | Type                    | Description          |
|--------|-------------------------|----------------------|
| `name` | `str           \| Path` | The name of the file |


<a id="get_data.get_data"></a>
#### get_data
```python
async def get_data(workers: int = None)
```
Use the task queue to get the data from the MetaTrader5 terminal.
#### Parameters:
| Name      | Type  | Description                                    |
|-----------|-------|------------------------------------------------|
| `workers` | `int` | The number of workers to use in the task queue |
