# Order

## Table of contents
- [Order](#Order)
- [\_\_init\_\_](#__init__)
- [orders_total](#orders_total)
- [get_order](#get_order)
- [get_orders](#get_orders)
- [check](#check)
- [send](#send)
- [calc_margin](#calc_margin)
- [calc_profit](#calc_profit)

<a id="Order"></a>
### Order
```python
class Order(TradeRequest)
```
Trade order related functions and attributes. Subclass of TradeRequest.

<a id="__init__"></a>
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

<a id="orders_total"></a>
### <a id=order.Order.orders_total> orders_total
```python
async def orders_total()
```
Get the total number of active orders.
#### Returns
| Type  | Description                   |
|-------|-------------------------------|
| `int` | total number of active orders |

<a id="get_order"></a>
### get_order
```python
async def get_order(self, ticket: int) -> TradeOrder
```
Get an active trade order by ticket.

<a id="get_orders"></a>
### get_orders
```python
async def get_orders(self, *, ticket: int = 0, symbol: str = '', group: str = '', retries=3) -> tuple[TradeOrder]:
```
Get active trade orders. If ticket is provided, it will return the order with the specified ticket.
If symbol is provided, it will return all orders for the specified symbol.
If group is provided, it will return all orders for the specified group.
#### Parameters
| Name     | Type   | Description                          | Default |
|----------|--------|--------------------------------------|---------|
| `ticket` | `int`  | Order ticket                         | 0       |
| `symbol` | `str`  | Symbol name                          | ''      |
| `group`  | `str`  | Group name                           | ''      |
#### Returns
| Type                | Description                                          |
|---------------------|------------------------------------------------------|
| `tuple[TradeOrder]` | A Tuple of active trade orders as TradeOrder objects |

#### Raises
| Exception    | Description       |
|--------------|-------------------|
| `OrderError` | If not successful |

<a id="check"></a>
### check
```python
async def check() -> OrderCheckResult
```
Check funds sufficiency for performing a required trading operation and the possibility of executing it at the current market price.
#### Returns
| Type               | Description                |
|--------------------|----------------------------|
| `OrderCheckResult` | An OrderCheckResult object |
#### Raises:
| Exception    | Description       |
|--------------|-------------------|
| `OrderError` | If not successful |


<a id="send"></a>
### send
```python
async def send() -> OrderSendResult
```
Send a request to perform a trading operation from the terminal to the trade server.
#### Returns
| Type              | Description               |
|-------------------|---------------------------|
| `OrderSendResult` | An OrderSendResult object |
#### Raises:
| Exception    | Description       |
|--------------|-------------------|
| `OrderError` | If not successful |

<a id="calc_margin"></a>
### calc_margin
```python
async def calc_margin() -> float
```
Return the required margin in the account currency to perform a specified trading operation.
#### Returns
| Type    | Description                       |
|---------|-----------------------------------|
| `float` | Returns float value if successful |
#### Raises
| Exception    | Description       |
|--------------|-------------------|
| `OrderError` | If not successful |

<a id="calc_profit"></a>
### calc_profit
```python
async def calc_profit() -> float
```
Return profit in the account currency for a specified trading operation.
#### Returns
| Type    | Description                       |
|---------|-----------------------------------|
| `float` | Returns float value if successful |
| `None`  | If not successful                 |
