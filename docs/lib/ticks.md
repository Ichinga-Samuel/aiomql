# Tick and Ticks
Module for working with price ticks.

## Table of Contents
- [Tick](#tick.tick)
  - [\_\_init\_\_](#tick.__init__)
  - [set_attributes](#tick.set_attributes)

- [Ticks](#ticks.ticks)
  - [\__init\__](#ticks.__init__)
  - [ta](#ticks.ta)
  - [ta_lib](#ticks.ta_lib)
  - [data](#ticks.data)
  - [rename](#ticks.rename)


<a id='tick.tick'></a>
## Tick
```python
class Tick()
```
Price Tick of a Financial Instrument.
#### Attributes:
| Name          | Type       | Description                                                           | Default |
|---------------|------------|-----------------------------------------------------------------------|---------|
| `symbol`      | `Symbol`   | The Financial Instrument as a Symbol Object                           | None    |
| `time`        | `datetime` | Time of the last prices update for the symbol                         | None    |
| `bid`         | `float`    | Current Bid price                                                     | None    |
| `ask`         | `float`    | Current Ask price                                                     | None    |
| `last`        | `float`    | Price of the last deal (Last)                                         | None    |
| `volume`      | `float`    | Volume for the current Last price                                     | None    |
| `time_msc`    | `int`      | Time of the last prices update for the symbol in milliseconds         | None    |
| `flags`       | `TickFlag` | Tick flags                                                            | None    |
| `volume_real` | `float`    | Volume for the current Last price                                     | None    |
| `Index`       | `int`      | Custom attribute representing the position of the tick in a sequence. | None    |
| `index`       | `int`      | Index of the tick in the input dataframe object.                      | None    |


<a id="tick.__init__"></a>
### \__init\__
```python
def __init__(self, **kwargs):
```
Initialize the Tick class. Set attributes from keyword arguments.The `bid`, `ask`, `last`, `time` and `volume` must be present


<a id="tick.set_attributes"></a>
### set_attributes
```python
def set_attributes(**kwargs)
```
Set attributes from keyword arguments


<a id="tick.dict"></a>
### dict
```python
def dict(exclude: set = None, include: set = None) -> dict
```
Return a dictionary of the tick attributes.

#### Parameters:
| Name      | Type  | Description                                         | Default |
|-----------|-------|-----------------------------------------------------|---------|
| `exclude` | `set` | A set of attributes to exclude from the dictionary. | None    |
| `include` | `set` | A set of attributes to include in the dictionary.   | None    |


<a id="ticks.ticks"></a>
## Ticks
```python
class Ticks
```
Container data class for price ticks. Arrange in chronological order. Saves data with a pandas DataFrame.
Supports iteration, slicing and assignment. Similar to `Candles` class but for price ticks.
  
#### Attributes:
| Name          | Type        | Description                                                          | Default |
|---------------|-------------|----------------------------------------------------------------------|---------|
| `data`        | `DataFrame` | DataFrame of price ticks arranged in chronological order.            | None    |
| `time`        | `Series`    | Time of the last prices update for the symbol                        | None    |
| `bid`         | `Series`    | Current Bid price                                                    | None    |
| `ask`         | `Series`    | Current Ask price                                                    | None    |
| `last`        | `Series`    | Price of the last deal (Last)                                        | None    |
| `volume`      | `Series`    | Volume for the current Last price                                    | None    |
| `time_msc`    | `Series`    | Time of the last prices update for the symbol in milliseconds        | None    |
| `flags`       | `Series`    | Tick flags                                                           | None    |
| `volume_real` | `Series`    | Volume for the current Last price                                    | None    |
| `Index`       | `Series`    | Custom attribute representing the position of the tick in a sequence | None    |
| `index`       | `Series`    | Custom attribute representing the index of the tick in the DataFrame | None    |


<a id="ticks.__init__"></a>
### \__init\__
```python
def __init__(*, data: DataFrame | Iterable, flip=False):
```
Initialize the Ticks class. Creates a DataFrame of price ticks from the data argument.
#### Arguments:
| Name   | Type                      | Description                                                                                 | Default |
|--------|---------------------------|---------------------------------------------------------------------------------------------|---------|
| `data` | `DataFrame` \| `Iterable` | Dataframe of price ticks or any iterable object that can be converted to a pandas DataFrame | None    |
| `flip` | `bool`                    | If flip is True reverse data chronological order.                                           | False   |


<a id="ticks.ta"></a>
### ta
```python
@property
def ta()
```
Access to the pandas_ta library for performing technical analysis on the underlying data attribute.
#### Returns:
| Name        | Type        | Description           |
|-------------|-------------|-----------------------|
| `pandas_ta` | `pandas_ta` | The pandas_ta library |


<a id="ticks.ta_lib"></a>
### ta_lib
```python
@property
def ta_lib()
```
Access to the ta library for performing technical analysis. Not dependent on the underlying data attribute.
#### Returns:
| Name | Type | Description    |
|------|------|----------------|
| `ta` | `ta` | The ta library |


<a id="ticks.data"></a>
### data
```python
@property
def data() -> DataFrame
```
DataFrame of price ticks arranged in chronological order.
#### Returns:
| Name   | Type        | Description                                               |
|--------|-------------|-----------------------------------------------------------|
| `data` | `DataFrame` | DataFrame of price ticks arranged in chronological order. |


<a id="ticks.rename"></a>
### rename
```python
def rename(inplace=True, **kwargs) -> _Ticks | None
```
Rename columns of the candle class.
#### Arguments:
| Name      | Type   | Description                                                                               | Default |
|-----------|--------|-------------------------------------------------------------------------------------------|---------|
| `inplace` | `bool` | Rename the columns inplace or return a new instance of the class with the renamed columns | True    |
| `kwargs`  |        | The new names of the columns                                                              |         |

#### Returns:
| Type    | Description                                                               |
|---------|---------------------------------------------------------------------------|
| `Ticks` | A new instance of the class with the renamed columns if inplace is False. |
| `None`  | If inplace is True                                                        |
