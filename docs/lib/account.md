# Account

## Table of Contents
- [Account](#account.Account)
- [\_\_init\_\_](#account.__init__)
- [\_\_aenter\_\_](#account.__aenter__)
- [\_\_aexit\_\_](#account.__aexit__)
- [sign_in](#account.sign_in)
- [refresh](#account.refresh)
- [has_symbol](#account.has_symbol)
- [symbols_get](#account.symbols_get)

<a id="Account"></a>
### Account
```python
class Account(AccountInfo)
```
Singleton class for managing a trading account. A subclass of AccountInfo. 
All AccountInfo attributes are available in this class.
#### Attributes
| Name        | Type              | Description                                          | Default |
|-------------|-------------------|------------------------------------------------------|---------|
| `connected` | `bool`            | Status of connection to MetaTrader 5 Terminal        | False   |
| `symbols`   | `set[SymbolInfo]` | A set of available symbols for the financial market. | set()   |

<a id="account.__init__"></a>
#### \_\_init\_\_
```python
def __init__(self, *args, **kwargs)
```
Initializes the Account class. Inherits all attributes from the AccountInfo class.

<a id="account.__aenter__"></a>
### __aenter__
```python
async def __aenter__() -> 'Account'
```
Async context manager for the Account class. Connects to a trading account and returns the account instance.
#### Returns:
| Type      | Description                      |  
|-----------|----------------------------------|
| `Account` | An instance of the Account class |
#### Raises:
| Exception    | Description    |
|--------------|----------------|
| `LoginError` | If login fails |

<a id="account.__aexit__"></a>
### __aexit__
```python
async def __aexit__(exc_type, exc_value, traceback)
```
Async context manager for the Account class. Disconnects from the trading account.

<a id="account.sign_in"></a>
### sign_in
```python
async def sign_in() -> bool
```
Connect to a trading account.
#### Returns:
| Type   | Description                             |
|--------|-----------------------------------------|
| `bool` | True if login was successful else False |

<a id="account.refresh"></a>
### refresh
```python
async def refresh()
```
Refreshes the account instance with the latest data from the MetaTrader 5 terminal

<a id="account.has_symbol"></a>
### has_symbol
```python
def has_symbol(symbol: str | Type[SymbolInfo])
```
Checks to see if a symbol is available for a trading account
#### Parameters:
| Name     | Type                | Description                          |
|----------|---------------------|--------------------------------------|
| `symbol` | `str`\|`SymbolInfo` | A symbol name or SymbolInfo instance |
#### Returns:
| Type   | Description                            |
|--------|----------------------------------------|
| `bool` | True if symbol is available else False |

<a id="account.symbols_get"></a>
### symbols_get
```python
async def symbols_get() -> set[SymbolInfo]
```
Get all financial instruments from the MetaTrader 5 terminal available for the current account.
#### Returns:
| Type              | Description                   |
|-------------------|-------------------------------|
| `set[SymbolInfo]` | A set of SymbolInfo instances |
