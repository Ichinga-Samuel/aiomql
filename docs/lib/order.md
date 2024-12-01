# Order

## Table of contents
- [Order](#order.order)
- [\_\_init\_\_](#order.__init__)
- [orders_total](#order.orders_total)
- [get_order](#order.get_pending_order)
- [get_orders](#order.get_pending_orders)
- [check](#order.check)
- [send](#order.send)
- [calc_margin](#order.calc_margin)
- [calc_profit](#order.calc_profit)
- [calc_loss](#order.calc_loss)
- [request](#order.request)
- [modify](#order.modify)

<a id="order.order"></a>
### Order
```python
class Order(_Base, TradeRequest)
```
Trade order related functions and attributes. Subclass of TradeRequest.

<a id="order.__init__"></a>
### \_\_init\_\_
```python
def __init__(**kwargs)
```
Initialize the order object with keyword arguments, symbol must be provided.
Provides default values for action, type_time and type_filling if not provided.
#### Arguments
| Name           | Type                | Description                            | Default          |
|----------------|---------------------|----------------------------------------|------------------|
| `action`       | `TradeAction`       | Trade action                           | TradeAction.DEAL |
| `type_time`    | `OrderTime`         | Order time                             | OrderTime.DAY    |
| `type_filling` | `OrderFilling`      | Order filling                          | OrderFilling.FOK |

<a id="order.orders_total"></a>
```python
async def orders_total()
```
Get the total number of active pending orders.
#### Returns
| Type  | Description                   |
|-------|-------------------------------|
| `int` | total number of active orders |

<a id="order.get_pending_order"></a>
### get_pending order
```python
async def get_pending_order(self, ticket: int) -> TradeOrder
```
Get an active pending trade order by ticket.

<a id="order.get_pending_orders"></a>
### get_pending_orders
```python
async def get_pending_orders(self, *, ticket: int = 0, symbol: str = '', group: str = '') -> tuple[TradeOrder, ...]:
```
Get active trade orders. If ticket is provided, it will return the order with the specified ticket.
If symbol is provided, it will return all orders for the specified symbol.
If group is provided, it will return all orders for the specified group.

#### Parameters:
| Name     | Type   | Description                          | Default |
|----------|--------|--------------------------------------|---------|
| `ticket` | `int`  | Order ticket                         | 0       |
| `symbol` | `str`  | Symbol name                          | ''      |
| `group`  | `str`  | Group name                           | ''      |

#### Returns:
| Type                     | Description                                          |
|--------------------------|------------------------------------------------------|
| `tuple[TradeOrder, ...]` | A Tuple of active trade orders as TradeOrder objects |

<a id="order.check"></a>
### check
```python
async def check(**kwargs) -> OrderCheckResult
```
#### Parameters:
| Type   | Description                                  |
|--------|----------------------------------------------|
| kwargs | Update the request dict with extra arguments |

Check if an order is okay.

#### Returns:
| Type               | Description                |
|--------------------|----------------------------|
| `OrderCheckResult` | An OrderCheckResult object |

#### Raises:
| Exception    | Description       |
|--------------|-------------------|
| `OrderError` | If not successful |

<a id="order.send"></a>
### send
```python
async def send() -> OrderSendResult
```
Send a request to perform a trading operation from the terminal to the trade server.

#### Returns:
| Type              | Description               |
|-------------------|---------------------------|
| `OrderSendResult` | An OrderSendResult object |

#### Raises:
| Exception    | Description       |
|--------------|-------------------|
| `OrderError` | If not successful |

<a id="order.calc_margin"></a>
### calc_margin:
```python
async def calc_margin() -> float
```
Return the required margin in the account currency to perform a specified trading operation.

#### Returns:
| Type    | Description                       |
|---------|-----------------------------------|
| `float` | Returns float value if successful |

<a id="order.calc_profit"></a>
### calc_profit
```python
async def calc_profit() -> float
```
Return profit in the account currency for a specified trading operation.

#### Returns:
| Type    | Description                       |
|---------|-----------------------------------|
| `float` | Returns float value if successful |
| `None`  | If not successful                 |

<a id="order.calc_loss"></a>
### calc_profit
```python
async def calc_loss() -> float
```
Return loss in the account currency for a specified trading operation.
#### Returns
| Type    | Description                       |
|---------|-----------------------------------|
| `float` | Returns float value if successful |
| `None`  | If not successful                 |

<a id="order.request"></a>
### request
```python
@property
async def request() -> dict
```
Return the trade request object as a dict

#### Returns
| Type   | Description                      |
|--------|----------------------------------|
| `dict` | Returns the trade request object |


<a id="order.modify"></a>
### modify
```python
def modify(**kwargs)
```
Modify the order object with keyword arguments.
