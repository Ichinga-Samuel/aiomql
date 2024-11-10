# Trader
Trader class module. Handles the creation of an order and the placing of trades

## Table of Contents
- [Trader](#trader)
- [\_\_init\_\_](#trader.__init__)
- [set_trade_stop_levels_points](#trader.set_trade_stop_levels_points)
- [set_trade_stop_levels_pips](#trader.set_trade_stop_levels_pips)
- [create_order_with_points](#trade.create_order_with_points)
- [create_order_with_sl](#trade.create_order_with_sl)
- [create_order_with_stops](#trade.create_order_with_stops)
- [create_order_no_stops](#trade.create_order_no_stops)
- [send_order](#trader.send_order)
- [check_order](#trader.check_order)
- [record_trade](#trader.record_trade)
- [place_trade](#trader.place_trade)

<a name="trader.trader"></a>
### Trader
```python
class Trader()
```
Base class for creating a Trader object. Handles the creation of an order and the placing of trades

#### Attributes:
| Name         | Type     | Description                                           | Default |
|--------------|----------|-------------------------------------------------------|---------|
| `ram`        | `RAM`    | Risk Assessment Management System.                    | None    |
| `config`     | `Config` | Config instance.                                      | None    |
| `order`      | `Order`  | Order instance.                                       | None    |
| `symbol`     | `Symbol` | The Financial Instrument                              | None    |
| `parameters` | `dict`   | A dictionary of parameters associated with the trade. | None    |

<a name="trader.__init__"></a>
### \_\_init\_\_
```python
def __init__(*, symbol: Symbol, ram: RAM = None)
```
#### Parameters:
| Name     | Type     | Description                             | Default |
|----------|----------|-----------------------------------------|---------|
| `symbol` | `Symbol` | The Financial instrument                |         |
| `ram`    | `RAM`    | Risk Assessment and Management instance | None    |


<a name="trader.set_trade_stop_levels_pips"></a>
### set_trade_stop_levels_pips
```python
async def set_trade_stop_levels_pips(*, pips: float, risk_to_reward: float = None):
```
Sets the stop loss and take profit for the order. This method uses pips as defined for forex instruments.

#### Parameters:
| Name             | Type    | Description                   | Default |
|------------------|---------|-------------------------------|---------|
| `pips`           | `float` | Target pips                   |         |
| `risk_to_reward` | `float` | Optional risk to reward ratio | None    |


<a name="trader.set_trade_stop_levels_points"></a>
### set_trade_stop_levels_points
```python
async def set_trade_stop_levels_points(*, points: float, risk_to_reward: float = None):
```
Sets the stop loss and take profit for the order. This method uses points as defined for forex instruments.

#### Parameters:
| Name             | Type    | Description                   | Default |
|------------------|---------|-------------------------------|---------|
| `points`         | `float` | Target points                 |         |
| `risk_to_reward` | `float` | Optional risk to reward ratio | None    |


<a name="trader.create_order_no_stops"></a>
### create_order_no_stops
```python
async def create_order_no_stops(*, order_type: OrderType, volume: float = None)
```
Create an order without setting stop loss and take profit. Using minimum lot size.

#### Parameters:
| Name         | Type        | Description         | Default |
|--------------|-------------|---------------------|---------|
| `order_type` | `OrderType` | The order type      |         |
| `volume`     | `float`     | The volume to trade | None    |


<a name="trader.create_order_with_stops"></a>
### create_order_with_stops
```python
async def create_order_with_stops(*, order_type: OrderType, sl: float, tp: float, amount_to_risk: float = None)
```
Create an order with stop loss and take profit levels. Use the amount to risk per trade to 
calculate the volume.

#### Parameters:
| Name             | Type        | Description        | Default |
|------------------|-------------|--------------------|---------|
| `order_type`     | `OrderType` | The order type     |         |
| `sl`             | `float`     | The stop loss`     |         |
| `tp`             | `float`     | The take profit`   |         |
| `amount_to_risk` | `float`     | The amount to risk | None    |


<a name="trader.create_order_with_sl"></a>
### create_order_with_sl
```python
async def create_order_with_sl(*, order_type: OrderType, sl: float, amount_to_risk: float = None, risk_to_reward: float = None)
```
Create an order with a given stop_loss level. Use the amount to risk per trade to calculate the volume.

#### Parameters:
| Name             | Type        | Description                              | Default |
|------------------|-------------|------------------------------------------|---------|
| `order_type`     | `OrderType` | The order type                           |         |
| `sl`             | `float`     | The stop loss`                           |         |
| `risk_to_reward` | `float`     | Risk to reward ratio. Optional parameter | None    |
| `amount_to_risk` | `float`     | The amount to risk                       | None    |


<a name="trader.create_order_with_points"></a>
### create_order_with_points
```python
async def create_order_with_points(*, order_type: OrderType, points: float, amount_to_risk: float = None, risk_to_reward: float = None)
```
Create an order with specific points to risk. Use the amount to risk per trade to calculate the volume.

#### Parameters:
| Name             | Type        | Description                              | Default |
|------------------|-------------|------------------------------------------|---------|
| `order_type`     | `OrderType` | The order type                           |         |
| `points`         | `float`     | Points to risk                           |         |
| `risk_to_reward` | `float`     | Risk to reward ratio. Optional parameter | None    |
| `amount_to_risk` | `float`     | The amount to risk                       | None    |


<a name="trader.send_order"></a>
### send_order
```python
async def send_order() -> OrderSendResult
```
Sends the order to the broker for execution.

#### Returns:
| Type              | Description                |
|-------------------|----------------------------|
| `OrderSendResult` | The OrderSendResult object |


<a name="trader.check_order"></a>
### check_order
```python
async def check_order() -> OrderCheckResult
```
Checks the status of the order before placing the trade.

#### Returns:
| Type               | Description                 |
|--------------------|-----------------------------|
| `OrderCheckResult` | The OrderCheckResult object |

<a name="trader.record_trade"></a>
### record_trade
```python
async def record_trade(*, result: OrderSendResult, parameters: dict = None, name: str = '')
```
Records the trade and the order details if `Config.record_trades` is true. Trades are recorded as either json or csv.

#### Parameters:
| Name         | Type              | Description                                                  | Default |
|--------------|-------------------|--------------------------------------------------------------|---------|
| `result`     | `OrderSendResult` | The result of the placed order                               |         |
| `parameters` | `dict`            | parameters to saved instead of the ones in `self.parameters` | None    |
| `name`       | `str`             | Name for the csv or json file                                | ''      |

<a name="trader.place_trade"></a>
### place_trade
```python
@abstractmethod
async def place_trade(self, *args, **kwargs)
```
Places a trade. All traders must implement this method.
