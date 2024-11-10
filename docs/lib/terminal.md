# Terminal

## Table of Contents
- [Terminal](#terminal.terminal)
- [initialize](#terminal.initialize)
- [version](#terminal.version)
- [info](#terminal.info)
- [symbols_total](#terminal.symbols_total)

<a id="terminal.terminal"></a>
### Terminal
```python
class Terminal(_Base, TerminalInfo)
```
Terminal Class. Get information about the MetaTrader 5 terminal. The class is a subclass of the TerminalInfo
class. It inherits all the attributes and methods of the TerminalInfo class and adds some useful methods.

#### Attributes:
| Name      | Type         | Description                   | Default |
|-----------|--------------|-------------------------------|---------|
| `version` | `Version`    | MetaTrader5 Terminal Version. | None    |


<a id="terminal.initialize"></a>
### initialize
```python
async def initialize() -> bool
```
Establish a connection with the MetaTrader 5 terminal. There are three call options. Call without parameters.
The terminal for connection is found automatically. Call specifying the path to the MetaTrader 5 terminal we
want to connect to. word path as a keyword argument Call specifying the trading account path and parameters
i.e. login, password, server, as keyword arguments, path can be omitted.

#### Returns:
| Type   | Description                   |
|--------|-------------------------------|
| `bool` | True if successful else False |


<a id="terminal.version"></a>
### version
```python
async def version()
```
Get the MetaTrader 5 terminal version. This method returns the terminal version, build and release date as
a tuple of three values

#### Returns:
| Type      | Description                        |
|-----------|------------------------------------|
| `Version` | version of tuple as Version object |

#### Raises:
| Exception    | Description                                |
|--------------|--------------------------------------------|
| `ValueError` | If the terminal version cannot be obtained |


<a id="terminal.info"></a>
### info
```python
async def info()
```
Get the connected MetaTrader 5 client terminal status and settings. gets terminal info in the form of a
named tuple structure (namedtuple). Return None in case of an error. The info on the error can be
obtained using last_error().

#### Returns:
| Type           | Description                                        |
|----------------|----------------------------------------------------|
| `TerminalInfo` | Terminal status and settings as a terminal object. |


<a id="terminal.symbols_total"></a>
### symbols_total
```python
async def symbols_total() -> int
```
Get the number of all financial instruments in the MetaTrader 5 terminal.

#### Returns:
| Type  | Description                       |
|-------|-----------------------------------|
| `int` | Total number of available symbols |
