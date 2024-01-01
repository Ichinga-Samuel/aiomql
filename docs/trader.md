## <a id="trader"></a> Trader
Trader class module. Handles the creation of an order and the placing of trades

```python
class Trader()
```
Base class for creating a Trader object. Handles the creation of an order and the placing of trades
### Attributes:
| Name        | Type        | Description                                          |Default|
|-------------|-------------|------------------------------------------------------|---|
| **ram**     | **RAM**     | Risk Assessment Management System.                   |None|
| **config**  | **Config**  | Config instance.                                     |None|
| **order**   | **Order**   | Order instance.                                      |None|
| **symbol**  | **Symbol**  | The Financial Instrument                             |None|
| **params**  | **Dict**    | A dictionary of parameters associated with the trade. |None|

### \_\_init\_\_
```python
def __init__(*, symbol: Symbol, ram: RAM = None)
```
### Parameters:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**symbol**| **Symbol** | The Financial instrument | None |
|**ram**| **RAM** | Risk Assessment and Management instance | None |

### create\_order
```python
async def create_order(*, order_type: OrderType, **kwargs)
```
Complete the order object with the required values. Creates a simple order.
#### Parameters:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**order_type**| **OrderType** | Type of order | None |
|**kwargs**|  | keyword arguments as required for the specific trader |  |

### set\_order\_limits
```python
async def set_order_limits(pips: float)
```
Sets the stop loss and take profit for the order. This method uses pips as defined for forex instruments.
#### Parameters:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**pips**| **float** | Target pips | None |

### set\_trade\_stop\_levels
```python
async def set_trade_stop_levels(*, points)
```
sets the stop loss and take profit for the order. This method uses points as defined by MetaTrader5 for all symbols.

#### Parameters:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**points**| **float** | Target points | None |

### send\_order
```python
async def send_order()
```
Sends the order to the broker for execution. Record the trade.

### check_order
```python
async def check_order()
```
Checks the status of the order before placing the trade.

#### Returns:
|Type|Description|
|---|---|
|**bool**|True if order is valid else False|

### record_trade
```python
async def record_trade(result: OrderSendResult)
```
Records the trade and the order details if **Config.record_trades** is true.
#### Parameters:
|Name| Type               | Description                    | Default           |
|---|--------------------|--------------------------------|-------------------|
|**result**| **OrderSendResult** | The result of the placed order | None |

### place\_trade
```python
async def place_trade(order_type: OrderType, params: dict = None, **kwargs)
```
Places a trade based on the order_type.
#### Parameters:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**order_type**| **OrderType** | Type of order | None |
|**params**| **dict** | parameters to be saved with the trade | None |
|**kwargs**|  | keyword arguments as required for the specific trader |  |
