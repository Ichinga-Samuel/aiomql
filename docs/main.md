# Table of Contents

* [aiomql](#aiomql)
* [aiomql.account](#aiomql.account)
  * [Account](#aiomql.account.Account)
    * [refresh](#aiomql.account.Account.refresh)
    * [account\_info](#aiomql.account.Account.account_info)
    * [\_\_aenter\_\_](#aiomql.account.Account.__aenter__)
    * [sign\_in](#aiomql.account.Account.sign_in)
    * [has\_symbol](#aiomql.account.Account.has_symbol)
    * [symbols\_get](#aiomql.account.Account.symbols_get)
* [aiomql.bot\_builder](#aiomql.bot_builder)
  * [Bot](#aiomql.bot_builder.Bot)
    * [initialize](#aiomql.bot_builder.Bot.initialize)
    * [execute](#aiomql.bot_builder.Bot.execute)
    * [start](#aiomql.bot_builder.Bot.start)
    * [add\_strategy](#aiomql.bot_builder.Bot.add_strategy)
    * [add\_strategies](#aiomql.bot_builder.Bot.add_strategies)
    * [add\_strategy\_all](#aiomql.bot_builder.Bot.add_strategy_all)
    * [init\_symbols](#aiomql.bot_builder.Bot.init_symbols)
    * [init\_symbol](#aiomql.bot_builder.Bot.init_symbol)
* [aiomql.candle](#aiomql.candle)
  * [Candle](#aiomql.candle.Candle)
    * [\_\_init\_\_](#aiomql.candle.Candle.__init__)
    * [set\_attributes](#aiomql.candle.Candle.set_attributes)
    * [mid](#aiomql.candle.Candle.mid)
    * [is\_bullish](#aiomql.candle.Candle.is_bullish)
    * [is\_bearish](#aiomql.candle.Candle.is_bearish)
  * [Candles](#aiomql.candle.Candles)
    * [\_\_init\_\_](#aiomql.candle.Candles.__init__)
    * [ta](#aiomql.candle.Candles.ta)
    * [ta\_lib](#aiomql.candle.Candles.ta_lib)
    * [data](#aiomql.candle.Candles.data)
    * [rename](#aiomql.candle.Candles.rename)
* [aiomql.core.base](#aiomql.core.base)
  * [Base](#aiomql.core.base.Base)
    * [set\_attributes](#aiomql.core.base.Base.set_attributes)
    * [annotations](#aiomql.core.base.Base.annotations)
    * [get\_dict](#aiomql.core.base.Base.get_dict)
    * [class\_vars](#aiomql.core.base.Base.class_vars)
    * [dict](#aiomql.core.base.Base.dict)
    * [Meta](#aiomql.core.base.Base.Meta)
* [aiomql.core.config](#aiomql.core.config)
  * [Config](#aiomql.core.config.Config)
    * [account\_info](#aiomql.core.config.Config.account_info)
* [aiomql.core.constants](#aiomql.core.constants)
  * [TradeAction](#aiomql.core.constants.TradeAction)
  * [OrderFilling](#aiomql.core.constants.OrderFilling)
  * [OrderTime](#aiomql.core.constants.OrderTime)
  * [OrderType](#aiomql.core.constants.OrderType)
    * [opposite](#aiomql.core.constants.OrderType.opposite)
  * [BookType](#aiomql.core.constants.BookType)
  * [TimeFrame](#aiomql.core.constants.TimeFrame)
    * [time](#aiomql.core.constants.TimeFrame.time)
  * [CopyTicks](#aiomql.core.constants.CopyTicks)
  * [PositionType](#aiomql.core.constants.PositionType)
  * [PositionReason](#aiomql.core.constants.PositionReason)
  * [DealType](#aiomql.core.constants.DealType)
  * [DealEntry](#aiomql.core.constants.DealEntry)
  * [DealReason](#aiomql.core.constants.DealReason)
  * [OrderReason](#aiomql.core.constants.OrderReason)
  * [SymbolChartMode](#aiomql.core.constants.SymbolChartMode)
  * [SymbolCalcMode](#aiomql.core.constants.SymbolCalcMode)
  * [SymbolTradeMode](#aiomql.core.constants.SymbolTradeMode)
  * [SymbolTradeExecution](#aiomql.core.constants.SymbolTradeExecution)
  * [SymbolSwapMode](#aiomql.core.constants.SymbolSwapMode)
  * [DayOfWeek](#aiomql.core.constants.DayOfWeek)
  * [SymbolOrderGTCMode](#aiomql.core.constants.SymbolOrderGTCMode)
  * [SymbolOptionRight](#aiomql.core.constants.SymbolOptionRight)
  * [SymbolOptionMode](#aiomql.core.constants.SymbolOptionMode)
  * [AccountTradeMode](#aiomql.core.constants.AccountTradeMode)
  * [TickFlag](#aiomql.core.constants.TickFlag)
  * [TradeRetcode](#aiomql.core.constants.TradeRetcode)
  * [AccountStopOutMode](#aiomql.core.constants.AccountStopOutMode)
  * [AccountMarginMode](#aiomql.core.constants.AccountMarginMode)
* [aiomql.core.errors](#aiomql.core.errors)
  * [Error](#aiomql.core.errors.Error)
* [aiomql.core.exceptions](#aiomql.core.exceptions)
  * [LoginError](#aiomql.core.exceptions.LoginError)
  * [VolumeError](#aiomql.core.exceptions.VolumeError)
  * [SymbolError](#aiomql.core.exceptions.SymbolError)
  * [OrderError](#aiomql.core.exceptions.OrderError)
* [aiomql.core.meta\_trader](#aiomql.core.meta_trader)
  * [MetaTrader](#aiomql.core.meta_trader.MetaTrader)
    * [\_\_aenter\_\_](#aiomql.core.meta_trader.MetaTrader.__aenter__)
    * [\_\_aexit\_\_](#aiomql.core.meta_trader.MetaTrader.__aexit__)
    * [login](#aiomql.core.meta_trader.MetaTrader.login)
    * [initialize](#aiomql.core.meta_trader.MetaTrader.initialize)
    * [shutdown](#aiomql.core.meta_trader.MetaTrader.shutdown)
    * [version](#aiomql.core.meta_trader.MetaTrader.version)
    * [account\_info](#aiomql.core.meta_trader.MetaTrader.account_info)
    * [orders\_get](#aiomql.core.meta_trader.MetaTrader.orders_get)
* [aiomql.core.models](#aiomql.core.models)
  * [AccountInfo](#aiomql.core.models.AccountInfo)
  * [TerminalInfo](#aiomql.core.models.TerminalInfo)
  * [SymbolInfo](#aiomql.core.models.SymbolInfo)
  * [BookInfo](#aiomql.core.models.BookInfo)
  * [TradeOrder](#aiomql.core.models.TradeOrder)
  * [TradeRequest](#aiomql.core.models.TradeRequest)
  * [OrderCheckResult](#aiomql.core.models.OrderCheckResult)
  * [OrderSendResult](#aiomql.core.models.OrderSendResult)
  * [TradePosition](#aiomql.core.models.TradePosition)
  * [TradeDeal](#aiomql.core.models.TradeDeal)
* [aiomql.core](#aiomql.core)
* [aiomql.executor](#aiomql.executor)
  * [Executor](#aiomql.executor.Executor)
    * [add\_workers](#aiomql.executor.Executor.add_workers)
    * [remove\_workers](#aiomql.executor.Executor.remove_workers)
    * [add\_worker](#aiomql.executor.Executor.add_worker)
    * [run](#aiomql.executor.Executor.run)
    * [execute](#aiomql.executor.Executor.execute)
* [aiomql.history](#aiomql.history)
  * [History](#aiomql.history.History)
    * [\_\_init\_\_](#aiomql.history.History.__init__)
    * [init](#aiomql.history.History.init)
    * [get\_deals](#aiomql.history.History.get_deals)
    * [deals\_total](#aiomql.history.History.deals_total)
    * [get\_orders](#aiomql.history.History.get_orders)
    * [orders\_total](#aiomql.history.History.orders_total)
* [aiomql.lib.strategies.finger\_trap](#aiomql.lib.strategies.finger_trap)
  * [Entry](#aiomql.lib.strategies.finger_trap.Entry)
* [aiomql.lib.strategies](#aiomql.lib.strategies)
* [aiomql.lib.symbols.forex\_symbol](#aiomql.lib.symbols.forex_symbol)
  * [ForexSymbol](#aiomql.lib.symbols.forex_symbol.ForexSymbol)
    * [pip](#aiomql.lib.symbols.forex_symbol.ForexSymbol.pip)
    * [compute\_volume](#aiomql.lib.symbols.forex_symbol.ForexSymbol.compute_volume)
* [aiomql.lib.symbols](#aiomql.lib.symbols)
* [aiomql.lib.traders.simple\_deal\_trader](#aiomql.lib.traders.simple_deal_trader)
  * [DealTrader](#aiomql.lib.traders.simple_deal_trader.DealTrader)
    * [create\_order](#aiomql.lib.traders.simple_deal_trader.DealTrader.create_order)
* [aiomql.lib.traders](#aiomql.lib.traders)
* [aiomql.lib](#aiomql.lib)
* [aiomql.order](#aiomql.order)
  * [Order](#aiomql.order.Order)
    * [\_\_init\_\_](#aiomql.order.Order.__init__)
    * [orders\_total](#aiomql.order.Order.orders_total)
    * [orders](#aiomql.order.Order.orders)
    * [check](#aiomql.order.Order.check)
    * [send](#aiomql.order.Order.send)
    * [calc\_margin](#aiomql.order.Order.calc_margin)
    * [calc\_profit](#aiomql.order.Order.calc_profit)
* [aiomql.positions](#aiomql.positions)
  * [Positions](#aiomql.positions.Positions)
    * [\_\_init\_\_](#aiomql.positions.Positions.__init__)
    * [positions\_total](#aiomql.positions.Positions.positions_total)
    * [positions\_get](#aiomql.positions.Positions.positions_get)
    * [close\_all](#aiomql.positions.Positions.close_all)
* [aiomql.ram](#aiomql.ram)
  * [RAM](#aiomql.ram.RAM)
    * [\_\_init\_\_](#aiomql.ram.RAM.__init__)
    * [get\_amount](#aiomql.ram.RAM.get_amount)
    * [get\_volume](#aiomql.ram.RAM.get_volume)
* [aiomql.records](#aiomql.records)
  * [Records](#aiomql.records.Records)
    * [\_\_init\_\_](#aiomql.records.Records.__init__)
    * [get\_records](#aiomql.records.Records.get_records)
    * [read\_update](#aiomql.records.Records.read_update)
    * [update\_rows](#aiomql.records.Records.update_rows)
    * [update\_records](#aiomql.records.Records.update_records)
    * [update\_record](#aiomql.records.Records.update_record)
* [aiomql.result](#aiomql.result)
  * [Result](#aiomql.result.Result)
    * [\_\_init\_\_](#aiomql.result.Result.__init__)
    * [to\_csv](#aiomql.result.Result.to_csv)
    * [save\_csv](#aiomql.result.Result.save_csv)
* [aiomql.strategy](#aiomql.strategy)
  * [Strategy](#aiomql.strategy.Strategy)
    * [\_\_init\_\_](#aiomql.strategy.Strategy.__init__)
    * [sleep](#aiomql.strategy.Strategy.sleep)
    * [trade](#aiomql.strategy.Strategy.trade)
* [aiomql.symbol](#aiomql.symbol)
  * [Symbol](#aiomql.symbol.Symbol)
    * [pip](#aiomql.symbol.Symbol.pip)
    * [info\_tick](#aiomql.symbol.Symbol.info_tick)
    * [symbol\_select](#aiomql.symbol.Symbol.symbol_select)
    * [info](#aiomql.symbol.Symbol.info)
    * [init](#aiomql.symbol.Symbol.init)
    * [book\_add](#aiomql.symbol.Symbol.book_add)
    * [book\_get](#aiomql.symbol.Symbol.book_get)
    * [book\_release](#aiomql.symbol.Symbol.book_release)
    * [compute\_volume](#aiomql.symbol.Symbol.compute_volume)
    * [currency\_conversion](#aiomql.symbol.Symbol.currency_conversion)
    * [copy\_rates\_from](#aiomql.symbol.Symbol.copy_rates_from)
    * [copy\_rates\_from\_pos](#aiomql.symbol.Symbol.copy_rates_from_pos)
    * [copy\_rates\_range](#aiomql.symbol.Symbol.copy_rates_range)
    * [copy\_ticks\_from](#aiomql.symbol.Symbol.copy_ticks_from)
    * [copy\_ticks\_range](#aiomql.symbol.Symbol.copy_ticks_range)
* [aiomql.terminal](#aiomql.terminal)
  * [Terminal](#aiomql.terminal.Terminal)
    * [initialize](#aiomql.terminal.Terminal.initialize)
    * [version](#aiomql.terminal.Terminal.version)
    * [info](#aiomql.terminal.Terminal.info)
    * [symbols\_total](#aiomql.terminal.Terminal.symbols_total)
* [aiomql.ticks](#aiomql.ticks)
  * [Tick](#aiomql.ticks.Tick)
    * [set\_attributes](#aiomql.ticks.Tick.set_attributes)
  * [Ticks](#aiomql.ticks.Ticks)
    * [\_\_init\_\_](#aiomql.ticks.Ticks.__init__)
    * [ta](#aiomql.ticks.Ticks.ta)
    * [ta\_lib](#aiomql.ticks.Ticks.ta_lib)
    * [data](#aiomql.ticks.Ticks.data)
    * [rename](#aiomql.ticks.Ticks.rename)
* [aiomql.trader](#aiomql.trader)
  * [Trader](#aiomql.trader.Trader)
    * [\_\_init\_\_](#aiomql.trader.Trader.__init__)
    * [create\_order](#aiomql.trader.Trader.create_order)
    * [set\_order\_limits](#aiomql.trader.Trader.set_order_limits)
    * [place\_trade](#aiomql.trader.Trader.place_trade)
* [aiomql.utils](#aiomql.utils)
  * [dict\_to\_string](#aiomql.utils.dict_to_string)

<a id="aiomql"></a>

# aiomql

<a id="aiomql.account"></a>

# aiomql.account

<a id="aiomql.account.Account"></a>

## Account Objects

```python
class Account(AccountInfo)
```

A class for managing a trading account. A singleton class.
A subclass of AccountInfo. All AccountInfo attributes are available in this class.

**Attributes**:

- `connected` _bool_ - Status of connection to MetaTrader 5 Terminal
- `symbols` _set[SymbolInfo]_ - A set of available symbols for the financial market.
  

**Notes**:

  Other Account properties are defined in the AccountInfo class.

<a id="aiomql.account.Account.refresh"></a>

#### refresh

```python
async def refresh()
```

Refreshes the account instance with the latest account details from the MetaTrader 5 terminal

<a id="aiomql.account.Account.account_info"></a>

#### account\_info

```python
@property
def account_info() -> dict
```

Get account login, server and password details. If the login attribute of the account instance returns
a falsy value, the config instance is used to get the account details.

**Returns**:

- `dict` - A dict of login, server and password details
  

**Notes**:

  This method will only look for config details in the config instance if the login attribute of the
  account Instance returns a falsy value

<a id="aiomql.account.Account.__aenter__"></a>

#### \_\_aenter\_\_

```python
async def __aenter__() -> 'Account'
```

Connect to a trading account and return the account instance.
Async context manager for the Account class.

**Returns**:

- `Account` - An instance of the Account class
  

**Raises**:

- `LoginError` - If login fails

<a id="aiomql.account.Account.sign_in"></a>

#### sign\_in

```python
async def sign_in() -> bool
```

Connect to a trading account.

**Returns**:

- `bool` - True if login was successful else False

<a id="aiomql.account.Account.has_symbol"></a>

#### has\_symbol

```python
def has_symbol(symbol: str | Type[SymbolInfo])
```

Checks to see if a symbol is available for a trading account

**Arguments**:

  symbol (str | SymbolInfo):
  

**Returns**:

- `bool` - True if symbol is present otherwise False

<a id="aiomql.account.Account.symbols_get"></a>

#### symbols\_get

```python
async def symbols_get() -> set[SymbolInfo]
```

Get all financial instruments from the MetaTrader 5 terminal available for the current account.

**Returns**:

- `set[Symbol]` - A set of available symbols.

<a id="aiomql.bot_builder"></a>

# aiomql.bot\_builder

<a id="aiomql.bot_builder.Bot"></a>

## Bot Objects

```python
class Bot()
```

The bot class. Create a bot instance to run your strategies.

**Attributes**:

- `account` _Account_ - Account Object.
- `executor` - The default thread executor.
- `symbols` _set[Symbols]_ - A set of symbols for the trading session

<a id="aiomql.bot_builder.Bot.initialize"></a>

#### initialize

```python
async def initialize()
```

Prepares the bot by signing in to the trading account and initializing the symbols for the trading session.

**Raises**:

  SystemExit if sign in was not successful

<a id="aiomql.bot_builder.Bot.execute"></a>

#### execute

```python
def execute()
```

Execute the bot.

<a id="aiomql.bot_builder.Bot.start"></a>

#### start

```python
async def start()
```

Starts the bot by calling the initialize method and running the strategies in the executor.

<a id="aiomql.bot_builder.Bot.add_strategy"></a>

#### add\_strategy

```python
def add_strategy(strategy: Strategy)
```

Add a strategy to the executor. An added strategy will only run if it's symbol was successfully initialized.

**Arguments**:

- `strategy` _Strategy_ - A Strategy instance to run on bot
  

**Notes**:

  Make sure the symbol has been added to the market

<a id="aiomql.bot_builder.Bot.add_strategies"></a>

#### add\_strategies

```python
def add_strategies(strategies: Iterable[Strategy])
```

Add multiple strategies at the same time

**Arguments**:

- `strategies` - A list of strategies

<a id="aiomql.bot_builder.Bot.add_strategy_all"></a>

#### add\_strategy\_all

```python
def add_strategy_all(*, strategy: Type[Strategy], params: dict | None = None)
```

Use this to run a single strategy on all available instruments in the market using the default parameters
i.e one set of parameters for all trading symbols

**Arguments**:

- `strategy` _Strategy_ - Strategy class
- `params` _dict_ - A dictionary of parameters for the strategy

<a id="aiomql.bot_builder.Bot.init_symbols"></a>

#### init\_symbols

```python
async def init_symbols()
```

Initialize the symbols for the current trading session. This method is called internally by the bot.

<a id="aiomql.bot_builder.Bot.init_symbol"></a>

#### init\_symbol

```python
async def init_symbol(symbol: Symbol) -> Symbol
```

Initialize a symbol before the beginning of a trading sessions.
Removes it from the list of symbols if it was not successfully initialized or not available
for the current market.

**Arguments**:

- `symbol` _Symbol_ - Symbol object to be initialized
  

**Returns**:

- `Symbol` - if successfully initialized

<a id="aiomql.candle"></a>

# aiomql.candle

Candle and Candles classes for handling bars from the MetaTrader 5 terminal.

<a id="aiomql.candle.Candle"></a>

## Candle Objects

```python
class Candle()
```

A class representing bars from the MetaTrader 5 terminal as a customized class analogous to Japanese Candlesticks.
You can subclass this class for added customization.

**Attributes**:

- `time` _int_ - Period start time.
- `open` _int_ - Open price
- `high` _float_ - The highest price of the period
- `low` _float_ - The lowest price of the period
- `close` _float_ - Close price
- `tick_volume` _float_ - Tick volume
- `real_volume` _float_ - Trade volume
- `spread` _float_ - Spread
- `Index` _int_ - Custom attribute representing the position of the candle in a sequence.

<a id="aiomql.candle.Candle.__init__"></a>

#### \_\_init\_\_

```python
def __init__(**kwargs)
```

Create a Candle object from keyword arguments.

**Arguments**:

- `**kwargs` - Candle attributes and values as keyword arguments.

<a id="aiomql.candle.Candle.set_attributes"></a>

#### set\_attributes

```python
def set_attributes(**kwargs)
```

Set keyword arguments as instance attributes

**Arguments**:

- `**kwargs` - Instance attributes and values as keyword arguments

<a id="aiomql.candle.Candle.mid"></a>

#### mid

```python
@property
def mid() -> float
```

The median of open and close

**Returns**:

- `float` - The median of open and close

<a id="aiomql.candle.Candle.is_bullish"></a>

#### is\_bullish

```python
def is_bullish() -> bool
```

A simple check to see if the candle is bullish.

**Returns**:

- `bool` - True or False

<a id="aiomql.candle.Candle.is_bearish"></a>

#### is\_bearish

```python
def is_bearish() -> bool
```

A simple check to see if the candle is bearish.

**Returns**:

- `bool` - True or False

<a id="aiomql.candle.Candles"></a>

## Candles Objects

```python
class Candles(Generic[_Candle])
```

An iterable container class of Candle objects in chronological order.

**Attributes**:

- `Index` _Series['int']_ - A pandas Series of the indexes of all candles in the object.
- `time` _Series['int']_ - A pandas Series of the time of all candles in the object.
- `open` _Series[float]_ - A pandas Series of the opening price of all candles in the object.
- `high` _Series[float]_ - A pandas Series of the high price of all candles in the object.
- `low` _Series[float]_ - A pandas Series of the low price of all candles in the object.
- `close` _Series[float]_ - A pandas Series of the closing price of all candles in the object.
- `tick_volume` _Series[float]_ - A pandas Series of the tick volume of all candles in the object.
- `real_volume` _Series[float]_ - A pandas Series of the real volume of all candles in the object.
- `spread` _Series[float]_ - A pandas Series of the spread of all candles in the object.
- `timeframe` _TimeFrame_ - The timeframe of the candles in the object.
- `Candle` _Type[Candle]_ - The Candle class for representing the candles in the object.
  
  properties:
- `data` _DataFrame_ - A pandas DataFrame of all candles in the object.
  

**Notes**:

  The candle class can be customized by subclassing the Candle class and passing the subclass as the candle keyword argument.
  Or defining it on the class body as a class attribute.

<a id="aiomql.candle.Candles.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*,
             data: DataFrame | _Candles | Iterable,
             flip=False,
             candle_class: Type[_Candle] = None)
```

A container class of Candle objects in chronological order.

**Arguments**:

- `data` _DataFrame|Candles|Iterable_ - A pandas dataframe, a Candles object or any suitable iterable
  

**Arguments**:

- `flip` _bool_ - Reverse the chronological order of the candles to the oldest first. Defaults to False.
- `candle_class` - A subclass of Candle to use as the candle class. Defaults to Candle.

<a id="aiomql.candle.Candles.ta"></a>

#### ta

```python
@property
def ta()
```

Access to the pandas_ta library for performing technical analysis on the underlying data attribute.

**Returns**:

- `pandas_ta` - The pandas_ta library

<a id="aiomql.candle.Candles.ta_lib"></a>

#### ta\_lib

```python
@property
def ta_lib()
```

Access to the ta library for performing technical analysis. Not dependent on the underlying data attribute.

**Returns**:

- `ta` - The ta library

<a id="aiomql.candle.Candles.data"></a>

#### data

```python
@property
def data() -> DataFrame
```

The original data passed to the class as a pandas DataFrame

<a id="aiomql.candle.Candles.rename"></a>

#### rename

```python
def rename(inplace=True, **kwargs) -> _Candles | None
```

Rename columns of the candles class.

**Arguments**:

- `inplace` _bool_ - Rename the columns inplace or return a new instance of the class with the renamed columns
- `**kwargs` - The new names of the columns
  

**Returns**:

- `Candles` - A new instance of the class with the renamed columns if inplace is False.
- `None` - If inplace is True

<a id="aiomql.core.base"></a>

# aiomql.core.base

<a id="aiomql.core.base.Base"></a>

## Base Objects

```python
class Base()
```

A base class for all data model classes in the aiomql package.
This class provides a set of common methods and attributes for all data model classes.
For the data model classes attributes are annotated on the class body and are set as object attributes when the
class is instantiated.

**Arguments**:

- `**kwargs` - Object attributes and values as keyword arguments. Only added if they are annotated on the class body.
  
  Class Attributes:
- `mt5` _MetaTrader_ - An instance of the MetaTrader class
- `config` _Config_ - An instance of the Config class
- `Meta` _Type[Meta]_ - The Meta class for configuration of the data model class

<a id="aiomql.core.base.Base.set_attributes"></a>

#### set\_attributes

```python
def set_attributes(**kwargs)
```

Set keyword arguments as object attributes

**Arguments**:

- `**kwargs` - Object attributes and values as keyword arguments
  

**Raises**:

- `AttributeError` - When assigning an attribute that does not belong to the class or any parent class
  

**Notes**:

  Only sets attributes that have been annotated on the class body.

<a id="aiomql.core.base.Base.annotations"></a>

#### annotations

```python
@property
@cache
def annotations() -> dict
```

Class annotations from all ancestor classes and the current class.

**Returns**:

- `dict` - A dictionary of class annotations

<a id="aiomql.core.base.Base.get_dict"></a>

#### get\_dict

```python
def get_dict(exclude: set = None, include: set = None) -> dict
```

Returns class attributes as a dict, with the ability to filter

**Arguments**:

- `exclude` - A set of attributes to be excluded
- `include` - Specific attributes to be returned
  

**Returns**:

- `dict` - A dictionary of specified class attributes
  

**Notes**:

  You can only set either of include or exclude. If you set both, include will take precedence

<a id="aiomql.core.base.Base.class_vars"></a>

#### class\_vars

```python
@property
@cache
def class_vars()
```

Annotated class attributes

**Returns**:

- `dict` - A dictionary of available class attributes in all ancestor classes and the current class.

<a id="aiomql.core.base.Base.dict"></a>

#### dict

```python
@property
def dict() -> dict
```

All instance and class attributes as a dictionary, except those excluded in the Meta class.

**Returns**:

- `dict` - A dictionary of instance and class attributes

<a id="aiomql.core.base.Base.Meta"></a>

## Meta Objects

```python
class Meta()
```

A class for defining class attributes to be excluded or included in the dict property

**Attributes**:

- `exclude` _set_ - A set of attributes to be excluded
- `include` _set_ - Specific attributes to be returned. Include supercedes exclude.

<a id="aiomql.core.base.Base.Meta.filter"></a>

#### filter

```python
@classmethod
@property
def filter(cls) -> set
```

Combine the exclude and include attributes to return a set of attributes to be excluded.

**Returns**:

- `set` - A set of attributes to be excluded

<a id="aiomql.core.config"></a>

# aiomql.core.config

<a id="aiomql.core.config.Config"></a>

## Config Objects

```python
class Config()
```

A class for handling configuration settings for the aiomql package.

**Arguments**:

- `**kwargs` - Configuration settings as keyword arguments.
  Variables set this way supersede those set in the config file.
  

**Attributes**:

- `record_trades` _bool_ - Whether to keep record of trades or not.
- `filename` _str_ - Name of the config file
- `records_dir` _str_ - Path to the directory where trade records are saved
- `win_percentage` _float_ - Percentage of achieved target profit in a trade to be considered a win
- `login` _int_ - Trading account number
- `password` _str_ - Trading account password
- `server` _str_ - Broker server
- `path` _str_ - Path to terminal file
- `timeout` _int_ - Timeout for terminal connection
  

**Notes**:

  By default, the config class looks for a file named aiomql.json.
  You can change this by passing the filename keyword argument to the constructor.
  By passing reload=True to the load_config method, you can reload and search again for the config file.

<a id="aiomql.core.config.Config.account_info"></a>

#### account\_info

```python
def account_info() -> dict['login', 'password', 'server']
```

Returns Account login details as found in the config object if available

**Returns**:

- `dict` - A dictionary of login details

<a id="aiomql.core.constants"></a>

# aiomql.core.constants

<a id="aiomql.core.constants.TradeAction"></a>

## TradeAction Objects

```python
class TradeAction(Repr, IntEnum)
```

TRADE_REQUEST_ACTION Enum.

**Attributes**:

- `DEAL` _int_ - Delete the pending order placed previously Place a trade order for an immediate execution with the
  specified parameters (market order).
- `PENDING` _int_ - Delete the pending order placed previously
- `SLTP` _int_ - Modify Stop Loss and Take Profit values of an opened position
- `MODIFY` _int_ - Modify the parameters of the order placed previously
- `REMOVE` _int_ - Delete the pending order placed previously
- `CLOSE_BY` _int_ - Close a position by an opposite one

<a id="aiomql.core.constants.OrderFilling"></a>

## OrderFilling Objects

```python
class OrderFilling(Repr, IntEnum)
```

ORDER_TYPE_FILLING Enum.

**Attributes**:

- `FOK` _int_ - This execution policy means that an order can be executed only in the specified volume.
  If the necessary amount of a financial instrument is currently unavailable in the market, the order will
  not be executed. The desired volume can be made up of several available offers.
  
- `IOC` _int_ - An agreement to execute a deal at the maximum volume available in the market within the volume
  specified in the order. If the request cannot be filled completely, an order with the available volume will
  be executed, and the remaining volume will be canceled.
  
- `RETURN` _int_ - This policy is used only for market (ORDER_TYPE_BUY and ORDER_TYPE_SELL), limit and stop limit
  orders (ORDER_TYPE_BUY_LIMIT, ORDER_TYPE_SELL_LIMIT,ORDER_TYPE_BUY_STOP_LIMIT and
  ORDER_TYPE_SELL_STOP_LIMIT) and only for the symbols with Market or Exchange execution modes. If filled
  partially, a market or limit order with the remaining volume is not canceled, and is processed further.
  During activation of the ORDER_TYPE_BUY_STOP_LIMIT and ORDER_TYPE_SELL_STOP_LIMIT orders, an appropriate
  limit order ORDER_TYPE_BUY_LIMIT/ORDER_TYPE_SELL_LIMIT with the ORDER_FILLING_RETURN type is created.

<a id="aiomql.core.constants.OrderTime"></a>

## OrderTime Objects

```python
class OrderTime(Repr, IntEnum)
```

ORDER_TIME Enum.

**Attributes**:

- `GTC` _int_ - Good till cancel order
- `DAY` _int_ - Good till current trade day order
- `SPECIFIED` _int_ - The order is active until the specified date
- `SPECIFIED_DAY` _int_ - The order is active until 23:59:59 of the specified day. If this time appears to be out of
  a trading session, the expiration is processed at the nearest trading time.

<a id="aiomql.core.constants.OrderType"></a>

## OrderType Objects

```python
class OrderType(Repr, IntEnum)
```

ORDER_TYPE Enum.

**Attributes**:

- `BUY` _int_ - Market buy order
- `SELL` _int_ - Market sell order
- `BUY_LIMIT` _int_ - Buy Limit pending order
- `SELL_LIMIT` _int_ - Sell Limit pending order
- `BUY_STOP` _int_ - Buy Stop pending order
- `SELL_STOP` _int_ - Sell Stop pending order
- `BUY_STOP_LIMIT` _int_ - Upon reaching the order price, Buy Limit pending order is placed at StopLimit price
- `SELL_STOP_LIMIT` _int_ - Upon reaching the order price, Sell Limit pending order is placed at StopLimit price
- `CLOSE_BY` _int_ - Order for closing a position by an opposite one
  
  Properties:
- `opposite` _int_ - Gets the opposite of an order type

<a id="aiomql.core.constants.OrderType.opposite"></a>

#### opposite

```python
@property
def opposite()
```

Gets the opposite of an order type for closing an open position

**Returns**:

- `int` - integer value of opposite order type

<a id="aiomql.core.constants.BookType"></a>

## BookType Objects

```python
class BookType(Repr, IntEnum)
```

BOOK_TYPE Enum.

**Attributes**:

- `SELL` _int_ - Sell order (Offer)
- `BUY` _int_ - Buy order (Bid)
- `SELL_MARKET` _int_ - Sell order by Market
- `BUY_MARKET` _int_ - Buy order by Market

<a id="aiomql.core.constants.TimeFrame"></a>

## TimeFrame Objects

```python
class TimeFrame(Repr, IntEnum)
```

TIMEFRAME Enum.

**Attributes**:

- `M1` _int_ - One Minute
- `M2` _int_ - Two Minutes
- `M3` _int_ - Three Minutes
- `M4` _int_ - Four Minutes
- `M5` _int_ - Five Minutes
- `M6` _int_ - Six Minutes
- `M10` _int_ - Ten Minutes
- `M15` _int_ - Fifteen Minutes
- `M20` _int_ - Twenty Minutes
- `M30` _int_ - Thirty Minutes
- `H1` _int_ - One Hour
- `H2` _int_ - Two Hours
- `H3` _int_ - Three Hours
- `H4` _int_ - Four Hours
- `H6` _int_ - Six Hours
- `H8` _int_ - Eight Hours
- `D1` _int_ - One Day
- `W1` _int_ - One Week
- `MN1` _int_ - One Month
  
  Properties:
- `time` - return the value of the timeframe object in seconds. Used as a property
  

**Methods**:

- `get` - get a timeframe object from a time value in seconds

<a id="aiomql.core.constants.TimeFrame.time"></a>

#### time

```python
@property
def time()
```

The number of seconds in a TIMEFRAME

**Returns**:

- `int` - The number of seconds in a TIMEFRAME
  

**Examples**:

  >>> t = TimeFrame.H1
  >>> print(t.time)
  3600

<a id="aiomql.core.constants.CopyTicks"></a>

## CopyTicks Objects

```python
class CopyTicks(Repr, IntEnum)
```

COPY_TICKS Enum. This defines the types of ticks that can be requested using the copy_ticks_from() and
copy_ticks_range() functions.

**Attributes**:

- `ALL` _int_ - All ticks
- `INFO` _int_ - Ticks containing Bid and/or Ask price changes
- `TRADE` _int_ - Ticks containing Last and/or Volume price changes

<a id="aiomql.core.constants.PositionType"></a>

## PositionType Objects

```python
class PositionType(Repr, IntEnum)
```

POSITION_TYPE Enum. Direction of an open position (buy or sell)

**Attributes**:

- `BUY` _int_ - Buy
- `SELL` _int_ - Sell

<a id="aiomql.core.constants.PositionReason"></a>

## PositionReason Objects

```python
class PositionReason(Repr, IntEnum)
```

POSITION_REASON Enum. The reason for opening a position is contained in the POSITION_REASON Enum

**Attributes**:

- `CLIENT` _int_ - The position was opened as a result of activation of an order placed from a desktop terminal
- `MOBILE` _int_ - The position was opened as a result of activation of an order placed from a mobile application
- `WEB` _int_ - The position was opened as a result of activation of an order placed from the web platform
- `EXPERT` _int_ - The position was opened as a result of activation of an order placed from an MQL5 program,
  i.e. an Expert Advisor or a script

<a id="aiomql.core.constants.DealType"></a>

## DealType Objects

```python
class DealType(Repr, IntEnum)
```

DEAL_TYPE enum. Each deal is characterized by a type, allowed values are enumerated in this enum

**Attributes**:

- `BUY` _int_ - Buy
- `SELL` _int_ - Sell
- `BALANCE` _int_ - Balance
- `CREDIT` _int_ - Credit
- `CHARGE` _int_ - Additional Charge
- `CORRECTION` _int_ - Correction
- `BONUS` _int_ - Bonus
- `COMMISSION` _int_ - Additional Commission
- `COMMISSION_DAILY` _int_ - Daily Commission
- `COMMISSION_MONTHLY` _int_ - Monthly Commission
- `COMMISSION_AGENT_DAILY` _int_ - Daily Agent Commission
- `COMMISSION_AGENT_MONTHLY` _int_ - Monthly Agent Commission
- `INTEREST` _int_ - Interest Rate
- `DEAL_DIVIDEND` _int_ - Dividend Operations
- `DEAL_DIVIDEND_FRANKED` _int_ - Franked (non-taxable) dividend operations
- `DEAL_TAX` _int_ - Tax Charges
  
- `BUY_CANCELED` _int_ - Canceled buy deal. There can be a situation when a previously executed buy deal is canceled.
  In this case, the type of the previously executed deal (DEAL_TYPE_BUY) is changed to DEAL_TYPE_BUY_CANCELED,
  and its profit/loss is zeroized. Previously obtained profit/loss is charged/withdrawn using a separated
  balance operation
  
- `SELL_CANCELED` _int_ - Canceled sell deal. There can be a situation when a previously executed sell deal is
  canceled. In this case, the type of the previously executed deal (DEAL_TYPE_SELL) is changed to
  DEAL_TYPE_SELL_CANCELED, and its profit/loss is zeroized. Previously obtained profit/loss is
  charged/withdrawn using a separated balance operation.

<a id="aiomql.core.constants.DealEntry"></a>

## DealEntry Objects

```python
class DealEntry(Repr, IntEnum)
```

DEAL_ENTRY Enum. Deals differ not only in their types set in DEAL_TYPE enum, but also in the way they change
positions. This can be a simple position opening, or accumulation of a previously opened position (market entering),
position closing by an opposite deal of a corresponding volume (market exiting), or position reversing, if the
opposite-direction deal covers the volume of the previously opened position.

**Attributes**:

- `IN` _int_ - Entry In
- `OUT` _int_ - Entry Out
- `INOUT` _int_ - Reverse
- `OUT_BY` _int_ - Close a position by an opposite one

<a id="aiomql.core.constants.DealReason"></a>

## DealReason Objects

```python
class DealReason(Repr, IntEnum)
```

DEAL_REASON Enum. The reason for deal execution is contained in the DEAL_REASON property. A deal can be executed
as a result of triggering of an order placed from a mobile application or an MQL5 program, as well as as a result
of the StopOut event, variation margin calculation, etc.

**Attributes**:

- `CLIENT` _int_ - The deal was executed as a result of activation of an order placed from a desktop terminal
- `MOBILE` _int_ - The deal was executed as a result of activation of an order placed from a desktop terminal
- `WEB` _int_ - The deal was executed as a result of activation of an order placed from the web platform
- `EXPERT` _int_ - The deal was executed as a result of activation of an order placed from an MQL5 program, i.e.
  an Expert Advisor or a script
- `SL` _int_ - The deal was executed as a result of Stop Loss activation
- `TP` _int_ - The deal was executed as a result of Take Profit activation
- `SO` _int_ - The deal was executed as a result of the Stop Out event
- `ROLLOVER` _int_ - The deal was executed due to a rollover
- `VMARGIN` _int_ - The deal was executed after charging the variation margin
- `SPLIT` _int_ - The deal was executed after the split (price reduction) of an instrument, which had an open
  position during split announcement

<a id="aiomql.core.constants.OrderReason"></a>

## OrderReason Objects

```python
class OrderReason(Repr, IntEnum)
```

ORDER_REASON Enum.

**Attributes**:

- `CLIENT` _int_ - The order was placed from a desktop terminal
- `MOBILE` _int_ - The order was placed from a mobile application
- `WEB` _int_ - The order was placed from a web platform
- `EXPERT` _int_ - The order was placed from an MQL5-program, i.e. by an Expert Advisor or a script
- `SL` _int_ - The order was placed as a result of Stop Loss activation
- `TP` _int_ - The order was placed as a result of Take Profit activation
- `SO` _int_ - The order was placed as a result of the Stop Out event

<a id="aiomql.core.constants.SymbolChartMode"></a>

## SymbolChartMode Objects

```python
class SymbolChartMode(Repr, IntEnum)
```

SYMBOL_CHART_MODE Enum. A symbol price chart can be based on Bid or Last prices. The price selected for symbol
charts also affects the generation and display of bars in the terminal.
Possible values of the SYMBOL_CHART_MODE property are described in this enum

**Attributes**:

- `BID` _int_ - Bars are based on Bid prices
- `LAST` _int_ - Bars are based on last prices

<a id="aiomql.core.constants.SymbolCalcMode"></a>

## SymbolCalcMode Objects

```python
class SymbolCalcMode(Repr, IntEnum)
```

SYMBOL_CALC_MODE Enum. The SYMBOL_CALC_MODE enumeration is used for obtaining information about how the margin
requirements for a symbol are calculated.

**Attributes**:

- `FOREX` _int_ - Forex mode - calculation of profit and margin for Forex
- `FOREX_NO_LEVERAGE` _int_ - Forex No Leverage mode – calculation of profit and margin for Forex symbols without
  taking into account the leverage
- `FUTURES` _int_ - Futures mode - calculation of margin and profit for futures
- `CFD` _int_ - CFD mode - calculation of margin and profit for CFD
- `CFDINDEX` _int_ - CFD index mode - calculation of margin and profit for CFD by indexes
- `CFDLEVERAGE` _int_ - CFD Leverage mode - calculation of margin and profit for CFD at leverage trading
- `EXCH_STOCKS` _int_ - Calculation of margin and profit for trading securities on a stock exchange
- `EXCH_FUTURES` _int_ - Calculation of margin and profit for trading futures contracts on a stock exchange
- `EXCH_OPTIONS` _int_ - value is 34
- `EXCH_OPTIONS_MARGIN` _int_ - value is 36
- `EXCH_BONDS` _int_ - Exchange Bonds mode – calculation of margin and profit for trading bonds on a stock exchange
- `STOCKS_MOEX` _int_ - Exchange MOEX Stocks mode –calculation of margin and profit for trading securities on MOEX
- `EXCH_BONDS_MOEX` _int_ - Exchange MOEX Bonds mode – calculation of margin and profit for trading bonds on MOEX
  
- `SERV_COLLATERAL` _int_ - Collateral mode - a symbol is used as a non-tradable asset on a trading account.
  The market value of an open position is calculated based on the volume, current market price, contract size
  and liquidity ratio. The value is included into Assets, which are added to Equity. Open positions of such
  symbols increase the Free Margin amount and are used as additional margin (collateral) for open positions

<a id="aiomql.core.constants.SymbolTradeMode"></a>

## SymbolTradeMode Objects

```python
class SymbolTradeMode(Repr, IntEnum)
```

SYMBOL_TRADE_MODE Enum. There are several symbol trading modes. Information about trading modes of a certain
symbol is reflected in the values this enumeration

**Attributes**:

- `DISABLED` _int_ - Trade is disabled for the symbol
- `LONGONLY` _int_ - Allowed only long positions
- `SHORTONLY` _int_ - Allowed only short positions
- `CLOSEONLY` _int_ - Allowed only position close operations
- `FULL` _int_ - No trade restrictions

<a id="aiomql.core.constants.SymbolTradeExecution"></a>

## SymbolTradeExecution Objects

```python
class SymbolTradeExecution(Repr, IntEnum)
```

SYMBOL_TRADE_EXECUTION Enum. The modes, or execution policies, define the rules for cases when the price has
changed or the requested volume cannot be completely fulfilled at the moment.

**Attributes**:

- `REQUEST` _int_ - Executing a market order at the price previously received from the broker. Prices for a certain
  market order are requested from the broker before the order is sent. Upon receiving the prices, order
  execution at the given price can be either confirmed or rejected.
  
- `INSTANT` _int_ - Executing a market order at the specified price immediately. When sending a trade request to be
  executed, the platform automatically adds the current prices to the order.
  - If the broker accepts the price, the order is executed.
  - If the broker does not accept the requested price, a "Requote" is sent — the broker returns prices,
  at which this order can be executed.
  
- `MARKET` _int_ - A broker makes a decision about the order execution price without any additional discussion with the trader.
  Sending the order in such a mode means advance consent to its execution at this price.
  
- `EXCHANGE` _int_ - Trade operations are executed at the prices of the current market offers.

<a id="aiomql.core.constants.SymbolSwapMode"></a>

## SymbolSwapMode Objects

```python
class SymbolSwapMode(Repr, IntEnum)
```

SYMBOL_SWAP_MODE Enum. Methods of swap calculation at position transfer are specified in enumeration
ENUM_SYMBOL_SWAP_MODE. The method of swap calculation determines the units of measure of the SYMBOL_SWAP_LONG and
SYMBOL_SWAP_SHORT parameters. For example, if swaps are charged in the client deposit currency, then the values of
those parameters are specified as an amount of money in the client deposit currency.

**Attributes**:

- `DISABLED` _int_ - Swaps disabled (no swaps)
- `POINTS` _int_ - Swaps are charged in points
- `CURRENCY_SYMBOL` _int_ - Swaps are charged in money in base currency of the symbol
- `CURRENCY_MARGIN` _int_ - Swaps are charged in money in margin currency of the symbol
- `CURRENCY_DEPOSIT` _int_ - Swaps are charged in money, in client deposit currency
  
- `INTEREST_CURRENT` _int_ - Swaps are charged as the specified annual interest from the instrument price at
  calculation of swap (standard bank year is 360 days)
  
- `INTEREST_OPEN` _int_ - Swaps are charged as the specified annual interest from the open price of position
  (standard bank year is 360 days)
  
- `REOPEN_CURRENT` _int_ - Swaps are charged by reopening positions. At the end of a trading day the position is
  closed. Next day it is reopened by the close price +/- specified number of points
  (parameters SYMBOL_SWAP_LONG and SYMBOL_SWAP_SHORT)
  
- `REOPEN_BID` _int_ - Swaps are charged by reopening positions. At the end of a trading day the position is closed.
  Next day it is reopened by the current Bid price +/- specified number of
  points (parameters SYMBOL_SWAP_LONG and SYMBOL_SWAP_SHORT)

<a id="aiomql.core.constants.DayOfWeek"></a>

## DayOfWeek Objects

```python
class DayOfWeek(Repr, IntEnum)
```

DAY_OF_WEEK Enum.

**Attributes**:

- `SUNDAY` _int_ - Sunday
- `MONDAY` _int_ - Monday
- `TUESDAY` _int_ - Tuesday
- `WEDNESDAY` _int_ - Wednesday
- `THURSDAY` _int_ - Thursday
- `FRIDAY` _int_ - Friday
- `SATURDAY` _int_ - Saturday

<a id="aiomql.core.constants.SymbolOrderGTCMode"></a>

## SymbolOrderGTCMode Objects

```python
class SymbolOrderGTCMode(Repr, IntEnum)
```

SYMBOL_ORDER_GTC_MODE Enum. If the SYMBOL_EXPIRATION_MODE property is set to SYMBOL_EXPIRATION_GTC
(good till canceled), the expiration of pending orders, as well as of
Stop Loss/Take Profit orders should be additionally set using the ENUM_SYMBOL_ORDER_GTC_MODE enumeration.

**Attributes**:

- `GTC` _int_ - Pending orders and Stop Loss/Take Profit levels are valid for an unlimited period
  until theirConstants, Enumerations and explicit cancellation
  
- `DAILY` _int_ - Orders are valid during one trading day. At the end of the day, all Stop Loss and
  Take Profit levels, as well as pending orders are deleted.
  
- `DAILY_NO_STOPS` _int_ - When a trade day changes, only pending orders are deleted,
  while Stop Loss and Take Profit levels are preserved

<a id="aiomql.core.constants.SymbolOptionRight"></a>

## SymbolOptionRight Objects

```python
class SymbolOptionRight(Repr, IntEnum)
```

SYMBOL_OPTION_RIGHT Enum. An option is a contract, which gives the right, but not the obligation,
to buy or sell an underlying asset (goods, stocks, futures, etc.) at a specified price on or before a specific date.
The following enumerations describe option properties, including the option type and the right arising from it.

**Attributes**:

- `CALL` _int_ - A call option gives you the right to buy an asset at a specified price.
- `PUT` _int_ - A put option gives you the right to sell an asset at a specified price.

<a id="aiomql.core.constants.SymbolOptionMode"></a>

## SymbolOptionMode Objects

```python
class SymbolOptionMode(Repr, IntEnum)
```

SYMBOL_OPTION_MODE Enum.

**Attributes**:

- `EUROPEAN` _int_ - European option may only be exercised on a specified date (expiration, execution date, delivery date)
- `AMERICAN` _int_ - American option may be exercised on any trading day or before expiry. The period within which
  a buyer can exercise the option is specified for it.

<a id="aiomql.core.constants.AccountTradeMode"></a>

## AccountTradeMode Objects

```python
class AccountTradeMode(Repr, IntEnum)
```

ACCOUNT_TRADE_MODE Enum. There are several types of accounts that can be opened on a trade server.
The type of account on which an MQL5 program is running can be found out using
the ENUM_ACCOUNT_TRADE_MODE enumeration.

**Attributes**:

- `DEMO` - Demo account
- `CONTEST` - Contest account
- `REAL` - Real Account

<a id="aiomql.core.constants.TickFlag"></a>

## TickFlag Objects

```python
class TickFlag(Repr, IntFlag)
```

TICK_FLAG Enum. TICK_FLAG defines possible flags for ticks. These flags are used to describe ticks obtained by the
copy_ticks_from() and copy_ticks_range() functions.

**Attributes**:

- `BID` _int_ - Bid price changed
- `ASK` _int_ - Ask price changed
- `LAST` _int_ - Last price changed
- `VOLUME` _int_ - Volume changed
- `BUY` _int_ - last Buy price changed
- `SELL` _int_ - last Sell price changed

<a id="aiomql.core.constants.TradeRetcode"></a>

## TradeRetcode Objects

```python
class TradeRetcode(Repr, IntEnum)
```

TRADE_RETCODE Enum. Return codes for order send/check operations

**Attributes**:

- `REQUOTE` _int_ - Requote
- `REJECT` _int_ - Request rejected
- `CANCEL` _int_ - Request canceled by trader
- `PLACED` _int_ - Order placed
- `DONE` _int_ - Request completed
- `DONE_PARTIAL` _int_ - Only part of the request was completed
- `ERROR` _int_ - Request processing error
- `TIMEOUT` _int_ - Request canceled by timeout
- `INVALID` _int_ - Invalid request
- `INVALID_VOLUME` _int_ - Invalid volume in the request
- `INVALID_PRICE` _int_ - Invalid price in the request
- `INVALID_STOPS` _int_ - Invalid stops in the request
- `TRADE_DISABLED` _int_ - Trade is disabled
- `MARKET_CLOSED` _int_ - Market is closed
- `NO_MONEY` _int_ - There is not enough money to complete the request
- `PRICE_CHANGED` _int_ - Prices changed
- `PRICE_OFF` _int_ - There are no quotes to process the request
- `INVALID_EXPIRATION` _int_ - Invalid order expiration date in the request
- `ORDER_CHANGED` _int_ - Order state changed
- `TOO_MANY_REQUESTS` _int_ - Too frequent requests
- `NO_CHANGES` _int_ - No changes in request
- `SERVER_DISABLES_AT` _int_ - Autotrading disabled by server
- `CLIENT_DISABLES_AT` _int_ - Autotrading disabled by client terminal
- `LOCKED` _int_ - Request locked for processing
- `FROZEN` _int_ - Order or position frozen
- `INVALID_FILL` _int_ - Invalid order filling type
- `CONNECTION` _int_ - No connection with the trade server
- `ONLY_REAL` _int_ - Operation is allowed only for live accounts
- `LIMIT_ORDERS` _int_ - The number of pending orders has reached the limit
- `LIMIT_VOLUME` _int_ - The volume of orders and positions for the symbol has reached the limit
- `INVALID_ORDER` _int_ - Incorrect or prohibited order type
- `POSITION_CLOSED` _int_ - Position with the specified POSITION_IDENTIFIER has already been closed
- `INVALID_CLOSE_VOLUME` _int_ - A close volume exceeds the current position volume
  
- `CLOSE_ORDER_EXIST` _int_ - A close order already exists for a specified position. This may happen when working in
  the hedging system:
  · when attempting to close a position with an opposite one, while close orders for the position already exist
  · when attempting to fully or partially close a position if the total volume of the already present close
  orders and the newly placed one exceeds the current position volume
  
- `LIMIT_POSITIONS` _int_ - The number of open positions simultaneously present on an account can be limited by the
  server settings.After a limit is reached, the server returns the TRADE_RETCODE_LIMIT_POSITIONS error when
  attempting to place an order. The limitation operates differently depending on the position accounting type:
  · Netting — number of open positions is considered. When a limit is reached, the platform does not let
  placing new orders whose execution may increase the number of open positions. In fact, the platform
  allows placing orders only for the symbols that already have open positions.
  The current pending orders are not considered since their execution may lead to changes in the current
  positions but it cannot increase their number.
  
  · Hedging — pending orders are considered together with open positions, since a pending order activation
  always leads to opening a new position. When a limit is reached, the platform does not allow placing
  both new market orders for opening positions and pending orders.
  
- `REJECT_CANCEL` _int_ - The pending order activation request is rejected, the order is canceled.
- `LONG_ONLY` _int_ - The request is rejected, because the "Only long positions are allowed" rule is set for the
  symbol (POSITION_TYPE_BUY)
- `SHORT_ONLY` _int_ - The request is rejected, because the "Only short positions are allowed" rule is set for the
  symbol (POSITION_TYPE_SELL)
- `CLOSE_ONLY` _int_ - The request is rejected, because the "Only position closing is allowed" rule is set for the
  symbol
- `FIFO_CLOSE` _int_ - The request is rejected, because "Position closing is allowed only by FIFO rule" flag is set
  for the trading account (ACCOUNT_FIFO_CLOSE=true)

<a id="aiomql.core.constants.AccountStopOutMode"></a>

## AccountStopOutMode Objects

```python
class AccountStopOutMode(Repr, IntEnum)
```

ACCOUNT_STOPOUT_MODE Enum.

**Attributes**:

- `PERCENT` _int_ - Account stop out mode in percents
- `MONEY` _int_ - Account stop out mode in money

<a id="aiomql.core.constants.AccountMarginMode"></a>

## AccountMarginMode Objects

```python
class AccountMarginMode(Repr, IntEnum)
```

ACCOUNT_MARGIN_MODE Enum.

**Attributes**:

- `RETAIL_NETTING` _int_ - Used for the OTC markets to interpret positions in the "netting"
  mode (only one position can exist for one symbol). The margin is calculated based on the symbol
  type (SYMBOL_TRADE_CALC_MODE).
  
- `EXCHANGE` _int_ - Used for the exchange markets. Margin is calculated based on the discounts specified in
  symbol settings. Discounts are set by the broker, but not less than the values set by the exchange.
  
- `HEDGING` _int_ - Used for the exchange markets where individual positions are possible
  (hedging, multiple positions can exist for one symbol). The margin is calculated based on the symbol
  type (SYMBOL_TRADE_CALC_MODE) taking into account the hedged margin (SYMBOL_MARGIN_HEDGED).

<a id="aiomql.core.errors"></a>

# aiomql.core.errors

<a id="aiomql.core.errors.Error"></a>

## Error Objects

```python
class Error()
```

Error class for handling errors from MetaTrader 5.

<a id="aiomql.core.exceptions"></a>

# aiomql.core.exceptions

Exceptions for the aiomql package.

<a id="aiomql.core.exceptions.LoginError"></a>

## LoginError Objects

```python
class LoginError(Exception)
```

Raised when an error occurs when logging in.

<a id="aiomql.core.exceptions.VolumeError"></a>

## VolumeError Objects

```python
class VolumeError(Exception)
```

Raised when a volume is not valid or out of range for a symbol.

<a id="aiomql.core.exceptions.SymbolError"></a>

## SymbolError Objects

```python
class SymbolError(Exception)
```

Raised when a symbol is not provided where required or not available in the Market Watch.

<a id="aiomql.core.exceptions.OrderError"></a>

## OrderError Objects

```python
class OrderError(Exception)
```

Raised when an error occurs when working with the order class.

<a id="aiomql.core.meta_trader"></a>

# aiomql.core.meta\_trader

<a id="aiomql.core.meta_trader.MetaTrader"></a>

## MetaTrader Objects

```python
class MetaTrader(metaclass=BaseMeta)
```

<a id="aiomql.core.meta_trader.MetaTrader.__aenter__"></a>

#### \_\_aenter\_\_

```python
async def __aenter__() -> 'MetaTrader'
```

Async context manager entry point.
Initializes the connection to the MetaTrader terminal.

**Returns**:

- `MetaTrader` - An instance of the MetaTrader class.

<a id="aiomql.core.meta_trader.MetaTrader.__aexit__"></a>

#### \_\_aexit\_\_

```python
async def __aexit__(exc_type, exc_val, exc_tb)
```

Async context manager exit point. Closes the connection to the MetaTrader terminal.

<a id="aiomql.core.meta_trader.MetaTrader.login"></a>

#### login

```python
async def login(login: int,
                password: str,
                server: str,
                timeout: int = 60000) -> bool
```

Connects to the MetaTrader terminal using the specified login, password and server.

**Arguments**:

- `login` _int_ - The trading account number.
- `password` _str_ - The trading account password.
- `server` _str_ - The trading server name.
- `timeout` _int_ - The timeout for the connection in seconds.
  

**Returns**:

- `bool` - True if successful, False otherwise.

<a id="aiomql.core.meta_trader.MetaTrader.initialize"></a>

#### initialize

```python
async def initialize(path: str = "",
                     login: int = 0,
                     password: str = "",
                     server: str = "",
                     timeout: int | None = None,
                     portable=False) -> bool
```

Initializes the connection to the MetaTrader terminal. All parameters are optional.

**Arguments**:

- `path` _str_ - The path to the MetaTrader terminal executable.
- `login` _int_ - The trading account number.
- `password` _str_ - The trading account password.
- `server` _str_ - The trading server name.
- `timeout` _int_ - The timeout for the connection in seconds.
- `portable` _bool_ - If True, the terminal will be launched in portable mode.
  

**Returns**:

- `bool` - True if successful, False otherwise.

<a id="aiomql.core.meta_trader.MetaTrader.shutdown"></a>

#### shutdown

```python
async def shutdown() -> None
```

Closes the connection to the MetaTrader terminal.

**Returns**:

- `None` - None

<a id="aiomql.core.meta_trader.MetaTrader.version"></a>

#### version

```python
async def version() -> tuple[int, int, str] | None
```



<a id="aiomql.core.meta_trader.MetaTrader.account_info"></a>

#### account\_info

```python
async def account_info() -> AccountInfo | None
```



<a id="aiomql.core.meta_trader.MetaTrader.orders_get"></a>

#### orders\_get

```python
async def orders_get(group: str = "",
                     ticket: int = 0,
                     symbol: str = "") -> tuple[TradeOrder] | None
```

Get active orders with the ability to filter by symbol or ticket. There are three call options.
Call without parameters. Return active orders on all symbols

**Arguments**:

- `symbol` _str_ - Symbol name. Optional named parameter. If a symbol is specified, the ticket parameter is ignored.
  
- `group` _str_ - The filter for arranging a group of necessary symbols. Optional named parameter. If the group is specified, the function
  returns only active orders meeting a specified criteria for a symbol name.
  
- `ticket` _int_ - Order ticket (ORDER_TICKET). Optional named parameter.
  

**Returns**:

- `list[TradeOrder]` - A list of active trade orders as TradeOrder objects

<a id="aiomql.core.models"></a>

# aiomql.core.models

<a id="aiomql.core.models.AccountInfo"></a>

## AccountInfo Objects

```python
class AccountInfo(Base)
```

Account Information Class.

**Attributes**:

- `login` - int
- `password` - str
- `server` - str
- `trade_mode` - AccountTradeMode
- `balance` - float
- `leverage` - float
- `profit` - float
- `point` - float
- `amount` - float = 0
- `equity` - float
- `credit` - float
- `margin` - float
- `margin_level` - float
- `margin_free` - float
- `margin_mode` - AccountMarginMode
- `margin_so_mode` - AccountStopoutMode
- `margin_so_call` - float
- `margin_so_so` - float
- `margin_initial` - float
- `margin_maintenance` - float
- `fifo_close` - bool
- `limit_orders` - float
- `currency` - str = "USD"
- `trade_allowed` - bool = True
- `trade_expert` - bool = True
- `currency_digits` - int
- `assets` - float
- `liabilities` - float
- `commission_blocked` - float
- `name` - str
- `company` - str

<a id="aiomql.core.models.TerminalInfo"></a>

## TerminalInfo Objects

```python
class TerminalInfo(Base)
```

Terminal information class. Holds information about the terminal.

**Attributes**:

- `community_account` - bool
- `community_connection` - bool
- `connected` - bool
- `dlls_allowed` - bool
- `trade_allowed` - bool
- `tradeapi_disabled` - bool
- `email_enabled` - bool
- `ftp_enabled` - bool
- `notifications_enabled` - bool
- `mqid` - bool
- `build` - int
- `maxbars` - int
- `codepage` - int
- `ping_last` - int
- `community_balance` - float
- `retransmission` - float
- `company` - str
- `name` - str
- `language` - str
- `path` - str
- `data_path` - str
- `commondata_path` - str

<a id="aiomql.core.models.SymbolInfo"></a>

## SymbolInfo Objects

```python
class SymbolInfo(Base)
```

Symbol Information Class. Symbols are financial instruments available for trading in the MetaTrader 5 terminal.

**Attributes**:

- `name` - str
- `custom` - bool
- `chart_mode` - SymbolChartMode
- `select` - bool
- `visible` - bool
- `session_deals` - int
- `session_buy_orders` - int
- `session_sell_orders` - int
- `volume` - float
- `volumehigh` - float
- `volumelow` - float
- `time` - int
- `digits` - int
- `spread` - float
- `spread_float` - bool
- `ticks_bookdepth` - int
- `trade_calc_mode` - SymbolCalcMode
- `trade_mode` - SymbolTradeMode
- `start_time` - int
- `expiration_time` - int
- `trade_stops_level` - int
- `trade_freeze_level` - int
- `trade_exemode` - SymbolTradeExecution
- `swap_mode` - SymbolSwapMode
- `swap_rollover3days` - DayOfWeek
- `margin_hedged_use_leg` - bool
- `expiration_mode` - int
- `filling_mode` - int
- `order_mode` - int
- `order_gtc_mode` - SymbolOrderGTCMode
- `option_mode` - SymbolOptionMode
- `option_right` - SymbolOptionRight
- `bid` - float
- `bidhigh` - float
- `bidlow` - float
- `ask` - float
- `askhigh` - float
- `asklow` - float
- `last` - float
- `lasthigh` - float
- `lastlow` - float
- `volume_real` - float
- `volumehigh_real` - float
- `volumelow_real` - float
- `option_strike` - float
- `point` - float
- `trade_tick_value` - float
- `trade_tick_value_profit` - float
- `trade_tick_value_loss` - float
- `trade_tick_size` - float
- `trade_contract_size` - float
- `trade_accrued_interest` - float
- `trade_face_value` - float
- `trade_liquidity_rate` - float
- `volume_min` - float
- `volume_max` - float
- `volume_step` - float
- `volume_limit` - float
- `swap_long` - float
- `swap_short` - float
- `margin_initial` - float
- `margin_maintenance` - float
- `session_volume` - float
- `session_turnover` - float
- `session_interest` - float
- `session_buy_orders_volume` - float
- `session_sell_orders_volume` - float
- `session_open` - float
- `session_close` - float
- `session_aw` - float
- `session_price_settlement` - float
- `session_price_limit_min` - float
- `session_price_limit_max` - float
- `margin_hedged` - float
- `price_change` - float
- `price_volatility` - float
- `price_theoretical` - float
- `price_greeks_delta` - float
- `price_greeks_theta` - float
- `price_greeks_gamma` - float
- `price_greeks_vega` - float
- `price_greeks_rho` - float
- `price_greeks_omega` - float
- `price_sensitivity` - float
- `basis` - str
- `category` - str
- `currency_base` - str
- `currency_profit` - str
- `currency_margin` - Any
- `bank` - str
- `description` - str
- `exchange` - str
- `formula` - Any
- `isin` - Any
- `name` - str
- `page` - str
- `path` - str

<a id="aiomql.core.models.BookInfo"></a>

## BookInfo Objects

```python
class BookInfo(Base)
```

Book Information Class.

**Attributes**:

- `type` - BookType
- `price` - float
- `volume` - float
- `volume_dbl` - float

<a id="aiomql.core.models.TradeOrder"></a>

## TradeOrder Objects

```python
class TradeOrder(Base)
```

Trade Order Class.

**Attributes**:

- `ticket` - int
- `time_setup` - int
- `time_setup_msc` - int
- `time_expiration` - int
- `time_done` - int
- `time_done_msc` - int
- `type` - OrderType
- `type_time` - OrderTime
- `type_filling` - OrderFilling
- `state` - int
- `magic` - int
- `position_id` - int
- `position_by_id` - int
- `reason` - OrderReason
- `volume_current` - float
- `volume_initial` - float
- `price_open` - float
- `sl` - float
- `tp` - float
- `price_current` - float
- `price_stoplimit` - float
- `symbol` - str
- `comment` - str
- `external_id` - str

<a id="aiomql.core.models.TradeRequest"></a>

## TradeRequest Objects

```python
class TradeRequest(Base)
```

Trade Request Class.

**Attributes**:

- `action` - TradeAction
- `type` - OrderType
- `order` - int
- `symbol` - str
- `volume` - float
- `sl` - float
- `tp` - float
- `price` - float
- `deviation` - float
- `stop_limit` - float
- `type_time` - OrderTime
- `type_filling` - OrderFilling
- `expiration` - int
- `position` - int
- `position_by` - int
- `comment` - str
- `magic` - int
- `deviation` - int
- `comment` - str

<a id="aiomql.core.models.OrderCheckResult"></a>

## OrderCheckResult Objects

```python
class OrderCheckResult(Base)
```

Order Check Result

**Attributes**:

- `retcode` - int
- `balance` - float
- `equity` - float
- `profit` - float
- `margin` - float
- `margin_free` - float
- `margin_level` - float
- `comment` - str
- `request` - TradeRequest

<a id="aiomql.core.models.OrderSendResult"></a>

## OrderSendResult Objects

```python
class OrderSendResult(Base)
```

Order Send Result

**Attributes**:

- `retcode` - int
- `deal` - int
- `order` - int
- `volume` - float
- `price` - float
- `bid` - float
- `ask` - float
- `comment` - str
- `request` - TradeRequest
- `request_id` - int
- `retcode_external` - int
- `profit` - float

<a id="aiomql.core.models.TradePosition"></a>

## TradePosition Objects

```python
class TradePosition(Base)
```

Trade Position

**Attributes**:

- `ticket` - int
- `time` - int
- `time_msc` - int
- `time_update` - int
- `time_update_msc` - int
- `type` - OrderType
- `magic` - float
- `identifier` - int
- `reason` - PositionReason
- `volume` - float
- `price_open` - float
- `sl` - float
- `tp` - float
- `price_current` - float
- `swap` - float
- `profit` - float
- `symbol` - str
- `comment` - str
- `external_id` - str

<a id="aiomql.core.models.TradeDeal"></a>

## TradeDeal Objects

```python
class TradeDeal(Base)
```

Trade Deal

**Attributes**:

- `ticket` - int
- `order` - int
- `time` - int
- `time_msc` - int
- `type` - DealType
- `entry` - DealEntry
- `magic` - int
- `position_id` - int
- `reason` - DealReason
- `volume` - float
- `price` - float
- `commission` - float
- `swap` - float
- `profit` - float
- `fee` - float
- `sl` - float
- `tp` - float
- `symbol` - str
- `comment` - str
- `external_id` - str

<a id="aiomql.core"></a>

# aiomql.core

<a id="aiomql.executor"></a>

# aiomql.executor

<a id="aiomql.executor.Executor"></a>

## Executor Objects

```python
class Executor()
```

Executor class for running multiple strategies on multiple symbols concurrently.

**Attributes**:

- `executor` _ThreadPoolExecutor_ - The executor object.
- `workers` _list_ - List of strategies.

<a id="aiomql.executor.Executor.add_workers"></a>

#### add\_workers

```python
def add_workers(strategies: Sequence[type(Strategy)])
```

Add multiple strategies at once

**Arguments**:

- `strategies` _Sequence[Strategy]_ - A sequence of strategies.

<a id="aiomql.executor.Executor.remove_workers"></a>

#### remove\_workers

```python
def remove_workers(*symbols: Sequence[Symbol])
```

Removes any worker running on a symbol not successfully initialized.

**Arguments**:

- `*symbols` - Successfully initialized symbols.

<a id="aiomql.executor.Executor.add_worker"></a>

#### add\_worker

```python
def add_worker(strategy: type(Strategy))
```

Add a strategy instance to the list of workers

**Arguments**:

- `strategy` _Strategy_ - A strategy object

<a id="aiomql.executor.Executor.run"></a>

#### run

```python
@staticmethod
def run(strategy: type(Strategy))
```

Wraps the coroutine trade method of each strategy with 'asyncio.run'.

**Arguments**:

- `strategy` _Strategy_ - A strategy object

<a id="aiomql.executor.Executor.execute"></a>

#### execute

```python
async def execute(workers: int = 0)
```

Run the strategies with a threadpool executor.

**Arguments**:

- `workers` - Number of workers to use in executor pool. Defaults to zero which uses all workers.
  

**Notes**:

  No matter the number specified, the executor will always use a minimum of 5 workers.

<a id="aiomql.history"></a>

# aiomql.history

<a id="aiomql.history.History"></a>

## History Objects

```python
class History()
```

The history class handles completed trade deals and trade orders in the trading history of an account.

**Attributes**:

- `deals` _list[TradeDeal]_ - Iterable of trade deals
- `orders` _list[TradeOrder]_ - Iterable of trade orders
- `total_deals` - Total number of deals
- `total_orders` _int_ - Total number orders
- `group` _str_ - Filter for selecting history by symbols.
- `ticket` _int_ - Filter for selecting history by ticket number
- `position` _int_ - Filter for selecting history deals by position
- `initialized` _bool_ - check if initial request has been sent to the terminal to get history.
- `mt5` _MetaTrader_ - MetaTrader instance
- `config` _Config_ - Config instance

<a id="aiomql.history.History.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*,
             date_from: datetime | float = 0,
             date_to: datetime | float = 0,
             group: str = "",
             ticket: int = 0,
             position: int = 0)
```

**Arguments**:

- `date_from` _datetime, float_ - Date the orders are requested from. Set by the 'datetime' object or as a
  number of seconds elapsed since 1970.01.01. Defaults to twenty-four hours from the current time in 'utc'
  
- `date_to` _datetime, float_ - Date up to which the orders are requested. Set by the 'datetime' object or as a
  number of seconds elapsed since 1970.01.01. Defaults to the current time in "utc"
  
- `group` _str_ - Filter for selecting history by symbols.
- `ticket` _int_ - Filter for selecting history by ticket number
- `position` _int_ - Filter for selecting history deals by position

<a id="aiomql.history.History.init"></a>

#### init

```python
async def init(deals=True, orders=True) -> bool
```

Get history deals and orders

**Arguments**:

- `deals` _bool_ - If true get history deals during initial request to terminal
- `orders` _bool_ - If true get history orders during initial request to terminal
  

**Returns**:

- `bool` - True if all requests were successful else False

<a id="aiomql.history.History.get_deals"></a>

#### get\_deals

```python
async def get_deals() -> list[TradeDeal]
```

Get deals from trading history using the parameters set in the constructor.

**Returns**:

- `list[TradeDeal]` - A list of trade deals

<a id="aiomql.history.History.deals_total"></a>

#### deals\_total

```python
async def deals_total() -> int
```

Get total number of deals within the specified period in the constructor.

**Returns**:

- `int` - Total number of Deals

<a id="aiomql.history.History.get_orders"></a>

#### get\_orders

```python
async def get_orders() -> list[TradeOrder]
```

Get orders from trading history using the parameters set in the constructor.

**Returns**:

- `list[TradeOrder]` - A list of trade orders

<a id="aiomql.history.History.orders_total"></a>

#### orders\_total

```python
async def orders_total() -> int
```

Get total number of orders within the specified period in the constructor.

**Returns**:

- `int` - Total number of orders

<a id="aiomql.lib.strategies.finger_trap"></a>

# aiomql.lib.strategies.finger\_trap

<a id="aiomql.lib.strategies.finger_trap.Entry"></a>

## Entry Objects

```python
@dataclass
class Entry()
```

Entry class for FingerTrap strategy.Will be used to store entry conditions and other entry related data.

**Attributes**:

- `bearish` _bool_ - True if the market is bearish
- `bullish` _bool_ - True if the market is bullish
- `ranging` _bool_ - True if the market is ranging
- `snooze` _float_ - Time to wait before checking for entry conditions
- `trend` _str_ - The current trend of the market
- `last_candle` _Candle_ - The last candle of the market
- `new` _bool_ - True if the last candle is new
- `order_type` _OrderType_ - The type of order to place
- `pips` _int_ - The number of pips to place the order from the current price

<a id="aiomql.lib.strategies"></a>

# aiomql.lib.strategies

<a id="aiomql.lib.symbols.forex_symbol"></a>

# aiomql.lib.symbols.forex\_symbol

<a id="aiomql.lib.symbols.forex_symbol.ForexSymbol"></a>

## ForexSymbol Objects

```python
class ForexSymbol(Symbol)
```

Subclass of Symbol for Forex Symbols. Handles the conversion of currency and the computation of stop loss,
take profit and volume.

<a id="aiomql.lib.symbols.forex_symbol.ForexSymbol.pip"></a>

#### pip

```python
@property
def pip()
```

Returns the pip value of the symbol. This is ten times the point value for forex symbols.

**Returns**:

- `float` - The pip value of the symbol.

<a id="aiomql.lib.symbols.forex_symbol.ForexSymbol.compute_volume"></a>

#### compute\_volume

```python
async def compute_volume(*,
                         amount: float,
                         pips: float,
                         use_minimum: bool = True) -> float
```

Compute volume given an amount to risk and target pips. Round the computed volume to the nearest step.

**Arguments**:

- `amount` _float_ - Amount to risk. Given in terms of the account currency.
- `pips` _float_ - Target pips.
  

**Arguments**:

- `use_minimum` _bool_ - If True, the minimum volume is returned if the computed volume is less than the minimum volume.
  

**Returns**:

- `float` - volume
  

**Raises**:

- `VolumeError` - If the computed volume is less than the minimum volume or greater than the maximum volume.

<a id="aiomql.lib.symbols"></a>

# aiomql.lib.symbols

<a id="aiomql.lib.traders.simple_deal_trader"></a>

# aiomql.lib.traders.simple\_deal\_trader

<a id="aiomql.lib.traders.simple_deal_trader.DealTrader"></a>

## DealTrader Objects

```python
class DealTrader(Trader)
```

A base class for placing trades based on the number of pips to target

<a id="aiomql.lib.traders.simple_deal_trader.DealTrader.create_order"></a>

#### create\_order

```python
async def create_order(*, order_type: OrderType, pips: float = 0)
```

Using the number of target pips it determines the lot size, stop loss and take profit for the order,
and updates the order object with the values.

**Arguments**:

- `order_type` _OrderType_ - Type of order
- `pips` _float_ - Target pips

<a id="aiomql.lib.traders"></a>

# aiomql.lib.traders

<a id="aiomql.lib"></a>

# aiomql.lib

<a id="aiomql.order"></a>

# aiomql.order

Order Class

<a id="aiomql.order.Order"></a>

## Order Objects

```python
class Order(TradeRequest)
```

Trade order related functions and properties. Subclass of TradeRequest.

<a id="aiomql.order.Order.__init__"></a>

#### \_\_init\_\_

```python
def __init__(**kwargs)
```

Initialize the order object with keyword arguments, symbol must be provided.
Provide default values for action, type_time and type_filling if not provided.

**Arguments**:

- `**kwargs` - Keyword arguments must match the attributes of TradeRequest as well as the attributes of
  Order class as specified in the annotations in the class definition.
  
  Default Values:
- `action` _TradeAction.DEAL_ - Trade action
- `type_time` _OrderTime.DAY_ - Order time
- `type_filling` _OrderFilling.FOK_ - Order filling
  

**Raises**:

- `SymbolError` - If symbol is not provided

<a id="aiomql.order.Order.orders_total"></a>

#### orders\_total

```python
async def orders_total()
```

Get the number of active orders.

**Returns**:

- `(int)` - total number of active orders

<a id="aiomql.order.Order.orders"></a>

#### orders

```python
async def orders() -> tuple[TradeOrder]
```

Get the list of active orders for the current symbol.

**Returns**:

- `tuple[TradeOrder]` - A Tuple of active trade orders as TradeOrder objects

<a id="aiomql.order.Order.check"></a>

#### check

```python
async def check() -> OrderCheckResult
```

Check funds sufficiency for performing a required trading operation and the possibility to execute it at

**Returns**:

- `OrderCheckResult` - An OrderCheckResult object
  

**Raises**:

- `OrderError` - If not successful

<a id="aiomql.order.Order.send"></a>

#### send

```python
async def send() -> OrderSendResult
```

Send a request to perform a trading operation from the terminal to the trade server.

**Returns**:

- `OrderSendResult` - An OrderSendResult object
  

**Raises**:

- `OrderError` - If not successful

<a id="aiomql.order.Order.calc_margin"></a>

#### calc\_margin

```python
async def calc_margin() -> float
```

Return the required margin in the account currency to perform a specified trading operation.

**Returns**:

- `float` - Returns float value if successful
  

**Raises**:

- `OrderError` - If not successful

<a id="aiomql.order.Order.calc_profit"></a>

#### calc\_profit

```python
async def calc_profit() -> float
```

Return profit in the account currency for a specified trading operation.

**Returns**:

- `float` - Returns float value if successful
  

**Raises**:

- `OrderError` - If not successful

<a id="aiomql.positions"></a>

# aiomql.positions

Handle Open positions.

<a id="aiomql.positions.Positions"></a>

## Positions Objects

```python
class Positions()
```

Get Open Positions.

**Attributes**:

- `symbol` _str_ - Financial instrument name.
- `group` _str_ - The filter for arranging a group of necessary symbols. Optional named parameter.
  If the group is specified, the function returns only positions meeting a specified criteria for a symbol name.
- `ticket` _int_ - Position ticket.
- `mt5` _MetaTrader_ - MetaTrader instance.

<a id="aiomql.positions.Positions.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*, symbol: str = "", group: str = "", ticket: int = 0)
```

Get Open Positions.

**Arguments**:

- `symbol` _str_ - Financial instrument name.
- `group` _str_ - The filter for arranging a group of necessary symbols. Optional named parameter. If the group
  is specified, the function returns only positions meeting a specified criteria for a symbol name.
- `ticket` _int_ - Position ticket

<a id="aiomql.positions.Positions.positions_total"></a>

#### positions\_total

```python
async def positions_total() -> int
```

Get the number of open positions.

**Returns**:

- `int` - Return total number of open positions

<a id="aiomql.positions.Positions.positions_get"></a>

#### positions\_get

```python
async def positions_get()
```

Get open positions with the ability to filter by symbol or ticket.

**Returns**:

- `list[TradePosition]` - A list of open trade positions

<a id="aiomql.positions.Positions.close_all"></a>

#### close\_all

```python
async def close_all() -> int
```

Close all open positions for the trading account.

**Returns**:

- `int` - Return number of positions closed.

<a id="aiomql.ram"></a>

# aiomql.ram

Risk Assessment and Management

<a id="aiomql.ram.RAM"></a>

## RAM Objects

```python
class RAM()
```

<a id="aiomql.ram.RAM.__init__"></a>

#### \_\_init\_\_

```python
def __init__(**kwargs)
```

Risk Assessment and Management. All provided keyword arguments are set as attributes.

**Arguments**:

- `kwargs` _Dict_ - Keyword arguments.
  
  Defaults:
- `risk_to_reward` _float_ - Risk to reward ratio 1
- `risk` _float_ - Percentage of account balance to risk per trade 0.01 # 1%
- `amount` _float_ - Amount to risk per trade in terms of account currency 0
- `pips` _float_ - Target pips 0
- `volume` _float_ - Volume to trade 0

<a id="aiomql.ram.RAM.get_amount"></a>

#### get\_amount

```python
async def get_amount(risk: float = 0) -> float
```

Calculate the amount to risk per trade as a percentage of free margin.

**Arguments**:

- `risk` _float_ - Percentage of account balance to risk per trade. Defaults to zero.
  

**Returns**:

- `float` - Amount to risk per trade

<a id="aiomql.ram.RAM.get_volume"></a>

#### get\_volume

```python
async def get_volume(*,
                     symbol: Symbol,
                     pips: float = 0,
                     amount: float = 0) -> float
```

Calculate the volume to trade. if pips is not provided, the pips attribute is used.
If the amount attribute or amount argument is zero, the amount is calculated using the get_amount method based on the risk.

**Arguments**:

- `symbol` _Symbol_ - Financial instrument
  

**Arguments**:

- `pips` _float_ - Target pips. Defaults to zero.
- `amount` _float_ - Amount to risk per trade. Defaults to zero.
  

**Returns**:

- `float` - Volume to trade

<a id="aiomql.records"></a>

# aiomql.records

This module contains the Records class, which is used to read and update trade records from csv files.

<a id="aiomql.records.Records"></a>

## Records Objects

```python
class Records()
```

This utility class read trade records from csv files, and update them based on their closing positions.

**Attributes**:

- `config` - Config object
- `records_dir(Path)` - Path to directory containing record of placed trades, If not given takes the default
  from the config

<a id="aiomql.records.Records.__init__"></a>

#### \_\_init\_\_

```python
def __init__(records_dir: Path = '')
```

Initialize the Records class.

**Arguments**:

- `records_dir` _Path_ - Path to directory containing record of placed trades.

<a id="aiomql.records.Records.get_records"></a>

#### get\_records

```python
async def get_records()
```

Get trade records from records_dir folder

**Yields**:

- `files` - Trade record files

<a id="aiomql.records.Records.read_update"></a>

#### read\_update

```python
async def read_update(file: Path)
```

Read and update trade records

**Arguments**:

- `file` - Trade record file

<a id="aiomql.records.Records.update_rows"></a>

#### update\_rows

```python
async def update_rows(rows: list[dict]) -> list[dict]
```

Update the rows of entered trades in the csv file with the actual profit.

**Arguments**:

- `rows` - A list of dictionaries from the dictionary writer object of the csv file.
  

**Returns**:

- `list[dict]` - A list of dictionaries with the actual profit and win status.

<a id="aiomql.records.Records.update_records"></a>

#### update\_records

```python
async def update_records()
```

Update trade records in the records_dir folder.

<a id="aiomql.records.Records.update_record"></a>

#### update\_record

```python
async def update_record(file: Path | str)
```

Update a single trade record file.

<a id="aiomql.result"></a>

# aiomql.result

<a id="aiomql.result.Result"></a>

## Result Objects

```python
class Result()
```

A base class for handling trade results and strategy parameters for record keeping and reference purpose.
The data property must be implemented in the subclass

**Attributes**:

- `config` _Config_ - The configuration object
- `name` - Any desired name for the result file object

<a id="aiomql.result.Result.__init__"></a>

#### \_\_init\_\_

```python
def __init__(result: OrderSendResult, parameters: dict = None, name: str = '')
```

Prepare result data

**Arguments**:

  result:
  parameters:
  name:

<a id="aiomql.result.Result.to_csv"></a>

#### to\_csv

```python
async def to_csv()
```

Record trade results and associated parameters as a csv file

<a id="aiomql.result.Result.save_csv"></a>

#### save\_csv

```python
async def save_csv()
```

Save trade results and associated parameters as a csv file in a separate thread

<a id="aiomql.strategy"></a>

# aiomql.strategy

The base class for creating strategies.

<a id="aiomql.strategy.Strategy"></a>

## Strategy Objects

```python
class Strategy(ABC)
```

The base class for creating strategies.

**Attributes**:

- `symbol` _Symbol_ - The Financial Instrument as a Symbol Object
- `parameters` _Dict_ - A dictionary of parameters for the strategy.
  
  Class Attributes:
- `name` _str_ - A name for the strategy.
- `account` _Account_ - Account instance.
- `mt5` _MetaTrader_ - MetaTrader instance.
- `config` _Config_ - Config instance.
  

**Notes**:

  Define the name of a strategy as a class attribute. If not provided, the class name will be used as the name.

<a id="aiomql.strategy.Strategy.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*, symbol: Symbol, params: dict = None)
```

Initiate the parameters dict and add name and symbol fields.
Use class name as strategy name if name is not provided

**Arguments**:

- `symbol` _Symbol_ - The Financial instrument
- `params` _Dict_ - Trading strategy parameters

<a id="aiomql.strategy.Strategy.sleep"></a>

#### sleep

```python
@staticmethod
async def sleep(secs: float)
```

Sleep for the needed amount of seconds in between requests to the terminal.
computes the accurate amount of time needed to sleep ensuring that the next request is made at the start of
a new bar and making cooperative multitasking possible.

**Arguments**:

- `secs` _float_ - The time in seconds. Usually the timeframe you are trading on.

<a id="aiomql.strategy.Strategy.trade"></a>

#### trade

```python
@abstractmethod
async def trade()
```

Place trades using this method. This is the main method of the strategy.
It will be called by the strategy runner.

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

<a id="aiomql.terminal"></a>

# aiomql.terminal

Terminal related functions and properties

<a id="aiomql.terminal.Terminal"></a>

## Terminal Objects

```python
class Terminal(TerminalInfo)
```

Terminal Class. Get information about the MetaTrader 5 terminal. The class is a subclass of the TerminalInfo
class. It inherits all the attributes and methods of the TerminalInfo class and adds some useful methods.

**Notes**:

  Other attributes are defined in the TerminalInfo Class

<a id="aiomql.terminal.Terminal.initialize"></a>

#### initialize

```python
async def initialize() -> bool
```

Establish a connection with the MetaTrader 5 terminal. There are three call options. Call without parameters.
The terminal for connection is found automatically. Call specifying the path to the MetaTrader 5 terminal we
want to connect to. word path as a keyword argument Call specifying the trading account path and parameters
i.e login, password, server, as keyword arguments, path can be omitted.

**Returns**:

- `bool` - True if successful else False

<a id="aiomql.terminal.Terminal.version"></a>

#### version

```python
async def version()
```

Get the MetaTrader 5 terminal version. This method returns the terminal version, build and release date as
a tuple of three values

**Returns**:

- `Version` - version of tuple as Version object
  

**Raises**:

- `ValueError` - If the terminal version cannot be obtained

<a id="aiomql.terminal.Terminal.info"></a>

#### info

```python
async def info()
```

Get the connected MetaTrader 5 client terminal status and settings. gets terminal info in the form of a
named tuple structure (namedtuple). Return None in case of an error. The info on the error can be
obtained using last_error().

**Returns**:

- `Terminal` - Terminal status and settings as a terminal object.

<a id="aiomql.terminal.Terminal.symbols_total"></a>

#### symbols\_total

```python
async def symbols_total() -> int
```

Get the number of all financial instruments in the MetaTrader 5 terminal.

**Returns**:

- `int` - Total number of available symbols

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

<a id="aiomql.trader"></a>

# aiomql.trader

Trader class module. Handles the creation of an order and the placing of trades

<a id="aiomql.trader.Trader"></a>

## Trader Objects

```python
class Trader()
```

Base class for creating a Trader object. Handles the creation of an order and the placing of trades

**Attributes**:

- `symbol` _Symbol_ - Financial instrument class Symbol class or any subclass of it.
- `ram` _RAM_ - RAM instance
- `order` _Order_ - Trade order
  
  Class Attributes:
- `name` _str_ - A name for the strategy.
- `account` _Account_ - Account instance.
- `mt5` _MetaTrader_ - MetaTrader instance.
- `config` _Config_ - Config instance.

<a id="aiomql.trader.Trader.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*, symbol: Symbol, ram: RAM = None)
```

Initializes the order object and RAM instance

**Arguments**:

- `symbol` _Symbol_ - Financial instrument
- `ram` _RAM_ - Risk Assessment and Management instance

<a id="aiomql.trader.Trader.create_order"></a>

#### create\_order

```python
async def create_order(*, order_type: OrderType, **kwargs)
```

Complete the order object with the required values. Creates a simple order.
Uses the ram instance to set the volume.

**Arguments**:

- `order_type` _OrderType_ - Type of order
- `kwargs` - keyword arguments as required for the specific trader

<a id="aiomql.trader.Trader.set_order_limits"></a>

#### set\_order\_limits

```python
async def set_order_limits(pips: float)
```

Sets the stop loss and take profit for the order.
This method uses pips as defined for forex instruments.

**Arguments**:

- `pips` - Target pips

<a id="aiomql.trader.Trader.place_trade"></a>

#### place\_trade

```python
async def place_trade(order_type: OrderType, params: dict = None, **kwargs)
```

Places a trade based on the order_type.

**Arguments**:

- `order_type` _OrderType_ - Type of order
- `params` - parameters to be saved with the trade
- `kwargs` - keyword arguments as required for the specific trader

<a id="aiomql.utils"></a>

# aiomql.utils

Utility functions for aiomql.

<a id="aiomql.utils.dict_to_string"></a>

#### dict\_to\_string

```python
def dict_to_string(data: dict, multi=False) -> str
```

Convert a dict to a string. Use for logging.

**Arguments**:

- `data` _dict_ - The dict to convert.
- `multi` _bool, optional_ - If True, each key-value pair will be on a new line. Defaults to False.
  

**Returns**:

- `str` - The string representation of the dict.

