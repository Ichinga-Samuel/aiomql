<a id="aiomql.symbol"></a>

# aiomql.symbol

Symbol class for handling a financial instrument.

<a id="aiomql.symbol.Symbol"></a>

## Symbol Objects

```python
class Symbol(SymbolInfo)
```

Main class for handling a financial instrument. A subclass of SymbolInfo and Base it has attributes and methods
for working with a financial instrument.

**Attributes**:

- `tick` _Tick_ - Price tick object for instrument
- `account` - An instance of the current trading account
  

**Notes**:

  Full properties are on the SymbolInfo Object.
  Make sure Symbol is always initialized with a name argument

<a id="aiomql.symbol.Symbol.pip"></a>

#### pip

```python
@property
def pip()
```

Returns the pip value of the symbol. This is ten times the point value for forex symbols.

**Returns**:

- `float` - The pip value of the symbol.

<a id="aiomql.symbol.Symbol.info_tick"></a>

#### info\_tick

```python
async def info_tick(*, name: str = "") -> Tick
```

Get the current price tick of a financial instrument.

**Arguments**:

- `name` - if name is supplied get price tick of that financial instrument
  

**Returns**:

- `Tick` - Return a Tick Object
  

**Raises**:

- `ValueError` - If request was unsuccessful and None was returned

<a id="aiomql.symbol.Symbol.symbol_select"></a>

#### symbol\_select

```python
async def symbol_select(*, enable: bool = True) -> bool
```

Select a symbol in the MarketWatch window or remove a symbol from the window.
Update the select property

**Arguments**:

- `enable` _bool_ - Switch. Optional unnamed parameter. If 'false', a symbol should be removed from
  the MarketWatch window.
  

**Returns**:

- `bool` - True if successful, otherwise – False.

<a id="aiomql.symbol.Symbol.info"></a>

#### info

```python
async def info() -> SymbolInfo
```

Get data on the specified financial instrument and update the symbol object properties

**Returns**:

- `(SymbolInfo)` - SymbolInfo if successful
  

**Raises**:

- `ValueError` - If request was unsuccessful and None was returned

<a id="aiomql.symbol.Symbol.init"></a>

#### init

```python
async def init() -> bool
```

Initialized the symbol by pulling properties from the terminal

**Returns**:

- `bool` - Returns True if symbol info was successful initialized

<a id="aiomql.symbol.Symbol.book_add"></a>

#### book\_add

```python
async def book_add() -> bool
```

Subscribes the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.
If the symbol is not in the list of instruments for the market, This method will return False

**Returns**:

- `bool` - True if successful, otherwise – False.

<a id="aiomql.symbol.Symbol.book_get"></a>

#### book\_get

```python
async def book_get() -> tuple[BookInfo]
```

Returns a tuple of BookInfo featuring Market Depth entries for the specified symbol.

**Returns**:

- `tuple[BookInfo]` - Returns the Market Depth contents as a tuples of BookInfo Objects
  

**Raises**:

- `ValueError` - If request was unsuccessful and None was returned

<a id="aiomql.symbol.Symbol.book_release"></a>

#### book\_release

```python
async def book_release() -> bool
```

Cancels subscription of the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.

**Returns**:

- `bool` - True if successful, otherwise – False.

<a id="aiomql.symbol.Symbol.compute_volume"></a>

#### compute\_volume

```python
async def compute_volume(*,
                         amount: float,
                         pips: float,
                         use_minimum: bool = True) -> float
```

Computes the volume of a trade based on the amount and the number of pips to target.
This is a dummy method that returns the minimum volume of the symbol. It is meant to be overridden by a subclass
Checkout Forex Symbol implementation in srciomql\lib\ForexSymbol.py

**Arguments**:

- `amount` _float_ - Amount to risk in the trade
- `pips` _float_ - Number of pips to target
  

**Arguments**:

- `use_minimum` _bool_ - If True, the minimum volume is returned if the computed volume is less than the minimum volume.
  

**Returns**:

- `float` - Returns the volume of the trade

<a id="aiomql.symbol.Symbol.currency_conversion"></a>

#### currency\_conversion

```python
async def currency_conversion(*, amount: float, base: str,
                              quote: str) -> float
```

Convert from one currency to the other.

**Arguments**:

- `amount` - amount to convert given in terms of the quote currency
- `base` - The base currency of the pair
- `quote` - The quote currency of the pair
  

**Returns**:

- `float` - Amount in terms of the base currency or None if it failed to convert
  

**Raises**:

- `ValueError` - If conversion is impossible

<a id="aiomql.symbol.Symbol.copy_rates_from"></a>

#### copy\_rates\_from

```python
async def copy_rates_from(*,
                          timeframe: TimeFrame,
                          date_from: datetime | int,
                          count: int = 500) -> Candles
```

Get bars from the MetaTrader 5 terminal starting from the specified date.

**Arguments**:

- `timeframe` _TimeFrame_ - Timeframe the bars are requested for. Set by a value from the TimeFrame enumeration. Required unnamed parameter.
  
- `date_from` _datetime | int_ - Date of opening of the first bar from the requested sample. Set by the 'datetime' object or as a number
  of seconds elapsed since 1970.01.01. Required unnamed parameter.
  
- `count` _int_ - Number of bars to receive. Required unnamed parameter.
  

**Returns**:

- `Candles` - Returns a Candles object as a collection of rates ordered chronologically
  

**Raises**:

- `ValueError` - If request was unsuccessful and None was returned

<a id="aiomql.symbol.Symbol.copy_rates_from_pos"></a>

#### copy\_rates\_from\_pos

```python
async def copy_rates_from_pos(*,
                              timeframe: TimeFrame,
                              count: int = 500,
                              start_position: int = 0) -> Candles
```

Get bars from the MetaTrader 5 terminal starting from the specified index.

**Arguments**:

- `timeframe` _TimeFrame_ - TimeFrame value from TimeFrame Enum. Required keyword only parameter
  
- `count` _int_ - Number of bars to return. Keyword argument defaults to 500
  
- `start_position` _int_ - Initial index of the bar the data are requested from. The numbering of bars goes from
  present to past. Thus, the zero bar means the current one. Keyword argument defaults to 0.
  

**Returns**:

- `Candles` - Returns a Candles object as a collection of rates ordered chronologically.
  

**Raises**:

- `ValueError` - If request was unsuccessful and None was returned

<a id="aiomql.symbol.Symbol.copy_rates_range"></a>

#### copy\_rates\_range

```python
async def copy_rates_range(*, timeframe: TimeFrame, date_from: datetime | int,
                           date_to: datetime | int) -> Candles
```

Get bars in the specified date range from the MetaTrader 5 terminal.

**Arguments**:

- `timeframe` _TimeFrame_ - Timeframe for the bars using the TimeFrame enumeration. Required unnamed parameter.
  
- `date_from` _datetime | int_ - Date the bars are requested from. Set by the 'datetime' object or as a number of seconds
  elapsed since 1970.01.01. Bars with the open time >= date_from are returned. Required unnamed parameter.
  
- `date_to` _datetime | int_ - Date, up to which the bars are requested. Set by the 'datetime' object or as a number of
  seconds elapsed since 1970.01.01. Bars with the open time <= date_to are returned. Required unnamed parameter.
  

**Returns**:

- `Candles` - Returns a Candles object as a collection of rates ordered chronologically.
  

**Raises**:

- `ValueError` - If request was unsuccessful and None was returned

<a id="aiomql.symbol.Symbol.copy_ticks_from"></a>

#### copy\_ticks\_from

```python
async def copy_ticks_from(*,
                          date_from: datetime | int,
                          count: int = 100,
                          flags: CopyTicks = CopyTicks.ALL) -> Ticks
```

Get ticks from the MetaTrader 5 terminal starting from the specified date.

Args: date_from (datetime | int): Date the ticks are requested from. Set by the 'datetime' object or as a
number of seconds elapsed since 1970.01.01.

count (int): Number of requested ticks. Defaults to 100

flags (CopyTicks): A flag to define the type of the requested ticks from CopyTicks enum. INFO is the default

**Returns**:

- `Candles` - Returns a Candles object as a collection of ticks ordered chronologically.
  

**Raises**:

- `ValueError` - If request was unsuccessful and None was returned

<a id="aiomql.symbol.Symbol.copy_ticks_range"></a>

#### copy\_ticks\_range

```python
async def copy_ticks_range(*,
                           date_from: datetime | int,
                           date_to: datetime | int,
                           flags: CopyTicks = CopyTicks.ALL) -> Ticks
```

Get ticks for the specified date range from the MetaTrader 5 terminal.

**Arguments**:

- `date_from` - Date the bars are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Bars with
  the open time >= date_from are returned. Required unnamed parameter.
  
- `date_to` - Date, up to which the bars are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Bars
  with the open time <= date_to are returned. Required unnamed parameter.
  
  flags (CopyTicks):
  

**Returns**:

- `Candles` - Returns a Candles object as a collection of ticks ordered chronologically.
  

**Raises**:

- `ValueError` - If request was unsuccessful and None was returned.

