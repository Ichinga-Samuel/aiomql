## <a id="symbol"></a> Symbol

Symbol class for handling a financial instrument.

```python
class Symbol(SymbolInfo)
```
Main class for handling a financial instrument. A subclass of SymbolInfo and Base it has attributes and methods
for working with a financial instrument.

### Attributes:
|Name|Type|Description|Default|
|---|---|---|---|
|**name**|**str**|The name of the symbol.|None|
|**mt5**|**MetaTrader**|MetaTrader instance.|None|
|**config**|**Config**|Config instance.|None|
|**account**|**Account**|Account instance.|None|
|**tick**|**Tick**|The current price tick of the symbol.|None|

### Methods:
|Name|Description|
|---|---|
|**pip**|Returns the pip value of the symbol. This is ten times the point value for forex symbols.|
|**info_tick**|Get the current price tick of a financial instrument.|
|**symbol_select**|Select a symbol in the MarketWatch window or remove a symbol from the window.|
|**info**|Get data on the specified financial instrument and update the symbol object properties.|
|**init**|Initialized the symbol by pulling properties from the terminal.|
|**book_add**|Subscribes the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.|
|**book_get**|Returns a tuple of BookInfo featuring Market Depth entries for the specified symbol.|
|**book_release**|Cancels subscription of the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.|
|**compute_volume**|Computes the volume of a trade based on the amount and the number of pips to target.|
|**currency_conversion**|Convert from one currency to the other.|
|**copy_rates_from**|Get bars from the MetaTrader 5 terminal starting from the specified date.|
|**copy_rates_from_pos**|Get bars from the MetaTrader 5 terminal starting from the specified index.|
|**copy_rates_range**|Get bars in the specified date range from the MetaTrader 5 terminal.|
|**copy_ticks_from**|Get ticks from the MetaTrader 5 terminal starting from the specified date.|
|**copy_ticks_range**|Get ticks for the specified date range from the MetaTrader 5 terminal.|

### Notes:
Full properties are on the SymbolInfo Object.
Make sure Symbol is always initialized with a name argument

<a id="aiomql.symbol.Symbol.pip"></a>

### pip
```python
@property
def pip()
```
Returns the pip value of the symbol. This is ten times the point value for forex symbols.

## Returns:
|Type|Description|
|---|---|
|**float**|The pip value of the symbol.|

### info\_tick
```python
async def info_tick(*, name: str = "") -> Tick
```
Get the current price tick of a financial instrument.
#### Arguments:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**name**| **str** | The name of the symbol. | None |


#### Returns:
|Type|Description|
|---|---|
|**Tick**|Return a Tick Object|

#### Raises:
|Exception|Description|
|---|---|
|**ValueError**|If request was unsuccessful and None was returned|

### symbol\_select
```python
async def symbol_select(*, enable: bool = True) -> bool
```
Select a symbol in the MarketWatch window or remove a symbol from the window.
Update the select property
#### Arguments:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**enable**| **bool** | Switch. Optional unnamed parameter. If 'false', a symbol should be removed from the MarketWatch window. | None |

#### Returns:
|Type|Description|
|---|---|
|**bool**|True if successful, otherwise False.|

### info
```python
async def info() -> SymbolInfo
```
Get data on the specified financial instrument and update the symbol object properties

#### Returns:
|Type|Description|
|---|---|
|**SymbolInfo**|SymbolInfo if successful|

#### Raises:
|Exception|Description|
|---|---|
|**ValueError**|If request was unsuccessful and None was returned|

### init
```python
async def init() -> bool
```
Initialized the symbol by pulling properties from the terminal
#### Returns:
|Type|Description|
|---|---|
|**bool**|Returns True if symbol info was successful initialized|

### book\_add
```python
async def book_add() -> bool
```
Subscribes the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.
If the symbol is not in the list of instruments for the market, This method will return False
#### Returns:
|Type|Description|
|---|---|

### book\_get
```python
async def book_get() -> tuple[BookInfo]
```
Returns a tuple of BookInfo featuring Market Depth entries for the specified symbol.
#### Returns:
|Type|Description|
|---|---|
|**tuple[BookInfo]**|Returns the Market Depth contents as a tuples of BookInfo Objects|
#### Raises:
|Exception|Description|
|---|---|
|**ValueError**|If request was unsuccessful and None was returned|

### book\_release
```python
async def book_release() -> bool
```
Cancels subscription of the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.
#### Returns:
|Type|Description|
|---|---|
|**bool**|True if successful, otherwise � False.|
#### compute\_volume
```python
async def compute_volume(*,
                         amount: float,
                         pips: float,
                         use_minimum: bool = True) -> float
```
Computes the volume of a trade based on the amount and the number of pips to target.
This is a dummy method that returns the minimum volume of the symbol. It is meant to be overridden by a subclass
Checkout Forex Symbol implementation in [ForexSymbol](#forexsymbol) 

#### Arguments:
| Name           | Type               | Description                                                                                                                                                                                                | Default |
|----------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| **amount**     | **float** | Amount to risk in the trade                                                                                                                                                                                | None    |
| **pips**       | **float** | Number of pips to target                                                                                                                                                                                   | None    |
| **use_limits** | **bool** | If True, the minimum volume is returned if the computed volume is less than the minimum volume and the maximum volume is returned if the computed volume is greater than the maximum volume for the symbol | False   |

#### Returns:
|Type|Description|
|---|---|
|**float**|Returns the volume of the trade|

### currency\_conversion
```python
async def currency_conversion(*, amount: float, base: str,
                              quote: str) -> float
```
Convert from one currency to the other.
#### Arguments:

|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**amount**| **float** | Amount to convert given in terms of the quote currency | None |
|**base**| **str** | The base currency of the pair | None |
|**quote**| **str** | The quote currency of the pair | None |

#### Returns:
|Type|Description|
|---|---|
|**float**|Amount in terms of the base currency or None if it failed to convert|
  
#### Raises:
|Exception|Description|
|---|---|
|**ValueError**|If conversion is impossible|

### copy\_rates\_from
```python
async def copy_rates_from(*,
                          timeframe: TimeFrame,
                          date_from: datetime | int,
                          count: int = 500) -> Candles
```
Get bars from the MetaTrader 5 terminal starting from the specified date.
#### Arguments:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**timeframe**| **TimeFrame** | Timeframe the bars are requested for. Set by a value from the TimeFrame enumeration. | Required unnamed parameter |
|**date_from**| **datetime, int** | Date of opening of the first bar from the requested sample. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. | Required unnamed parameter |
|**count**| **int** | Number of bars to receive. | Required unnamed parameter |
#### Returns:
|Type|Description|
|---|---|
|**Candles**|Returns a Candles object as a collection of rates ordered chronologically|
#### Raises:
|Exception|Description|
|---|---|
|**ValueError**|If request was unsuccessful and None was returned|

### copy\_rates\_from\_pos
```python
async def copy_rates_from_pos(*,
                              timeframe: TimeFrame,
                              count: int = 500,
                              start_position: int = 0) -> Candles
```
Get bars from the MetaTrader 5 terminal starting from the specified index.
#### Arguments:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**timeframe**| **TimeFrame** | TimeFrame value from TimeFrame Enum. Required keyword only parameter | Required keyword only parameter |
|**count**| **int** | Number of bars to return. Keyword argument defaults to 500 | 500 |
|**start_position**| **int** | Initial index of the bar the data are requested from. The numbering of bars goes from present to past. Thus, the zero bar means the current one. Keyword argument defaults to 0. | 0 |
#### Returns:
|Type|Description|
|---|---|
|**Candles**|Returns a Candles object as a collection of rates ordered chronologically.|
#### Raises:
|Exception|Description|
|---|---|
|**ValueError**|If request was unsuccessful and None was returned|

### copy\_rates\_range
```python
async def copy_rates_range(*, timeframe: TimeFrame, date_from: datetime | int,
                           date_to: datetime | int) -> Candles
```
Get bars in the specified date range from the MetaTrader 5 terminal.
#### Arguments:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**timeframe**| **TimeFrame** | Timeframe for the bars using the TimeFrame enumeration. Required unnamed parameter. | Required unnamed parameter |
|date_from|datetime, int|Date the bars are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Bars with the open time >= date_from are returned. Required unnamed parameter.|Required unnamed parameter|
|date_to|datetime, int|Date, up to which the bars are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Bars with the open time <= date_to are returned. Required unnamed parameter.|Required unnamed parameter|
#### Returns:
|Type|Description|
|---|---|
|**Candles**|Returns a Candles object as a collection of rates ordered chronologically.|
#### Raises:
|Exception|Description|
|---|---|
|**ValueError**|If request was unsuccessful and None was returned|

### copy\_ticks\_from
```python
async def copy_ticks_from(*,
                          date_from: datetime | int,
                          count: int = 100,
                          flags: CopyTicks = CopyTicks.ALL) -> Ticks
```
Get ticks from the MetaTrader 5 terminal starting from the specified date.
#### Arguments:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**date_from**| **datetime, int** | Date the ticks are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. | Required unnamed parameter |
|**count**| **int** | Number of requested ticks. Defaults to 100 | Required unnamed parameter |
|**flags**| **CopyTicks** | A flag to define the type of the requested ticks from CopyTicks enum. INFO is the default | Required unnamed parameter |
#### Returns:
|Type|Description|
|---|---|
|**Ticks**|Returns a Ticks object as a collection of ticks ordered chronologically.|
#### Raises:
|Exception|Description|
|---|---|
|**ValueError**|If request was unsuccessful and None was returned|

### copy\_ticks\_range
```python
async def copy_ticks_range(*,
                           date_from: datetime | int,
                           date_to: datetime | int,
                           flags: CopyTicks = CopyTicks.ALL) -> Ticks
```
Get ticks for the specified date range from the MetaTrader 5 terminal.
#### Arguments:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**date_from**| **datetime, int** | Date the ticks are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. | Required unnamed parameter |
|**date_to**| **datetime, int** | Date, up to which the ticks are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. | Required unnamed parameter |
|**flags**| **CopyTicks** | A flag to define the type of the requested ticks from CopyTicks enum. INFO is the default | Required unnamed parameter |
#### Returns:
|Type|Description|
|---|---|
|**Ticks**|Returns a Ticks object as a collection of ticks ordered chronologically.|
#### Raises:
|Exception|Description|
|---|---|
|**ValueError**|If request was unsuccessful and None was returned|

### compute_volume
```python
async def compute_volume(*,
                         amount: float,
                         pips: float,
                         use_limits: bool = True) -> float
```
Computes the volume of a trade based on the amount and the number of pips to target.
This is a dummy method that returns the minimum volume of the symbol. It is meant to be overridden by a subclass
Checkout Forex Symbol implementation in [ForexSymbol](#forexsymbol)
