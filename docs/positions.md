## <a id="positions"></a> Positions

```python
class Positions
```
Get and handle Open positions.

**Attributes**:

|Name|Type|Description|Default|
|---|---|---|---|
|**symbol**|**str**|Financial instrument name.|""|
|**group**|**str**|The filter for arranging a group of necessary symbols. Optional named parameter. If the group is specified, the function returns only positions meeting a specified criteria for a symbol name.|""|
|**ticket**|**int**|Position ticket.|0|
|**mt5**|**MetaTrader**|MetaTrader instance.|None|

- `symbol` _str_ - Financial instrument name.
- `group` _str_ - The filter for arranging a group of necessary symbols. Optional named parameter.
  If the group is specified, the function returns only positions meeting a specified criteria for a symbol name.
- `ticket` _int_ - Position ticket.
- `mt5` _MetaTrader_ - MetaTrader instance.

<a id="positions.Positions.__init__"></a> #### \_\_init\_\_

```python
def __init__(*, symbol: str = "", group: str = "", ticket: int = 0)
```
Get Open Positions.

|Name|Type|Description|Default|
|---|---|---|---|
|**symbol**|**str**|Financial instrument name.|""|
|**group**|**str**|The filter for arranging a group of necessary symbols. Optional named parameter. If the group is specified, the function returns only positions meeting a specified criteria for a symbol name.|""|
|**ticket**|**int**|Position ticket.|0|

#### <a id="positions.Positions.positions_total"></a> positions_total
```python
async def positions_total() -> int
```
Get the number of open positions.

**Returns**:

|Type|Description|
|---|---|
|**int**|Return total number of open positions|

#### <a id="positions.Positions.positions_get"></a> positions_get

```python
async def positions_get()
```
Get open positions with the ability to filter by symbol or ticket.

**Returns**:

|Type|Description|
|---|---|
|**list[TradePosition]**|A list of open trade positions|




#### <a id="aiomql.positions.Positions.close_all"></a> close_all
```python
async def close_all() -> int
```
Close all open positions for the trading account.

**Returns**:
- `int` - Return number of positions closed.

