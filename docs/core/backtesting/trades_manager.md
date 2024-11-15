# TradesManager

## Table of Contents
- [trades_manager](#trades_manager.trades_manager)
  - [TradesManager](#trades_manager.trades_manager)
    - [update](#trades_manager.trade_manager.update)
    - [values](#trades_manager.trade_manager.values)
    - [keys](#trades_manager.trade_manager.keys)
    - [items](#trades_manager.trade_manager.items)
    - [to_dict](#trades_manager.trade_manager.to_dict)
  - [PositionsManager](#trades_manager.positions_manager)
    - [\__init\__](#positions_manager.__init__)
    - [margin](#positions_manager.margin)
    - [close](#positions_manager.close)
    - [get_margin](#positions_manager.get_margin)
    - [delete_margin](#positions_manager.delete_margin)
    - [set_margin](#positions_manager.set_margin)
    - [positions_get](#positions_manager.positions_get)
    - [positions_total](#positions_manager.positions_total)
    - [open_positions](#positions_manager.open_positions)
  - [OrdersManager](#trades_manager.orders_manager)
    - [get_orders_range](#orders_manager.get_orders_range)
    - [history_orders_get](#orders_manager.history_orders_get)
    - [history_orders_total](#orders_manager.history_orders_total)
  - [DealsManager](#trades_manager.deals_manager)
    - [get_deals_range](#deals_manager.get_deals_range)
    - [history_deals_get](#deals_manager.history_deals_get)
    - [history_deals_total](#deals_manager.history_deals_total)


<a id="trades_manager.trades_manager"></a>
### TradesManager
```python
class TradeManager(Generic[TradeData])
```
A generic class to manage trades data during a backtest. It is the parent class of the
PositionsManager, OrdersManager, and DealsManager. It implements some dict-like methods to manage the data.
It has a private attribute _data to store the data. It exposes the data through the values, keys, and items methods.
It also has a `to_dict` method to convert the data to a dictionary.

#### Parameters:
| Name    | Type                   | Description                  |
|---------|------------------------|------------------------------|
| `_data` | `dict[int, TradeData]` | The data to store the trades |


#### Examples:
```python
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
{'123456' - {'ticket': 123456, 'symbol': 'EURUSD', 'volume': 0.1}}
>>> pos = manager.get(123456)
>>> pos
TradePosition(ticket=123456, symbol='EURUSD', volume=0.1)
>>> pos in manager
True
>>> len(manager)
1
>>> pos in manager
False
```
  
<a id="trades_manager.update"></a>
#### update
```python
def update(*, ticket: int, **kwargs)
```
Update the data of a trade. Given the ticket of the trade and the new data to update.

#### Parameters:
| Name       | Type  | Description                        |
|------------|-------|------------------------------------|
| `ticket`   | `int` | The ticket of the trade to update. |
| `**kwargs` |       | The new data to update.            |


<a id="trades_manager.values"></a>
### values
```python
def values() -> tuple[TradeData, ...]
```
Returns the values of the data.


<a id="trades_manager.keys"></a>
### keys
```python
def keys() -> tuple[int, ...]
```
Returns the keys of the data.


<a id="trades_manager.items"></a>
### items
```python
def items() -> tuple[tuple[int, TradeData], ...]
```
Returns the items of the data.


<a id="trades_manager.to_dict"></a>
### to_dict
```python
def to_dict()
```
Convert the data to a dictionary.


<a id="trades_manager.positions_manager"></a>
```python
class PositionsManager(TradeManager)
```
A class to manage the open positions during a backtest. It is a subclass of  It has an additional
attribute _open_positions to store the open positions. It also has a margins attribute to store the margins of the
open positions. It overrides some methods of the TradeManager class to manage the open positions.

#### Attributes:
| Name             | Type               | Description                                                                                                              |
|------------------|--------------------|--------------------------------------------------------------------------------------------------------------------------|
| `data`           | `dict`             | The data to store the trades. This used for continuation of the backtesting, if it was stopped with some open positions. |
| `open_positions` | `set[int]`         | The open positions.                                                                                                      |
| `margins`        | `dict[int, float]` | The margins of the open positions.                                                                                       |
  

<a id="positions_manager.__init__"></a>
#### \__init\__
```python
def __init__(*, data: dict = None, open_positions: set[int] = None, margins: dict = None)
```
Positions manager manages the open positions during a backtest. It is a subclass of  It has an
additional attribute _open_positions to store the open positions. It also has a margins attribute to store the
margins of the open positions. It overrides some methods of the TradeManager class to manage the open positions.

#### Parameters:
| Name             | Type               | Description                                                                                                              |
|------------------|--------------------|--------------------------------------------------------------------------------------------------------------------------|
| `data`           | `dict`             | The data to store the trades. This used for continuation of the backtesting, if it was stopped with some open positions. |
| `open_positions` | `set[int]`         | The open positions.                                                                                                      |
| `margins`        | `dict[int, float]` | The margins of the open positions.                                                                                       |


<a id="positions_manager.margin"></a>
### margin
```python
@property
def margin()
```
Returns the total margin of all open positions


<a id="positions_manager.close"></a>
### close
```python
def close(*, ticket: int) -> bool
```
Close a position. Given the ticket of the position to close.

#### Parameters:
| Name     | Type  | Description                          |
|----------|-------|--------------------------------------|
| `ticket` | `int` | The ticket of the position to close. |


<a id="positions_manager.get_margin"></a>
#### get_margin
```python
def get_margin(*, ticket: int) -> float
```
Get the margin of a position. Given the ticket of the position.

#### Parameters:
| Name     | Type  | Description                 |
|----------|-------|-----------------------------|
| `ticket` | `int` | The ticket of the position. |


#### Returns:
| Type    | Description                 |
|---------|-----------------------------|
| `float` | The margin of the position. |


<a id="positions_manager.delete_margin"></a>
### delete_margin
```python
def delete_margin(*, ticket: int)
```
Delete the margin of a position. Given the ticket of the position.

#### Parameters:
| Name     | Type  | Description                 |
|----------|-------|-----------------------------|
| `ticket` | `int` | The ticket of the position. |


<a id="positions_manager.set_margin"></a>
### set_margin
```python
def set_margin(*, ticket: int, margin: float)
```
Set the margin of a position. Given the ticket of the position and the margin.

#### Parameters:
| Name     | Type    | Description                 |
|----------|---------|-----------------------------|
| `ticket` | `int`   | The ticket of the position. |
| `margin` | `float` | The margin of the position. |


<a id="positions_manager.positions_get"></a>
### positions_get
```python
def positions_get(*, ticket: int = None, symbol: str = None, group: None = None) -> tuple[TradePosition, ...]
```
Get positions. Given the ticket, symbol, or group of the positions.

#### Parameters:
| Name     | Type  | Description                 |
|----------|-------|-----------------------------|
| `ticket` | `int` | The ticket of the position. |
| `symbol` | `str` | The symbol of the position. |
| `group`  | `str` | The group of the position.  |

#### Returns:
| Type                   | Description                 |
|------------------------|-----------------------------|
| `tuple[TradePosition]` | The positions.              |

#### Returns:
| Type                        | Description                 |
|-----------------------------|-----------------------------|
| `tuple[TradePosition, ...]` | The positions.              |


<a id="positions_manager.positions_total"></a>
### positions_total
```python
def positions_total() -> int
```
Get the total number of open positions.

#### Returns:
| Type  | Description                         |
|-------|-------------------------------------|
| `int` | The total number of open positions. |


<a id="positions_manager.open_positions"></a>
#### open_positions
```python
@property
def open_positions() -> tuple[TradePosition, ...]
```
Returns the open positions.

#### Parameters:
| Name     | Type  | Description                 |
|----------|-------|-----------------------------|
| `ticket` | `int` | The ticket of the position. |


<a id="trades_manager.orders_manager"></a>
### OrdersManager
```python
class OrdersManager(TradeManager)
```
Managers orders data during a backtest. It is a subclass of  It manages access to the historical
orders data


<a id="orders_manager.get_orders_range"></a>
#### get_orders_range
```python
def get_orders_range(*, date_from: float, date_to: float) -> tuple[TradeData, ...]
```
Get orders within a date range. Given the start and end date of the range.

#### Parameters:
| Name        | Type    | Description                  |
|-------------|---------|------------------------------|
| `date_from` | `float` | The start date of the range. |
| `date_to`   | `float` | The end date of the range.   |

#### Returns:
| Type               | Description                       |
|--------------------|-----------------------------------|
| `tuple[TradeData]` | The orders within the date range. |
 

#### Returns:
| Type               | Description                       |
|--------------------|-----------------------------------|
| `tuple[TradeData]` | The orders within the date range. |


<a id="orders_manager.history_orders_get"></a>
#### history_orders_get
```python
def history_orders_get(*, date_from: float | datetime = None, date_to: float | datetime = None,
                       group: str = "", ticket: int = None, position: int = None) -> tuple[TradeOrder, ...]
```
Get historical orders. Given the start and end date of the range, the group, ticket, or position of the
orders.

#### Parameters:
| Name        | Type    | Description                  |
|-------------|---------|------------------------------|
| `date_from` | `float` | The start date of the range. |
| `date_to`   | `float` | The end date of the range.   |
| `group`     | `str`   | The group of the orders.     |
| `ticket`    | `int`   | The ticket of the order.     |
| `position`  | `int`   | The position of the order.   |

#### Returns:
| Type                | Description            |
|---------------------|------------------------|
| `tuple[TradeOrder]` | The historical orders. |


<a id="orders_manager.history_orders_total"></a>
### history_orders_total
```python
def history_orders_total(*, date_from: datetime | float,
                         date_to: datetime | float) -> int
```
Get the total number of historical orders. Given the start and end date of the range.

#### Parameters:
| Name        | Type    | Description                  |
|-------------|---------|------------------------------|
| `date_from` | `float` | The start date of the range. |
| `date_to`   | `float` | The end date of the range.   |


<a id="trades_manager.deals_manager"></a>
### DealsManager
```python
class DealsManager(TradeManager)
```

<a id="deals_manager.get_deals_range"></a>
#### get_deals_range
```python
def get_deals_range(*, date_from: float, date_to: float) -> tuple[TradeData, ...]
```
Get deals within a date range. Given the start and end date of the range.

#### Parameters:
| Name        | Type    | Description                  |
|-------------|---------|------------------------------|
| `date_from` | `float` | The start date of the range. |
| `date_to`   | `float` | The end date of the range.   |

#### Returns:
| Type               | Description                       |
|--------------------|-----------------------------------|
| `tuple[TradeData]` | The deals within the date range.  |


<a id="deals_manager.history_deals_get"></a>
### history_deals_get
```python
def history_deals_get(*,
                      date_from: float | datetime = None,
                      date_to: float | datetime = None,
                      group: str = "",
                      ticket: int = None,
                      position: int = None) -> tuple[TradeDeal, ...]
```
History deals get. Given the start and end date of the range, the group, ticket, or position of the deals.

#### Parameters:
| Name        | Type    | Description                  |
|-------------|---------|------------------------------|
| `date_from` | `float` | The start date of the range. |
| `date_to`   | `float` | The end date of the range.   |
| `group`     | `str`   | The group of the deals.      |
| `ticket`    | `int`   | The ticket of the deal.      |
| `position`  | `int`   | The position of the deal.    |


<a id="deals_manager.history_deals_total"></a>
#### history_deals_total
```python
def history_deals_total(*, date_from: datetime | float,
                        date_to: datetime | float) -> int
```
Get the total number of historical deals. Given the start and end date of the range

#### Parameters:
| Name        | Type    | Description                  |
|-------------|---------|------------------------------|
| `date_from` | `float` | The start date of the range. |
| `date_to`   | `float` | The end date of the range.   |

#### Returns:
| Type  | Description                           |
|-------|---------------------------------------|
| `int` | The total number of historical deals. |
