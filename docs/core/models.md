# models

`aiomql.core.models` — Data models mirroring MetaTrader 5 structures.

## Overview

Defines data-model classes that correspond to the named-tuple structures returned by the
MetaTrader 5 terminal. All models inherit from [`Base`](base.md) and provide typed attributes,
dictionary conversion, and string representations.

## Classes

### `AccountInfo`

> Trading account information.

Key fields: `login`, `server`, `trade_mode`, `balance`, `leverage`, `profit`, `equity`,
`margin`, `margin_free`, `margin_level`, `currency`.

---

### `TerminalInfo`

> MetaTrader 5 terminal details.

Key fields: `connected`, `trade_allowed`, `tradeapi_disabled`, `build`, `company`,
`name`, `path`, `data_path`.

---

### `SymbolInfo`

> Trading instrument (symbol) properties.

Extensive attributes covering pricing, volume limits, spread, margin parameters, swap
settings, option properties, and session schedules.

| Method / Property | Description |
|-------------------|-------------|
| `__repr__()` | `"SymbolInfo(name=<name>)"` |
| `__str__()` | The symbol name |
| `__eq__(other)` | Equality by symbol name |
| `__hash__()` | Hash of the symbol name |

---

### `BookInfo`

> Market depth entry.

Fields: `type` (`BookType`), `price`, `volume`, `volume_dbl`.

---

### `TradeOrder`

> Pending or historical order.

Key fields: `ticket`, `type` (`OrderType`), `state`, `time_setup`, `volume_current`,
`volume_initial`, `price_open`, `sl`, `tp`, `symbol`, `comment`.

---

### `TradeRequest`

> Trade request structure sent to `order_send` / `order_check`.

Key fields: `action` (`TradeAction`), `type` (`OrderType`), `symbol`, `volume`,
`price`, `sl`, `tp`, `deviation`, `magic`, `comment`, `type_filling`, `type_time`.

---

### `OrderCheckResult`

> Result of `order_check`.

Key fields: `retcode`, `balance`, `equity`, `profit`, `margin`, `margin_free`,
`margin_level`, `request` (`TradeRequest`), `comment`.

| Method | Description |
|--------|-------------|
| `__init__(**kwargs)` | Converts `request` dict to `TradeRequest` |
| `__getstate__()` | Serialises `request` as a plain dict |
| `__setstate__(state)` | Restores `request` from dict |

---

### `OrderSendResult`

> Result of `order_send`.

Key fields: `retcode`, `deal`, `order`, `volume`, `price`, `bid`, `ask`,
`request` (`TradeRequest`), `comment`, `request_id`.

---

### `TradePosition`

> Open position information.

Key fields: `ticket`, `type` (`PositionType`), `symbol`, `volume`, `price_open`,
`price_current`, `sl`, `tp`, `profit`, `swap`, `magic`, `comment`.

---

### `TradeDeal`

> Completed deal record.

Key fields: `ticket`, `type` (`DealType`), `entry` (`DealEntry`), `symbol`, `volume`,
`price`, `profit`, `swap`, `commission`, `magic`, `comment`, `position_id`, `order`.
