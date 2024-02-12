# Positions

## Table of contents
- [Positions](#positions)
- [Attributes](#attributes)
- [\_\_init\_\_](#__init__)
- [positions_total](#positions_total)
- [positions_get](#positions_get)
- [close](#close)
- [close_by](#close_by)
- [close_all](#close_all)

<a id="positions"></a>
### Positions
```python
class Positions
```
Get and handle Open positions.

#### Attributes
| Name     | Type         | Description                                                                                                                                                                                     | Default |
|----------|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| `symbol` | `str`        | Financial instrument name.                                                                                                                                                                      | ""      |
| `group`  | `str`        | The filter for arranging a group of necessary symbols. Optional named parameter. If the group is specified, the function returns only positions meeting a specified criteria for a symbol name. | ""      |
| `ticket` | `int`        | Position ticket.                                                                                                                                                                                | 0       |
| `mt5`    | `MetaTrader` | MetaTrader instance.                                                                                                                                                                            | None    |

<a id="__init__"></a>
### \_\_init\_\_
```python
def __init__(*, symbol: str = "", group: str = "", ticket: int = 0)
```
Get Open Positions.
#### Arguments
| Name     | Type  | Description                                                                                                                                                                           | Default |
|----------|-------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| `symbol` | `str` | Financial instrument name.                                                                                                                                                            | ""      |
| `group`  | `str` | The filter for arranging a group of symbols. Optional named parameter. If the group is specified, the function returns only positions meeting a specified criteria for a symbol name. | ""      |
| `ticket` | `int` | Position ticket.                                                                                                                                                                      | 0       |

<a id="positions_total"></a>
### positions_total
```python
async def positions_total() -> int
```
Get the number of open positions.
#### Returns
| Type  | Description                           |
|-------|---------------------------------------|
| `int` | Return total number of open positions |

<a id="positions_get"></a> 
### positions_get
```python
async def positions_get(self, symbol: str = '', group: str = '', ticket: int = 0, retries=3) -> list[TradePosition]:
```
Get open positions with the ability to filter by symbol or ticket.
#### Arguments
| Name     | Type   | Description                                                                                                                                                                           | Default |
|----------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| `symbol` | `str`  | Financial instrument name.                                                                                                                                                            | ""      |
| `group`  | `str`  | The filter for arranging a group of symbols. Optional named parameter. If the group is specified, the function returns only positions meeting a specified criteria for a symbol name. | ""      |
| `ticket` | `int`  | Position ticket.                                                                                                                                                                      | 0       |

#### Returns
| Type                  | Description                    |
|-----------------------|--------------------------------|
| `list[TradePosition]` | A list of open trade positions |


<a id="close"></a>
### close
```python
async def close(self, *, ticket: int, symbol: str, price: float, volume: float, order_type: OrderType):
```
Close a position by ticket number.
#### Arguments
| Name         | Type        | Description                | Default |
|--------------|-------------|----------------------------|---------|
| `ticket`     | `int`       | Position ticket.           |         |
| `symbol`     | `str`       | Financial instrument name. |         |
| `price`      | `float`     | Closing price.             |         |
| `volume`     | `float`     | Volume to close.           |         |
| `order_type` | `OrderType` | Order type.                |         |

<a id="close_by"></a>
### close_by
```python
async def close_by(self, pos: TradePosition):
```
Close a position by position object.
#### Arguments
| Name  | Type            | Description     |
|-------|-----------------|-----------------|
| `pos` | `TradePosition` | Position object |

<a id="close_all"></a>
### close_all
```python
async def close_all() -> int
```
Close all open positions for the trading account.
#### Returns
| Type  | Description                          |
|-------|--------------------------------------|
| `int` | Return total number of closed trades |
