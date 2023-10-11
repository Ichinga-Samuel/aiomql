<a id="aiomql.ticks"></a>

# aiomql.ticks

Module for working with price ticks.

<a id="aiomql.ticks.Tick"></a>

## Tick Objects

```python
class Tick()
```

Price Tick of a Financial Instrument.

**Attributes**:

- `time` _int_ - Time of the last prices update for the symbol
- `bid` _float_ - Current Bid price
- `ask` _float_ - Current Ask price
- `last` _float_ - Price of the last deal (Last)
- `volume` _float_ - Volume for the current Last price
- `time_msc` _int_ - Time of the last prices update for the symbol in milliseconds
- `flags` _TickFlag_ - Tick flags
- `volume_real` _float_ - Volume for the current Last price
- `Index` _int_ - Custom attribute representing the position of the tick in a sequence.

<a id="aiomql.ticks.Tick.set_attributes"></a>

#### set\_attributes

```python
def set_attributes(**kwargs)
```

Set attributes from keyword arguments

<a id="aiomql.ticks.Ticks"></a>

## Ticks Objects

```python
class Ticks()
```

Container data class for price ticks. Arrange in chronological order.
Supports iteration, slicing and assignment

**Arguments**:

- `data` _DataFrame | tuple[tuple]_ - Dataframe of price ticks or a tuple of tuples
  

**Arguments**:

- `flip` _bool_ - If flip is True reverse data chronological order.
  

**Attributes**:

- `data` - Dataframe Object holding the ticks

<a id="aiomql.ticks.Ticks.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*, data: DataFrame | Iterable, flip=False)
```

Initialize the Ticks class. Creates a DataFrame of price ticks from the data argument.

**Arguments**:

- `data` _DataFrame | Iterable_ - Dataframe of price ticks or any iterable object that can be converted to a
  pandas DataFrame
- `flip` _bool_ - If flip is True reverse data chronological order.

<a id="aiomql.ticks.Ticks.ta"></a>

#### ta

```python
@property
def ta()
```

Access to the pandas_ta library for performing technical analysis on the underlying data attribute.

**Returns**:

- `pandas_ta` - The pandas_ta library

<a id="aiomql.ticks.Ticks.ta_lib"></a>

#### ta\_lib

```python
@property
def ta_lib()
```

Access to the ta library for performing technical analysis. Not dependent on the underlying data attribute.

**Returns**:

- `ta` - The ta library

<a id="aiomql.ticks.Ticks.data"></a>

#### data

```python
@property
def data() -> DataFrame
```

DataFrame of price ticks arranged in chronological order.

<a id="aiomql.ticks.Ticks.rename"></a>

#### rename

```python
def rename(inplace=True, **kwargs) -> _Ticks | None
```

Rename columns of the candle class.

**Arguments**:

- `inplace` _bool_ - Rename the columns inplace or return a new instance of the class with the renamed columns
- `**kwargs` - The new names of the columns
  

**Returns**:

- `Ticks` - A new instance of the class with the renamed columns if inplace is False.
- `None` - If inplace is True

