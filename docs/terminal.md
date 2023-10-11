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

