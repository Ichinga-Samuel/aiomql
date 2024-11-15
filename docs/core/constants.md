# Constants
MetaTrader 5 constants defined as Enums.

## Table of Contents
- [TradeAction](#TradeAction)
- [OrderFilling](#OrderFilling)
- [OrderTime](#OrderTime)
- [OrderType](#OrderType)
  - [opposite](#ordertype.opposite)
- [BookType](#BookType)
- [TimeFrame](#TimeFrame)
  - [get_timeframe](#timeframe.get_timeframe)
  - [seconds](#timeframe.seconds)
  - [all](#timeframe.all)
- [CopyTicks](#CopyTicks)
- [PositionType](#PositionType)
- [PositionReason](#PositionReason)
- [DealType](#DealType)
- [DealEntry](#DealEntry)
- [DealReason](#DealReason)
- [OrderReason](#OrderReason)
- [SymbolChartMode](#SymbolChartMode)
- [SymbolCalcMode](#SymbolCalcMode)
- [SymbolTradeMode](#SymbolTradeMode)
- [SymbolTradeExecution](#SymbolTradeExecution)
- [SymbolSwapMode](#SymbolSwapMode)
- [DayOfWeek](#DayOfWeek)
- [SymbolOrderGTCMode](#SymbolOrderGTCMode)
- [SymbolOptionRight](#SymbolOptionRight)
- [SymbolOptionMode](#SymbolOptionMode)
- [AccountTradeMode](#AccountTradeMode)
- [TickFlag](#TickFlag)
- [TradeRetcode](#TradeRetcode)
- [AccountStopOutMode](#AccountStopOutMode)
- [AccountMarginMode](#AccountMarginMode)

<a id="TradeAction"></a>
## TradeAction
```python
class TradeAction(Repr, IntEnum)
```
The TRADE_REQUEST_ACTION Enum.
### Members
| Name       | Value | Description                                                                                  |
|------------|-------|----------------------------------------------------------------------------------------------|
| `DEAL`     | 0     | Place a trade order for an immediate execution with the specified parameters (market order). |
| `PENDING`  | 1     | Place a pending order with the specified parameters.                                         |
| `SLTP`     | 2     | Modify Stop Loss and Take Profit values of an opened position.                               |
| `MODIFY`   | 3     | Modify the parameters of the order placed previously.                                        |
| `REMOVE`   | 4     | Delete the pending order placed previously.                                                  |
| `CLOSE_BY` | 5     | Close a position by an opposite one.                                                         |

<a id="OrderFilling"></a>
## OrderFilling
```python
class OrderFilling(Repr, IntEnum)
```
ORDER_TYPE_FILLING Enum.
### Members
| Name     | Value | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|----------|-------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `FILL`   | 0     | This execution policy means that an order can be executed only in the specified volume. If the necessary amount of a financial instrument is currently unavailable in the market, the order will not be executed. The desired volume can be made up of several available offers.                                                                                                                                                                                                                                                                                                                                |
| `FOK`    | 1     | This execution policy means that an order can be executed only in the specified volume. If the necessary amount of a financial instrument is currently unavailable in the market, the order will not be executed. The desired volume can be made up of several available offers.                                                                                                                                                                                                                                                                                                                                |
| `IOC`    | 2     | An agreement to execute a deal at the maximum volume available in the market within the volume specified in the order. If the request cannot be filled completely, an order with the available volume will be executed, and the remaining volume will be canceled.                                                                                                                                                                                                                                                                                                                                              |
| `RETURN` | 3     | This policy is used only for market (ORDER_TYPE_BUY and ORDER_TYPE_SELL), limit and stop limit orders (ORDER_TYPE_BUY_LIMIT, ORDER_TYPE_SELL_LIMIT,ORDER_TYPE_BUY_STOP_LIMIT and ORDER_TYPE_SELL_STOP_LIMIT) and only for the symbols with Market or Exchange execution modes. If filled partially, a market or limit order with the remaining volume is not canceled, and is processed further. During activation of the ORDER_TYPE_BUY_STOP_LIMIT and ORDER_TYPE_SELL_STOP_LIMIT orders, an appropriate limit order ORDER_TYPE_BUY_LIMIT/ORDER_TYPE_SELL_LIMIT with the ORDER_FILLING_RETURN type is created. |

<a id="OrderTime"></a>
## OrderTime
```python
class OrderTime(Repr, IntEnum)
```
ORDER_TIME Enum.
### Members
| Name            | Value | Description                                                                                                                                                            |
|-----------------|-------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `GTC`           | 0     | Good till cancel order                                                                                                                                                 |
| `DAY`           | 1     | Good till current trade day order                                                                                                                                      |
| `SPECIFIED`     | 2     | The order is active until the specified date                                                                                                                           |
| `SPECIFIED_DAY` | 3     | The order is active until 23:59:59 of the specified day. If this time appears to be out of a trading session, the expiration is processed at the nearest trading time. |

<a id="OrderType"></a>
## OrderType
```python
class OrderType(Repr, IntEnum)
```
ORDER_TYPE Enum.
### Members
| Name              | Value | Description                                                                          |
|-------------------|-------|--------------------------------------------------------------------------------------|
| `BUY`             | 0     | Market buy order                                                                     |
| `SELL`            | 1     | Market sell order                                                                    |
| `BUY_LIMIT`       | 2     | Buy Limit pending order                                                              |
| `SELL_LIMIT`      | 3     | Sell Limit pending order                                                             |
| `BUY_STOP`        | 4     | Buy Stop pending order                                                               |
| `SELL_STOP`       | 5     | Sell Stop pending order                                                              |
| `BUY_STOP_LIMIT`  | 6     | Upon reaching the order price, Buy Limit pending order is placed at StopLimit price  |
| `SELL_STOP_LIMIT` | 7     | Upon reaching the order price, Sell Limit pending order is placed at StopLimit price |
| `CLOSE_BY`        | 8     | Order for closing a position by an opposite one                                      |

### Properties
| Name       | Description                        |
|------------|------------------------------------|
| `opposite` | Gets the opposite of an order type |

<a id="ordertype.opposite"></a>
#### opposite
```python
@property
def opposite()
```
Gets the opposite of an order type for closing an open position
#### Returns
| Type | Description                          |
|------|--------------------------------------|
| int  | integer value of opposite order type |

<a id="BookType"></a>
## BookType
```python
class BookType(Repr, IntEnum)
```
BOOK_TYPE Enum.
### Members
| Name          | Value | Description          |
|---------------|-------|----------------------|
| `SELL`        | 0     | Sell order (Offer)   |
| `BUY`         | 1     | Buy order (Bid)      |
| `SELL_MARKET` | 2     | Sell order by Market |
| `BUY_MARKET`  | 3     | Buy order by Market  |

<a id="TimeFrame"></a>
## TimeFrame
```python
class TimeFrame(Repr, IntEnum)
```
TIMEFRAME Enum.
### Members
| Name  | Value   | Description     |
|-------|---------|-----------------|
| `M1`  | 60      | One Minute      |
| `M2`  | 120     | Two Minutes     |
| `M3`  | 180     | Three Minutes   |
| `M4`  | 240     | Four Minutes    |
| `M5`  | 300     | Five Minutes    |
| `M6`  | 360     | Six Minutes     |
| `M10` | 600     | Ten Minutes     |
| `M15` | 900     | Fifteen Minutes |
| `M20` | 1200    | Twenty Minutes  |
| `M30` | 1800    | Thirty Minutes  |
| `H1`  | 3600    | One Hour        |
| `H2`  | 7200    | Two Hours       |
| `H3`  | 10800   | Three Hours     |
| `H4`  | 14400   | Four Hours      |
| `H6`  | 21600   | Six Hours       |
| `H8`  | 28800   | Eight Hours     |
| `D1`  | 86400   | One Day         |
| `W1`  | 604800  | One Week        |
| `MN1` | 2592000 | One Month       |


<a id="timeframe.seconds"></a> 
### seconds
```python
@property
def seconds() -> int
```
The number of seconds in a TIMEFRAME


<a id="timeframe.get_timeframe"></a>
#### get_timeframe
```python
@property
def get_timeframe()
```
Get a timeframe object from a time value in seconds

#### Returns:
| Type      | Description                 |
|-----------|-----------------------------|
| TimeFrame | The corresponding timeframe |


<a id="timeframe.all"></a>
#### all
```python
@classmethod
def all()
```
Get all the timeframes

#### Returns:
| Type                  | Description                 |
|-----------------------|-----------------------------|
| tuple[TimeFrame, ...] | All the timeframes          |


<a id="CopyTicks"></a>
## CopyTicks
```python
class CopyTicks(Repr, IntEnum)
```
COPY_TICKS Enum. This defines the types of ticks that can be requested using the copy_ticks_from() and 
copy_ticks_range() functions.

### Members
| Name    | Value | Description                                       |
|---------|-------|---------------------------------------------------|
| `ALL`   | 0     | All ticks                                         |
| `INFO`  | 1     | Ticks containing Bid and/or Ask price changes     |
| `TRADE` | 2     | Ticks containing Last and/or Volume price changes |

<a id="PositionType"></a>
## PositionType
```python
class PositionType(Repr, IntEnum)
```
POSITION_TYPE Enum. Direction of an open position (buy or sell)
### Members
| Name   | Value | Description |
|--------|-------|-------------|
| `BUY`  | 0     | Buy         |
| `SELL` | 1     | Sell        |

<a id="PositionReason"></a>
## PositionReason
```python
class PositionReason(Repr, IntEnum)
```
POSITION_REASON Enum. The reason for opening a position is contained in the POSITION_REASON Enum
### Members
| Name     | Value | Description                                                                                    |
|----------|-------|------------------------------------------------------------------------------------------------|
| `CLIENT` | 0     | The position was opened as a result of activation of an order placed from a desktop terminal   |
| `MOBILE` | 1     | The position was opened as a result of activation of an order placed from a mobile application |
| `WEB`    | 2     | The position was opened as a result of activation of an order placed from the web platform     |
| `EXPERT` | 3     | The position was opened as a result of activation of an order placed from an MQL5 program      |

<a id="DealType"></a>
## DealType
```python
class DealType(Repr, IntEnum)
```
DEAL_TYPE enum. Each deal is characterized by a type, allowed values are enumerated in this enum
### Members
| Name                       | Value | Description                                                                                                                                                                                                                                                                                                                              |
|----------------------------|-------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `BUY`                      | 0     | Buy                                                                                                                                                                                                                                                                                                                                      |
| `SELL`                     | 1     | Sell                                                                                                                                                                                                                                                                                                                                     |
| `BALANCE`                  | 2     | Balance                                                                                                                                                                                                                                                                                                                                  |
| `CREDIT`                   | 3     | Credit                                                                                                                                                                                                                                                                                                                                   |
| `CHARGE`                   | 4     | Additional Charge                                                                                                                                                                                                                                                                                                                        |
| `CORRECTION`               | 5     | Correction                                                                                                                                                                                                                                                                                                                               |
| `BONUS`                    | 6     | Bonus                                                                                                                                                                                                                                                                                                                                    |
| `COMMISSION`               | 7     | Additional Commission                                                                                                                                                                                                                                                                                                                    |
| `COMMISSION_DAILY`         | 8     | Daily Commission                                                                                                                                                                                                                                                                                                                         |
| `COMMISSION_MONTHLY`       | 9     | Monthly Commission                                                                                                                                                                                                                                                                                                                       |
| `COMMISSION_AGENT_DAILY`   | 10    | Daily Agent Commission                                                                                                                                                                                                                                                                                                                   |
| `COMMISSION_AGENT_MONTHLY` | 11    | Monthly Agent Commission                                                                                                                                                                                                                                                                                                                 |
| `INTEREST`                 | 12    | Interest Rate                                                                                                                                                                                                                                                                                                                            |
| `DEAL_DIVIDEND`            | 13    | Dividend Operations                                                                                                                                                                                                                                                                                                                      |
| `DEAL_DIVIDEND_FRANKED`    | 14    | Franked (non-taxable) dividend operations                                                                                                                                                                                                                                                                                                |
| `DEAL_TAX`                 | 15    | Tax Charges                                                                                                                                                                                                                                                                                                                              |
| `BUY_CANCELED`             | 16    | Canceled buy deal. There can be a situation when a previously executed buy deal is canceled. In this case, the type of the previously executed deal (DEAL_TYPE_BUY) is changed to DEAL_TYPE_BUY_CANCELED, and its profit/loss is zeroized. Previously obtained profit/loss is charged/withdrawn using a separated balance operation      |
| `SELL_CANCELED`            | 17    | Canceled sell deal. There can be a situation when a previously executed sell deal is canceled. In this case, the type of the previously executed deal (DEAL_TYPE_SELL) is changed to DEAL_TYPE_SELL_CANCELED, and its profit/loss is zeroized. Previously obtained profit/loss is charged/withdrawn using a separated balance operation. |

<a id="DealEntry"></a>
## DealEntry
```python
class DealEntry(Repr, IntEnum)
```
DEAL_ENTRY Enum. Deals differ not only in their types set in DEAL_TYPE enum, but also in the way they change
positions. This can be a simple position opening, or accumulation of a previously opened position (market entering),
position closing by an opposite deal of a corresponding volume (market exiting), or position reversing, if the
opposite-direction deal covers the volume of the previously opened position.
### Members
| Name     | Value | Description                         |
|----------|-------|-------------------------------------|
| `IN`     | 0     | Entry In                            |
| `OUT`    | 1     | Entry Out                           |
| `INOUT`  | 2     | Reverse                             |
| `OUT_BY` | 3     | Close a position by an opposite one |

<a id="DealReason"></a>
## DealReason
```python
class DealReason(Repr, IntEnum)
```
DEAL_REASON Enum. The reason for deal execution is contained in the DEAL_REASON property. A deal can be executed
as a result of triggering of an order placed from a mobile application or an MQL5 program, as well as as a result
of the StopOut event, variation margin calculation, etc.
### Members
| Name       | Value | Description                                                                                                                    |
|------------|-------|--------------------------------------------------------------------------------------------------------------------------------|
| `CLIENT`   | 0     | The deal was executed as a result of activation of an order placed from a desktop terminal                                     |
| `MOBILE`   | 1     | The deal was executed as a result of activation of an order placed from a desktop terminal                                     |
| `WEB`      | 2     | The deal was executed as a result of activation of an order placed from the web platform                                       |
| `EXPERT`   | 3     | The deal was executed as a result of activation of an order placed from an MQL5 program, i.e. an Expert Advisor or a script    |
| `SL`       | 4     | The deal was executed as a result of Stop Loss activation                                                                      |
| `TP`       | 5     | The deal was executed as a result of Take Profit activation                                                                    |
| `SO`       | 6     | The deal was executed as a result of the Stop Out event                                                                        |
| `ROLLOVER` | 7     | The deal was executed due to a rollover                                                                                        |
| `VMARGIN`  | 8     | The deal was executed after charging the variation margin                                                                      |
| `SPLIT`    | 9     | The deal was executed after the split (price reduction) of an instrument, which had an open position during split announcement |

<a id="OrderReason"></a>
## OrderReason
```python
class OrderReason(Repr, IntEnum)
```
ORDER_REASON Enum.
### Members
| Name     | Value | Description                                                                      |
|----------|-------|----------------------------------------------------------------------------------|
| `CLIENT` | 0     | The order was placed from a desktop terminal                                     |
| `MOBILE` | 1     | The order was placed from a mobile application                                   |
| `WEB`    | 2     | The order was placed from a web platform                                         |
| `EXPERT` | 3     | The order was placed from an MQL5-program, i.e. by an Expert Advisor or a script |
| `SL`     | 4     | The order was placed as a result of Stop Loss activation                         |
| `TP`     | 5     | The order was placed as a result of Take Profit activation                       |
| `SO`     | 6     | The order was placed as a result of the Stop Out event                           |

<a id="SymbolChartMode"></a>
## SymbolChartMode
```python
class SymbolChartMode(Repr, IntEnum)
```
SYMBOL_CHART_MODE Enum. A symbol price chart can be based on Bid or Last prices. The price selected for symbol
charts also affects the generation and display of bars in the terminal.
Possible values of the SYMBOL_CHART_MODE property are described in this enum

### Members
| Name   | Value | Description                   |
|--------|-------|-------------------------------|
| `BID`  | 0     | Bars are based on Bid prices  |
| `LAST` | 1     | Bars are based on last prices |

<a id="SymbolCalcMode"></a>
## SymbolCalcMode
```python
class SymbolCalcMode(Repr, IntEnum)
```
SYMBOL_CALC_MODE Enum. The SYMBOL_CALC_MODE enumeration is used for obtaining information about how the margin
requirements for a symbol are calculated.
### Members
| Name                  | Value | Description                                                                                                                                                                                                                                                                                                                                                                                                      |
|-----------------------|-------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `FOREX`               | 0     | Forex mode - calculation of profit and margin for Forex                                                                                                                                                                                                                                                                                                                                                          |
| `FOREX_NO_LEVERAGE`   | 1     | Forex No Leverage mode – calculation of profit and margin for Forex symbols without taking into account the leverage                                                                                                                                                                                                                                                                                             |
| `FUTURES`             | 2     | Futures mode - calculation of margin and profit for futures                                                                                                                                                                                                                                                                                                                                                      |
| `CFD`                 | 3     | CFD mode - calculation of margin and profit for CFD                                                                                                                                                                                                                                                                                                                                                              |
| `CFDINDEX`            | 4     | CFD index mode - calculation of margin and profit for CFD by indexes                                                                                                                                                                                                                                                                                                                                             |
| `CFDLEVERAGE`         | 5     | CFD Leverage mode - calculation of margin and profit for CFD at leverage trading                                                                                                                                                                                                                                                                                                                                 |
| `EXCH_STOCKS`         | 6     | Calculation of margin and profit for trading securities on a stock exchange                                                                                                                                                                                                                                                                                                                                      |
| `EXCH_FUTURES`        | 7     | Calculation of margin and profit for trading futures contracts on a stock exchange                                                                                                                                                                                                                                                                                                                               |
| `EXCH_OPTIONS`        | 8     | value is 34                                                                                                                                                                                                                                                                                                                                                                                                      |
| `EXCH_OPTIONS_MARGIN` | 9     | value is 36                                                                                                                                                                                                                                                                                                                                                                                                      |
| `EXCH_BONDS`          | 10    | Exchange Bonds mode – calculation of margin and profit for trading bonds on a stock exchange                                                                                                                                                                                                                                                                                                                     |
| `EXCH_STOCKS_MOEX`    | 11    | Exchange MOEX Stocks mode –calculation of margin and profit for trading securities on MOEX                                                                                                                                                                                                                                                                                                                       |
| `EXCH_BONDS_MOEX`     | 12    | Exchange MOEX Bonds mode – calculation of margin and profit for trading bonds on MOEX                                                                                                                                                                                                                                                                                                                            |
| `SERV_COLLATERAL`     | 13    | Collateral mode - a symbol is used as a non-tradable asset on a trading account. The market value of an open position is calculated based on the volume, current market price, contract size and liquidity ratio. The value is included into Assets, which are added to Equity. Open positions of such symbols increase the Free Margin amount and are used as additional margin (collateral) for open positions |


<a id="SymbolTradeMode"></a>
## SymbolTradeMode
```python
class SymbolTradeMode(Repr, IntEnum)
```
SYMBOL_TRADE_MODE Enum. There are several symbol trading modes. Information about trading modes of a certain
symbol is reflected in the values this enumeration
### Members
| Name        | Value | Description                            |
|-------------|-------|----------------------------------------|
| `DISABLED`  | 0     | Trade is disabled for the symbol       |
| `LONGONLY`  | 1     | Allowed only long positions            |
| `SHORTONLY` | 2     | Allowed only short positions           |
| `CLOSEONLY` | 3     | Allowed only position close operations |
| `FULL`      | 4     | No trade restrictions                  |

<a id="SymbolTradeExecution"></a>
## SymbolTradeExecution
```python
class SymbolTradeExecution(Repr, IntEnum)
```
SYMBOL_TRADE_EXECUTION Enum. The modes, or execution policies, define the rules for cases when the price has
changed or the requested volume cannot be completely fulfilled at the moment.
### Members
| Name       | Value | Description                                                                                 |
|------------|-------|---------------------------------------------------------------------------------------------|
| `REQUEST`  | 0     | Executing a market order at the price previously received from the broker                   |
| `INSTANT`  | 1     | Executing a market order at the specified price immediately                                 |
| `MARKET`   | 2     | A broker makes a decision about the order execution price without any additional discussion |
| `EXCHANGE` | 3     | Trade operations are executed at the prices of the current market offers                    |

<a id="SymbolSwapMode"></a>
## SymbolSwapMode
```python
class SymbolSwapMode(Repr, IntEnum)
```
SYMBOL_SWAP_MODE Enum. Methods of swap calculation at position transfer are specified in enumeration
ENUM_SYMBOL_SWAP_MODE. The method of swap calculation determines the units of measure of the SYMBOL_SWAP_LONG and
SYMBOL_SWAP_SHORT parameters. For example, if swaps are charged in the client deposit currency, then the values of
those parameters are specified as an amount of money in the client deposit currency.
### Members
| Name               | Value | Description                                                                                                                                                                                                                       |
|--------------------|-------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `DISABLED`         | 0     | Swaps disabled (no swaps)                                                                                                                                                                                                         |
| `POINTS`           | 1     | Swaps are charged in points                                                                                                                                                                                                       |
| `CURRENCY_SYMBOL`  | 2     | Swaps are charged in money in base currency of the symbol                                                                                                                                                                         |
| `CURRENCY_MARGIN`  | 3     | Swaps are charged in money in margin currency of the symbol                                                                                                                                                                       |
| `CURRENCY_DEPOSIT` | 4     | Swaps are charged in money, in client deposit currency                                                                                                                                                                            |
| `INTEREST_CURRENT` | 5     | Swaps are charged as the specified annual interest from the instrument price at calculation of swap (standard bank year is 360 days)                                                                                              |
| `INTEREST_OPEN`    | 6     | Swaps are charged as the specified annual interest from the open price of position (standard bank year is 360 days)                                                                                                               |
| `REOPEN_CURRENT`   | 7     | Swaps are charged by reopening positions. At the end of a trading day the position is closed. Next day it is reopened by the close price +/- specified number of points (parameters SYMBOL_SWAP_LONG and SYMBOL_SWAP_SHORT)       |
| `REOPEN_BID`       | 8     | Swaps are charged by reopening positions. At the end of a trading day the position is closed. Next day it is reopened by the current Bid price +/- specified number of points (parameters SYMBOL_SWAP_LONG and SYMBOL_SWAP_SHORT) |

<a id="DayOfWeek"></a>
## DayOfWeek
```python
class DayOfWeek(Repr, IntEnum)
```
DAY_OF_WEEK Enum.
### Members
| Name        | Value | Description |
|-------------|-------|-------------|
| `SUNDAY`    | 0     | Sunday      |
| `MONDAY`    | 1     | Monday      |
| `TUESDAY`   | 2     | Tuesday     |
| `WEDNESDAY` | 3     | Wednesday   |
| `THURSDAY`  | 4     | Thursday    |
| `FRIDAY`    | 5     | Friday      |
| `SATURDAY`  | 6     | Saturday    |


<a id="SymbolOrderGTCMode"></a>
## SymbolOrderGTCMode
```python
class SymbolOrderGTCMode(Repr, IntEnum)
```
SYMBOL_ORDER_GTC_MODE Enum. If the SYMBOL_EXPIRATION_MODE property is set to SYMBOL_EXPIRATION_GTC
(good till canceled), the expiration of pending orders, as well as of
Stop Loss/Take Profit orders should be additionally set using the ENUM_SYMBOL_ORDER_GTC_MODE enumeration.
### Members
| Name             | Value | Description                                                                                                                                  |
|------------------|-------|----------------------------------------------------------------------------------------------------------------------------------------------|
| `GTC`            | 0     | Pending orders and Stop Loss/Take Profit levels are valid for an unlimited period                                                            |
| `DAILY`          | 1     | Orders are valid during one trading day. At the end of the day, all Stop Loss and Take Profit levels, as well as pending orders are deleted. |
| `DAILY_NO_STOPS` | 2     | When a trade day changes, only pending orders are deleted, while Stop Loss and Take Profit levels are preserved                              |

<a id="SymbolOptionRight"></a>
## SymbolOptionRight
```python
class SymbolOptionRight(Repr, IntEnum)
```
SYMBOL_OPTION_RIGHT Enum. An option is a contract, which gives the right, but not the obligation,
to buy or sell an underlying asset (goods, stocks, futures, etc.) at a specified price on or before a specific date.
The following enumerations describe option properties, including the option type and the right arising from it.
### Members
| Name   | Value | Description                                                                                   |
|--------|-------|-----------------------------------------------------------------------------------------------|
| `CALL` | 0     | A call option gives you the right to buy an asset at a specified price.                       |
| `PUT`  | 1     | A put option gives you the right to sell an asset at a specified price.                       |

<a id="SymbolOptionMode"></a>
## SymbolOptionMode
```python
class SymbolOptionMode(Repr, IntEnum)
```
SYMBOL_OPTION_MODE Enum.
### Members
| Name       | Value | Description                                                                                                                                        |
|------------|-------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| `EUROPEAN` | 0     | European option may only be exercised on a specified date (expiration, execution date, delivery date)                                              |
| `AMERICAN` | 1     | American option may be exercised on any trading day or before expiry. The period within which a buyer can exercise the option is specified for it. |

<a id="AccountTradeMode"></a>
## AccountTradeMode
```python
class AccountTradeMode(Repr, IntEnum)
```
ACCOUNT_TRADE_MODE Enum. There are several types of accounts that can be opened on a trade server.
The type of account on which an MQL5 program is running can be found out using
the ENUM_ACCOUNT_TRADE_MODE enumeration.
### Members
| Name      | Value | Description     |
|-----------|-------|-----------------|
| `DEMO`    | 0     | Demo account    |
| `CONTEST` | 1     | Contest account |
| `REAL`    | 2     | Real Account    |

<a id="TickFlag"></a>
## TickFlag
```python
class TickFlag(Repr, IntFlag)
```
TICK_FLAG Enum. TICK_FLAG defines possible flags for ticks. These flags are used to describe ticks obtained by the
copy_ticks_from() and copy_ticks_range() functions.
### Members
| Name     | Value | Description             |
|----------|-------|-------------------------|    
| `BID`    | 2     | Bid price changed       |
| `ASK`    | 4     | Ask price changed       |
| `LAST`   | 8     | Last price changed      |
| `VOLUME` | 16    | Volume changed          |
| `BUY`    | 32    | last Buy price changed  |
| `SELL`   | 64    | last Sell price changed |

<a id="TradeRetcode"></a>
## TradeRetcode
```python
class TradeRetcode(Repr, IntEnum)
```
TRADE_RETCODE Enum. Return codes for order send/check operations
### Members
| Name                   | Value | Description                                                                                                                                    |
|------------------------|-------|------------------------------------------------------------------------------------------------------------------------------------------------|
| `OK`                   | 10009 | OK                                                                                                                                             |
| `REQUOTE`              | 10004 | Requote                                                                                                                                        |
| `REJECT`               | 10006 | Reject                                                                                                                                         |
| `CANCEL`               | 10007 | Cancel                                                                                                                                         |
| `PLACED`               | 10008 | Placed                                                                                                                                         |
| `DONE`                 | 10009 | Done                                                                                                                                           |
| `DONE_PARTIAL`         | 10010 | Done Partial                                                                                                                                   |
| `ERROR`                | 10011 | Error                                                                                                                                          |
| `TIMEOUT`              | 10012 | Timeout                                                                                                                                        |
| `INVALID`              | 10013 | Invalid                                                                                                                                        |
| `INVALID_VOLUME`       | 10014 | Invalid Volume                                                                                                                                 |
| `INVALID_PRICE`        | 10015 | Invalid Price                                                                                                                                  |
| `INVALID_STOPS`        | 10016 | Invalid Stops                                                                                                                                  |
| `TRADE_DISABLED`       | 10017 | Trade is disabled                                                                                                                              |
| `MARKET_CLOSED`        | 10018 | Market is closed                                                                                                                               |
| `NO_MONEY`             | 10019 | No money                                                                                                                                       |
| `PRICE_CHANGED`        | 10020 | Price changed                                                                                                                                  |
| `PRICE_OFF`            | 10021 | Price off                                                                                                                                      |
| `INVALID_EXPIRATION`   | 10022 | Invalid expiration                                                                                                                             |
| `ORDER_CHANGED`        | 10023 | Order state changed                                                                                                                            |
| `TOO_MANY_REQUESTS`    | 10024 | Too frequent requests                                                                                                                          |
| `NO_CHANGES`           | 10025 | No changes in request                                                                                                                          |
| `SERVER_DISABLES_AT`   | 10026 | Autotrading disabled by server                                                                                                                 |
| `CLIENT_DISABLES_AT`   | 10027 | Autotrading disabled by client terminal                                                                                                        |
| `LOCKED`               | 10028 | Request locked for processing                                                                                                                  |
| `FROZEN`               | 10029 | Order or position frozen                                                                                                                       |
| `INVALID_FILL`         | 10030 | Invalid order filling type                                                                                                                     |
| `CONNECTION`           | 10031 | No connection with the trade server                                                                                                            |
| `ONLY_REAL`            | 10032 | Operation is allowed only for live accounts                                                                                                    |
| `LIMIT_ORDERS`         | 10033 | The number of pending orders has reached the limit                                                                                             |
| `LIMIT_VOLUME`         | 10034 | The volume of orders and positions for the symbol has reached the limit                                                                        |
| `INVALID_ORDER`        | 10035 | Incorrect or prohibited order type                                                                                                             |
| `POSITION_CLOSED`      | 10036 | Position with the specified POSITION_IDENTIFIER has already been closed                                                                        |
| `INVALID_CLOSE_VOLUME` | 10037 | A close volume exceeds the current position volume                                                                                             |
| `CLOSE_ORDER_EXIST`    | 10038 | A close order already exists for a specified position. This may happen when working in the hedging system                                      |
| `LIMIT_POSITIONS`      | 10039 | The number of open positions simultaneously present on an account can be limited by the server settings                                        |
| `REJECT_CANCEL`        | 10040 | The pending order activation request is rejected, the order is canceled                                                                        |
| `LONG_ONLY`            | 10041 | The request is rejected, because the "Only long positions are allowed" rule is set for the symbol (POSITION_TYPE_BUY)                          |
| `SHORT_ONLY`           | 10042 | The request is rejected, because the "Only short positions are allowed" rule is set for the symbol (POSITION_TYPE_SELL)                        |
| `CLOSE_ONLY`           | 10043 | The request is rejected, because the "Only position closing is allowed" rule is set for the symbol                                             |
| `FIFO_CLOSE`           | 10044 | The request is rejected, because "Position closing is allowed only by FIFO rule" flag is set for the trading account (ACCOUNT_FIFO_CLOSE=true) |

<a id="AccountStopOutMode"></a>
## AccountStopOutMode
```python
class AccountStopOutMode(Repr, IntEnum)
```
ACCOUNT_STOPOUT_MODE Enum.
### Members
| Name      | Value | Description                       |
|-----------|-------|-----------------------------------|
| `PERCENT` | 0     | Account stop out mode in percents |
| `MONEY`   | 1     | Account stop out mode in money    |

<a id="AccountMarginMode"></a>
## AccountMarginMode
```python
class AccountMarginMode(Repr, IntEnum)
```
ACCOUNT_MARGIN_MODE Enum.
### Members
| Name             | Value | Description                                                                                                                                                                                                                                                            |
|------------------|-------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `RETAIL_NETTING` | 0     | Used for the OTC markets to interpret positions in the "netting" mode (only one position can exist for one symbol). The margin is calculated based on the symbol type (SYMBOL_TRADE_CALC_MODE).                                                                        |    
| `EXCHANGE`       | 1     | Used for the exchange markets. Margin is calculated based on the discounts specified in symbol settings. Discounts are set by the broker, but not less than the values set by the exchange.                                                                            |
| `RETAIL_HEDGING` | 2     | Used for the exchange markets where individual positions are possible (hedging, multiple positions can exist for one symbol). The margin is calculated based on the symbol type (SYMBOL_TRADE_CALC_MODE) taking into account the hedged margin (SYMBOL_MARGIN_HEDGED). |
