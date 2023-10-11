<a id="aiomql.trader"></a>

# aiomql.trader

Trader class module. Handles the creation of an order and the placing of trades

<a id="aiomql.trader.Trader"></a>

## Trader Objects

```python
class Trader()
```

Base class for creating a Trader object. Handles the creation of an order and the placing of trades

**Attributes**:

- `symbol` _Symbol_ - Financial instrument class Symbol class or any subclass of it.
- `ram` _RAM_ - RAM instance
- `order` _Order_ - Trade order
  
  Class Attributes:
- `name` _str_ - A name for the strategy.
- `account` _Account_ - Account instance.
- `mt5` _MetaTrader_ - MetaTrader instance.
- `config` _Config_ - Config instance.

<a id="aiomql.trader.Trader.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*, symbol: Symbol, ram: RAM = None)
```

Initializes the order object and RAM instance

**Arguments**:

- `symbol` _Symbol_ - Financial instrument
- `ram` _RAM_ - Risk Assessment and Management instance

<a id="aiomql.trader.Trader.create_order"></a>

#### create\_order

```python
async def create_order(*, order_type: OrderType, **kwargs)
```

Complete the order object with the required values. Creates a simple order.
Uses the ram instance to set the volume.

**Arguments**:

- `order_type` _OrderType_ - Type of order
- `kwargs` - keyword arguments as required for the specific trader

<a id="aiomql.trader.Trader.set_order_limits"></a>

#### set\_order\_limits

```python
async def set_order_limits(pips: float)
```

Sets the stop loss and take profit for the order.
This method uses pips as defined for forex instruments.

**Arguments**:

- `pips` - Target pips

<a id="aiomql.trader.Trader.place_trade"></a>

#### place\_trade

```python
async def place_trade(order_type: OrderType, params: dict = None, **kwargs)
```

Places a trade based on the order_type.

**Arguments**:

- `order_type` _OrderType_ - Type of order
- `params` - parameters to be saved with the trade
- `kwargs` - keyword arguments as required for the specific trader

