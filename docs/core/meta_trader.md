# MetaTrader 
The MetaTrader Class provides an asynchronous wrapper around the MetaTrader5 API.

## Table of Contents
- [MetaTrader](#meta_trader.meta_trader)
- [\__aenter\__](#meta_trader.__aenter__)
- [\__aexit\__](#meta_trader.__aexit__)
- [login](#meta_trader.login)
- [initialize](#meta_trader.initialize)
- [login_sync](#meta_trader.login_sync)
- [initialize_sync](#meta_trader.initialize_sync)
- [shutdown](#meta_trader.shutdown)
- [version](#meta_trader.version)
- [account_info](#meta_trader.account_info)
- [terminal_info](#meta_trader.terminal_info)
- [last_error](#meta_trader.last_error)
- [symbols_total](#meta_trader.symbols_total)
- [symbols_get](#meta_trader.symbols_get)
- [symbol_info](#meta_trader.symbol_info)
- [symbol_info_tick](#meta_trader.symbol_info_tick)
- [symbol_select](#meta_trader.symbol_select)
- [market_book_add](#meta_trader.market_book_add)
- [market_book_get](#meta_trader.market_book_get)
- [market_book_release](#meta_trader.market_book_release)
- [copy_rates_from](#meta_trader.copy_rates_from)
- [copy_rates_from_pos](#meta_trader.copy_rates_from_pos)
- [copy_rates_range](#meta_trader.copy_rates_range)
- [copy_ticks_from](#meta_trader.copy_ticks_from)
- [copy_ticks_range](#meta_trader.copy_ticks_range)
- [orders_total](#meta_trader.orders_total)
- [orders_get](#meta_trader.orders_get)
- [order_calc_margin](#meta_trader.order_calc_margin)
- [order_calc_profit](#meta_trader.order_calc_profit)
- [order_check](#meta_trader.order_check)
- [order_send](#meta_trader.order_send)
- [positions_total](#meta_trader.positions_total)
- [positions_get](#meta_trader.positions_get)
- [history_orders_total](#meta_trader.history_orders_total)
- [history_orders_get](#meta_trader.history_orders_get)
- [history_deals_total](#meta_trader.history_deals_total)
- [history_deals_get](#meta_trader.history_deals_get)

<a id="meta_trader.meta_trader"></a>
### MetaTrader
```python
class MetaTrader(MetaCore)
```
The MetaTrader class is a wrapper around the MetaTrader terminal.
It provides methods for connecting to the MetaTrader terminal and retrieving data from it.

#### Attributes:
| Name  | Type  | Description                                            | Default                |
|-------|-------|--------------------------------------------------------|------------------------|
| error | Error | The last error encountered by the MetaTrader terminal. | Error(1, 'Successful') |

#### Notes:
All the attributes, enums and constants of the MetaTrader5 class are also available here. Although, they are more easily
accessible and used via the various enums and models defined in the module.


<a id="meta_trader.__aenter__"></a> 
### \__aenter\__ 
```python
async def __aenter__() -> 'MetaTrader'
```
Async context manager entry point.
Initializes the connection to the MetaTrader terminal.

#### Returns:
| Type         | Description                         |
|--------------|-------------------------------------|
| `MetaTrader` | An instance of the MetaTrader class |


<a id="meta_trader.__aexit__"></a> 
### \__aexit\__
```python
async def __aexit__(exc_type, exc_val, exc_tb)
```
Async context manager exit point. Closes the connection to the MetaTrader terminal.


<a id="meta_trader.login"></a>
### login
```python
async def login(*, login: int, password: str, server: str, timeout: int = 60000) -> bool
```
Connects to the MetaTrader terminal using the specified login, password and server.

#### Parameters:
| Name       | Type  | Description                                |
|------------|-------|--------------------------------------------|
| `login`    | `int` | The trading account number.                |
| `password` | `str` | The trading account password.              |
| `server`   | `str` | The trading server name.                   |
| `timeout`  | `int` | The timeout for the connection in seconds. |

#### Returns:
| Type   | Description                          |
|--------|--------------------------------------|
| `bool` | True if successful, False otherwise. |


<a id="meta_trader.login_sync"></a>
#### login_sync
```python
async def login_sync(*, login: int, password: str, server: str, timeout: int = 60000) -> bool
```
A synchronous version of the login method.
Connects to the MetaTrader terminal using the specified login, password and server.

#### Parameters:
| Name       | Type  | Description                                |
|------------|-------|--------------------------------------------|
| `login`    | `int` | The trading account number.                |
| `password` | `str` | The trading account password.              |
| `server`   | `str` | The trading server name.                   |
| `timeout`  | `int` | The timeout for the connection in seconds. |

#### Returns:
| Type   | Description                          |
|--------|--------------------------------------|
| `bool` | True if successful, False otherwise. |


<a id="meta_trader.initialize"></a>
### initialize
```python
async def initialize(path: str = "", login: int = 0, password: str = "", server: str = "",
                     timeout: int | None = None, portable=False) -> bool
```
Initializes the connection to the MetaTrader terminal. All parameters are optional.

#### Parameters:
| Name       | Type          | Description                                              |
|------------|---------------|----------------------------------------------------------|
| `path`     | `str`         | The path to the MetaTrader terminal executable.          |
| `login`    | `int`         | The trading account number.                              |
| `password` | `str`         | The trading account password.                            |
| `server`   | `str`         | The trading server name.                                 |
| `timeout`  | `int \| None` | The timeout for the connection in seconds.               |
| `portable` | `bool`        | If True, the terminal will be launched in portable mode. |

#### Returns:
| Type   | Description                          |
|--------|--------------------------------------|
| `bool` | True if successful, False otherwise. |


<a id="meta_trader.initialize_sync"></a>
### initialize_sync
```python
async def initialize_sync(path: str = "", login: int = 0, password: str = "", server: str = "",
                          timeout: int | None = None, portable=False) -> bool
```
Initializes the connection to the MetaTrader terminal. All parameters are optional.

#### Parameters:
| Name       | Type          | Description                                              |
|------------|---------------|----------------------------------------------------------|
| `path`     | `str`         | The path to the MetaTrader terminal executable.          |
| `login`    | `int`         | The trading account number.                              |
| `password` | `str`         | The trading account password.                            |
| `server`   | `str`         | The trading server name.                                 |
| `timeout`  | `int \| None` | The timeout for the connection in seconds.               |
| `portable` | `bool`        | If True, the terminal will be launched in portable mode. |

#### Returns:
| Type   | Description                          |
|--------|--------------------------------------|
| `bool` | True if successful, False otherwise. |


<a id="meta_trader.shutdown"></a>
### shutdown
```python
async def shutdown() -> None
```
Closes the connection to the MetaTrader terminal.


<a id="meta_trader.version"></a>
### version
```python
async def version() -> tuple[int, int, str] | None
```
Returns the version of the MetaTrader terminal.

#### Returns:
| Type                   | Description                                                                                   |
|------------------------|-----------------------------------------------------------------------------------------------|
| `tuple[int, int, str]` | A tuple of the MetaTrader terminal version. `Terminal Version`, `Build`, `Build Release Date` |


<a id="meta_trader.account_info"></a>
### account_info
```python
async def account_info() -> AccountInfo | None
```
Returns the account information for the connected account.

#### Returns:
| Type          | Description                          |
|---------------|--------------------------------------|
| `AccountInfo` | An instance of the AccountInfo class |


<a id="meta_trader.terminal_info"></a>
### terminal_info
```python
async def terminal_info() -> TerminalInfo | None
```

Returns the terminal information for the connected terminal.
### Returns
| Type           | Description                                    |
|----------------|------------------------------------------------|
| `TerminalInfo` | An instance of the TerminalInfo class. A tuple |


<a id="meta_trader.last_error"></a>
### last_error
```python
async def last_error() -> tuple[int, str]
```
Returns the last error code and description.

#### Returns:
| Type              | Description                                     |
|-------------------|-------------------------------------------------|
| `tuple[int, str]` | A tuple of the last error code and description. |


<a id="meta_trader.symbols_total"></a>
### symbols_total
```python
async def symbols_total() -> int
```
Returns the total number of symbols.

#### Returns:
| Type  | Description                  |
|-------|------------------------------|
| `int` | The total number of symbols. |


<a id="meta_trader.symbols_get"></a>
### symbols_get
```python
async def symbols_get(group: str = "") -> tuple[SymbolInfo] | None
```
Returns the symbol information for all symbols or for a specified group.

#### Parameters:
| Name    | Type  | Description                                                                                                                                            |
|---------|-------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| `group` | `str` | The group name. Optional named parameter. If the group is specified, the function returns only symbols meeting a specified criteria for a symbol name. |

#### Returns:
| Type                | Description                    |
|---------------------|--------------------------------|
| `tuple[SymbolInfo]` | A tuple of SymbolInfo objects. |


<a id="meta_trader.symbol_info"></a>
### symbol_info
```python
async def symbol_info(symbol: str) -> SymbolInfo | None
```
Returns the symbol information for the specified symbol.

#### Parameters:
| Name     | Type  | Description      |
|----------|-------|------------------|
| `symbol` | `str` | The symbol name. |

#### Returns:
| Type         | Description                          |
|--------------|--------------------------------------|
| `SymbolInfo` | An instance of the SymbolInfo class. |


<a id="meta_trader.symbol_info_tick"></a>
### symbol_info_tick
```python
async def symbol_info_tick(symbol: str) -> Tick | None
```
Returns the latest tick for the specified symbol.

#### Parameters:
| Name     | Type  | Description      |
|----------|-------|------------------|
| `symbol` | `str` | The symbol name. |

#### Returns:
| Type   | Description                    |
|--------|--------------------------------|
| `Tick` | An instance of the Tick class. |


<a id="meta_trader.symbol_select"></a>
### symbol_select
```python
async def symbol_select(symbol: str, enable: bool) -> bool
```
Selects or unselects the specified symbol in the Market Watch window.

#### Parameters:
| Name     | Type   | Description                                                                    |
|----------|--------|--------------------------------------------------------------------------------|
| `symbol` | `str`  | The symbol name.                                                               |
| `enable` | `bool` | If True, the symbol will be selected. If False, the symbol will be unselected. |

#### Returns:
| Type   | Description                          |
|--------|--------------------------------------|
| `bool` | True if successful, False otherwise. |


<a id="meta_trader.market_book_add"></a>
### market_book_add
```python
async def market_book_add(symbol: str) -> bool
```
Adds the specified symbol to the market book.

#### Parameters:
| Name     | Type  | Description      |
|----------|-------|------------------|
| `symbol` | `str` | The symbol name. |

#### Returns:
| Type   | Description                          |
|--------|--------------------------------------|
| `bool` | True if successful, False otherwise. |


<a id="meta_trader.market_book_get"></a>
### market_book_get
```python
async def market_book_get(symbol: str) -> tuple[BookInfo] | None
```
Returns the market depth for the specified symbol.

#### Parameters:
| Name     | Type  | Description      |
|----------|-------|------------------|
| `symbol` | `str` | The symbol name. |

#### Returns:
| Type              | Description                  |
|-------------------|------------------------------|
| `tuple[BookInfo]` | A tuple of BookInfo objects. |


<a id="meta_trader.market_book_release"></a>
### market_book_release
```python
async def market_book_release(symbol: str) -> bool
```
Removes the specified symbol from the market book.

#### Parameters:
| Name     | Type  | Description      |
|----------|-------|------------------|
| `symbol` | `str` | The symbol name. |

#### Returns:
| Type   | Description                          |
|--------|--------------------------------------|
| `bool` | True if successful, False otherwise. |


<a id="meta_trader.copy_rates_from"></a>
### copy_rates_from
```python
async def copy_rates_from(symbol: str, timeframe: TimeFrame, date_from: datetime | int,
                          count: int) -> numpy.ndarray | None
``` 
Returns the OHLCV rates for the specified symbol and timeframe starting from the specified date.

#### Parameters:
| Name        | Type                | Description                    |
|-------------|---------------------|--------------------------------|
| `symbol`    | `str`               | The symbol name.               |
| `timeframe` | `TimeFrame`         | The timeframe.                 |
| `date_from` | `datetime` or `int` | The date to start from.        |
| `count`     | `int`               | The number of rates to return. |

#### Returns:
| Type            | Description                   |
|-----------------|-------------------------------|
| `numpy.ndarray` | A numpy array of OHLCV rates. |


<a id="meta_trader.copy_rates_from_pos"></a>
### copy_rates_from_pos 
```python
async def copy_rates_from_pos(symbol: str, timeframe: TimeFrame, start_pos: int, count: int) -> numpy.ndarray | None
```
Returns the OHLCV rates for the specified symbol and timeframe starting from the specified position.

#### Parameters:
| Name        | Type        | Description                    |
|-------------|-------------|--------------------------------|
| `symbol`    | `str`       | The symbol name.               |
| `timeframe` | `TimeFrame` | The timeframe.                 |
| `start_pos` | `int`       | The position to start from.    |
| `count`     | `int`       | The number of rates to return. |

#### Returns:
| Type            | Description                   |
|-----------------|-------------------------------|
| `numpy.ndarray` | A numpy array of OHLCV rates. |


<a id="meta_trader.copy_rates_range"></a>
### copy_rates_range
```python
async def copy_rates_range(symbol: str, timeframe: TimeFrame, date_from: datetime | int,
                           date_to: datetime | int) -> numpy.ndarray | None
```
Returns the OHLCV rates for the specified symbol and timeframe between the specified dates.

#### Parameters:
| Name        | Type                | Description      |
|-------------|---------------------|------------------|
| `symbol`    | `str`               | The symbol name. |
| `timeframe` | `TimeFrame`         | The timeframe.   |
| `date_from` | `datetime` or `int` | The start date.  |
| `date_to`   | `datetime` or `int` | The end date.    |

#### Returns:
| Type            | Description                   |
|-----------------|-------------------------------|
| `numpy.ndarray` | A numpy array of OHLCV rates. |


<a id="meta_trader.copy_ticks_from"></a>
### copy_ticks_from
```python
async def copy_ticks_from(symbol: str, date_from: datetime | int, count: int, flags: CopyTicks) -> tuple[Tick] | None
```
Returns the ticks for the specified symbol starting from the specified date.

#### Parameters:
| Name        | Type                | Description                    |
|-------------|---------------------|--------------------------------|
| `symbol`    | `str`               | The symbol name.               |
| `date_from` | `datetime` or `int` | The date to start from.        |
| `count`     | `int`               | The number of ticks to return. |
| `flags`     | `CopyTicks`         | The CopyTicks flags.           |

#### Returns:
| Type          | Description              |
|---------------|--------------------------|
| `tuple[Tick]` | A tuple of Tick objects. |


<a id="meta_trader.copy_ticks_range"></a>
### copy_ticks_range
```python
async def copy_ticks_range(symbol: str, date_from: datetime | int, date_to: datetime | int,
                           flags: CopyTicks) -> tuple[Tick] | None
```
Returns the ticks for the specified symbol between the specified dates.

#### Parameters:
| Name        | Type                | Description          |
|-------------|---------------------|----------------------|
| `symbol`    | `str`               | The symbol name.     |
| `date_from` | `datetime` or `int` | The start date.      |
| `date_to`   | `datetime` or `int` | The end date.        |
| `flags`     | `CopyTicks`         | The CopyTicks flags. |

#### Returns:
| Type          | Description              |
|---------------|--------------------------|
| `tuple[Tick]` | A tuple of Tick objects. |


<a id="meta_trader.orders_total"></a>
### orders_total
```python
async def orders_total() -> int
```
Returns the total number of active orders.

#### Returns:
| Type  | Description                        |
|-------|------------------------------------|
| `int` | The total number of active orders. |


<a id="meta_trader.orders_get"></a>
### orders_get
```python
async def orders_get(group: str = "", ticket: int = 0, symbol: str = "") -> tuple[TradeOrder, ...] | None
```
Get active orders with the ability to filter by symbol or ticket. There are three call options.
Call without parameters. Return active orders on all symbols

#### Parameters:
| Name     | Type  | Description                                                                                                                                                                                         |
|----------|-------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `group`  | `str` | The filter for arranging a group of necessary symbols. Optional named parameter. If the group is specified, the function returns only active orders meeting a specified criteria for a symbol name. |
| `ticket` | `int` | Order ticket (ORDER_TICKET). Optional named parameter.                                                                                                                                              |
| `symbol` | `str` | Symbol name. Optional named parameter. If a symbol is specified, the ticket parameter is ignored.                                                                                                   |

#### Returns:
| Type                     | Description                                          |
|--------------------------|------------------------------------------------------|
| `tuple[TradeOrder, ...]` | A tuple of active trade orders as TradeOrder objects |


<a id="meta_trader.order_calc_margin"></a>
### order_calc_margin
```python
async def order_calc_margin(action: OrderType, symbol: str, volume: float, price: float) -> float | None
```
Calculates the margin required to open a trade.

#### Parameters:
| Name     | Type        | Description       |
|----------|-------------|-------------------|
| `action` | `OrderType` | The order type.   |
| `symbol` | `str`       | The symbol name.  |
| `volume` | `float`     | The order volume. |
| `price`  | `float`     | The order price.  |

#### Returns:
| Type    | Description                          |
|---------|--------------------------------------|
| `float` | The margin required to open a trade. |


<a id="meta_trader.order_calc_profit"></a>
### order_calc_profit
```python
async def order_calc_profit(action: OrderType, symbol: str, volume: float, price_open: float,
                            price_close: float) -> float | None
```
Calculates the profit for a closed trade.

#### Parameters:
| Name          | Type        | Description            |
|---------------|-------------|------------------------|
| `action`      | `OrderType` | The order type.        |
| `symbol`      | `str`       | The symbol name.       |
| `volume`      | `float`     | The order volume.      |
| `price_open`  | `float`     | The order open price.  |
| `price_close` | `float`     | The order close price. |

#### Returns:
| Type    | Description                    |
|---------|--------------------------------|
| `float` | The profit for a closed trade. |


<a id="meta_trader.order_check"></a>
### order_check
```python
async def order_check(request: dict) -> OrderCheckResult
```
Checks the specified order for validity.

#### Parameters:
| Name      | Type   | Description        |
|-----------|--------|--------------------|
| `request` | `dict` | The order request. |

#### Returns:
| Type               | Description                                |
|--------------------|--------------------------------------------|
| `OrderCheckResult` | An instance of the OrderCheckResult class. |


<a id="meta_trader.order_send"></a>
### order_send
```python
async def order_send(request: dict) -> OrderSendResult
```
Sends the specified order request to the MetaTrader terminal.

#### Parameters:
| Name      | Type   | Description        |
|-----------|--------|--------------------|
| `request` | `dict` | The order request. |

#### Returns:
| Type              | Description                               |
|-------------------|-------------------------------------------|
| `OrderSendResult` | An instance of the OrderSendResult class. |


<a id="meta_trader.positions_total"></a>
### positions_total
```python
async def positions_total() -> int
```
Returns the total number of open positions.

#### Returns:
| Type  | Description                         |
|-------|-------------------------------------|
| `int` | The total number of open positions. |


<a id="meta_trader.positions_get"></a>
### positions_get
```python
async def positions_get(group: str = "", ticket: int = 0, symbol: str = "") -> tuple[TradePosition, ...] | None
```
Returns the open positions with the ability to filter by symbol or ticket. There are three call options.
Call without parameters. Return open positions on all symbols

#### Parameters:
| Name     | Type  | Description                                                                                                                                                                                          |
|----------|-------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `group`  | `str` | The filter for arranging a group of necessary symbols. Optional named parameter. If the group is specified, the function returns only open positions meeting a specified criteria for a symbol name. |
| `ticket` | `int` | Position ticket (POSITION_TICKET). Optional named parameter.                                                                                                                                         |
| `symbol` | `str` | Symbol name. Optional named parameter. If a symbol is specified, the ticket parameter is ignored.                                                                                                    |

#### Returns:
| Type                        | Description                                              |
|-----------------------------|----------------------------------------------------------|
| `tuple[TradePosition, ...]` | A tuple of open trade positions as TradePosition objects |


<a id="meta_trader.history_orders_total"></a>
### history_orders_total
```python
async def history_orders_total(date_from: datetime | int, date_to: datetime | int) -> int
```
Returns the total number of closed orders for the specified period.

#### Parameters:
| Name        | Type                | Description     |
|-------------|---------------------|-----------------|
| `date_from` | `datetime` or `int` | The start date. |
| `date_to`   | `datetime` or `int` | The end date.   |

#### Returns:
| Type  | Description                                                 |
|-------|-------------------------------------------------------------|
| `int` | The total number of closed orders for the specified period. |


<a id="meta_trader.history_orders_get"></a>
### history_orders_get
```python
async def history_orders_get(date_from: datetime | int = None, date_to: datetime | int = None, group: str = "",
                             ticket: int = 0, position: int = 0) -> tuple[TradeOrder, ...] | None
```
Returns the closed orders for the specified period with the ability to filter by symbol or ticket. There are three call options.
Call without parameters. Return closed orders on all symbols

#### Parameters:
| Name        | Type                | Description                                                                                                                                                                                         |
|-------------|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `date_from` | `datetime` or `int` | The start date. Optional named parameter.                                                                                                                                                           |
| `date_to`   | `datetime` or `int` | The end date. Optional named parameter.                                                                                                                                                             |
| `group`     | `str`               | The filter for arranging a group of necessary symbols. Optional named parameter. If the group is specified, the function returns only closed orders meeting a specified criteria for a symbol name. |
| `ticket`    | `int`               | Order ticket (ORDER_TICKET). Optional named parameter.                                                                                                                                              |
| `position`  | `int`               | Position ticket (POSITION_TICKET). Optional named parameter.                                                                                                                                        |

#### Returns:
| Type                     | Description                                          |
|--------------------------|------------------------------------------------------|
| `tuple[TradeOrder, ...]` | A tuple of closed trade orders as TradeOrder objects |


<a id="meta_trader.history_deals_total"></a>
### history_deals_total
```python
async def history_deals_total(date_from: datetime | int, date_to: datetime | int) -> int
```
Returns the total number of closed deals for the specified period.

#### Parameters:
| Name        | Type                | Description     |
|-------------|---------------------|-----------------|
| `date_from` | `datetime` or `int` | The start date. |
| `date_to`   | `datetime` or `int` | The end date.   |

#### Returns:
| Type  | Description                                                |
|-------|------------------------------------------------------------|
| `int` | The total number of closed deals for the specified period. |

<a id="meta_trader.history_deals_get"></a>
### history_deals_get
```python
async def history_deals_get(date_from: datetime | int = None, date_to: datetime | int = None, group: str = "",
                            ticket: int = 0,position: int = 0) -> tuple[TradeDeal, ...] | None
```
Returns the closed deals for the specified period with the ability to filter by symbol or ticket. There are three call options.
Call without parameters. Return closed deals on all symbols

#### Parameters:
| Name        | Type                | Description                                                                                                                                                                                        |
|-------------|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `date_from` | `datetime` or `int` | The start date. Optional named parameter.                                                                                                                                                          |
| `date_to`   | `datetime` or `int` | The end date. Optional named parameter.                                                                                                                                                            |
| `group`     | `str`               | The filter for arranging a group of necessary symbols. Optional named parameter. If the group is specified, the function returns only closed deals meeting a specified criteria for a symbol name. |
| `ticket`    | `int`               | Order ticket (ORDER_TICKET). Optional named parameter.                                                                                                                                             |
| `position`  | `int`               | Position ticket (POSITION_TICKET). Optional named parameter.                                                                                                                                       |

#### Returns:
| Type                    | Description                                        |
|-------------------------|----------------------------------------------------|
| `tuple[TradeDeal, ...]` | A tuple of closed trade deals as TradeDeal objects |
