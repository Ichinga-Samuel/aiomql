# Table of Contents

* [backtest\_engine](#backtest_engine)
  * [BackTestEngine](#backtest_engine.BackTestEngine)
    * [\_\_init\_\_](#backtest_engine.BackTestEngine.__init__)
    * [setup\_test\_range](#backtest_engine.BackTestEngine.setup_test_range)
    * [setup\_data](#backtest_engine.BackTestEngine.setup_data)
    * [next](#backtest_engine.BackTestEngine.next)
    * [data](#backtest_engine.BackTestEngine.data)
    * [reset](#backtest_engine.BackTestEngine.reset)
    * [go\_to](#backtest_engine.BackTestEngine.go_to)
    * [fast\_forward](#backtest_engine.BackTestEngine.fast_forward)
    * [tracker](#backtest_engine.BackTestEngine.tracker)
    * [save\_result\_to\_json](#backtest_engine.BackTestEngine.save_result_to_json)
    * [close\_all\_open](#backtest_engine.BackTestEngine.close_all_open)
    * [wrap\_up](#backtest_engine.BackTestEngine.wrap_up)
    * [preload\_ticks](#backtest_engine.BackTestEngine.preload_ticks)
    * [get\_price\_tick](#backtest_engine.BackTestEngine.get_price_tick)
    * [check\_order](#backtest_engine.BackTestEngine.check_order)
    * [check\_account](#backtest_engine.BackTestEngine.check_account)
    * [check\_position](#backtest_engine.BackTestEngine.check_position)
    * [close\_position\_manually](#backtest_engine.BackTestEngine.close_position_manually)
    * [close\_position](#backtest_engine.BackTestEngine.close_position)
    * [modify\_stops](#backtest_engine.BackTestEngine.modify_stops)
    * [update\_account](#backtest_engine.BackTestEngine.update_account)
    * [deposit](#backtest_engine.BackTestEngine.deposit)
    * [withdraw](#backtest_engine.BackTestEngine.withdraw)
    * [setup\_account](#backtest_engine.BackTestEngine.setup_account)
    * [setup\_account\_sync](#backtest_engine.BackTestEngine.setup_account_sync)
    * [prices](#backtest_engine.BackTestEngine.prices)
    * [ticks](#backtest_engine.BackTestEngine.ticks)
    * [rates](#backtest_engine.BackTestEngine.rates)
    * [symbols](#backtest_engine.BackTestEngine.symbols)
    * [order\_send](#backtest_engine.BackTestEngine.order_send)
    * [order\_check](#backtest_engine.BackTestEngine.order_check)
    * [get\_terminal\_info](#backtest_engine.BackTestEngine.get_terminal_info)
    * [get\_version](#backtest_engine.BackTestEngine.get_version)
    * [get\_symbols\_total](#backtest_engine.BackTestEngine.get_symbols_total)
    * [get\_symbols](#backtest_engine.BackTestEngine.get_symbols)
    * [get\_account\_info](#backtest_engine.BackTestEngine.get_account_info)
    * [get\_symbol\_info\_tick](#backtest_engine.BackTestEngine.get_symbol_info_tick)
    * [get\_symbol\_info](#backtest_engine.BackTestEngine.get_symbol_info)
    * [get\_rates\_from](#backtest_engine.BackTestEngine.get_rates_from)
    * [get\_rates\_from\_pos](#backtest_engine.BackTestEngine.get_rates_from_pos)
    * [get\_rates\_range](#backtest_engine.BackTestEngine.get_rates_range)
    * [get\_ticks\_from](#backtest_engine.BackTestEngine.get_ticks_from)
    * [get\_ticks\_range](#backtest_engine.BackTestEngine.get_ticks_range)
    * [order\_calc\_margin](#backtest_engine.BackTestEngine.order_calc_margin)
    * [order\_calc\_profit](#backtest_engine.BackTestEngine.order_calc_profit)
    * [get\_orders\_total](#backtest_engine.BackTestEngine.get_orders_total)
    * [get\_orders](#backtest_engine.BackTestEngine.get_orders)
    * [get\_positions\_total](#backtest_engine.BackTestEngine.get_positions_total)
    * [get\_positions](#backtest_engine.BackTestEngine.get_positions)
    * [get\_history\_orders\_total](#backtest_engine.BackTestEngine.get_history_orders_total)
    * [get\_history\_orders](#backtest_engine.BackTestEngine.get_history_orders)
    * [get\_history\_deals\_total](#backtest_engine.BackTestEngine.get_history_deals_total)
    * [get\_history\_deals](#backtest_engine.BackTestEngine.get_history_deals)

<a id="backtest_engine"></a>

# backtest\_engine

<a id="backtest_engine.BackTestEngine"></a>

## BackTestEngine Objects

```python
class BackTestEngine()
```

<a id="backtest_engine.BackTestEngine.__init__"></a>

#### \_\_init\_\_

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

**Arguments**:

- `data` _BackTestData, optional_ - The data to use for backtesting. Defaults to None.
  
- `speed` _int, optional_ - The speed of the backtest. Defaults to 60 seconds.
  
- `start` _float | datetime, optional_ - The start time of the backtest. Defaults to 0. If a float is passed,
  it is assumed to be a timestamp.
  
- `end` _float | datetime, optional_ - The end time of the backtest. Defaults to 0. If a float is passed,
  it is assumed to be a timestamp.
  
- `restart` _bool, optional_ - Whether to restart the backtest from the beginning. Defaults to True.
  This is useful when resuming a backtest using a saved BackTestData instance.
  
- `use_terminal` _bool, optional_ - Whether to use the terminal for backtesting. Defaults to None. If None,
  it uses the global config setting. If use terminal is true, the backtest engine will use the terminal to
  get price data, compute margins, profit and check order viability. If false, it will use the data
  provided in the BackTestData instance and default algorithm for the calculations
  
- `name` _str, optional_ - The name of the backtest. Defaults to "". If not provided,
  it is generated from the start and end times.
  
- `stop_time` _float | datetime, optional_ - The time to stop the backtest. Defaults to None.
  If a float is passed, it is assumed to be a timestamp. If not given it is assumed to be the end of the backtest range.
  
- `close_open_positions_on_exit` _bool, optional_ - Whether to close all open positions when the backtest
  is stopped. Defaults to True.
  
- `preload` _bool, optional_ - Whether to preload the ticks for the backtest. Defaults to True.
  
- `assign_to_config` _bool, optional_ - Whether to assign the backtest engine to the global config instance.
  Defaults to True.
  
- `account_info` _dict, optional_ - A dictionary of account information to use for the backtest. Defaults to None. Use this to set
  the account information for the backtest.
  

**Attributes**:

- `_data` _BackTestData_ - The data used for backtesting. This is the data that is saved to disk when the
  backtest is stopped.
  
- `mt5` _MetaTrader_ - The MetaTrader instance for the backtest engine.
  
- `config` _Config_ - The global configuration instance.
  
- `name` _str_ - The name of the backtest.
  
- `stop_testing` _bool_ - Whether to stop the backtest.
  
- `use_terminal` _bool_ - Whether to use the terminal for backtesting.
  
- `close_open_positions_on_exit` _bool_ - Whether to close all open positions when the backtest is stopped.
  
- `stop_time` _int_ - The time to stop the backtest.
  
- `preload` _bool_ - Whether to preload the ticks for the backtest.
  
- `preloaded_ticks` _dict_ - A dictionary of preloaded ticks for the backtest.
  
- `account_lock` _RLock_ - A reentrant lock for the account data.
  
- `account_info` _dict_ - A dictionary of account information for the backtest.

<a id="backtest_engine.BackTestEngine.setup_test_range"></a>

#### setup\_test\_range

```python
def setup_test_range(*,
                     start: float | datetime = None,
                     end: float | datetime = None,
                     speed: int = 60,
                     restart: bool = True)
```

Setup the test range for the backtest engine. This is used to set the range of the backtest and the speed
at which it runs.

**Arguments**:

- `start` _float | datetime, optional_ - The start time of the backtest. Defaults to None. If a float is passed,
  it is assumed to be a timestamp.
  
- `end` _float | datetime, optional_ - The end time of the backtest. Defaults to None. If a float is passed,
  it is assumed to be a timestamp.
  
- `speed` _int, optional_ - The speed of the backtest. Defaults to 60.
  
- `restart` _bool, optional_ - Whether to restart the backtest. Defaults to True.
  This is useful when resuming a backtest using a saved BackTestData.

<a id="backtest_engine.BackTestEngine.setup_data"></a>

#### setup\_data

```python
def setup_data(*, restart: bool = True)
```

Sets up the data for the backtest engine. This includes the orders, positions, deals and account
information. This data is handled by specialized classes such as the BackTestAccount and the TradeManager
classes.

**Arguments**:

- `restart` _bool, optional_ - Whether to restart the data. Defaults to True.

<a id="backtest_engine.BackTestEngine.next"></a>

#### next

```python
def next() -> Cursor
```

Move the cursor to the next time step in the backtest range.

<a id="backtest_engine.BackTestEngine.data"></a>

#### data

```python
@property
def data()
```

The BackTestData instance used for the backtest. If not provided, a new instance is created,
and the data is made persistent when the backtest is stopped.

<a id="backtest_engine.BackTestEngine.reset"></a>

#### reset

```python
def reset(clear_data: bool = False)
```

Reset the backtest engine. This is useful when restarting the backtest from the beginning.

<a id="backtest_engine.BackTestEngine.go_to"></a>

#### go\_to

```python
def go_to(*, time: datetime | float)
```

Move the cursor to a specific time in the backtest range. You can pass a datetime object or a timestamp.
You can't go back in time or beyond the limits of the range.

<a id="backtest_engine.BackTestEngine.fast_forward"></a>

#### fast\_forward

```python
def fast_forward(*, steps: int)
```

Fast-forward the backtester by the given steps.

<a id="backtest_engine.BackTestEngine.tracker"></a>

#### tracker

```python
async def tracker()
```

The tracker monitors and updates open positions on every iteration. It is called by the controller.

<a id="backtest_engine.BackTestEngine.save_result_to_json"></a>

#### save\_result\_to\_json

```python
@error_handler_sync
def save_result_to_json()
```

Saves the result to a json file at the end of testing.

<a id="backtest_engine.BackTestEngine.close_all_open"></a>

#### close\_all\_open

```python
async def close_all_open()
```

Closes all open position at the end of testing

<a id="backtest_engine.BackTestEngine.wrap_up"></a>

#### wrap\_up

```python
@error_handler
async def wrap_up()
```

Wraps up the backtest. This is called at the end of testing to save the results and close all open
positions.

<a id="backtest_engine.BackTestEngine.preload_ticks"></a>

#### preload\_ticks

```python
async def preload_ticks(*, symbol: str)
```

Pull a month data on ticks from the terminal. Starting from the current time.

**Arguments**:

- `symbol` _str_ - The symbol to preload ticks for.

<a id="backtest_engine.BackTestEngine.get_price_tick"></a>

#### get\_price\_tick

```python
@async_cache
async def get_price_tick(*, symbol: str, time: int) -> Tick | None
```

Get the price tick for a symbol at a given time. If the preload option is set to True,
it will use the preloaded ticks when available.

**Arguments**:

- `symbol` _str_ - The symbol to get the price tick for.
- `time` _int_ - The time to get the price tick.

<a id="backtest_engine.BackTestEngine.check_order"></a>

#### check\_order

```python
@error_handler
async def check_order(*, ticket: int)
```

"
Check if the order has reached its take profit or stop loss levels and close the order if it has.
Checks only **OrderType.BUY** and **OrderType.SELL** orders that have reached their take profit or stop loss levels.

**Arguments**:

- `ticket` _int_ - Order ticket

<a id="backtest_engine.BackTestEngine.check_account"></a>

#### check\_account

```python
def check_account()
```

Checks an account status. This method is called at each iteration to check if the account has burned out.

<a id="backtest_engine.BackTestEngine.check_position"></a>

#### check\_position

```python
async def check_position(*, ticket: int)
```

Update the profit of an open position based on the current price of the symbol. It is called by the
tracker to update the profit of open positions.

**Arguments**:

- `ticket` _int_ - Position ticket

<a id="backtest_engine.BackTestEngine.close_position_manually"></a>

#### close\_position\_manually

```python
@error_handler_sync
async def close_position_manually(*, ticket: int)
```

Close a position manually without. Usually at the end of testing.

<a id="backtest_engine.BackTestEngine.close_position"></a>

#### close\_position

```python
async def close_position(*, ticket: int) -> bool
```

Close an open position for the trading account using the position ticket.

**Arguments**:

- `ticket` - Position ticket
  

**Returns**:

- `bool` - True if the position is closed successfully, False otherwise

<a id="backtest_engine.BackTestEngine.modify_stops"></a>

#### modify\_stops

```python
@error_handler(response=False)
def modify_stops(*, ticket: int, sl: int, tp: int) -> bool
```

Modify the stop loss and take profit levels of an open position.

**Arguments**:

- `ticket` _int_ - Position ticket
- `sl` _int_ - stop loss level
- `tp` _int_ - Take profit level
  

**Returns**:

- `bool` - True if the stops are modified successfully, False otherwise

<a id="backtest_engine.BackTestEngine.update_account"></a>

#### update\_account

```python
def update_account(*,
                   profit: float = None,
                   margin: float = 0,
                   gain: float = 0)
```

Update the account. This method is protected by thread lock.

**Arguments**:

- `profit` _float_ - The current profit of one or more open positions. Can be positive or negative.
- `margin` _float_ - The margin set aside for a trade. It is released when the trade is closed.
- `gain` _gain_ - The gain realized when the trade is closed.

<a id="backtest_engine.BackTestEngine.deposit"></a>

#### deposit

```python
def deposit(*, amount: float)
```

Make deposit to the trading account

<a id="backtest_engine.BackTestEngine.withdraw"></a>

#### withdraw

```python
def withdraw(*, amount: float)
```

Make a withdrawal from the trading account. You can not withdraw more than what you have

<a id="backtest_engine.BackTestEngine.setup_account"></a>

#### setup\_account

```python
@error_handler
async def setup_account(**kwargs)
```

Setup the trading account before the begining of a backtesting session.

**Arguments**:

  (**kwargs, Any): Attributes for the backetest account object can be set here.

<a id="backtest_engine.BackTestEngine.setup_account_sync"></a>

#### setup\_account\_sync

```python
@error_handler_sync
def setup_account_sync(**kwargs)
```

Set up the backtesting account in sync mode

<a id="backtest_engine.BackTestEngine.prices"></a>

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

**Returns**:

  dict[str, DataFrame]: A dictionary mapping dataframe of prices to symbols.

<a id="backtest_engine.BackTestEngine.ticks"></a>

#### ticks

```python
@cached_property
def ticks() -> dict[str, DataFrame]
```

Similar to prices above, but returns prices exactly as they are without reindexing and filling up.

**Returns**:

  dict[str, DataFrame]: A dictionary mapping symbols to dataframes of ticks.

<a id="backtest_engine.BackTestEngine.rates"></a>

#### rates

```python
@cached_property
def rates() -> dict[str, dict[int, DataFrame]]
```

This property is useful when backtesting with the use_terminal option set to false. It returns a nested dict
that maps symbols to a dict mapping timeframes to rates. The timeframes are mapped using their integer values.

**Returns**:

  dict[str, dict[int, DataFrame]]: A dictionary containing the symbol rates.

<a id="backtest_engine.BackTestEngine.symbols"></a>

#### symbols

```python
@cached_property
def symbols() -> dict[str, SymbolInfo]
```

A dictionary of symbols and SymbolInfo object. Used when use_terminal is set to false.

**Returns**:

  dict[str, SymbolInfo]

<a id="backtest_engine.BackTestEngine.order_send"></a>

#### order\_send

```python
@error_handler
async def order_send(*, request: dict, use_terminal=False) -> OrderSendResult
```

Simulates the sending of an order to the broker. An OrderSendResult is object is created at the end of this
operation as would be created if it was done in live trading. When an order is successful a positions object is
created, an order and deal object is created as well. When use_terminal is set to true the margin and profit
are calculated by sending to the broker. This increases accuracy but slows down the backtester. Check order is
called to make sure the order is valid and would go through if it was a live trade.

**Arguments**:

- `request` _dict_ - The order request as a dict.
- `use_terminal` _bool_ - A flag to override the use_terminal attribute. If true, the terminal will
  be used even if the use_terminal attribute is True.
  

**Returns**:

- `OrderSendResult` - An object containing the result of the order send operation.

<a id="backtest_engine.BackTestEngine.order_check"></a>

#### order\_check

```python
@error_handler
async def order_check(*,
                      request: dict,
                      use_terminal: bool = False) -> OrderCheckResult
```

Checks the order before placing it. If use_terminal, the order is checked with the broker, but the entire result
is not used. Details such as balance, profit, equity, margin, and margin level are calculated by the backtester.

**Arguments**:

- `request` _dict_ - The order request as a dict.
- `use_terminal` _bool_ - A flag to override the use_terminal attribute. If true, the terminal will used.
  

**Returns**:

- `OrderCheckResult` - The result of the order check.

<a id="backtest_engine.BackTestEngine.get_terminal_info"></a>

#### get\_terminal\_info

```python
@error_handler
async def get_terminal_info() -> TerminalInfo
```

Get the terminal information

**Returns**:

- `TerminalInfo` - The terminal information

<a id="backtest_engine.BackTestEngine.get_version"></a>

#### get\_version

```python
@error_handler
async def get_version() -> tuple[int, int, str]
```

Get the version of the terminal.

**Returns**:

  tuple[int, int, str]: The version of the terminal

<a id="backtest_engine.BackTestEngine.get_symbols_total"></a>

#### get\_symbols\_total

```python
@error_handler
async def get_symbols_total() -> int
```

Get the total number of symbols available in the terminal.

**Returns**:

- `int` - The total number of symbols available.

<a id="backtest_engine.BackTestEngine.get_symbols"></a>

#### get\_symbols

```python
@error_handler
async def get_symbols(*, group: str = "") -> tuple[SymbolInfo, ...]
```

Get the symbols available in the terminal. Filter by group if provided.

**Arguments**:

- `group` _str_ - The group to filter by (default is "")
  

**Returns**:

  tuple[SymbolInfo, ...]: A tuple of symbol information

<a id="backtest_engine.BackTestEngine.get_account_info"></a>

#### get\_account\_info

```python
@error_handler_sync
def get_account_info() -> AccountInfo
```

Get the account information

**Returns**:

- `AccountInfo` - The account information

<a id="backtest_engine.BackTestEngine.get_symbol_info_tick"></a>

#### get\_symbol\_info\_tick

```python
@error_handler
async def get_symbol_info_tick(*, symbol: str) -> Tick
```

Get the price tick for a symbol at the current time

**Arguments**:

- `symbol` _str_ - The symbol
  

**Returns**:

- `Tick` - The price tick

<a id="backtest_engine.BackTestEngine.get_symbol_info"></a>

#### get\_symbol\_info

```python
@error_handler
async def get_symbol_info(*, symbol: str) -> SymbolInfo
```

Get the symbol information

**Arguments**:

- `symbol` _str_ - The symbol to get information for
  

**Returns**:

- `SymbolInfo` - The symbol information

<a id="backtest_engine.BackTestEngine.get_rates_from"></a>

#### get\_rates\_from

```python
@error_handler
async def get_rates_from(*, symbol: str, timeframe: TimeFrame,
                         date_from: datetime | float,
                         count: int) -> np.ndarray
```

Get rates from a specific date to the current date. Used by the backtester to get rates for a symbol

**Arguments**:

- `symbol` _str_ - The symbol to get rates for
- `timeframe` _TimeFrame_ - The timeframe of the rates
- `date_from` _datetime | float_ - The date from which to get the rates
- `count` _int_ - The number of rates to get
  

**Returns**:

- `np.ndarray` - An array of rates

<a id="backtest_engine.BackTestEngine.get_rates_from_pos"></a>

#### get\_rates\_from\_pos

```python
@error_handler
async def get_rates_from_pos(*, symbol: str, timeframe: TimeFrame,
                             start_pos: int, count: int) -> np.ndarray
```

Get a number of rates counting from a specific position. With position zero being the current time.

**Arguments**:

- `symbol` _str_ - The symbol to get rates for
- `timeframe` _TimeFrame_ - The timeframe of the rates
- `start_pos` _int_ - The position to start from
- `count` _int_ - The number of rates to get
  

**Returns**:

- `np.ndarray` - An array of rates

<a id="backtest_engine.BackTestEngine.get_rates_range"></a>

#### get\_rates\_range

```python
@error_handler
async def get_rates_range(*, symbol: str, timeframe: TimeFrame,
                          date_from: datetime | float,
                          date_to: datetime | float) -> np.ndarray
```

Get rates within a specific date range. Used by the backtester to get rates for a symbol

**Arguments**:

- `symbol` _str_ - The symbol to get rates for
- `timeframe` _TimeFrame_ - The timeframe of the rates
- `date_from` _datetime | float_ - The date from which to get the rates
- `date_to` _datetime | float_ - The date to which to get the rates
  

**Returns**:

- `np.ndarray` - An array of rates

<a id="backtest_engine.BackTestEngine.get_ticks_from"></a>

#### get\_ticks\_from

```python
@error_handler
async def get_ticks_from(*,
                         symbol: str,
                         date_from: datetime | float,
                         count: int,
                         flags: CopyTicks = CopyTicks.ALL) -> np.ndarray
```

Get a specified number of ticks counting from a specific date.

**Arguments**:

- `symbol` _str_ - The symbol to get ticks for
- `date_from` _datetime | float_ - The date from which to get the ticks
- `count` _int_ - The number of ticks to get
- `flags` _CopyTicks_ - The flags to use when getting the ticks
  

**Returns**:

- `np.ndarray` - An array of ticks

<a id="backtest_engine.BackTestEngine.get_ticks_range"></a>

#### get\_ticks\_range

```python
@error_handler
async def get_ticks_range(*,
                          symbol: str,
                          date_from: datetime | float,
                          date_to: datetime | float,
                          flags: CopyTicks = CopyTicks.ALL) -> np.ndarray
```

Get ticks within a specific date range.

**Arguments**:

- `symbol` _str_ - The symbol to get ticks for
- `date_from` _datetime | float_ - The date from which to get the ticks
- `date_to` _datetime | float_ - The date to which to get the ticks
- `flags` _CopyTicks_ - The flags to use when getting the ticks
  

**Returns**:

- `np.ndarray` - An array of ticks

<a id="backtest_engine.BackTestEngine.order_calc_margin"></a>

#### order\_calc\_margin

```python
@error_handler
async def order_calc_margin(*,
                            action: Literal[OrderType.BUY, OrderType.SELL],
                            symbol: str,
                            volume: float,
                            price: float,
                            use_terminal: bool = None)
```

Calculate the margin required for a trade.

**Arguments**:

- `action` _Literal[OrderType.BUY, OrderType.SELL]_ - Type of order
- `symbol` _str_ - Symbol name
- `volume` _float_ - Volume of the trade
- `price` _float_ - The price at which the trade is opened
- `use_terminal` _bool_ - A flag to override the use_terminal attribute. If true, the terminal will be used
  even if the use_terminal attribute is True.
  

**Returns**:

- `float` - The margin required for the trade

<a id="backtest_engine.BackTestEngine.order_calc_profit"></a>

#### order\_calc\_profit

```python
@error_handler
async def order_calc_profit(*,
                            action: Literal[OrderType.BUY, OrderType.SELL],
                            symbol: str,
                            volume: float,
                            price_open: float,
                            price_close: float,
                            use_terminal=None)
```

Calculate the profit for a trade.

**Arguments**:

- `action` _Literal[OrderType.BUY, OrderType.SELL]_ - Type of order
- `symbol` _str_ - Symbol name
- `volume` _float_ - Volume of the trade
- `price_open` _float_ - The price at which the trade is opened
- `price_close` _float_ - The price at which the trade is closed
- `use_terminal` _bool_ - A flag to override the use_terminal attribute. If true, the terminal will be used
  even if the use_terminal attribute is True.
  

**Returns**:

- `float` - The profit of the trade

<a id="backtest_engine.BackTestEngine.get_orders_total"></a>

#### get\_orders\_total

```python
@error_handler_sync
def get_orders_total() -> int
```

Get the total number of pending orders.

**Returns**:

- `int` - Total number of pending orders

<a id="backtest_engine.BackTestEngine.get_orders"></a>

#### get\_orders

```python
@error_handler_sync
def get_orders(*,
               symbol: str = "",
               group: str = "",
               ticket: int = None) -> tuple[TradeOrder, ...]
```

Get pending orders from the terminal history. This has to do with pending orders, which this backtester
doesn't support yet.

**Arguments**:

- `symbol` - Symbol name
- `group` - Group name
- `ticket` - Order ticket
  

**Returns**:

  tuple[TradeOrder, ...]: Pending orders

<a id="backtest_engine.BackTestEngine.get_positions_total"></a>

#### get\_positions\_total

```python
@error_handler_sync
def get_positions_total() -> int
```

Get the total number of open positions.

**Returns**:

- `int` - Total number of open positions

<a id="backtest_engine.BackTestEngine.get_positions"></a>

#### get\_positions

```python
@error_handler_sync
def get_positions(*,
                  symbol: str = None,
                  group: str = None,
                  ticket: int = None) -> tuple[TradePosition, ...]
```

Get open positions from the terminal history.

**Arguments**:

- `symbol` - The symbol name
- `group` - Group argument to filter by
- `ticket` - Position ticket
  

**Returns**:

  tuple[TradePosition, ...]: Open positions

<a id="backtest_engine.BackTestEngine.get_history_orders_total"></a>

#### get\_history\_orders\_total

```python
@error_handler_sync
def get_history_orders_total(*, date_from: datetime | float,
                             date_to: datetime | float) -> int
```

Get the total number of orders in the terminal history.

**Arguments**:

- `date_from` - The start date of the history
  
- `date_to` - The end date of the history
  

**Returns**:

- `int` - Total number of orders in the history

<a id="backtest_engine.BackTestEngine.get_history_orders"></a>

#### get\_history\_orders

```python
@error_handler_sync
def get_history_orders(*,
                       date_from: datetime | float = None,
                       date_to: datetime | float = None,
                       group: str = "",
                       ticket: int = None,
                       position: int = None) -> tuple[TradeOrder, ...]
```

Get orders from the terminal history.

**Arguments**:

- `date_from` - Date from which to start the history
- `date_to` - Date to which to end the history
- `group` - group keyword to filter by
- `ticket` - ticket id to filter by
- `position` - position id to filter by
  

**Returns**:

  tuple[TradeOrder, ...]: Orders in the history

<a id="backtest_engine.BackTestEngine.get_history_deals_total"></a>

#### get\_history\_deals\_total

```python
@error_handler_sync
def get_history_deals_total(*, date_from: datetime | float,
                            date_to: datetime | float) -> int
```

Get the total number of deals in the terminal history.

**Arguments**:

- `date_from` - Date from which to start the history
- `date_to` - Date to which to end the history
  

**Returns**:

- `int` - Total number of deals in the history

<a id="backtest_engine.BackTestEngine.get_history_deals"></a>

#### get\_history\_deals

```python
@error_handler_sync
def get_history_deals(*,
                      date_from: datetime | float = None,
                      date_to: datetime | float = None,
                      group: str = None,
                      position: int = None,
                      ticket: int = None) -> tuple[TradeDeal, ...]
```

Get deals from the terminal history.

**Arguments**:

- `date_from` - Date from which to start the history
- `date_to` - Date to which to end the history
- `group` - group keyword to filter by
- `position` - position id to filter by
- `ticket` - ticket id to filter by
  

**Returns**:

  tuple[TradeDeal, ...]: Deals in the history

