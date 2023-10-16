## <a id="trader"></a> Trader
Trader class module. Handles the creation of an order and the placing of trades

```python
class Trader()
```
Base class for creating a Trader object. Handles the creation of an order and the placing of trades
### Attributes:
|Name|Type|Description|Default|
|---|---|---|---|
|**name**|**str**|A name for the strategy.|None|
|**account**|**Account**|Account instance.|None|
|**mt5**|**MetaTrader**|MetaTrader instance.|None|
|**config**|**Config**|Config instance.|None|
|**symbol**|**Symbol**|The Financial Instrument as a Symbol Object|None|
|**parameters**|**Dict**|A dictionary of parameters for the strategy.|None|

### \_\_init\_\_
```python
def __init__(*, symbol: Symbol, ram: RAM = None)
```
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**symbol**| **Symbol** | The Financial instrument | None |
|**ram**| **RAM** | Risk Assessment and Management instance | None |
Initializes the order object and RAM instance
#### Arguments:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**symbol**| **Symbol** | The Financial instrument | None |
|**ram**| **RAM** | Risk Assessment and Management instance | None |
### create\_order
```python
async def create_order(*, order_type: OrderType, **kwargs)
```
Complete the order object with the required values. Creates a simple order.
Uses the ram instance to set the volume.
#### Arguments:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**order_type**| **OrderType** | Type of order | None |
|**kwargs**|  | keyword arguments as required for the specific trader |  |

### set\_order\_limits
```python
async def set_order_limits(pips: float)
```
Sets the stop loss and take profit for the order.
This method uses pips as defined for forex instruments.
#### Arguments:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**pips**| **float** | Target pips | None |

### place\_trade
```python
async def place_trade(order_type: OrderType, params: dict = None, **kwargs)
```
Places a trade based on the order_type.
#### Arguments:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**order_type**| **OrderType** | Type of order | None |
|**params**| **dict** | parameters to be saved with the trade | None |
|**kwargs**|  | keyword arguments as required for the specific trader |  |
