## <a id="ticks"></a> ticks
Module for working with price ticks.

```python
class Tick()
```
Price Tick of a Financial Instrument.
### Attributes:
|Name|Type|Description|Default|
|---|---|---|---|
|**symbol**|**Symbol**|The Financial Instrument as a Symbol Object|None|
|**time**|**datetime**|Time of the last prices update for the symbol|None|
|**bid**|**float**|Current Bid price|None|
|**ask**|**float**|Current Ask price|None|
|**last**|**float**|Price of the last deal (Last)|None|
|**volume**|**float**|Volume for the current Last price|None|
|**time_msc**|**int**|Time of the last prices update for the symbol in milliseconds|None|
|**flags**|**TickFlag**|Tick flags|None|
|**volume_real**|**float**|Volume for the current Last price|None|
|**Index**|**int**|Custom attribute representing the position of the tick in a sequence.|None|

### set\_attributes
```python
def set_attributes(**kwargs)
```
Set attributes from keyword arguments

## Ticks
```python
class Ticks()
```
Container data class for price ticks. Arrange in chronological order.
Supports iteration, slicing and assignment
### Attributes:
|Name|Type|Description|Default|
|---|---|---|---|
|**data**|**DataFrame**|DataFrame of price ticks arranged in chronological order.|None|

### \_\_init\_\_
```python
def __init__(*, data: DataFrame | Iterable, flip=False)
```
Initialize the Ticks class. Creates a DataFrame of price ticks from the data argument.
#### Arguments:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**data**| **DataFrame** \| **Iterable** | Dataframe of price ticks or any iterable object that can be converted to a pandas DataFrame | None |
|**flip**| **bool** | If flip is True reverse data chronological order. | False |

### ta
```python
@property
def ta()
```
Access to the pandas_ta library for performing technical analysis on the underlying data attribute.
#### Returns:
|Name|Type|Description|
|---|---|---|
|**pandas_ta**|**pandas_ta**|The pandas_ta library|

### ta\_lib
```python
@property
def ta_lib()
```
Access to the ta library for performing technical analysis. Not dependent on the underlying data attribute.
#### Returns:
|Name|Type|Description|
|---|---|---|
|**ta**|**ta**|The ta library|

### data
```python
@property
def data() -> DataFrame
```
DataFrame of price ticks arranged in chronological order.
#### Returns:
|Name|Type|Description|
|---|---|---|
|**data**|**DataFrame**|DataFrame of price ticks arranged in chronological order.|

### rename
```python
def rename(inplace=True, **kwargs) -> _Ticks | None
```
Rename columns of the candle class.
#### Arguments:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**inplace**| **bool** | Rename the columns inplace or return a new instance of the class with the renamed columns | True |
|**kwargs**| | The new names of the columns | |
#### Returns:
|Type|Description|
|---|---|
|**Ticks**|A new instance of the class with the renamed columns if inplace is False.|
|**None**|If inplace is True|
