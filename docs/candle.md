## <a id="candle"></a> Candle
Candle and Candles classes for handling bars from the MetaTrader 5 terminal.
```python
class Candle
```
A class representing bars from the MetaTrader 5 terminal as a customized class analogous to Japanese Candlesticks.
You can subclass this class for added customization.

### Attributes
|Name|Type|Description|
|---|---|---|
|**time**|**int**|Period start time|
|**open**|**int**|Open price|
|**high**|**float**|The highest price of the period|
|**low**|**float**|The lowest price of the period|
|**close**|**float**|Close price|
|**tick_volume**|**float**|Tick volume|
|**real_volume**|**float**|Trade volume|
|**spread**|**float**|Spread|
|**Index**|**int**|Custom attribute representing the position of the candle in a sequence.|

### \_\_init\_\_
```python
def __init__(**kwargs)
```
Create a Candle object from keyword arguments. Kwargs are set as instance attributes.
#### Arguments: 
|Name|Type|Description|
|---|---|---|
|**kwargs**|**Any**|Candle attributes and values as keyword arguments.|

### set\_attributes
```python
def set_attributes(**kwargs)
```
Set keyword arguments as instance attributes

### mid
```python
@property
def mid() -> float
```
The median of open and close
#### Returns:
|Type|Description|
|---|---|
|**float**|The median of open and close|

### is_bullish
```python
def is_bullish() -> bool
```
A simple check to see if the candle is bullish.
#### Returns:
|Type|Description|
|---|---|
|**bool**|True or False|

### is_bearish
```python
def is_bearish() -> bool
```
A simple check to see if the candle is bearish.
#### Returns:
|Type|Description|
|---|---|
|bool|True or False|

## <a id="candles"></a> Candles
```python
class Candles(Generic[_Candle])
```
An iterable container class of Candle objects in chronological order. A wrapper around Pandas DataFrame object.
### Attributes:
|Name|Type|Description|
|---|---|---|
|**data**|**DataFrame**|A pandas DataFrame of all candles in the object.|
|**Index**|**Series['int']**|A pandas Series of the indexes of all candles in the object|
|**time**|**Series['int']**|A pandas Series of the time of all candles in the object|
|**open**|**Series[float]**|A pandas Series of the opening price of all candles in the object|
|**high**|**Series[float]**|A pandas Series of the high price of all candles in the object|
|**low**|**Series[float]**|A pandas Series of the low price of all candles in the object|
|**close**|**Series[float]**|A pandas Series of the closing price of all candles in the object|
|**tick_volume**|**Series[float]**|A pandas Series of the tick volume of all candles in the object|
|**real_volume**|**Series[float]**|A pandas Series of the real volume of all candles in the object|
|**spread**|**Series[float]**|A pandas Series of the spread of all candles in the object|
|**timeframe**|**TimeFrame**|The timeframe of the candles in the object|
|**Candle**|**Type[Candle]**|The Candle class for representing the candles in the object.|
|**data**|**DataFrame**|A pandas DataFrame of all candles in the object.|

**Notes**: When subclassing this class make sure to Candle attribute is set to your desired candle class.

#### \_\_init\_\_
```python
def __init__(*,
             data: DataFrame | _Candles | Iterable,
             flip=False,
             candle_class: Type[_Candle] = None)
```
A container class of Candle objects in chronological order.
#### Arguments:
|Name|Type|Description|Default|
|---|---|---|---|
|**data**|**DataFrame** or **Candles** or **Iterable**|A pandas dataframe, a Candles object or any suitable iterable|
|**flip**|**bool**|Reverse the chronological order of the candles to the oldest first.|False|
|**candle_class**|**Type[Candle]**|A subclass of Candle to use as the candle class.|Candle|

#### ta
```python
@property
def ta()
```
Access to the pandas_ta library for performing technical analysis on the underlying data attribute. Use this as you would use the pandas_ta library.

#### Returns:
|Type|Description|
|---|---|
|**pandas_ta**|The pandas_ta library|

#### ta\_lib
```python
@property
def ta_lib()
```
Access to the ta library for performing technical analysis. Not dependent on the underlying data attribute. Use this for
functions that require pandas Series as input.

#### Returns:
|Type|Description|
|---|---|
|ta|The ta library|

#### data
```python
@property
def data() -> DataFrame
```
A pandas DataFrame of all candles in the object.

#### rename
```python
def rename(inplace=True, **kwargs) -> _Candles | None
```
Rename columns of the candles class.
#### Arguments:
| Name    | Type     |Description|Default|
|---------|----------|---|---|
| inplace | **bool** |Rename the columns inplace or return a new instance of the class with the renamed columns|True|
| **kwargs** | **str**  |The new names of the columns||

#### Returns:
|Type|Description|
|---|---|
|**Candles**|A new instance of the class with the renamed columns if inplace is False.|
