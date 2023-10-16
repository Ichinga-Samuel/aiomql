## <a id="terminal"></a> Terminal
Terminal related functions and properties

```python
class Terminal(TerminalInfo)
```
Terminal Class. Get information about the MetaTrader 5 terminal. The class is a subclass of the TerminalInfo
class. It inherits all the attributes and methods of the TerminalInfo class and adds some useful methods.
### Attributes:
|Name| Type                | Description                                    | Default |
|---|---------------------|------------------------------------------------|----|
|**initialized**|**bool** | check if initial request has been sent to the terminal to get terminal info. | False |
|**mt5**|**MetaTrader** | MetaTrader instance                            | None |
|**config**|**Config** | Config instance                                | None |

### Notes:
Other attributes are defined in the TerminalInfo Class

### initialize
```python
async def initialize() -> bool
```
Establish a connection with the MetaTrader 5 terminal. There are three call options. Call without parameters.
The terminal for connection is found automatically. Call specifying the path to the MetaTrader 5 terminal we
want to connect to. word path as a keyword argument Call specifying the trading account path and parameters
i.e login, password, server, as keyword arguments, path can be omitted.
#### Returns:
|Type|Description|
|---|---|
|**bool**|True if successful else False|

### version
```python
async def version()
```
Get the MetaTrader 5 terminal version. This method returns the terminal version, build and release date as
a tuple of three values

#### Returns:
|Type|Description|
|---|---|
|**Version**|version of tuple as Version object|

#### Raises:
|Exception|Description|
|---|---|
|**ValueError**|If the terminal version cannot be obtained|

### info
```python
async def info()
```
Get the connected MetaTrader 5 client terminal status and settings. gets terminal info in the form of a
named tuple structure (namedtuple). Return None in case of an error. The info on the error can be
obtained using last_error().

#### Returns:
|Type|Description|
|---|---|
|**TerminalInfo**|Terminal status and settings as a terminal object.|

### symbols\_total
```python
async def symbols_total() -> int
```
Get the number of all financial instruments in the MetaTrader 5 terminal.

#### Returns:
|Type|Description|
|---|---|
|**int**|Total number of available symbols|
