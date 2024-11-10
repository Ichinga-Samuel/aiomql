# Symbol
Symbol class for handling a financial instrument.

## Table of Contents
- [Symbol](#symbol.symbol)
- [info_tick](#symbol.info_tick)
- [symbol_select](#symbol.symbol_select)
- [info](#symbol.info)
- [initialize](#symbol.initialize)
- [book_add](#symbol.book_add)
- [book_get](#symbol.book_get)
- [book_release](#symbol.book_release)
- [compute_volume](#symbol.compute_volume)
- [convert_currency](#symbol.convert_currency)
- [copy_rates_from](#symbol.copy_rates_from)
- [copy_rates_from_pos](#symbol.copy_rates_from_pos)
- [copy_rates_range](#symbol.copy_rates_range)
- [copy_ticks_from](#symbol.copy_ticks_from)
- [copy_ticks_range](#symbol.copy_ticks_range)
- [check_volume](#symbol.check_volume)
- [round_off_volume](#symbol.round_off_volume)


<a id="symbol.symbol"></a>
### Symbol
```python
class Symbol(_Base, SymbolInfo)
```
Main class for handling a financial instrument. A subclass of `SymbolInfo` where most of the attributes are defined.
for working with a financial instrument. 

#### Attributes:
| Name      | Type         | Description                           | Default |
|-----------|--------------|---------------------------------------|---------|
| `account` | `Account`    | Account instance.                     | None    |
| `tick`    | `Tick`       | The current price tick of the symbol. | None    |

#### Notes:
Make sure Symbol is always initialized with a name argument.

<a id="symbol.info_tick"></a>
### info_tick
```python
async def info_tick(*, name: str = "") -> Tick
```
Get the current price tick of a financial instrument.

#### Parameters:
| Name   | Type  | Description             | Default |
|--------|-------|-------------------------|---------|
| `name` | `str` | The name of the symbol. | ''      |

#### Returns:
| Type   | Description          |
|--------|----------------------|
| `Tick` | Return a Tick Object |


<a id="symbol.symbol_select"></a>
### symbol_select
```python
async def symbol_select(*, enable: bool = True) -> bool
```
Select a symbol in the MarketWatch window or remove a symbol from the window.
Update the select property

#### Parameters:
| Name     | Type   | Description                                                                                             | Default |
|----------|--------|---------------------------------------------------------------------------------------------------------|---------|
| `enable` | `bool` | Switch. Optional unnamed parameter. If 'false', a symbol should be removed from the MarketWatch window. | None    |

#### Returns:
| Type   | Description                          |
|--------|--------------------------------------|
| `bool` | True if successful, otherwise False. |


<a id="symbol.info"></a>
### info
```python
async def info() -> SymbolInfo
```
Get data on the specified financial instrument and update the symbol object properties

#### Returns:
| Type         | Description              |
|--------------|--------------------------|
| `SymbolInfo` | SymbolInfo if successful |

#### Raises:
| Exception    | Description                                       |
|--------------|---------------------------------------------------|
| `ValueError` | If request was unsuccessful and None was returned |


<a id="symbol.initialize"></a>
### init
```python
async def initialize() -> bool
```

Initialized the symbol by pulling properties from the terminal
#### Returns:
| Type   | Description                                            |
|--------|--------------------------------------------------------|
| `bool` | Returns True if symbol info was successful initialized |


<a id="symbol.book_add"></a>
### book_add
```python
async def book_add() -> bool
```
Subscribes the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.
If the symbol is not in the list of instruments for the market, This method will return False.

#### Returns:
| Type   | Description                          |
|--------|--------------------------------------|
| `bool` | True if successful, otherwise False. |


<a id="symbol.book_get"></a>
### book_get
```python
async def book_get() -> tuple[BookInfo, ...]
```
Returns a tuple of BookInfo featuring Market Depth entries for the specified symbol.
#### Returns:
| Type                   | Description                                                       |
|------------------------|-------------------------------------------------------------------|
| `tuple[BookInfo, ...]` | Returns the Market Depth contents as a tuples of BookInfo Objects |


<a id="symbol.book_release"></a>
### book_release
```python
async def book_release() -> bool
```
Cancels subscription of the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.

#### Returns:
| Type   | Description                          |
|--------|--------------------------------------|
| `bool` | True if successful, otherwise False. |


<a id="symbol.compute_volume"></a>
### compute_volume
```python
async def compute_volume(self) -> float
```
Computes the volume of a trade based on the amount or any other parameter.
This default implementation returns the minimum volume of the symbol. It is meant to be overridden by a subclass.

#### Returns
| Type    | Description                     |
|---------|---------------------------------|
| `float` | Returns the volume of the trade |


<a id="symbol.check_volume"></a>
### check_volume
```python
async def check_volume(*, volume: float) -> tuple[bool, float]
```
Check if the volume is within the limits of permitted volume for 
the symbol. If not, return the nearest limit.

#### Returns:
| Type                 | Description                                                                   |
|----------------------|-------------------------------------------------------------------------------|
| `tuple[bool, float]` | True and the input volume if within bounds, else False and the nearest limit. |


<a id="symbol.round_off_volume"></a>
### round_off_volume
```python
async def round_off_volume(*, volume: float, round_down: bool = False) -> float
```
Round off the volume to the nearest volume step.

#### Parameters:
| Name         | Type    | Description                                       | Default |
|--------------|---------|---------------------------------------------------|---------|
| `volume`     | `float` | The volume                                        |         |
| `round_down` | `float` | Round up or round down to the nearest volume step | False   |

#### Returns:
| Type    | Description                     |
|---------|---------------------------------|
| `float` | Returns the volume of the trade |


<a id="symbol.amount_in_quote_currency"></a>
### amount_in_quote_currency
```python
async def amount_quote_currency(*, amount: float) -> float
```
Convert an amount in the account_currency to the quote currency of the symbol.

#### Parameters:
| Name     | Type    | Description           |
|----------|---------|-----------------------|
| `amount` | `float` | The amount to convert |


<a id="symbol.convert_currency"></a>
### convert_currency
```python
async def convert_currency(*, amount: float, from_currency: str, to_currency: str) -> float
```
Convert from one currency to the other.

#### Parameters:
| Name            | Type    | Description                                            |
|-----------------|---------|--------------------------------------------------------|
| `amount`        | `float` | Amount to convert given in terms of the quote currency |
| `from_currency` | `str`   | The currency to convert from                           |
| `to_currency`   | `str`   | The currency to convert to                             |

#### Returns:
| Type    | Description                          |
|---------|--------------------------------------|
| `float` | Amount in terms of the base currency |


<a id="symbol.copy_rates_from"></a>
### copy_rates_from
```python
async def copy_rates_from(*, timeframe: TimeFrame, date_from: datetime | int, count: int = 500) -> Candles
```
Get bars from the MetaTrader 5 terminal starting from the specified date.

#### Parameters:
| Name        | Type            | Description                                                                                                                                  | Default                    |
|-------------|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------|----------------------------|
| `timeframe` | `TimeFrame`     | Timeframe the bars are requested for. Set by a value from the TimeFrame enumeration.                                                         | Required unnamed parameter |
| `date_from` | `datetime, int` | Date of opening of the first bar from the requested sample. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. | Required unnamed parameter |
| `count`     | `int`           | Number of bars to receive.                                                                                                                   | Required unnamed parameter |

#### Returns:
| Type      | Description                                                               |
|-----------|---------------------------------------------------------------------------|
| `Candles` | Returns a Candles object as a collection of rates ordered chronologically |

#### Raises:
| Exception    | Description                                       |
|--------------|---------------------------------------------------|
| `ValueError` | If request was unsuccessful and None was returned |


<a id="symbol.copy_rates_from_pos"></a>
### copy_rates_from_pos
```python
async def copy_rates_from_pos(*,timeframe: TimeFrame, count: int = 500, start_position: int = 0) -> Candles
```
Get bars from the MetaTrader 5 terminal starting from the specified index.

#### Parameters:
| Name             | Type        | Description                                                                                                                                                                      | Default                         |
|------------------|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|
| `timeframe`      | `TimeFrame` | TimeFrame value from TimeFrame Enum. Required keyword only parameter                                                                                                             | Required keyword only parameter |
| `count`          | `int`       | Number of bars to return. Keyword argument defaults to 500                                                                                                                       | 500                             |
| `start_position` | `int`       | Initial index of the bar the data are requested from. The numbering of bars goes from present to past. Thus, the zero bar means the current one. Keyword argument defaults to 0. | 0                               |

#### Returns:
| Type      | Description                                                                |
|-----------|----------------------------------------------------------------------------|
| `Candles` | Returns a Candles object as a collection of rates ordered chronologically. |

#### Raises:
| Exception    | Description                                       |
|--------------|---------------------------------------------------|
| `ValueError` | If request was unsuccessful and None was returned |

<a id="symbol.copy_rates_range"></a>
### copy_rates_range
```python
async def copy_rates_range(*, timeframe: TimeFrame, date_from: datetime | int,
                           date_to: datetime | int) -> Candles
```
Get bars in the specified date range from the MetaTrader 5 terminal.

#### Parameters:
| Name        | Type          | Description                                                                                                                                                                                             | Default                    |
|-------------|---------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------|
| `timeframe` | `TimeFrame`   | Timeframe for the bars using the TimeFrame enumeration. Required unnamed parameter.                                                                                                                     | Required unnamed parameter |
| date_from   | datetime, int | Date the bars are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Bars with the open time >= date_from are returned. Required unnamed parameter.       | Required unnamed parameter |
| date_to     | datetime, int | Date, up to which the bars are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Bars with the open time <= date_to are returned. Required unnamed parameter. | Required unnamed parameter |

#### Returns:
| Type      | Description                                                                |
|-----------|----------------------------------------------------------------------------|
| `Candles` | Returns a Candles object as a collection of rates ordered chronologically. |

#### Raises:
| Exception    | Description                                       |
|--------------|---------------------------------------------------|
| `ValueError` | If request was unsuccessful and None was returned |


<a id="symbol.copy_ticks_from"></a>
### copy_ticks_from
```python
async def copy_ticks_from(*, date_from: datetime | int, count: int = 100, flags: CopyTicks = CopyTicks.ALL) -> Ticks
```

Get ticks from the MetaTrader 5 terminal starting from the specified date.

#### Parameters:
| Name        | Type            | Description                                                                                                         | Default                    |
|-------------|-----------------|---------------------------------------------------------------------------------------------------------------------|----------------------------|
| `date_from` | `datetime, int` | Date the ticks are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. | Required unnamed parameter |
| `count`     | `int`           | Number of requested ticks. Defaults to 100                                                                          | Required unnamed parameter |
| `flags`     | `CopyTicks`     | A flag to define the type of the requested ticks from CopyTicks enum. INFO is the default                           | Required unnamed parameter |

#### Returns:
| Type    | Description                                                              |
|---------|--------------------------------------------------------------------------|
| `Ticks` | Returns a Ticks object as a collection of ticks ordered chronologically. |

#### Raises:
| Exception    | Description                                       |
|--------------|---------------------------------------------------|
| `ValueError` | If request was unsuccessful and None was returned |


<a id="symbol.copy_ticks_range"></a>
### copy_ticks_range
```python
async def copy_ticks_range(*, date_from: datetime | int, date_to: datetime | int, flags: CopyTicks = CopyTicks.ALL) -> Ticks
```
Get ticks for the specified date range from the MetaTrader 5 terminal.

#### Parameters:
| Name        | Type            | Description                                                                                                                 | Default                    |
|-------------|-----------------|-----------------------------------------------------------------------------------------------------------------------------|----------------------------|
| `date_from` | `datetime, int` | Date the ticks are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01.         | Required unnamed parameter |
| `date_to`   | `datetime, int` | Date, up to which the ticks are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. | Required unnamed parameter |
| `flags`     | `CopyTicks`     | A flag to define the type of the requested ticks from CopyTicks enum. INFO is the default                                   | Required unnamed parameter |

#### Returns:
| Type    | Description                                                              |
|---------|--------------------------------------------------------------------------|
| `Ticks` | Returns a Ticks object as a collection of ticks ordered chronologically. |

#### Raises:
| Exception    | Description                                       |
|--------------|---------------------------------------------------|
| `ValueError` | If request was unsuccessful and None was returned |
