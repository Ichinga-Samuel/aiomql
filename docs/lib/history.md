# History

## Table of contents
- [History](#history.history)
- [\_\_init\_\_](#history.__init__)
- [initialize](#history.initialize)
- [get_deals](#history.get_deals)
- [get_deals_by_ticket](#history.get_deals_by_ticket)
- [get_deals_by_position](#history.get_deals_by_position)
- [get_orders](#history.get_orders)
- [get_orders_by_position](#history.get_orders_by_position)
- [get_orders_by_ticket](#history.get_orders_by_ticket)

<a id='history.history'></a>
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
| `mt5`          | `MetaTrader`       | MetaTrader instance                                                    | None    |
| `config`       | `Config`           | Config instance                                                        | None    |


<a id='history.__init__'></a>
### \_\_init\_\_
```python
def __init__(*, date_from: datetime | float, date_to: datetime | float, group: str = "")
```

#### Parameters:
| Name        | Type              | Description                                                                                                                                                                      | Default |
|-------------|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| `date_from` | `datetime\|float` | Date the deals are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Defaults to twenty-four hours from the current time in 'utc' | 0       |
| `date_to`   | `datetime\|float` | Date up to which the deals are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Defaults to the current time in "utc"                 | 0       |
| `group`     | `str`             | Filter for selecting history by symbols.                                                                                                                                         | ""      |

<a id='history.initialize'></a>
### initialize
```python
async def initialize() -> bool
```
Get deals and orders within the timeframe specified in the constructor.

<a id='history.get_deals'></a>
### get_deals
```python
async def get_deals(self) -> tuple[TradeDeal, ...]
```
Get deals from trading history using the parameters set in the constructor.

#### Returns
| Name    | Type                    | Description           | 
|---------|-------------------------|-----------------------|
| `deals` | `tuple[TradeDeal, ...]` | A list of trade deals |

<a id='history.get_deals_by_ticket'></a>
### get_deals_by_ticket
```python
def get_deals_by_ticket(self, *, ticket: int) -> tuple[TradeDeal, ...]
```
Get deals by ticket number. This filters deals by ticket based on the deals already fetched in initialize.

#### Parameters
| Name     | Type  | Description          |
|----------|-------|----------------------|
| `ticket` | `int` | Ticket number to get |

#### Returns:
| Name    | Type                    | Description            |
|---------|-------------------------|------------------------|
| `deals` | `tuple[TradeDeal, ...]` | A tuple of trade deals |

<a id='history.get_deals_by_position'></a>
### get_deals_by_position
```python
async def get_deals_by_position(self, *, position: int) -> tuple[TradeDeal, ...]
```
Get deals by position
#### Parameters
| Name       | Type  | Description            |
|------------|-------|------------------------|
| `position` | `int` | Position number to get |

#### Returns
| Name    | Type                    | Description            |
|---------|-------------------------|------------------------|
| `deals` | `tuple[TradeDeal, ...]` | A tuple of trade deals |

<a id='history.get_orders'></a>
### get_orders
```python
async def get_orders(self) -> tuple[TradeOrder, ...]
```
Get orders from trading history using the parameters set in the constructor.

<a id='history.get_orders_by_position'></a>
### get_orders_by_position
```python
def get_orders_by_position(self, *, position: int) -> tuple[TradeOrder, ...]
```
Get orders by position.
#### Parameters
| Name       | Type  | Description            |
|------------|-------|------------------------|
| `position` | `int` | Position number to get |

#### Returns
| Name     | Type                     | Description             |
|----------|--------------------------|-------------------------|
| `orders` | `tuple[TradeOrder, ...]` | A tuple of trade orders |

<a id='history.get_orders_by_ticket'></a>
### get_orders_by_ticket
```python
def get_orders_by_ticket(self, *, position: int) -> tuple[TradeOrder, ...]
```

Get orders by ticket number. This filters orders by ticket based on the orders already fetched in initialize.
#### Parameters
| Name     | Type  | Description          |
|----------|-------|----------------------|
| `ticket` | `int` | ticket number to get |

#### Returns
| Name     | Type                     | Description             |
|----------|--------------------------|-------------------------|
| `orders` | `tuple[TradeOrder, ...]` | A tuple of trade orders |
