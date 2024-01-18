
- [Account](#Account)
  - [__aenter__](#Account.__aenter__)
  - [sign_in](#Account.sign_in)
  - [refresh](#Account.refresh)
  - [has_symbol](#Account.has_symbol)
  - [symbols_get](#Account.symbols_get)
  - [AccountInfo](#AccountInfo)
  - [Account](#Account)
  - [sign_in](#Account.sign_in)
  - [has_symbol](#Account.has_symbol)
  - [symbols_get](#Account.symbols_get)
- 

<a id="Account"></a>
### Account
```python
class Account(AccountInfo)
```
Singleton class for managing a trading account. A subclass of [AccountInfo](#AccountInfo). 
All AccountInfo attributes are available in this class.
### Attributes:
|Name|Type|Description|Default|
|---|---|---|---|
|**connected**|**bool**|Status of connection to MetaTrader 5 Terminal|False|
|symbols|set[SymbolInfo]|A set of available symbols for the financial market.|set()|

<a id="Account.__aenter__"></a>
#### __aenter__
```python
async def __aenter__() -> 'Account'
```
Async context manager for the Account class. Connects to a trading account and returns the account instance.
#### Returns:
|Type|Description|  
|---|---|
|**Account**|An instance of the Account class|
#### Raises:
|Exception|Description|
|---|---|
|**LoginError**|If login fails|

<a id="Account.sign_in"></a>
#### sign_in
```python
async def sign_in() -> bool
```
Connect to a trading account.
#### Returns:
|Type|Description|
|---|---|
|**bool**|True if login was successful else False|

<a id="Account.refresh"></a>
#### refresh
```python
async def refresh()
```
Refreshes the account instance with the latest data from the MetaTrader 5 terminal

<a id="Account.has_symbol"></a>
#### has_symbol
```python
def has_symbol(symbol: str | Type[SymbolInfo])
```
Checks to see if a symbol is available for a trading account
#### Parameters:
|Name|Type|Description|
|---|---|---|
|**symbol**|**str** or **SymbolInfo**|A symbol name or SymbolInfo instance|
#### Returns:
|Type|Description|
|---|---|
|**bool**|True if symbol is available else False|

<a id="Account.symbols_get"></a>
#### symbols_get
```python
async def symbols_get() -> set[SymbolInfo]
```
Get all financial instruments from the MetaTrader 5 terminal available for the current account.
#### Returns:
|Type|Description|
|---|---|
|**set[SymbolInfo]**|A set of SymbolInfo instances|