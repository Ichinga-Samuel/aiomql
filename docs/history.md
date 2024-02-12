# History

## Table of contents
- [History](#history)
- [\_\_init\_\_](#__init__)
- [init](#init)
- [get_deals](#get_deals)
- [deals_total](#deals_total)
- [get_orders](#get_orders)
- [orders_total](#orders_total)

<a id='history'></a>
### History
```python
class History
```
The history class handles completed trade deals and trade orders in the trading history of an account.
#### Attributes
| Name           | Type               | Description                                                            | Default |
|----------------|--------------------|------------------------------------------------------------------------|---------|
| `deals`        | `list[TradeDeal]`  | Iterable of trade deals                                                | []      |
| `orders`       | `list[TradeOrder]` | Iterable of trade orders                                               | []      |
| `total_deals`  | `int`              | Total number of deals                                                  | 0       |
| `total_orders` | `int`              | Total number orders                                                    | 0       |
| `group`        | `str`              | Filter for selecting history by symbols.                               | ""      |
| `ticket`       | `int`              | Filter for selecting history by ticket number                          | 0       |
| `position`     | `int`              | Filter for selecting history deals by position                         | 0       |
| `initialized`  | `bool`             | check if initial request has been sent to the terminal to get history. | False   |
| `mt5`          | `MetaTrader`       | MetaTrader instance                                                    | None    |
| `config`       | `Config`           | Config instance                                                        | None    |


<a id='__init__'></a>
### \_\_init\_\_
```python
def __init__(*,
             date_from: datetime | float = 0,
             date_to: datetime | float = 0,
             group: str = "",
             ticket: int = 0,
             position: int = 0)
```
#### Parameters
| Name        | Type              | Description                                                                                                                                                                      | Default |
|-------------|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| `date_from` | `datetime\|float` | Date the deals are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Defaults to twenty-four hours from the current time in 'utc' | 0       |
| `date_to`   | `datetime\|float` | Date up to which the deals are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Defaults to the current time in "utc"                 | 0       |
| `group`     | `str`             | Filter for selecting history by symbols.                                                                                                                                         | ""      |
| `ticket`    | `int`             | Filter for selecting history by ticket number                                                                                                                                    | 0       |
| `position`  | `int`             | Filter for selecting history deals by position                                                                                                                                   | 0       |

<a id='init'></a>
### init
```python
async def init(deals=True, orders=True) -> bool
```
Get history deals and orders
#### Parameters
| Name     | Type   | Description                                                   | Default |
|----------|--------|---------------------------------------------------------------|---------|
| `deals`  | `bool` | If true get history deals during initial request to terminal  | True    |
| `orders` | `bool` | If true get history orders during initial request to terminal | True    |
#### Returns
| Name   | Type   | Description                                     | Default |
|--------|--------|-------------------------------------------------|---------|
| `bool` | `bool` | True if all requests were successful else False | False   |

<a id='get_deals'></a>
### get_deals
```python
async def get_deals() -> list[TradeDeal]
```
Get deals from trading history using the parameters set in the constructor.
#### Returns
| Name    | Type              | Description           | Default |
|---------|-------------------|-----------------------|---------|
| `deals` | `list[TradeDeal]` | A list of trade deals | []      |

<a id='deals_total'></a>
### deals_total
```python
async def deals_total() -> int
```
Get total number of deals within the specified period in the constructor.
#### Returns
| Name          | Type  | Description           | Default |
|---------------|-------|-----------------------|---------|
| `total_deals` | `int` | Total number of deals | 0       |

<a id='get_orders'></a>
### get_orders
```python
async def get_orders() -> list[TradeOrder]
```
Get orders from trading history using the parameters set in the constructor.
#### Returns
| Name     | Type               | Description            | Default |
|----------|--------------------|------------------------|---------|
| `orders` | `list[TradeOrder]` | A list of trade orders | []      |

<a id='orders_total'></a>
### orders_total
```python
async def orders_total() -> int
```
Get total number of orders within the specified period in the constructor.
#### Returns
| Name           | Type  | Description         | Default |
|----------------|-------|---------------------|---------|
| `total_orders` | `int` | Total number orders | 0       |
