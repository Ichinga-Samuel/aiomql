## <a id="account"></a> Account

```python
class Account(AccountInfo)
```
Singleton class for managing a trading account. A subclass of [AccountInfo](#accountinfo). All AccountInfo attributes are available in this class.

### Attributes:
|Name|Type|Description|Default|
|---|---|---|---|
|**connected**|**bool**|Status of connection to MetaTrader 5 Terminal|False|
|symbols|set[SymbolInfo]|A set of available symbols for the financial market.|set()|

### Notes
Other Account properties are defined in the AccountInfo class.

### refresh
```python
async def refresh()
```
Refreshes the account instance with the latest data from the MetaTrader 5 terminal

### account_info
```python
@property
def account_info() -> dict
```
Get account login, server and password details. If the login attribute of the account instance returns
a falsy value, the config instance is used to get the account details.
#### Returns:
|Type|Description|
|---|---|
|**dict**|A dict of login, server and password details|
#### Note:
This method will only look for config details in the config instance if the login attribute of the account Instance returns a falsy value

### __aenter__
```python
async def __aenter__() -> 'Account'
```
Connect to a trading account and return the account instance.
Async context manager for the Account class.
#### Returns:
|Type|Description|  
|---|---|
|**Account**|An instance of the Account class|
#### Raises:
|Exception|Description|
|---|---|
|**LoginError**|If login fails|

### sign_in
```python
async def sign_in() -> bool
```
Connect to a trading account.
#### Returns:
|Type|Description|
|---|---|
|**bool**|True if login was successful else False|

### has_symbol
```python
def has_symbol(symbol: str | Type[SymbolInfo])
```
Checks to see if a symbol is available for a trading account\
#### Arguments:
|Name|Type|Description|
|---|---|---|
|**symbol**|**str** or **SymbolInfo**|A symbol name or SymbolInfo instance|
#### Returns:
|Type|Description|
|---|---|
|**bool**|True if symbol is available else False|

### symbols_get
```python
async def symbols_get() -> set[SymbolInfo]
```
Get all financial instruments from the MetaTrader 5 terminal available for the current account.
#### Returns:
|Type|Description|
|---|---|
|**set[SymbolInfo]**|A set of SymbolInfo instances|

