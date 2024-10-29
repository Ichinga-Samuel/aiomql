## <a id="order"></a> Order


```python
class Order(TradeRequest)
```
Trade order related functions and properties. Subclass of [TradeRequest](#traderequest).

### \_\_init\_\_
```python
def __init__(**kwargs)
```
Initialize the order object with keyword arguments, symbol must be provided.
Provides default values for action, type_time and type_filling if not provided.
#### Arguments:
|Name| Type                    | Description  | Default           |
|---|-------------------------|--------------|-------------------|
|**symbol**| **str** \|   **Symbol** | Symbol name. Required keyword argument |                   |
|**action**| **TradeAction**         | Trade action | TradeAction.DEAL  |
|**type_time**| **OrderTime**           | Order time   | OrderTime.DAY     |
|**type_filling**| **OrderFilling**        | Order filling | OrderFilling.FOK  |
#### Raises:

|Exception|Description|
|---|---|
|**SymbolError**|If symbol is not provided|

### <a id=order.Order.orders_total> orders_total
```python
async def orders_total()
```
Get the number of active orders.

#### Returns:
|Type|Description|
|---|---|
|**int**|total number of active orders|

### orders
```python
async def orders() -> tuple[TradeOrder]
```
Get the list of active orders for the current symbol.

#### Returns:
|Type|Description|
|---|---|
|**tuple[TradeOrder]**|A Tuple of active trade orders as TradeOrder objects|

### check
```python
async def check() -> OrderCheckResult
```
Check funds sufficiency for performing a required trading operation and the possibility to execute it at

#### Returns::

|Type|Description|
|---|---|
|**OrderCheckResult**|An OrderCheckResult object|

#### Raises:

|Exception|Description|
|---|---|
|**OrderError**|If not successful|
- `OrderError` - If not successful

#### <a id="order.Order.send"></a> send

```python
async def send() -> OrderSendResult
```
Send a request to perform a trading operation from the terminal to the trade server.

#### Returns:
|Type|Description|
|---|---|
|**OrderSendResult**|An OrderSendResult object|

#### Raises:
|Exception|Description|
|---|---|
|**OrderError**|If not successful|

### calc_margin
```python
async def calc_margin() -> float
```
Return the required margin in the account currency to perform a specified trading operation.
#### Returns:
|Type|Description|
|---|---|
|**float**|Returns float value if successful|

#### Raises:
|Exception|Description|
|---|---|
|**OrderError**|If not successful|


### calc_profit
```python
async def calc_profit() -> float
```
Return profit in the account currency for a specified trading operation.
#### Returns:
|Type|Description|
|---|---|
|**float**|Returns float value if successful|
#### Raises:
|Exception|Description|
|---|---|
|**OrderError**|If not successful|

