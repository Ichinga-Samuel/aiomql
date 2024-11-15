# BackTestEngine 

## Table of Contents

- [BackTestEngine](#backtest_engine.back_test_engine)
- [\__init\__](#backtest_engine.__init__)
- [setup_test_range](#backtest_engine.setup_test_range)
- [setup_data](#backtest_engine.setup_data)
- [next](#backtest_engine.next)
- [data](#backtest_engine.data)
- [reset](#backtest_engine.reset)
- [go_to](#backtest_engine.go_to)
- [fast_forward](#backtest_engine.fast_forward)
- [tracker](#backtest_engine.tracker)
- [save_result_to_json](#backtest_engine.save_result_to_json)
- [close_all_open](#backtest_engine.close_all_open)
- [wrap_up](#backtest_engine.wrap_up)
- [preload_ticks](#backtest_engine.preload_ticks)
- [get_price_tick](#backtest_engine.get_price_tick)
- [check_order](#backtest_engine.check_order)
- [check_account](#backtest_engine.check_account)
- [check_position](#backtest_engine.check_position)
- [close_position_manually](#backtest_engine.close_position_manually)
- [close_position](#backtest_engine.close_position)
- [modify_stops](#backtest_engine.modify_stops)
- [update_account](#backtest_engine.update_account)
- [deposit](#backtest_engine.deposit)
- [withdraw](#backtest_engine.withdraw)
- [setup_account](#backtest_engine.setup_account)
- [setup_account_sync](#backtest_engine.setup_account_sync)
- [prices](#backtest_engine.prices)
- [ticks](#backtest_engine.ticks)
- [rates](#backtest_engine.rates)
- [symbols](#backtest_engine.symbols)
- [order_send](#backtest_engine.order_send)
- [order_check](#backtest_engine.order_check)
- [get_terminal_info](#backtest_engine.get_terminal_info)
- [get_version](#backtest_engine.get_version)
- [get_symbols_total](#backtest_engine.get_symbols_total)
- [get_symbols](#backtest_engine.get_symbols)
- [get_account_info](#backtest_engine.get_account_info)
- [get_symbol_info_tick](#backtest_engine.get_symbol_info_tick)
- [get_symbol_info](#backtest_engine.get_symbol_info)
- [get_rates_from](#backtest_engine.get_rates_from)
- [get_rates_from_pos](#backtest_engine.get_rates_from_pos)
- [get_rates_range](#backtest_engine.get_rates_range)
- [get_ticks_from](#backtest_engine.get_ticks_from)
- [get_ticks_range](#backtest_engine.get_ticks_range)
- [order_calc_margin](#backtest_engine.order_calc_margin)
- [order_calc_profit](#backtest_engine.order_calc_profit)
- [get_orders_total](#backtest_engine.get_orders_total)
- [get_orders](#backtest_engine.get_orders)
- [get_positions_total](#backtest_engine.get_positions_total)
- [get_positions](#backtest_engine.get_positions)
- [get_history_orders_total](#backtest_engine.get_history_orders_total)
- [get_history_orders](#backtest_engine.get_history_orders)
- [get_history_deals_total](#backtest_engine.get_history_deals_total)
- [get_history_deals](#backtest_engine.get_history_deals)


<a id="backtest_engine.back_test_engine"></a>
#### BackTestEngine
```python
class BackTestEngine
```
The BackTestEngine class is used to simulate trading strategies on historical data that is either preloaded or provided
at runtime during the test.

#### Attributes:
| Name                           | Type           | Description                                                                                         |
|--------------------------------|----------------|-----------------------------------------------------------------------------------------------------|
| `_data`                        | `BackTestData` | The data used for backtesting. This is the data that is saved to disk when the backtest is stopped. |
| `mt5`                          | `MetaTrader`   | The MetaTrader instance for the backtest engine.                                                    |
| `config`                       | `Config`       | The global configuration instance.                                                                  |
| `name`                         | `str`          | The name of the backtest.                                                                           |
| `stop_testing`                 | `bool`         | Whether to stop the backtest.                                                                       |
| `use_terminal`                 | `bool`         | Whether to use the terminal for backtesting.                                                        |
| `close_open_positions_on_exit` | `bool`         | Whether to close all open positions when the backtest is stopped.                                   |
| `stop_time`                    | `int`          | The time to stop the backtest.                                                                      |
| `preload`                      | `bool`         | Whether to preload the ticks for the backtest.                                                      |
| `preloaded_ticks`              | `dict`         | A dictionary of preloaded ticks for the backtest.                                                   |
| `account_lock`                 | `RLock`        | A reentrant lock for the account data.                                                              |
| `account_info`                 | `dict`         | A dictionary of account information for the backtest.                                               |


<a id="backtest_engine.__init__"></a>
#### \__init\__
```python
def __init__(*,
             data: BackTestData = None,
             speed: int = 60,
             start: float | datetime = 0,
             end: float | datetime = 0,
             restart: bool = True,
             use_terminal: bool = None,
             name: str = "",
             stop_time: float | datetime = None,
             close_open_positions_on_exit: bool = True,
             preload=True,
             assign_to_config: bool = True,
             account_info: dict = None)
```
The BackTestEngine class is used to simulate trading strategies on historical data.
It can accept already saved data or create new data for backtesting on the fly. Ideally only one instance of
this class should be created per session. By default it is automatically assigned to the global config instance
during instantiation, replacing any existing backtest engine instance. But this is a configurable behaviour.
The start and end time can still be specified even when test data is provided. In that case it will be used
to set the range of the backtest.


#### Parameters:
| Name                           | Type                | Description                                                                                                                                                                                                                                                                                                                                                         |
|--------------------------------|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `data`                         | `BackTestData`      | The data to use for backtesting. Defaults to None.                                                                                                                                                                                                                                                                                                                  |
| `speed`                        | `int`               | The speed of the backtest. Defaults to 60 seconds.                                                                                                                                                                                                                                                                                                                  |
| `start`                        | `float \| datetime` | The start time of the backtest. Defaults to 0. If a float is passed, it is assumed to be a timestamp.                                                                                                                                                                                                                                                               |
| `end`                          | `float \| datetime` | The end time of the backtest. Defaults to 0. If a float is passed, it is assumed to be a timestamp.                                                                                                                                                                                                                                                                 |
| `restart`                      | `bool`              | Whether to restart the backtest from the beginning. Defaults to True. This is useful when resuming a backtest using a saved BackTestData instance.                                                                                                                                                                                                                  |
| `use_terminal`                 | `bool`              | Whether to use the terminal for backtesting. Defaults to None. If None, it uses the global config setting. If use terminal is true, the backtest engine will use the terminal to get price data, compute margins, profit and check order viability. If false, it will use the data provided in the BackTestData instance and default algorithm for the calculations |
| `name`                         | `str`               | The name of the backtest. Defaults to "". If not provided, it is generated from the start and end times.                                                                                                                                                                                                                                                            |
| `stop_time`                    | `float \| datetime` | The time to stop the backtest. Defaults to None. If a float is passed, it is assumed to be a timestamp. If not given it is assumed to be the end of the backtest range.                                                                                                                                                                                             |
| `close_open_positions_on_exit` | `bool`              | Whether to close all open positions when the backtest is stopped. Defaults to True.                                                                                                                                                                                                                                                                                 |
| `preload`                      | `bool`              | Whether to preload the ticks for the backtest. Defaults to True.                                                                                                                                                                                                                                                                                                    |
| `assign_to_config`             | `bool`              | Whether to assign the backtest engine to the global config instance. Defaults to True.                                                                                                                                                                                                                                                                              |
| `account_info`                 | `dict`              | A dictionary of account information to use for the backtest. Defaults to None. Use this to set the account information for the backtest.                                                                                                                                                                                                                            |


<a id="backtest_engine.setup_test_range"></a>
#### setup_test_range
```python
def setup_test_range(*,
                     start: float | datetime = None,
                     end: float | datetime = None,
                     speed: int = 60,
                     restart: bool = True)
```
Setup the test range for the backtest engine. This is used to set the range of the backtest and the speed
at which it runs.

#### Parameters:
| Name      | Type                | Description                                                                                                            |
|-----------|---------------------|------------------------------------------------------------------------------------------------------------------------|
| `start`   | `float \| datetime` | The start time of the backtest. Defaults to None. If a float is passed, it is assumed to be a timestamp.               |
| `end`     | `float \| datetime` | The end time of the backtest. Defaults to None. If a float is passed, it is assumed to be a timestamp.                 |
| `speed`   | `int`               | The speed of the backtest. Defaults to 60 seconds.                                                                     |
| `restart` | `bool`              | Whether to restart the backtest. Defaults to True. This is useful when resuming a backtest using a saved BackTestData. |


<a id="backtest_engine.setup_data"></a>
#### setup_data
```python
def setup_data(*, restart: bool = True)
```
Sets up the data for the backtest engine. This includes the orders, positions, deals and account
information. This data is handled by specialized classes such as the BackTestAccount and the TradeManager
classes.

#### Parameters:
| Name      | Type   | Description                                    |
|-----------|--------|------------------------------------------------|
| `restart` | `bool` | Whether to restart the data. Defaults to True. |


<a id="backtest_engine.next"></a>
#### next
```python
def next() -> Cursor
```
Move the cursor to the next time step in the backtest range.


<a id="backtest_engine.data"></a>
#### data
```python
@property
def data()
```
The BackTestData instance used for the backtest. If not provided, a new instance is created,
and the data is made persistent when the backtest is stopped.


<a id="backtest_engine.reset"></a>
#### reset
```python
def reset(clear_data: bool = False)
```
Reset the backtest engine. This is useful when restarting the backtest from the beginning. Clear trade data if any
when the `clear_data` parameter is true


<a id="backtest_engine.go_to"></a>
#### go_to
```python
def go_to(*, time: datetime | float)
```
Move the cursor to a specific time in the backtest range. You can pass a datetime object or a timestamp.
You can't go back in time or beyond the limits of the range.


<a id="backtest_engine.fast_forward"></a>
#### fast_forward
```python
def fast_forward(*, steps: int)
```
Fast-forward the backtester by the given steps.


<a id="backtest_engine.tracker"></a>
#### tracker
```python
async def tracker()
```
The tracker monitors and updates open positions on every iteration. It is called by the controller.


<a id="backtest_engine.save_result_to_json"></a>
#### save_result_to_json
```python
@error_handler_sync
def save_result_to_json()
```
Saves the result to a json file at the end of testing.


<a id="backtest_engine.close_all_open"></a>
#### close_all_open
```python
async def close_all_open()
```
Closes all open position at the end of testing

<a id="backtest_engine.wrap_up"></a>
#### wrap_up
```python
@error_handler
async def wrap_up()
```
Wraps up the backtest. This is called at the end of testing to save the results and close all open positions.


<a id="backtest_engine.preload_ticks"></a>
#### preload_ticks
```python
async def preload_ticks(*, symbol: str)
```
Pull a month data on ticks from the terminal. Starting from the current time.

#### Parameters:
| Name     | Type  | Description                      |
|----------|-------|----------------------------------|
| `symbol` | `str` | The symbol to preload ticks for. |


<a id="backtest_engine.get_price_tick"></a>
#### get_price_tick
```python
@async_cache
async def get_price_tick(*, symbol: str, time: int) -> Tick | None
```
Get the price tick for a symbol at a given time. If the preload option is set to True,
it will use the preloaded ticks when available.

#### Parameters:
| Name     | Type  | Description                           |
|----------|-------|---------------------------------------|
| `symbol` | `str` | The symbol to get the price tick for. |
| `time`   | `int` | The time to get the price tick.       |


<a id="backtest_engine.check_order"></a>
#### check_order
```python
@error_handler
async def check_order(*, ticket: int)
```
Check if the order has reached its take profit or stop loss levels and close the order if it has.
Checks only `OrderType.BUY` and `OrderType.SELL` orders that have reached their take profit or stop loss levels.

#### Parameters:
| Name     | Type  | Description  |
|----------|-------|--------------|
| `ticket` | `int` | Order ticket |


<a id="backtest_engine.check_account"></a>
#### check_account
```python
def check_account()
```
Checks an account status. This method is called at each iteration to check if the account has burned out.


<a id="backtest_engine.check_position"></a>
#### check_position
```python
async def check_position(*, ticket: int)
```
Update the profit of an open position based on the current price of the symbol. It is called by the
tracker to update the profit of open positions.

#### Parameters:
| Name     | Type  | Description      |
|----------|-------|------------------|
| `ticket` | `int` | Position ticket  |


<a id="backtest_engine.close_position_manually"></a>
#### close_position_manually
```python
@error_handler_sync
async def close_position_manually(*, ticket: int)
```
Close a position manually without. Usually at the end of testing.


<a id="backtest_engine.close_position"></a>
#### close_position
```python
async def close_position(*, ticket: int) -> bool
```
Close an open position for the trading account using the position ticket.

#### Parameters:
| Name     | Type  | Description      |
|----------|-------|------------------|
| `ticket` | `int` | Position ticket  |

#### Returns:
| Type   | Description                                                  |
|--------|--------------------------------------------------------------|
| `bool` | True if the position is closed successfully, False otherwise |


<a id="backtest_engine.modify_stops"></a>
#### modify_stops
```python
@error_handler(response=False)
def modify_stops(*, ticket: int, sl: int, tp: int) -> bool
```
Modify the stop loss and take profit levels of an open position.
#### Parameters:
| Name     | Type  | Description      |
|----------|-------|------------------|
| `ticket` | `int` | Position ticket  |
| `sl`     | `int` | stop loss level  |

#### Returns:
| Type   | Description                                                  |
|--------|--------------------------------------------------------------|
| `bool` | True if the stops are modified successfully, False otherwise |


<a id="backtest_engine.update_account"></a>
#### update_account
```python
def update_account(*,
                   profit: float = None,
                   margin: float = 0,
                   gain: float = 0)
```
Update the account. This method is protected by thread lock.

#### Parameters:
| Name     | Type    | Description                                                                    |
|----------|---------|--------------------------------------------------------------------------------|
| `profit` | `float` | The current profit of one or more open positions. Can be positive or negative. |
| `margin` | `float` | The margin set aside for a trade. It is released when the trade is closed.     |
| `gain`   | `gain`  | The gain realized when the trade is closed.                                    |


<a id="backtest_engine.deposit"></a>
#### deposit
```python
def deposit(*, amount: float)
```
Make deposit to the trading account


<a id="backtest_engine.withdraw"></a>
#### withdraw
```python
def withdraw(*, amount: float)
```
Make a withdrawal from the trading account. You can not withdraw more than what you have


<a id="backtest_engine.setup_account"></a>
#### setup_account
```python
@error_handler
async def setup_account(**kwargs)
```
Set up the trading account before the beginning of a backtesting session.

#### Parameters:
| Name     | Type | Description                                                 |
|----------|------|-------------------------------------------------------------|
| `kwargs` | dict | Attributes for the backtest account object can be set here. |


<a id="backtest_engine.setup_account_sync"></a>
#### setup_account_sync
```python
@error_handler_sync
def setup_account_sync(**kwargs)
```
Set up the backtesting account in sync mode


<a id="backtest_engine.prices"></a>
#### prices
```python
@cached_property
def prices() -> dict[str, DataFrame]
```
Get the prices for instruments used in the backtesting. This class is called when the use_terminal option
is set to False and trading data is provided in the data attribute. It makes sure that there is a price for each
symbol for every second covered in the backtesting range, by reindexing the price ticks using the backtesting
time span and filling up missing data using the nearest method.
This method returns a dictionaries of dataframe containing the prices for each symbol.
It's cached and there computed only once per backtesting session.

#### Returns:
| Type   | Description                                                  |
|--------|--------------------------------------------------------------|
| `dict` | A dictionary mapping dataframe of prices to symbols.         |


<a id="backtest_engine.ticks"></a>
#### ticks
```python
@cached_property
def ticks() -> dict[str, DataFrame]
```
Similar to prices above, but returns prices exactly as they are without reindexing and filling up.

#### Returns:
| Type   | Description                                                  |
|--------|--------------------------------------------------------------|
| `dict` | A dictionary mapping dataframe of prices to symbols.         |


<a id="backtest_engine.rates"></a>
#### rates
```python
@cached_property
def rates() -> dict[str, dict[int, DataFrame]]
```
This property is useful when backtesting with the use_terminal option set to false. It returns a nested dict
that maps symbols to a dict mapping timeframes to rates. The timeframes are mapped using their integer values.

#### Returns:
| Type                              | Description                               |
|-----------------------------------|-------------------------------------------|
| `dict[str, dict[int, DataFrame]]` | A dictionary containing the symbol rates. |


<a id="backtest_engine.symbols"></a>
#### symbols
```python
@cached_property
def symbols() -> dict[str, SymbolInfo]
```
A dictionary of symbols and SymbolInfo object. Used when use_terminal is set to false.
#### Returns:
| Type                    | Description                                    |
|-------------------------|------------------------------------------------|
| `dict[str, SymbolInfo]` | A dictionary of symbols and SymbolInfo object. |

  
<a id="backtest_engine.order_send"></a>
#### order_send
```python
@error_handler
async def order_send(*, request: dict, use_terminal=False) -> OrderSendResult
```
Simulates the sending of an order to the broker. An OrderSendResult is object is created at the end of this
operation as would be created if it was done in live trading. When an order is successful a positions object is
created, an order and deal object is created as well. The margin and profit are calculated by sending to the broker 
if `use_terminal` is true. This increases accuracy but slows down the backtester. The `check_order` method is 
called to make sure the order is valid and would go through if it was a live trade.

#### Parameters:

| Name           | Type | Description                                                                                                                   |
|----------------|------|-------------------------------------------------------------------------------------------------------------------------------|
| `request`      | dict | The order request as a dict.                                                                                                  |
| `use_terminal` | bool | A flag to override the use_terminal attribute. If true, the terminal will be used even if the use_terminal attribute is True. |


#### Returns:
| Type              | Description                                                  |
|-------------------|--------------------------------------------------------------|
| `OrderSendResult` | An object containing the result of the order send operation. |


<a id="backtest_engine.order_check"></a>
#### order_check
```python
@error_handler
async def order_check(*, request: dict, use_terminal: bool = False) -> OrderCheckResult
```
Checks the order before placing it. If `use_terminal` is true, the order is checked with the broker, 
but the entire result is not used. Details such as balance, profit, equity, margin, and margin level are calculated
by the backtester.

#### Parameters:
| Name           | Type | Description                                                                     |
|----------------|------|---------------------------------------------------------------------------------|
| `request`      | dict | The order request as a dict.                                                    |
| `use_terminal` | bool | A flag to override the use_terminal attribute. If true, the terminal will used. |
 

#### Returns:
| Type               | Description                    |
|--------------------|--------------------------------|
| `OrderCheckResult` | The result of the order check. |


<a id="backtest_engine.get_terminal_info"></a>
#### get_terminal_info
```python
@error_handler
async def get_terminal_info() -> TerminalInfo
```
Get the terminal information

#### Returns:
| Type           | Description              |
|----------------|--------------------------|
| `TerminalInfo` | The terminal information |


<a id="backtest_engine.get_version"></a>
#### get_version
```python
@error_handler
async def get_version() -> tuple[int, int, str]
```
Get the version of the terminal.

#### Returns:
| Type                   | Description                 |
|------------------------|-----------------------------|
| `tuple[int, int, str]` | The version of the terminal |

  
<a id="backtest_engine.get_symbols_total"></a>
#### get_symbols_total
```python
@error_handler
async def get_symbols_total() -> int
```
Get the total number of symbols available in the terminal.

#### Returns:
| Type | Description                                    |
|------|------------------------------------------------|
| `int` | The total number of symbols available.         |


<a id="backtest_engine.get_symbols"></a>
#### get_symbols
```python
@error_handler
async def get_symbols(*, group: str = "") -> tuple[SymbolInfo, ...]
```
Get the symbols available in the terminal. Filter by group if provided.

#### Parameters:
| Name     | Type | Description                                    |
|----------|------|------------------------------------------------|
| `group`  | str  | The group to filter by (default is "")         |


#### Returns:
| Type                     | Description                   |
|--------------------------|-------------------------------|
| `tuple[SymbolInfo, ...]` | A tuple of symbol information |


<a id="backtest_engine.get_account_info"></a>
#### get_account_info
```python
@error_handler_sync
def get_account_info() -> AccountInfo
```
Get the account information

#### Returns:
| Type          | Description             |
|---------------|-------------------------|
| `AccountInfo` | The account information |


<a id="backtest_engine.get_symbol_info_tick"></a>
#### get_symbol_info_tick
```python
@error_handler
async def get_symbol_info_tick(*, symbol: str) -> Tick
```
Get the price tick for a symbol at the current time

#### Parameters:
| Name     | Type | Description                           |
|----------|------|---------------------------------------|
| `symbol` | str  | The symbol to get the price tick for. |

  
#### Returns:
| Type   | Description    |
|--------|----------------|
| `Tick` | The price tick |


<a id="backtest_engine.get_symbol_info"></a>
#### get_symbol_info
```python
@error_handler
async def get_symbol_info(*, symbol: str) -> SymbolInfo
```
Get the symbol information

#### Parameters:
| Name     | Type | Description                           |
|----------|------|---------------------------------------|
| `symbol` | str  | The symbol to get information for     |


#### Returns:
| Type         | Description            |
|--------------|------------------------|
| `SymbolInfo` | The symbol information |


<a id="backtest_engine.get_rates_from"></a>
#### get_rates_from
```python
@error_handler
async def get_rates_from(*, symbol: str, timeframe: TimeFrame, date_from: datetime | float, count: int) -> np.ndarray
```
Get rates from a specific date to the current date. Used by the backtester to get rates for a symbol

#### Parameters:
| Name        | Type                | Description                          |
|-------------|---------------------|--------------------------------------|
| `symbol`    | `str`               | The symbol to get rates for          |
| `timeframe` | `TimeFrame`         | The timeframe of the rates           |
| `date_from` | `datetime \| float` | The date from which to get the rates |
| `count`     | `int`               | The number of rates to get           |


#### Returns:
| Type         | Description            |
|--------------|------------------------|
| `np.ndarray` | An array of rates      |


<a id="backtest_engine.get_rates_from_pos"></a>
#### get_rates_from_pos
```python
@error_handler
async def get_rates_from_pos(*, symbol: str, timeframe: TimeFrame, start_pos: int, count: int) -> np.ndarray
```
Get a number of rates counting from a specific position. With position zero being the current time.
#### Parameters:
| Name        | Type                | Description                          |
|-------------|---------------------|--------------------------------------|
| `symbol`    | `str`               | The symbol to get rates for          |
| `timeframe` | `TimeFrame`         | The timeframe of the rates           |
| `start_pos` | `int`               | The position to start from           |
| `count`     | `int`               | The number of rates to get           |

#### Returns:
| Type         | Description            |
|--------------|------------------------|
| `np.ndarray` | An array of rates      |


<a id="backtest_engine.get_rates_range"></a>
#### get_rates_range
```python
@error_handler
async def get_rates_range(*, symbol: str, timeframe: TimeFrame, date_from: datetime | float,
                          date_to: datetime | float) -> np.ndarray
```
Get rates within a specific date range. Used by the backtester to get rates for a symbol

#### Parameters:
| Name        | Type                | Description                          |
|-------------|---------------------|--------------------------------------|
| `symbol`    | `str`               | The symbol to get rates for          |
| `timeframe` | `TimeFrame`         | The timeframe of the rates           |
| `date_from` | `datetime \| float` | The date from which to get the rates |
| `date_to`   | `datetime \| float` | The date to which to get the rates   |


#### Returns:
| Type         | Description            |
|--------------|------------------------|
| `np.ndarray` | An array of rates      |


<a id="backtest_engine.get_ticks_from"></a>
#### get_ticks_from
```python
@error_handler
async def get_ticks_from(*, symbol: str, date_from: datetime | float, count: int,
                         flags: CopyTicks = CopyTicks.ALL) -> np.ndarray
```
Get a specified number of ticks counting from a specific date.

#### Parameters:
| Name        | Type                | Description                          |
|-------------|---------------------|--------------------------------------|
| `symbol`    | `str`               | The symbol to get ticks for          |
| `date_from` | `datetime \| float` | The date from which to get the ticks |
| `count`     | `int`               | The number of ticks to get           |
| `flags`     | `CopyTicks`         | The flags to use when getting ticks  |

#### Returns:
| Type         | Description            |
|--------------|------------------------|
| `np.ndarray` | An array of ticks      |


<a id="backtest_engine.get_ticks_range"></a>
#### get_ticks_range
```python
@error_handler
async def get_ticks_range(*, symbol: str, date_from: datetime | float, date_to: datetime | float,
                          flags: CopyTicks = CopyTicks.ALL) -> np.ndarray
```
Get ticks within a specific date range.
#### Parameters:
| Name        | Type                | Description                          |
|-------------|---------------------|--------------------------------------|
| `symbol`    | `str`               | The symbol to get ticks for          |
| `date_from` | `datetime \| float` | The date from which to get the ticks |
| `date_to`   | `datetime \| float` | The date to which to get the ticks   |
| `flags`     | `CopyTicks`         | The flags to use when getting ticks  |


#### Returns:
| Type         | Description            |
|--------------|------------------------|
| `np.ndarray` | An array of ticks      |


<a id="backtest_engine.order_calc_margin"></a>
#### order_calc_margin
```python
@error_handler
async def order_calc_margin(*, action: Literal[OrderType.BUY, OrderType.SELL], symbol: str, volume: float,
                            price: float, use_terminal: bool = None)
```
Calculate the margin required for a trade.

#### Parameters:
| Name           | Type                                     | Description                                                                                                                   |
|----------------|------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| `action`       | `Literal[OrderType.BUY, OrderType.SELL]` | Type of order                                                                                                                 |
| `symbol`       | `str`                                    | Symbol name                                                                                                                   |
| `volume`       | `float`                                  | Volume of the trade                                                                                                           |
| `price`        | `float`                                  | The price at which the trade is opened                                                                                        |
| `use_terminal` | `bool`                                   | A flag to override the use_terminal attribute. If true, the terminal will be used even if the use_terminal attribute is True. |


#### Returns:
| Type   | Description                        |
|--------|------------------------------------|
| `float` | The margin required for the trade |


<a id="backtest_engine.order_calc_profit"></a>
#### order_calc_profit
```python
@error_handler
async def order_calc_profit(*, action: Literal[OrderType.BUY, OrderType.SELL], symbol: str, volume: float,
                            price_open: float, price_close: float, use_terminal=None)
```
Calculate the profit for a trade.
#### Parameters:
| Name           | Type                                     | Description                                                                                                                     |
|----------------|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| `action`       | `Literal[OrderType.BUY, OrderType.SELL]` | Type of order                                                                                                                   |
| `symbol`       | `str`                                    | Symbol name                                                                                                                     |
| `volume`       | `float`                                  | Volume of the trade                                                                                                             |
| `price_open`   | `float`                                  | The price at which the trade is opened                                                                                          |
| `price_close`  | `float`                                  | The price at which the trade is closed                                                                                          |
| `use_terminal` | `bool`                                   | A flag to override the use_terminal attribute. If true, the terminal will be used even if the `use_terminal` attribute is True. |

#### Returns:
| Type    | Description             |
|---------|-------------------------|
| `float` | The profit of the trade |


<a id="backtest_engine.get_orders_total"></a>
#### get_orders_total
```python
@error_handler_sync
def get_orders_total() -> int
```
Get the total number of pending orders.

#### Returns:
| Type  | Description                    |
|-------|--------------------------------|
| `int` | Total number of pending orders |


<a id="backtest_engine.get_orders"></a>
#### get_orders
```python
@error_handler_sync
def get_orders(*, symbol: str = "", group: str = "", ticket: int = None) -> tuple[TradeOrder, ...]
```
Get pending orders from the terminal history. This has to do with pending orders, which this backtester
doesn't support yet.

#### Parameters:
| Name     | Type  | Description  |
|----------|-------|--------------|
| `symbol` | `str` | Symbol name  |
| `group`  | `str` | Group name   |
| `ticket` | `int` | Order ticket |

#### Returns:
| Type                     | Description    |
|--------------------------|----------------|
| `tuple[TradeOrder, ...]` | Pending orders |


<a id="backtest_engine.get_positions_total"></a>
#### get_positions_total
```python
@error_handler_sync
def get_positions_total() -> int
```
Get the total number of open positions.

#### Returns:
| Type  | Description                    |
|-------|--------------------------------|
| `int` | Total number of open positions |


<a id="backtest_engine.get_positions"></a>
#### get_positions
```python
@error_handler_sync
def get_positions(*, symbol: str = None, group: str = None, ticket: int = None) -> tuple[TradePosition, ...]
```
Get open positions from the terminal history.

#### Parameters:
| Name     | Type  | Description     |
|----------|-------|-----------------|
| `symbol` | `str` | Symbol name     |
| `group`  | `str` | Group name      |
| `ticket` | `int` | Position ticket |

#### Returns:
| Type                     | Description    |
|--------------------------|----------------|
| `tuple[TradePosition, ...]` | Open positions |


<a id="backtest_engine.get_history_orders_total"></a>
#### get_history_orders_total
```python
@error_handler_sync
def get_history_orders_total(*, date_from: datetime | float, date_to: datetime | float) -> int
```
Get the total number of orders in the terminal history.

#### Parameters:
| Name        | Type                | Description                           |
|-------------|---------------------|---------------------------------------|
| `date_from` | `datetime \| float` | The start date of the history         |
| `date_to`   | `datetime \| float` | The end date of the history           |

#### Returns:
| Type  | Description                    |
|-------|--------------------------------|
| `int` | Total number of orders in the history |


<a id="backtest_engine.get_history_orders"></a>
#### get_history_orders
```python
@error_handler_sync
def get_history_orders(*, date_from: datetime | float = None, date_to: datetime | float = None, group: str = "",
                       ticket: int = None, position: int = None) -> tuple[TradeOrder, ...]
```
Get orders from the terminal history.

#### Parameters:
| Name        | Type                | Description                           |
|-------------|---------------------|---------------------------------------|
| `date_from` | `datetime \| float` | Date from which to start the history  |
| `date_to`   | `datetime \| float` | Date to which to end the history      |
| `group`     | `str`               | group keyword to filter by            |
| `ticket`    | `int`               | ticket id to filter by                |
| `position`  | `int`               | position id to filter by              |


#### Returns:
| Type                     | Description           |
|--------------------------|-----------------------|
| `tuple[TradeOrder, ...]` | Orders in the history |


<a id="backtest_engine.get_history_deals_total"></a>
#### get_history_deals_total
```python
@error_handler_sync
def get_history_deals_total(*, date_from: datetime | float, date_to: datetime | float) -> int
```
Get the total number of deals in the terminal history.

#### Parameters:
| Name        | Type                | Description                          |
|-------------|---------------------|--------------------------------------|
| `date_from` | `datetime \| float` | Date from which to start the history |
| `date_to`   | `datetime \| float` | Date to which to end the history     |


#### Returns:
| Type  | Description                          |
|-------|--------------------------------------|
| `int` | Total number of deals in the history |


<a id="backtest_engine.get_history_deals"></a>
#### get_history_deals
```python
@error_handler_sync
def get_history_deals(*, date_from: datetime | float = None, date_to: datetime | float = None, group: str = None,
                      position: int = None, ticket: int = None) -> tuple[TradeDeal, ...]
```
Get deals from the terminal history.

#### Parameters:
| Name        | Type                | Description                           |
|-------------|---------------------|---------------------------------------|
| `date_from` | `datetime \| float` | Date from which to start the history  |
| `date_to`   | `datetime \| float` | Date to which to end the history      |
| `group`     | `str`               | group keyword to filter by            |
| `position`  | `int`               | position id to filter by              |
| `ticket`    | `int`               | ticket id to filter by                |

#### Returns:
| Type                    | Description          |
|-------------------------|----------------------|
| `tuple[TradeDeal, ...]` | Deals in the history |
