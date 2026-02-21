# constants

`aiomql.core.constants` — MetaTrader 5 constants as Pythonic `IntEnum` types.

## Overview

Wraps every MT5 constant group into a typed Python enum. Each enum inherits from `Repr`
(which provides MT5-style `__str__`) and `IntEnum`, giving both type safety and integer
interoperability with the MT5 API.

## Classes

### `Repr`

> Mixin that formats enum values as `{__enum_name__}_{name}`.

---

### `TradeAction`

> Trade request actions (`TRADE_ACTION_*`).

| Member | Description |
|--------|-------------|
| `DEAL` | Immediate market order |
| `PENDING` | Conditional pending order |
| `SLTP` | Modify SL/TP of an open position |
| `MODIFY` | Modify a pending order |
| `REMOVE` | Delete a pending order |
| `CLOSE_BY` | Close by an opposite position |

---

### `OrderFilling`

> Order filling policies (`ORDER_FILLING_*`).

`FOK` · `IOC` · `RETURN`

---

### `OrderTime`

> Time-in-force policies (`ORDER_TIME_*`).

`GTC` · `DAY` · `SPECIFIED` · `SPECIFIED_DAY`

---

### `OrderType`

> Order types (`ORDER_TYPE_*`).

`BUY` · `SELL` · `BUY_LIMIT` · `SELL_LIMIT` · `BUY_STOP` · `SELL_STOP` · `BUY_STOP_LIMIT` · `SELL_STOP_LIMIT` · `CLOSE_BY`

**Properties:**

| Property | Returns |
|----------|---------|
| `opposite` | The opposite order type |
| `is_long` | `True` for buy-side types |
| `is_short` | `True` for sell-side types |

---

### `TimeFrame`

> Chart timeframes (`TIMEFRAME_*`).

`M1` · `M2` · `M3` · `M4` · `M5` · `M6` · `M10` · `M15` · `M20` · `M30` · `H1` · `H2` · `H3` · `H4` · `H6` · `H8` · `H12` · `D1` · `W1` · `MN1`

| Member / Method | Description |
|-----------------|-------------|
| `seconds` *(property)* | Duration in seconds (e.g. `H1.seconds` → `3600`) |
| `get_timeframe(time)` | Look up a `TimeFrame` from a duration in seconds |
| `all` | Tuple of all timeframes |

---

### `CopyTicks`

> Tick copy modes (`COPY_TICKS_*`).

`ALL` · `INFO` · `TRADE`

---

### `PositionType`

> Position direction (`POSITION_TYPE_*`).

`BUY` · `SELL`

---

### `PositionReason`

> Reason for opening a position (`POSITION_REASON_*`).

`CLIENT` · `MOBILE` · `WEB` · `EXPERT`

---

### `DealType`

> Deal types (`DEAL_TYPE_*`).

`BUY` · `SELL` · `BALANCE` · `CREDIT` · `CHARGE` · `CORRECTION` · `BONUS` · `COMMISSION` · `COMMISSION_DAILY` · `COMMISSION_MONTHLY` · `COMMISSION_AGENT_DAILY` · `COMMISSION_AGENT_MONTHLY` · `INTEREST` · `BUY_CANCELED` · `SELL_CANCELED` · `DEAL_DIVIDEND` · `DEAL_DIVIDEND_FRANKED` · `DEAL_TAX`

---

### `DealEntry`

> Deal entry direction (`DEAL_ENTRY_*`).

`IN` · `OUT` · `INOUT` · `OUT_BY`

---

### `DealReason`

> Reason for deal execution (`DEAL_REASON_*`).

`CLIENT` · `MOBILE` · `WEB` · `EXPERT` · `SL` · `TP` · `SO` · `ROLLOVER` · `VMARGIN` · `SPLIT`

---

### `OrderReason`

> Reason for placing an order (`ORDER_REASON_*`).

`CLIENT` · `MOBILE` · `WEB` · `EXPERT` · `SL` · `TP` · `SO`

---

### Other Enums

| Enum | Members |
|------|---------|
| `BookType` | `SELL`, `BUY`, `SELL_MARKET`, `BUY_MARKET` |
| `SymbolChartMode` | `BID`, `LAST` |
| `SymbolCalcMode` | `FOREX`, `FUTURES`, `CFD`, `CFDINDEX`, `CFDLEVERAGE`, … |
| `SymbolTradeMode` | `DISABLED`, `LONGONLY`, `SHORTONLY`, `CLOSEONLY`, `FULL` |
| `SymbolTradeExecution` | `REQUEST`, `INSTANT`, `MARKET`, `EXCHANGE` |
| `SymbolSwapMode` | `DISABLED`, `POINTS`, `CURRENCY_SYMBOL`, … |
| `DayOfWeek` | `SUNDAY` through `SATURDAY` |
| `SymbolOrderGTCMode` | `GTC`, `DAILY`, `DAILY_NO_STOPS` |
| `SymbolOptionRight` | `CALL`, `PUT` |
| `SymbolOptionMode` | `EUROPEAN`, `AMERICAN` |
| `AccountTradeMode` | `DEMO`, `CONTEST`, `REAL` |
| `AccountStopOutMode` | `PERCENT`, `MONEY` |
| `AccountMarginMode` | `RETAIL_NETTING`, `EXCHANGE`, `RETAIL_HEDGING` |
| `TickFlag` | `BID`, `ASK`, `LAST`, `VOLUME`, `BUY`, `SELL` |
| `TradeRetcode` | `REQUOTE`, `DONE`, `ERROR`, `TIMEOUT`, `INVALID`, … |
