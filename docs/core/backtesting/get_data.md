# Table of Contents

* [get\_data](#get_data)
  * [Cursor](#get_data.Cursor)
  * [BackTestData](#get_data.BackTestData)
    * [set\_attrs](#get_data.BackTestData.set_attrs)
    * [fields](#get_data.BackTestData.fields)
  * [GetData](#get_data.GetData)
    * [\_\_init\_\_](#get_data.GetData.__init__)
    * [pickle\_data](#get_data.GetData.pickle_data)
    * [load\_data](#get_data.GetData.load_data)
    * [save\_data](#get_data.GetData.save_data)
    * [get\_data](#get_data.GetData.get_data)

<a id="get_data"></a>

# get\_data

<a id="get_data.Cursor"></a>

## Cursor Objects

```python
class Cursor(NamedTuple)
```

A cursor to iterate over the data. Marks the current position.

<a id="get_data.BackTestData"></a>

## BackTestData Objects

```python
@dataclass
class BackTestData()
```

The data class to store the backtesting data.

**Attributes**:

- `name` _str_ - The name of the backtest data.
- `terminal` _dict_ - The terminal information.
- `version` _tuple_ - The version of the terminal.
- `account` _dict_ - The account information.
- `symbols` _dict_ - The symbols information.
- `ticks` _dict_ - The ticks data.
- `rates` _dict_ - The rates data.
- `span` _range_ - The range of the data.
- `range` _range_ - The range of the data.
- `orders` _dict_ - The orders data.
- `deals` _dict_ - The deals data.
- `positions` _dict_ - The positions data.
- `open_positions` _set_ - The open positions.
- `cursor` _Cursor_ - The cursor to iterate over the data.
- `margins` _dict_ - The margins data.
- `fully_loaded` _bool_ - A flag to indicate if the data is fully loaded

<a id="get_data.BackTestData.set_attrs"></a>

#### set\_attrs

```python
def set_attrs(**kwargs)
```

Set the attributes of the class on the instance.

<a id="get_data.BackTestData.fields"></a>

#### fields

```python
@property
def fields()
```

A list of the fields of the class.

<a id="get_data.GetData"></a>

## GetData Objects

```python
class GetData()
```

A class to get the backtesting data from the MetaTrader5 terminal.

**Attributes**:

- `start` _datetime_ - The start date of the data.
- `end` _datetime_ - The end date of the data.
- `symbols` _Sequence[str]_ - The symbols to get the data for.
- `timeframes` _Sequence[TimeFrame]_ - The timeframes to get the data for.
- `name` _str_ - The name of the backtest data.
- `range` _range_ - The range of the data.
- `span` _range_ - The span of the data.
- `data` _BackTestData_ - The backtesting data.
- `mt5` _MetaTrader_ - The MetaTrader5 instance.
- `task_queue` _TaskQueue_ - The task queue to handle the requests.

<a id="get_data.GetData.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*,
             start: datetime,
             end: datetime,
             symbols: Sequence[str],
             timeframes: Sequence[TimeFrame],
             name: str = "")
```

Get the backtesting data from the MetaTrader5 terminal.

**Arguments**:

- `start` _datetime_ - The start date of the data.
- `end` _datetime_ - The end date of the data.
- `symbols` _Sequence[str]_ - The symbols to get the data for.
- `timeframes` _Sequence[TimeFrame]_ - The timeframes to get the data for.
- `name` _str_ - The name of the backtest data.

<a id="get_data.GetData.pickle_data"></a>

#### pickle\_data

```python
@classmethod
def pickle_data(cls, *, data: BackTestData, name: str | Path)
```

Pickle the data to a file.

**Arguments**:

- `data` _BackTestData_ - The data to pickle.
- `name` _str | Path_ - The name of the file to pickle the data to.

<a id="get_data.GetData.load_data"></a>

#### load\_data

```python
@classmethod
def load_data(cls, *, name: str | Path) -> BackTestData
```

Load the data from a file.

**Arguments**:

- `name` _str | Path_ - The name of the file to load the data from.

<a id="get_data.GetData.save_data"></a>

#### save\_data

```python
def save_data(*, name: str | Path = "")
```

Save the data to a file.

**Arguments**:

- `name` _str | Path_ - The name of the file to save the data to. If not provided, the name of the data is used.

<a id="get_data.GetData.get_data"></a>

#### get\_data

```python
async def get_data(workers: int = None)
```

Use the task queue to get the data from the MetaTrader5 terminal.

**Arguments**:

- `workers` _int_ - The number of workers to use in the task queue. If not provided, the default number of workers
  is used.

