# Symbol
Symbol class for handling a financial instrument.

## Table of Contents
- [Symbol](#Symbol)
  - [info_tick](#info_tick)
  - [symbol_select](#symbol_select)
  - [info](#info)
  - [init](#init)
  - [book_add](#book_add)
  - [book_get](#book_get)
  - [book_release](#book_release)
  - [compute_volume](#compute_volume)
  - [currency_conversion](#currency_conversion)
  - [convert_currency](#convert_currency)
  - [copy_rates_from](#copy_rates_from)
  - [copy_rates_from_pos](#copy_rates_from_pos)
  - [copy_rates_range](#copy_rates_range)
  - [copy_ticks_from](#copy_ticks_from)
  - [copy_ticks_range](#copy_ticks_range)
  - [check_volume](#check_volume)
  - [round_off_volume](#round_off_volume)

<a id="Symbol"></a>
### Symbol
```python
class Symbol(SymbolInfo)
```
Main class for handling a financial instrument. A subclass of `SymbolInfo` where most of the attributes are defined.
for working with a financial instrument. 
#### Attributes
| Name      | Type         | Description                           | Default |
|-----------|--------------|---------------------------------------|---------|
| `name`    | `str`        | The name of the symbol.               | None    |
| `mt5`     | `MetaTrader` | MetaTrader instance.                  | None    |
| `config`  | `Config`     | Config instance.                      | None    |
| `account` | `Account`    | Account instance.                     | None    |
| `tick`    | `Tick`       | The current price tick of the symbol. | None    |

#### Notes
Full properties are on the SymbolInfo Object.
Make sure Symbol is always initialized with a name argument

<a id="info_tick"></a>
### info\_tick
```python
async def info_tick(*, name: str = "") -> Tick
```
Get the current price tick of a financial instrument.
#### Parameters
| Name   | Type  | Description             | Default |
|--------|-------|-------------------------|---------|
| `name` | `str` | The name of the symbol. | ''      |
#### Returns
| Type   | Description          |
|--------|----------------------|
| `Tick` | Return a Tick Object |
#### Raises
| Exception    | Description                                       |
|--------------|---------------------------------------------------|
| `ValueError` | If request was unsuccessful and None was returned |

<a id="symbol_select"></a>
### symbol\_select
```python
async def symbol_select(*, enable: bool = True) -> bool
```
Select a symbol in the MarketWatch window or remove a symbol from the window.
Update the select property
#### Parameters
| Name     | Type   | Description                                                                                             | Default |
|----------|--------|---------------------------------------------------------------------------------------------------------|---------|
| `enable` | `bool` | Switch. Optional unnamed parameter. If 'false', a symbol should be removed from the MarketWatch window. | None    |
#### Returns
| Type   | Description                          |
|--------|--------------------------------------|
| `bool` | True if successful, otherwise False. |

<a id="info"></a>
### info
```python
async def info() -> SymbolInfo
```
Get data on the specified financial instrument and update the symbol object properties
#### Returns
| Type         | Description              |
|--------------|--------------------------|
| `SymbolInfo` | SymbolInfo if successful |
#### Raises
| Exception    | Description                                       |
|--------------|---------------------------------------------------|
| `ValueError` | If request was unsuccessful and None was returned |

<a id="init"></a>
### init
```python
async def init() -> bool
```
Initialized the symbol by pulling properties from the terminal
#### Returns
| Type   | Description                                            |
|--------|--------------------------------------------------------|
| `bool` | Returns True if symbol info was successful initialized |

<a id="book_add"></a>
### book\_add
```python
async def book_add() -> bool
```
Subscribes the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.
If the symbol is not in the list of instruments for the market, This method will return False
#### Returns
| Type   | Description                          |
|--------|--------------------------------------|
| `bool` | True if successful, otherwise False. |

<a id="book_get"></a>
### book\_get
```python
async def book_get() -> tuple[BookInfo]
```
Returns a tuple of BookInfo featuring Market Depth entries for the specified symbol.
#### Returns
| Type              | Description                                                       |
|-------------------|-------------------------------------------------------------------|
| `tuple[BookInfo]` | Returns the Market Depth contents as a tuples of BookInfo Objects |
#### Raises
| Exception    | Description                                       |
|--------------|---------------------------------------------------|
| `ValueError` | If request was unsuccessful and None was returned |

<a id="book_release"></a>
### book\_release
```python
async def book_release() -> bool
```
Cancels subscription of the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.
#### Returns
| Type   | Description                          |
|--------|--------------------------------------|
| `bool` | True if successful, otherwise False. |

<a id="compute_volume"></a>
### compute_volume
```python
async def compute_volume(*args, **kwargs) -> float
```
Computes the volume of a trade based on the amount or any other parameter.
This is a dummy method that returns the minimum volume of the symbol. It is meant to be overridden by a subclass.

#### Parameters
| Name         | Type    | Description                                                                                                                                                                                                | Default |
|--------------|---------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| `amount`     | `float` | Amount to risk in the trade                                                                                                                                                                                | None    |
| `points`     | `float` | Number of pips to target                                                                                                                                                                                   | None    |
| `use_limits` | `bool`  | If True, the minimum volume is returned if the computed volume is less than the minimum volume and the maximum volume is returned if the computed volume is greater than the maximum volume for the symbol | False   |
#### Returns
| Type    | Description                     |
|---------|---------------------------------|
| `float` | Returns the volume of the trade |

<a id="currency_conversion"></a>
### currency\_conversion
```python
async def currency_conversion(*, amount: float, base: str,
                              quote: str) -> float
```
Convert from one currency to the other. Returns the amount in terms of the base currency.
#### Parameters
| Name     | Type    | Description                                            | Default |
|----------|---------|--------------------------------------------------------|---------|
| `amount` | `float` | Amount to convert given in terms of the quote currency | None    |
| `base`   | `str`   | The base currency of the pair                          | None    |
| `quote`  | `str`   | The quote currency of the pair                         | None    |
#### Returns
| Type    | Description                          |
|---------|--------------------------------------|
| `float` | Amount in terms of the base currency |
#### Raises
| Exception    | Description          |
|--------------|----------------------|
| `ValueError` | If conversion failed |

<a id="convert_currency"></a>
```python
async def convert_currency(self, *, amount: float, base: str, quote: str) -> float:
```
Alias for currency_conversion

<a id="copy_rates_from"></a>
### copy\_rates\_from
```python
async def copy_rates_from(*,
                          timeframe: TimeFrame,
                          date_from: datetime | int,
                          count: int = 500) -> Candles
```
Get bars from the MetaTrader 5 terminal starting from the specified date.
#### Parameters
| Name        | Type            | Description                                                                                                                                  | Default                    |
|-------------|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------|----------------------------|
| `timeframe` | `TimeFrame`     | Timeframe the bars are requested for. Set by a value from the TimeFrame enumeration.                                                         | Required unnamed parameter |
| `date_from` | `datetime, int` | Date of opening of the first bar from the requested sample. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. | Required unnamed parameter |
| `count`     | `int`           | Number of bars to receive.                                                                                                                   | Required unnamed parameter |
#### Returns
| Type      | Description                                                               |
|-----------|---------------------------------------------------------------------------|
| `Candles` | Returns a Candles object as a collection of rates ordered chronologically |
#### Raises
| Exception    | Description                                       |
|--------------|---------------------------------------------------|
| `ValueError` | If request was unsuccessful and None was returned |

<a id="copy_rates_from_pos"></a>
### copy\_rates\_from\_pos
```python
async def copy_rates_from_pos(*,
                              timeframe: TimeFrame,
                              count: int = 500,
                              start_position: int = 0) -> Candles
```
Get bars from the MetaTrader 5 terminal starting from the specified index.
#### Parameters
| Name             | Type        | Description                                                                                                                                                                      | Default                         |
|------------------|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|
| `timeframe`      | `TimeFrame` | TimeFrame value from TimeFrame Enum. Required keyword only parameter                                                                                                             | Required keyword only parameter |
| `count`          | `int`       | Number of bars to return. Keyword argument defaults to 500                                                                                                                       | 500                             |
| `start_position` | `int`       | Initial index of the bar the data are requested from. The numbering of bars goes from present to past. Thus, the zero bar means the current one. Keyword argument defaults to 0. | 0                               |
#### Returns
| Type      | Description                                                                |
|-----------|----------------------------------------------------------------------------|
| `Candles` | Returns a Candles object as a collection of rates ordered chronologically. |
#### Raises
| Exception    | Description                                       |
|--------------|---------------------------------------------------|
| `ValueError` | If request was unsuccessful and None was returned |

<a id="copy_rates_range"></a>
### copy\_rates\_range
```python
async def copy_rates_range(*, timeframe: TimeFrame, date_from: datetime | int,
                           date_to: datetime | int) -> Candles
```
Get bars in the specified date range from the MetaTrader 5 terminal.
#### Parameters
| Name        | Type          | Description                                                                                                                                                                                             | Default                    |
|-------------|---------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------|
| `timeframe` | `TimeFrame`   | Timeframe for the bars using the TimeFrame enumeration. Required unnamed parameter.                                                                                                                     | Required unnamed parameter |
| date_from   | datetime, int | Date the bars are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Bars with the open time >= date_from are returned. Required unnamed parameter.       | Required unnamed parameter |
| date_to     | datetime, int | Date, up to which the bars are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Bars with the open time <= date_to are returned. Required unnamed parameter. | Required unnamed parameter |
#### Returns
| Type      | Description                                                                |
|-----------|----------------------------------------------------------------------------|
| `Candles` | Returns a Candles object as a collection of rates ordered chronologically. |
#### Raises
| Exception    | Description                                       |
|--------------|---------------------------------------------------|
| `ValueError` | If request was unsuccessful and None was returned |

<a id="copy_ticks_from"></a>
### copy\_ticks\_from
```python
async def copy_ticks_from(*,
                          date_from: datetime | int,
                          count: int = 100,
                          flags: CopyTicks = CopyTicks.ALL) -> Ticks
```
Get ticks from the MetaTrader 5 terminal starting from the specified date.
#### Parameters
| Name        | Type            | Description                                                                                                         | Default                    |
|-------------|-----------------|---------------------------------------------------------------------------------------------------------------------|----------------------------|
| `date_from` | `datetime, int` | Date the ticks are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. | Required unnamed parameter |
| `count`     | `int`           | Number of requested ticks. Defaults to 100                                                                          | Required unnamed parameter |
| `flags`     | `CopyTicks`     | A flag to define the type of the requested ticks from CopyTicks enum. INFO is the default                           | Required unnamed parameter |
#### Returns
| Type    | Description                                                              |
|---------|--------------------------------------------------------------------------|
| `Ticks` | Returns a Ticks object as a collection of ticks ordered chronologically. |
#### Raises
| Exception    | Description                                       |
|--------------|---------------------------------------------------|
| `ValueError` | If request was unsuccessful and None was returned |

<a id="copy_ticks_range"></a>
### copy\_ticks\_range
```python
async def copy_ticks_range(*,
                           date_from: datetime | int,
                           date_to: datetime | int,
                           flags: CopyTicks = CopyTicks.ALL) -> Ticks
```
Get ticks for the specified date range from the MetaTrader 5 terminal.
#### Parameters
| Name        | Type            | Description                                                                                                                 | Default                    |
|-------------|-----------------|-----------------------------------------------------------------------------------------------------------------------------|----------------------------|
| `date_from` | `datetime, int` | Date the ticks are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01.         | Required unnamed parameter |
| `date_to`   | `datetime, int` | Date, up to which the ticks are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. | Required unnamed parameter |
| `flags`     | `CopyTicks`     | A flag to define the type of the requested ticks from CopyTicks enum. INFO is the default                                   | Required unnamed parameter |
#### Returns
| Type    | Description                                                              |
|---------|--------------------------------------------------------------------------|
| `Ticks` | Returns a Ticks object as a collection of ticks ordered chronologically. |
#### Raises
| Exception    | Description                                       |
|--------------|---------------------------------------------------|
| `ValueError` | If request was unsuccessful and None was returned |

<a id="check_volume"></a>
### check_volume 
```python
async def check_volume(*, volume: float) -> tuple[bool, float]
```
Checks if the volume is within the minimum and maximum volume for the symbol. If not, return the nearest limit.
#### Parameters
| Name   | Type    | Description         | Default |
|--------|---------|---------------------|---------|
| volume | `float` | The volume to check | None    |
#### Returns
| Type                 | Description                                         |
|----------------------|-----------------------------------------------------|
| `tuple[bool, float]` | The boolean is True if the volume is within limits. |

<a id="round_off_volume"></a>
### round_off_volume
```python
async def round_off_volume(*, volume: float, round_down: bool = True) -> float
```
Rounds off the volume to the nearest minimum or maximum volume for the symbol.
#### Parameters
| Name         | Type    | Description               | Default |
|--------------|---------|---------------------------|---------|
| `volume`     | `float` | The volume to round off   | None    |
| `round_down` | `bool`  | To round_up or round_down | True    |
#### Returns
| Type    | Description         |
|---------|---------------------|
| `float` | The rounded volume. |
