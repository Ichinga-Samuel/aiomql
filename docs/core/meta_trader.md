# Table of Contents

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

