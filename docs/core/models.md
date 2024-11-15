# Models

This module contains the models used in the aiomql package. These models are used to represent the data returned from
the MetaTrader 5 terminal. They are all subclasses of the `Base` class.

## Table of Contents
- [AccountInfo](#models.account_info)
- [TerminalInfo](#models.terminal_info)
- [SymbolInfo](#models.symbol.info)
- [BookInfo](#models.book_info)
- [TradeOrder](#models.trade_order)
- [TradeRequest](#models_trade_request)
- [OrderCheckResult](#models.order_check_result)
- [OrderSendResult](#models.order_send_result)
- [TradePosition](#models.trade_position)
- [TradeDeal](#models.trade_deal)


<a id="models.account_info"></a>
### AccountInfo
```python
class AccountInfo(Base)
```
Account Information Class.
#### Attributes:
| Name                 | Type                 | Description                              | Default |
|----------------------|----------------------|------------------------------------------|---------|
| `login`              | `int`                | Account number                           |         |
| `password`           | `str`                | Account password                         |         |
| `server`             | `str`                | Trade server name                        |         |
| `trade_mode`         | AccountTradeMode     | Trade mode                               |         |
| `balance`            | `float`              | Account balance                          |         |
| `leverage`           | `float`              | Account leverage                         |         |
| `profit`             | `float`              | Account profit                           |         |
| `point`              | `float`              | Point size                               |         |
| `amount`             | `float`              | Account amount                           | 0       |
| `equity`             | `float`              | Account equity                           |         |
| `credit`             | `float`              | Account credit                           |         |
| `margin`             | `float`              | Account margin                           |         |
| `margin_level`       | `float`              | Margin level                             |         |
| `margin_free`        | `float`              | Free margin                              |         |
| `margin_mode`        | `AccountMarginMode`  | Margin calculation mode                  |         |
| `margin_so_mode`     | `AccountStopoutMode` | Stop out mode                            |         |
| `margin_so_call`     | `float`              | Margin call level                        |         |
| `margin_so_so`       | `float`              | Stop out level                           |         |
| `margin_initial`     | `float`              | Initial margin                           |         |
| `margin_maintenance` | `float`              | Maintenance margin                       |         |
| `fifo_close`         | `bool`               | FIFO close flag                          |         |
| `limit_orders`       | `float`              | Limit orders                             |         |
| `currency`           | `str`                | Account currency                         | "USD"   |
| `trade_allowed`      | `bool`               | Trade allowed flag                       | True    |
| `trade_expert`       | `bool`               | Trade expert flag                        | True    |
| `currency_digits`    | `int`                | Number of digits after the decimal point |         |
| `assets`             | `float`              | Assets                                   |         |
| `liabilities`        | `float`              | Liabilities                              |         |
| `commission_blocked` | `float`              | Blocked commission                       |         |
| `name`               | `str`                | Account name                             |         |
| `company`            | `str`                | Company name                             |         |


<a id="models.terminal_info"></a>
### TerminalInfo
```python
class TerminalInfo(Base)
```
Terminal information class. Holds information about the terminal.

#### Attributes:
| Name                    | Type    | Description                | Default |
|-------------------------|---------|----------------------------|---------|
| `community_account`     | `bool`  | Community account flag     |         |
| `community_connection`  | `bool`  | Community connection flag  |         |
| `connected`             | `bool`  | Connection flag            |         |
| `dlls_allowed`          | `bool`  | DLLs allowed flag          |         |
| `trade_allowed`         | `bool`  | Trade allowed flag         |         |
| `tradeapi_disabled`     | `bool`  | Trade API disabled flag    |         |
| `email_enabled`         | `bool`  | Email enabled flag         |         |
| `ftp_enabled`           | `bool`  | FTP enabled flag           |         |
| `notifications_enabled` | `bool`  | Notifications enabled flag |         |
| `mqid`                  | `bool`  | MQID                       |         |
| `build`                 | `int`   | Build number               |         |
| `maxbars`               | `int`   | Maximum number of bars     |         |
| `codepage`              | `int`   | Code page                  |         |
| `ping_last`             | `int`   | Last ping                  |         |
| `community_balance`     | `float` | Community balance          |         |
| `retransmission`        | `float` | Retransmission             |         |
| `company`               | `str`   | Company name               |         |
| `name`                  | `str`   | Terminal name              |         |
| `language`              | `str`   | Language                   |         |
| `path`                  | `str`   | Terminal path              |         |
| `data_path`             | `str`   | Data path                  |         |
| `commondata_path`       | `str`   | Common data path           |         |


<a id="models.symbol_info"></a>
### SymbolInfo
```python
class SymbolInfo(Base)
```
Symbol Information Class. Symbols are financial instruments available for trading in the MetaTrader 5 terminal.
#### Attributes:
| Name                         | Type                   | Description                | Default |
|------------------------------|------------------------|----------------------------|---------|
| `name`                       | `str`                  | Symbol name                |         |
| `custom`                     | `bool`                 | Custom symbol flag         |         |
| `chart_mode`                 | `SymbolChartMode`      | Chart mode                 |         |
| `select`                     | `bool`                 | Symbol selection flag      |         |
| `visible`                    | `bool`                 | Symbol visibility flag     |         |
| `session_deals`              | `int`                  | Session deals              |         |
| `session_buy_orders`         | `int`                  | Session buy orders         |         |
| `session_sell_orders`        | `int`                  | Session sell orders        |         |
| `volume`                     | `float`                | Volume                     |         |
| `volumehigh`                 | `float`                | Volume high                |         |
| `volumelow`                  | `float`                | Volume low                 |         |
| `time`                       | `int`                  | Time                       |         |
| `digits`                     | `int`                  | Digits                     |         |
| `spread`                     | `float`                | Spread                     |         |
| `spread_float`               | `bool`                 | Spread float flag          |         |
| `ticks_bookdepth`            | `int`                  | Ticks book depth           |         |
| `trade_calc_mode`            | `SymbolCalcMode`       | Trade calculation mode     |         |
| `trade_mode`                 | `SymbolTradeMode`      | Trade mode                 |         |
| `start_time`                 | `int`                  | Start time                 |         |
| `expiration_time`            | `int`                  | Expiration time            |         |
| `trade_stops_level`          | `int`                  | Trade stops level          |         |
| `trade_freeze_level`         | `int`                  | Trade freeze level         |         |
| `trade_exemode`              | `SymbolTradeExecution` | Trade execution mode       |         |
| `swap_mode`                  | `SymbolSwapMode`       | Swap mode                  |         |
| `swap_rollover3days`         | `DayOfWeek`            | Swap rollover 3 days       |         |
| `margin_hedged_use_leg`      | `bool`                 | Margin hedged use leg flag |         |
| `expiration_mode`            | `int`                  | Expiration mode            |         |
| `filling_mode`               | `int`                  | Filling mode               |         |
| `order_mode`                 | `int`                  | Order mode                 |         |
| `order_gtc_mode`             | `SymbolOrderGTCMode`   | Order GTC mode             |         |
| `option_mode`                | `SymbolOptionMode`     | Option mode                |         |
| `option_right`               | `SymbolOptionRight`    | Option right               |         |
| `bid`                        | `float`                | Bid                        |         |
| `bidhigh`                    | `float`                | Bid high                   |         |
| `bidlow`                     | `float`                | Bid low                    |         |
| `ask`                        | `float`                | Ask                        |         |
| `askhigh`                    | `float`                | Ask high                   |         |
| `asklow`                     | `float`                | Ask low                    |         |
| `last`                       | `float`                | Last                       |         |
| `lasthigh`                   | `float`                | Last high                  |         |
| `lastlow`                    | `float`                | Last low                   |         |
| `volume_real`                | `float`                | Volume real                |         |
| `volumehigh_real`            | `float`                | Volume high real           |         |
| `volumelow_real`             | `float`                | Volume low real            |         |
| `option_strike`              | `float`                | Option strike              |         |
| `point`                      | `float`                | Point                      |         |
| `trade_tick_value`           | `float`                | Trade tick value           |         |
| `trade_tick_value_profit`    | `float`                | Trade tick value profit    |         |
| `trade_tick_value_loss`      | `float`                | Trade tick value loss      |         |
| `trade_tick_size`            | `float`                | Trade tick size            |         |
| `trade_contract_size`        | `float`                | Trade contract size        |         |
| `trade_accrued_interest`     | `float`                | Trade accrued interest     |         |
| `trade_face_value`           | `float`                | Trade face value           |         |
| `trade_liquidity_rate`       | `float`                | Trade liquidity rate       |         |
| `volume_min`                 | `float`                | Volume min                 |         |
| `volume_max`                 | `float`                | Volume max                 |         |
| `volume_step`                | `float`                | Volume step                |         |
| `volume_limit`               | `float`                | Volume limit               |         |
| `swap_long`                  | `float`                | Swap long                  |         |
| `swap_short`                 | `float`                | Swap short                 |         |
| `margin_initial`             | `float`                | Initial margin             |         |
| `margin_maintenance`         | `float`                | Maintenance margin         |         |
| `session_volume`             | `float`                | Session volume             |         |
| `session_turnover`           | `float`                | Session turnover           |         |
| `session_interest`           | `float`                | Session interest           |         |
| `session_buy_orders_volume`  | `float`                | Session buy orders volume  |         |
| `session_sell_orders_volume` | `float`                | Session sell orders volume |         |
| `session_open`               | `float`                | Session open               |         |
| `session_close`              | `float`                | Session close              |         |
| `session_aw`                 | `float`                | Session AW                 |         |
| `session_price_settlement`   | `float`                | Session price settlement   |         |
| `session_price_limit_min`    | `float`                | Session price limit min    |         |
| `session_price_limit_max`    | `float`                | Session price limit max    |         |
| `margin_hedged`              | `float`                | Margin hedged              |         |
| `price_change`               | `float`                | Price change               |         |
| `price_volatility`           | `float`                | Price volatility           |         |
| `price_theoretical`          | `float`                | Price theoretical          |         |
| `price_greeks_delta`         | `float`                | Price greeks delta         |         |
| `price_greeks_theta`         | `float`                | Price greeks theta         |         |
| `price_greeks_gamma`         | `float`                | Price greeks gamma         |         |
| `price_greeks_vega`          | `float`                | Price greeks vega          |         |
| `price_greeks_rho`           | `float`                | Price greeks rho           |         |
| `price_greeks_omega`         | `float`                | Price greeks omega         |         |
| `price_sensitivity`          | `float`                | Price sensitivity          |         |
| `basis`                      | `str`                  | Basis                      |         |
| `category`                   | `str`                  | Category                   |         |
| `currency_base`              | `str`                  | Base currency              |         |
| `currency_profit`            | `str`                  | Profit currency            |         |
| `currency_margin`            | `Any`                  | Margin currency            |         |
| `bank`                       | `str`                  | Bank                       |         |
| `description`                | `str`                  | Description                |         |
| `exchange`                   | `str`                  | Exchange                   |         |
| `formula`                    | `Any`                  | Formula                    |         |
| `isin`                       | `Any`                  | ISIN                       |         |
| `name`                       | `str`                  | Name                       |         |
| `page`                       | `str`                  | Page                       |         |
| `path`                       | `str`                  | Path                       |         |


<a id="models.book_info"></a>
### BookInfo
```python
class BookInfo(Base)
```
Book Information Class.
#### Attributes:
| Name         | Type       | Description | Default |
|--------------|------------|-------------|---------|
| `symbol`     | `str`      | Symbol      |         |
| `type`       | `BookType` | Type        |         |
| `price`      | `float`    | Price       |         |
| `volume`     | `float`    | Volume      |         |
| `volume_dbl` | `float`    | Volume dbl  |         |


<a id="models.trade_order"></a>
#### TradeOrder
```python
class TradeOrder(Base)
```
Trade Order Class.

#### Attributes:
| Name              | Type           | Description     | Default |
|-------------------|----------------|-----------------|---------|
| `ticket`          | `int`          | Ticket          |         |
| `time_setup`      | `int`          | Time setup      |         |
| `time_setup_msc`  | `int`          | Time setup msc  |         |
| `time_expiration` | `int`          | Time expiration |         |
| `time_done`       | `int`          | Time done       |         |
| `time_done_msc`   | `int`          | Time done msc   |         |
| `type`            | `OrderType`    | Type            |         |
| `type_time`       | `OrderTime`    | Type time       |         |
| `type_filling`    | `OrderFilling` | Type filling    |         |
| `state`           | `int`          | State           |         |
| `magic`           | `int`          | Magic           |         |
| `position_id`     | `int`          | Position id     |         |
| `position_by_id`  | `int`          | Position by id  |         |
| `reason`          | `OrderReason`  | Reason          |         |
| `volume_current`  | `float`        | Volume current  |         |
| `volume_initial`  | `float`        | Volume initial  |         |
| `price_open`      | `float`        | Price open      |         |
| `sl`              | `float`        | SL              |         |
| `tp`              | `float`        | TP              |         |
| `price_current`   | `float`        | Price current   |         |
| `price_stoplimit` | `float`        | Price stoplimit |         |
| `symbol`          | `str`          | Symbol          |         |
| `comment`         | `str`          | Comment         |         |
| `external_id`     | `str`          | External id     |         |


<a id="models.trade_request"></a>
## TradeRequest
```python
class TradeRequest(Base)
```
Trade Request Class.
#### Attributes:
| Name           | Type         | Description  | Default |
|----------------|--------------|--------------|---------|
| `action`       | TradeAction  | Action       |         |
| `type`         | OrderType    | Type         |         |
| `order`        | `int`        | Order        |         |
| `symbol`       | `str`        | Symbol       |         |
| `volume`       | `float`      | Volume       |         |
| `sl`           | `float`      | SL           |         |
| `tp`           | `float`      | TP           |         |
| `price`        | `float`      | Price        |         |
| `deviation`    | `float`      | Deviation    |         |
| `stop_limit`   | `float`      | Stop limit   |         |
| `type_time`    | OrderTime    | Type time    |         |
| `type_filling` | OrderFilling | Type filling |         |
| `expiration`   | `int`        | Expiration   |         |
| `position`     | `int`        | Position     |         |
| `position_by`  | `int`        | Position by  |         |
| `comment`      | `str`        | Comment      |         |
| `magic`        | `int`        | Magic        |         |
| `deviation`    | `int`        | Deviation    |         |


<a id="models.order_check_result"></a>
### OrderCheckResult
```python
class OrderCheckResult(Base)
```
Order Check Result
#### Attributes:
| Name           | Type           | Description  | Default |
|----------------|----------------|--------------|---------|
| `retcode`      | `int`          | Retcode      |         |
| `balance`      | `float`        | Balance      |         |
| `equity`       | `float`        | Equity       |         |
| `profit`       | `float`        | Profit       |         |
| `margin`       | `float`        | Margin       |         |
| `margin_free`  | `float`        | Margin free  |         |
| `margin_level` | `float`        | Margin level |         |
| `comment`      | `str`          | Comment      |         |
| `request`      | `TradeRequest` | Request      |         |


<a id="models.order_send_result"></a>
### OrderSendResult
```python
class OrderSendResult(Base)
```
Order Send Result

#### Attributes:
| Name               | Type           | Description      | Default |
|--------------------|----------------|------------------|---------|
| `retcode`          | `int`          | Retcode          |         |
| `deal`             | `int`          | Deal             |         |
| `order`            | `int`          | Order            |         |
| `volume`           | `float`        | Volume           |         |
| `price`            | `float`        | Price            |         |
| `bid`              | `float`        | Bid              |         |
| `ask`              | `float`        | Ask              |         |
| `comment`          | `str`          | Comment          |         |
| `request`          | `TradeRequest` | Request          |         |
| `request_id`       | `int`          | Request id       |         |
| `retcode_external` | `int`          | Retcode external |         |
| `profit`           | `float`        | Profit           |         |


<a id="models.trade_position"></a>
### TradePosition
```python
class TradePosition(Base)
```
Trade Position
#### Attributes:
| Name              | Type             | Description     | Default |
|-------------------|------------------|-----------------|---------|
| `ticket`          | `int`            | Ticket          |         |
| `time`            | `int`            | Time            |         |
| `time_msc`        | `int`            | Time msc        |         |
| `time_update`     | `int`            | Time update     |         |
| `time_update_msc` | `int`            | Time update msc |         |
| `type`            | `OrderType`      | Type            |         |
| `magic`           | `float`          | Magic           |         |
| `identifier`      | `int`            | Identifier      |         |
| `reason`          | `PositionReason` | Reason          |         |
| `volume`          | `float`          | Volume          |         |
| `price_open`      | `float`          | Price open      |         |
| `sl`              | `float`          | SL              |         |
| `tp`              | `float`          | TP              |         |
| `price_current`   | `float`          | Price current   |         |
| `swap`            | `float`          | Swap            |         |
| `profit`          | `float`          | Profit          |         |
| `symbol`          | `str`            | Symbol          |         |
| `comment`         | `str`            | Comment         |         |
| `external_id`     | `str`            | External id     |         |


<a id="models.trade_deal"></a>
### TradeDeal
```python
class TradeDeal(Base)
```
Trade Deal
#### Attributes:
| Name          | Type         | Description | Default |
|---------------|--------------|-------------|---------|
| `ticket`      | `int`        | Ticket      |         |
| `order`       | `int`        | Order       |         |
| `time`        | `int`        | Time        |         |
| `time_msc`    | `int`        | Time msc    |         |
| `type`        | `DealType`   | Type        |         |
| `entry`       | `DealEntry`  | Entry       |         |
| `magic`       | `int`        | Magic       |         |
| `position_id` | `int`        | Position id |         |
| `reason`      | `DealReason` | Reason      |         |
| `volume`      | `float`      | Volume      |         |
| `price`       | `float`      | Price       |         |
| `commission`  | `float`      | Commission  |         |
| `swap`        | `float`      | Swap        |         |
| `profit`      | `float`      | Profit      |         |
| `fee`         | `float`      | Fee         |         |
| `sl`          | `float`      | SL          |         |
| `tp`          | `float`      | TP          |         |
| `symbol`      | `str`        | Symbol      |         |
| `comment`     | `str`        | Comment     |         |
| `external_id` | `str`        | External id |         |
