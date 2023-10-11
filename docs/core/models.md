# Table of Contents

* [aiomql.core.models](#aiomql.core.models)
  * [AccountInfo](#aiomql.core.models.AccountInfo)
  * [TerminalInfo](#aiomql.core.models.TerminalInfo)
  * [SymbolInfo](#aiomql.core.models.SymbolInfo)
  * [BookInfo](#aiomql.core.models.BookInfo)
  * [TradeOrder](#aiomql.core.models.TradeOrder)
  * [TradeRequest](#aiomql.core.models.TradeRequest)
  * [OrderCheckResult](#aiomql.core.models.OrderCheckResult)
  * [OrderSendResult](#aiomql.core.models.OrderSendResult)
  * [TradePosition](#aiomql.core.models.TradePosition)
  * [TradeDeal](#aiomql.core.models.TradeDeal)

<a id="aiomql.core.models"></a>

# aiomql.core.models

<a id="aiomql.core.models.AccountInfo"></a>

## AccountInfo Objects

```python
class AccountInfo(Base)
```

Account Information Class.

**Attributes**:

- `login` - int
- `password` - str
- `server` - str
- `trade_mode` - AccountTradeMode
- `balance` - float
- `leverage` - float
- `profit` - float
- `point` - float
- `amount` - float = 0
- `equity` - float
- `credit` - float
- `margin` - float
- `margin_level` - float
- `margin_free` - float
- `margin_mode` - AccountMarginMode
- `margin_so_mode` - AccountStopoutMode
- `margin_so_call` - float
- `margin_so_so` - float
- `margin_initial` - float
- `margin_maintenance` - float
- `fifo_close` - bool
- `limit_orders` - float
- `currency` - str = "USD"
- `trade_allowed` - bool = True
- `trade_expert` - bool = True
- `currency_digits` - int
- `assets` - float
- `liabilities` - float
- `commission_blocked` - float
- `name` - str
- `company` - str

<a id="aiomql.core.models.TerminalInfo"></a>

## TerminalInfo Objects

```python
class TerminalInfo(Base)
```

Terminal information class. Holds information about the terminal.

**Attributes**:

- `community_account` - bool
- `community_connection` - bool
- `connected` - bool
- `dlls_allowed` - bool
- `trade_allowed` - bool
- `tradeapi_disabled` - bool
- `email_enabled` - bool
- `ftp_enabled` - bool
- `notifications_enabled` - bool
- `mqid` - bool
- `build` - int
- `maxbars` - int
- `codepage` - int
- `ping_last` - int
- `community_balance` - float
- `retransmission` - float
- `company` - str
- `name` - str
- `language` - str
- `path` - str
- `data_path` - str
- `commondata_path` - str

<a id="aiomql.core.models.SymbolInfo"></a>

## SymbolInfo Objects

```python
class SymbolInfo(Base)
```

Symbol Information Class. Symbols are financial instruments available for trading in the MetaTrader 5 terminal.

**Attributes**:

- `name` - str
- `custom` - bool
- `chart_mode` - SymbolChartMode
- `select` - bool
- `visible` - bool
- `session_deals` - int
- `session_buy_orders` - int
- `session_sell_orders` - int
- `volume` - float
- `volumehigh` - float
- `volumelow` - float
- `time` - int
- `digits` - int
- `spread` - float
- `spread_float` - bool
- `ticks_bookdepth` - int
- `trade_calc_mode` - SymbolCalcMode
- `trade_mode` - SymbolTradeMode
- `start_time` - int
- `expiration_time` - int
- `trade_stops_level` - int
- `trade_freeze_level` - int
- `trade_exemode` - SymbolTradeExecution
- `swap_mode` - SymbolSwapMode
- `swap_rollover3days` - DayOfWeek
- `margin_hedged_use_leg` - bool
- `expiration_mode` - int
- `filling_mode` - int
- `order_mode` - int
- `order_gtc_mode` - SymbolOrderGTCMode
- `option_mode` - SymbolOptionMode
- `option_right` - SymbolOptionRight
- `bid` - float
- `bidhigh` - float
- `bidlow` - float
- `ask` - float
- `askhigh` - float
- `asklow` - float
- `last` - float
- `lasthigh` - float
- `lastlow` - float
- `volume_real` - float
- `volumehigh_real` - float
- `volumelow_real` - float
- `option_strike` - float
- `point` - float
- `trade_tick_value` - float
- `trade_tick_value_profit` - float
- `trade_tick_value_loss` - float
- `trade_tick_size` - float
- `trade_contract_size` - float
- `trade_accrued_interest` - float
- `trade_face_value` - float
- `trade_liquidity_rate` - float
- `volume_min` - float
- `volume_max` - float
- `volume_step` - float
- `volume_limit` - float
- `swap_long` - float
- `swap_short` - float
- `margin_initial` - float
- `margin_maintenance` - float
- `session_volume` - float
- `session_turnover` - float
- `session_interest` - float
- `session_buy_orders_volume` - float
- `session_sell_orders_volume` - float
- `session_open` - float
- `session_close` - float
- `session_aw` - float
- `session_price_settlement` - float
- `session_price_limit_min` - float
- `session_price_limit_max` - float
- `margin_hedged` - float
- `price_change` - float
- `price_volatility` - float
- `price_theoretical` - float
- `price_greeks_delta` - float
- `price_greeks_theta` - float
- `price_greeks_gamma` - float
- `price_greeks_vega` - float
- `price_greeks_rho` - float
- `price_greeks_omega` - float
- `price_sensitivity` - float
- `basis` - str
- `category` - str
- `currency_base` - str
- `currency_profit` - str
- `currency_margin` - Any
- `bank` - str
- `description` - str
- `exchange` - str
- `formula` - Any
- `isin` - Any
- `name` - str
- `page` - str
- `path` - str

<a id="aiomql.core.models.BookInfo"></a>

## BookInfo Objects

```python
class BookInfo(Base)
```

Book Information Class.

**Attributes**:

- `type` - BookType
- `price` - float
- `volume` - float
- `volume_dbl` - float

<a id="aiomql.core.models.TradeOrder"></a>

## TradeOrder Objects

```python
class TradeOrder(Base)
```

Trade Order Class.

**Attributes**:

- `ticket` - int
- `time_setup` - int
- `time_setup_msc` - int
- `time_expiration` - int
- `time_done` - int
- `time_done_msc` - int
- `type` - OrderType
- `type_time` - OrderTime
- `type_filling` - OrderFilling
- `state` - int
- `magic` - int
- `position_id` - int
- `position_by_id` - int
- `reason` - OrderReason
- `volume_current` - float
- `volume_initial` - float
- `price_open` - float
- `sl` - float
- `tp` - float
- `price_current` - float
- `price_stoplimit` - float
- `symbol` - str
- `comment` - str
- `external_id` - str

<a id="aiomql.core.models.TradeRequest"></a>

## TradeRequest Objects

```python
class TradeRequest(Base)
```

Trade Request Class.

**Attributes**:

- `action` - TradeAction
- `type` - OrderType
- `order` - int
- `symbol` - str
- `volume` - float
- `sl` - float
- `tp` - float
- `price` - float
- `deviation` - float
- `stop_limit` - float
- `type_time` - OrderTime
- `type_filling` - OrderFilling
- `expiration` - int
- `position` - int
- `position_by` - int
- `comment` - str
- `magic` - int
- `deviation` - int
- `comment` - str

<a id="aiomql.core.models.OrderCheckResult"></a>

## OrderCheckResult Objects

```python
class OrderCheckResult(Base)
```

Order Check Result

**Attributes**:

- `retcode` - int
- `balance` - float
- `equity` - float
- `profit` - float
- `margin` - float
- `margin_free` - float
- `margin_level` - float
- `comment` - str
- `request` - TradeRequest

<a id="aiomql.core.models.OrderSendResult"></a>

## OrderSendResult Objects

```python
class OrderSendResult(Base)
```

Order Send Result

**Attributes**:

- `retcode` - int
- `deal` - int
- `order` - int
- `volume` - float
- `price` - float
- `bid` - float
- `ask` - float
- `comment` - str
- `request` - TradeRequest
- `request_id` - int
- `retcode_external` - int
- `profit` - float

<a id="aiomql.core.models.TradePosition"></a>

## TradePosition Objects

```python
class TradePosition(Base)
```

Trade Position

**Attributes**:

- `ticket` - int
- `time` - int
- `time_msc` - int
- `time_update` - int
- `time_update_msc` - int
- `type` - OrderType
- `magic` - float
- `identifier` - int
- `reason` - PositionReason
- `volume` - float
- `price_open` - float
- `sl` - float
- `tp` - float
- `price_current` - float
- `swap` - float
- `profit` - float
- `symbol` - str
- `comment` - str
- `external_id` - str

<a id="aiomql.core.models.TradeDeal"></a>

## TradeDeal Objects

```python
class TradeDeal(Base)
```

Trade Deal

**Attributes**:

- `ticket` - int
- `order` - int
- `time` - int
- `time_msc` - int
- `type` - DealType
- `entry` - DealEntry
- `magic` - int
- `position_id` - int
- `reason` - DealReason
- `volume` - float
- `price` - float
- `commission` - float
- `swap` - float
- `profit` - float
- `fee` - float
- `sl` - float
- `tp` - float
- `symbol` - str
- `comment` - str
- `external_id` - str

