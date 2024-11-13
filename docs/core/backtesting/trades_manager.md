# Table of Contents

* [trades\_manager](#trades_manager)
  * [TradeManager](#trades_manager.TradeManager)
    * [update](#trades_manager.TradeManager.update)
    * [values](#trades_manager.TradeManager.values)
    * [keys](#trades_manager.TradeManager.keys)
    * [items](#trades_manager.TradeManager.items)
    * [to\_dict](#trades_manager.TradeManager.to_dict)
  * [PositionsManager](#trades_manager.PositionsManager)
    * [\_\_init\_\_](#trades_manager.PositionsManager.__init__)
    * [margin](#trades_manager.PositionsManager.margin)
    * [close](#trades_manager.PositionsManager.close)
    * [get\_margin](#trades_manager.PositionsManager.get_margin)
    * [delete\_margin](#trades_manager.PositionsManager.delete_margin)
    * [set\_margin](#trades_manager.PositionsManager.set_margin)
    * [positions\_get](#trades_manager.PositionsManager.positions_get)
    * [positions\_total](#trades_manager.PositionsManager.positions_total)
    * [open\_positions](#trades_manager.PositionsManager.open_positions)
  * [OrdersManager](#trades_manager.OrdersManager)
    * [get\_orders\_range](#trades_manager.OrdersManager.get_orders_range)
    * [history\_orders\_get](#trades_manager.OrdersManager.history_orders_get)
    * [history\_orders\_total](#trades_manager.OrdersManager.history_orders_total)
  * [DealsManager](#trades_manager.DealsManager)
    * [get\_deals\_range](#trades_manager.DealsManager.get_deals_range)
    * [history\_deals\_get](#trades_manager.DealsManager.history_deals_get)
    * [history\_deals\_total](#trades_manager.DealsManager.history_deals_total)

<a id="trades_manager"></a>

# trades\_manager

<a id="trades_manager.TradeManager"></a>

## TradeManager Objects

```python
class TradeManager(Generic[TradeData])
```

A generic class to manage trades data during a backtest. It is the parent class of the
PositionsManager, OrdersManager, and DealsManager. It implements some dict-like methods to manage the data.
It has a private attribute _data to store the data. It exposes the data through the values, keys, and items methods.
It also has a to_dict method to convert the data to a dictionary.

**Attributes**:

- `_data` _dict[int, TradeData]_ - The data to store the trades.
  

**Examples**:

  >>> manager = TradeManager()
  >>> manager[123456] = TradePosition(ticket=123456, symbol="EURUSD", volume=0.1)
  >>> manager.update(ticket=123456, symbol="EURUSD", volume=0.1)
  >>> manager[123456]
  TradePosition(ticket=123456, symbol='EURUSD', volume=0.1)
  >>> manager.values()
  (TradePosition(ticket=123456, symbol='EURUSD', volume=0.1),)
  >>> manager.keys()
  (123456,)
  >>> manager.items()
  ((123456, TradePosition(ticket=123456, symbol='EURUSD', volume=0.1)),)
  >>> manager.to_dict()
- `{123456` - {'ticket': 123456, 'symbol': 'EURUSD', 'volume': 0.1}}
  >>> pos = manager.get(123456)
  >>> pos
  TradePosition(ticket=123456, symbol='EURUSD', volume=0.1)
  >>> pos in manager
  True
  >>> len(manager)
  1
  >>> pos in manager
  False

<a id="trades_manager.TradeManager.update"></a>

#### update

```python
def update(*, ticket: int, **kwargs)
```

Update the data of a trade. Given the ticket of the trade and the new data to update.

**Arguments**:

- `ticket` _int_ - The ticket of the trade to update.
- `**kwargs` - The new data to update.

<a id="trades_manager.TradeManager.values"></a>

#### values

```python
def values() -> tuple[TradeData, ...]
```

Returns the values of the data.

<a id="trades_manager.TradeManager.keys"></a>

#### keys

```python
def keys() -> tuple[int, ...]
```

Returns the keys of the data.

<a id="trades_manager.TradeManager.items"></a>

#### items

```python
def items() -> tuple[tuple[int, TradeData], ...]
```

Returns the items of the data.

<a id="trades_manager.TradeManager.to_dict"></a>

#### to\_dict

```python
def to_dict()
```

Convert the data to a dictionary.

<a id="trades_manager.PositionsManager"></a>

## PositionsManager Objects

```python
class PositionsManager(TradeManager)
```

A class to manage the open positions during a backtest. It is a subclass of TradeManager. It has an additional
attribute _open_positions to store the open positions. It also has a margins attribute to store the margins of the
open positions. It overrides some methods of the TradeManager class to manage the open positions.

**Attributes**:

- `_open_positions` _set[int]_ - The open positions.
- `margins` _dict[int, float]_ - The margins of the open positions.

<a id="trades_manager.PositionsManager.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*,
             data: dict = None,
             open_positions: set[int] = None,
             margins: dict = None)
```

Positions manager manages the open positions during a backtest. It is a subclass of TradeManager. It has an
additional attribute _open_positions to store the open positions. It also has a margins attribute to store the
margins of the open positions. It overrides some methods of the TradeManager class to manage the open positions.

**Arguments**:

- `data` _dict, optional_ - The data to store the trades. This used for continuation of the backtesting, if it
  was stopped with some open positions.
  
- `open_positions` _set, optional_ - The open positions. Defaults to None.
  
- `margins` _dict, optional_ - The margins of the open positions. Defaults to None.

<a id="trades_manager.PositionsManager.margin"></a>

#### margin

```python
@property
def margin()
```

Returns the total margin of all open positions

<a id="trades_manager.PositionsManager.close"></a>

#### close

```python
def close(*, ticket: int) -> bool
```

Close a position. Given the ticket of the position to close.

**Arguments**:

- `ticket` _int_ - The ticket of the position to close.

<a id="trades_manager.PositionsManager.get_margin"></a>

#### get\_margin

```python
def get_margin(*, ticket: int) -> float
```

Get the margin of a position. Given the ticket of the position.

**Arguments**:

- `ticket` _int_ - The ticket of the position.
  

**Returns**:

- `float` - The margin of the position.

<a id="trades_manager.PositionsManager.delete_margin"></a>

#### delete\_margin

```python
def delete_margin(*, ticket: int)
```

Delete the margin of a position. Given the ticket of the position.

**Arguments**:

- `ticket` _int_ - The ticket of the position.

<a id="trades_manager.PositionsManager.set_margin"></a>

#### set\_margin

```python
def set_margin(*, ticket: int, margin: float)
```

Set the margin of a position. Given the ticket of the position and the margin.

**Arguments**:

- `ticket` _int_ - The ticket of the position.
- `margin` _float_ - The margin of the position

<a id="trades_manager.PositionsManager.positions_get"></a>

#### positions\_get

```python
def positions_get(*,
                  ticket: int = None,
                  symbol: str = None,
                  group: None = None) -> tuple[TradePosition, ...]
```

Get positions. Given the ticket, symbol, or group of the positions.

**Arguments**:

- `ticket` _int_ - The ticket of the position.
- `symbol` _str_ - The symbol of the position.
- `group` _str_ - The group
  

**Returns**:

  tuple[TradePosition, ...]: The positions

<a id="trades_manager.PositionsManager.positions_total"></a>

#### positions\_total

```python
def positions_total() -> int
```

Get the total number of open positions.

**Returns**:

- `int` - The total number of open positions.

<a id="trades_manager.PositionsManager.open_positions"></a>

#### open\_positions

```python
@property
def open_positions() -> tuple[TradePosition, ...]
```

Returns the open positions.

**Arguments**:

  tuple[TradePosition, ...]: The open positions.

<a id="trades_manager.OrdersManager"></a>

## OrdersManager Objects

```python
class OrdersManager(TradeManager)
```

Managers orders data during a backtest. It is a subclass of TradeManager. It manages access to the historical
orders data

<a id="trades_manager.OrdersManager.get_orders_range"></a>

#### get\_orders\_range

```python
def get_orders_range(*, date_from: float,
                     date_to: float) -> tuple[TradeData, ...]
```

Get orders within a date range. Given the start and end date of the range.

**Arguments**:

- `date_from` _float_ - The start date of the range.
- `date_to` _float_ - The end date of the range.
  

**Returns**:

  tuple[TradeData, ...]: The orders within the date range.

<a id="trades_manager.OrdersManager.history_orders_get"></a>

#### history\_orders\_get

```python
def history_orders_get(*,
                       date_from: float | datetime = None,
                       date_to: float | datetime = None,
                       group: str = "",
                       ticket: int = None,
                       position: int = None) -> tuple[TradeOrder, ...]
```

Get historical orders. Given the start and end date of the range, the group, ticket, or position of the
orders.

**Arguments**:

- `date_from` _float, datetime_ - The start date of the range.
- `date_to` _float, datetime_ - The end date of the range.
- `group` _str_ - The group of the orders.
- `ticket` _int_ - The ticket of the order.
- `position` _int_ - The position of the order.
  

**Returns**:

  tuple[TradeOrder, ...]: The historical orders.

<a id="trades_manager.OrdersManager.history_orders_total"></a>

#### history\_orders\_total

```python
def history_orders_total(*, date_from: datetime | float,
                         date_to: datetime | float) -> int
```

Get the total number of historical orders. Given the start and end date of the range.

**Arguments**:

- `date_from` _datetime, float_ - The start date of the range.
- `date_to` _datetime, float_ - The end date of the range.

<a id="trades_manager.DealsManager"></a>

## DealsManager Objects

```python
class DealsManager(TradeManager)
```

<a id="trades_manager.DealsManager.get_deals_range"></a>

#### get\_deals\_range

```python
def get_deals_range(*, date_from: float,
                    date_to: float) -> tuple[TradeData, ...]
```

Get deals within a date range. Given the start and end date of the range.

**Arguments**:

- `date_from` _float_ - The start date of the range.
- `date_to` _float_ - The end date of the range.
  

**Returns**:

  tuple[TradeData, ...]: The deals within the date range.

<a id="trades_manager.DealsManager.history_deals_get"></a>

#### history\_deals\_get

```python
def history_deals_get(*,
                      date_from: float | datetime = None,
                      date_to: float | datetime = None,
                      group: str = "",
                      ticket: int = None,
                      position: int = None) -> tuple[TradeDeal, ...]
```

History deals get. Given the start and end date of the range, the group, ticket, or position of the deals.

**Arguments**:

- `date_from` _float, datetime_ - The start date of the range.
- `date_to` _float, datetime_ - The end date of the range.
- `group` _str_ - The group of the deals.
- `ticket` _int_ - The ticket of the deal.
- `position` _int_ - The position of the deal.

<a id="trades_manager.DealsManager.history_deals_total"></a>

#### history\_deals\_total

```python
def history_deals_total(*, date_from: datetime | float,
                        date_to: datetime | float) -> int
```

Get the total number of historical deals. Given the start and end date of the range

**Arguments**:

- `date_from` _datetime, float_ - The start date of the range.
- `date_to` _datetime, float_ - The end date of the range.
  

**Returns**:

- `int` - The total number of historical deals.

