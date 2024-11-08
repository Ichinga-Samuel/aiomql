# Account

## Table of Contents
- [Account](#account.Account)
- [refresh](#account.refresh)


<a id="account.Account"></a>
### Account
```python
class Account(_Base, AccountInfo)
```
A singleton class for managing a trading account. A subclass of _Base and AccountInfo. It supports asynchronous context
management protocol.

#### Attributes
| Name        | Type              | Description                                          | Default |
|-------------|-------------------|------------------------------------------------------|---------|
| `connected` | `bool`            | Status of connection to MetaTrader 5 Terminal        | False   |

<a id="account.refresh"></a>
### refresh
```python
async def refresh()
```
Refreshes the account instance with the latest data from the MetaTrader 5 terminal
