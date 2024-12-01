# Positions

## Table of contents
- [Positions](#positions.positions)
- [\_\_init\_\_](#positions.__init__)
- [get_positions](#positions.get_positions)
- [get_position_by_ticket](#positions.get_position_by_ticket)
- [get_positions_by_symbol](#positions.get_positions_by_symbol)
- [close](#positions.close)
- [close_position_by_ticket](#positions.close_position_by_ticket)
- [close_position](#positions.close_position)
- [close_all](#positions.close_all)
- [get_total_positions](#positions.get_total_positions)

<a id="positions.positions"></a>
### Positions
```python
class Positions
```
Get and handle Open positions.

#### Attributes
| Name        | Type                        | Description                                                                         |
|-------------|-----------------------------|-------------------------------------------------------------------------------------|
| `positions` | `tuple[TradePosition, ...]` | Financial instrument name.                                                          |
| `mt5`       | `MetaTrader`                | MetaTrader instance.                                                                |
|`total_positions`| `int`                    | Total number of open positions. Can be set in `get_positions` or `get_total_positions`. |

<a id="positions.__init__"></a>
### \_\_init\_\_
```python
def __init__()
```
Initialize a position instance


<a id="positions.get_position"></a> 
### get_positions
```python
async def get_positions(*, symbol: str = None, ticket: int = None, group: str = None) -> tuple[TradePosition, ...]:
```
Get open positions, with the ability to filter by symbol, ticket, or group.

#### Parameters:
| Name     | Type  | Description     |
|----------|-------|-----------------|
| `symbol` | `str` | Symbol          |
| `ticket` | `int` | Position ticket |
| `group`  | `str` | Group name      |


#### Returns:
| Type                        | Description                    |
|-----------------------------|--------------------------------|
| `tuple[TradePosition, ...]` | A list of open trade positions |


<a id="positions.get_position_by_ticket"></a>
### get_position_by_ticket
```python
async def get_position_by_ticket(self, *, ticket: int) -> TradePosition
```
Get a position by ticket id.

#### Parameters:
| Name     | Type  | Description     |
|----------|-------|-----------------|
| `ticket` | `int` | Position ticket |

#### Returns:
| Type            | Description    |
|-----------------|----------------|
| `TradePosition` | Trade position |


<a id="positions.get_positions_by_symbol"></a>
### get_positions_by_symbol
```python
async def get_positions_by_symbol(self, *, symbol: str) -> tuple[TradePosition, ...]
```
Filter positions by symbols

#### Parameters:
| Name     | Type  | Description |
|----------|-------|-------------|
| `symbol` | `str` | Symbol      |

#### Returns:
| Type                        | Description    |
|-----------------------------|----------------|
| `tuple[TradePosition, ...]` | Trade position |


<a id="positions.close"></a>
### close
```python
async def close(self, *, ticket: int, symbol: str, price: float, volume: float, order_type: OrderType) -> OrderSendResult:
```
Close a position using its details.

#### Parameters:
| Name         | Type        | Description                |
|--------------|-------------|----------------------------|
| `ticket`     | `int`       | Position ticket.           |
| `symbol`     | `str`       | Financial instrument name. |
| `price`      | `float`     | Closing price.             |
| `volume`     | `float`     | Volume to close.           |
| `order_type` | `OrderType` | Order type.                |

#### Returns:
| Type               | Description                                        |
|--------------------|----------------------------------------------------|
| `OrderSendResult ` | The result of the order sent to close the position |


<a id="positions.close_position"></a>
### close_position
```python
async def close_position(self, *, position: TradePosition) -> OrderSendResult:
```
Close a position by position object.

#### Parameters:
| Name       | Type            | Description     |
|------------|-----------------|-----------------|
| `position` | `TradePosition` | Position object |

#### Returns:
| Type              | Description                                        |
|-------------------|----------------------------------------------------|
| `OrderSendResult` | The result of the order sent to close the position |


<a id='positions.close_position_by_ticket'></a>
### close_position_by_ticket
```python
async def close_position_by_ticket(self, *, position: TradePosition) -> OrderSendResult:
```
Close a position by position object.

#### Parameters:
| Name       | Type            | Description     |
|------------|-----------------|-----------------|
| `position` | `TradePosition` | Position object |

#### Returns:
| Type              | Description                                        |
|-------------------|----------------------------------------------------|
| `OrderSendResult` | The result of the order sent to close the position |


<a id="positions.close_all"></a>
### close_all
```python
async def close_all() -> int
```
Close all open positions for the trading account.

#### Returns:
| Type  | Description                          |
|-------|--------------------------------------|
| `int` | Return total number of closed trades |


<a id="positions.get_total_positions"></a>
### get_total_positions
```python
async def get_total_positions() -> int
```
Get the total number of open positions and set the `total_positions` attribute.

#### Returns:
| Type  | Description                          |
|-------|--------------------------------------|
| `int` | Return total number of open trades   |
