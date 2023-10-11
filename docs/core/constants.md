# Table of Contents

* [aiomql.core.constants](#aiomql.core.constants)
  * [TradeAction](#aiomql.core.constants.TradeAction)
  * [OrderFilling](#aiomql.core.constants.OrderFilling)
  * [OrderTime](#aiomql.core.constants.OrderTime)
  * [OrderType](#aiomql.core.constants.OrderType)
    * [opposite](#aiomql.core.constants.OrderType.opposite)
  * [BookType](#aiomql.core.constants.BookType)
  * [TimeFrame](#aiomql.core.constants.TimeFrame)
    * [time](#aiomql.core.constants.TimeFrame.time)
  * [CopyTicks](#aiomql.core.constants.CopyTicks)
  * [PositionType](#aiomql.core.constants.PositionType)
  * [PositionReason](#aiomql.core.constants.PositionReason)
  * [DealType](#aiomql.core.constants.DealType)
  * [DealEntry](#aiomql.core.constants.DealEntry)
  * [DealReason](#aiomql.core.constants.DealReason)
  * [OrderReason](#aiomql.core.constants.OrderReason)
  * [SymbolChartMode](#aiomql.core.constants.SymbolChartMode)
  * [SymbolCalcMode](#aiomql.core.constants.SymbolCalcMode)
  * [SymbolTradeMode](#aiomql.core.constants.SymbolTradeMode)
  * [SymbolTradeExecution](#aiomql.core.constants.SymbolTradeExecution)
  * [SymbolSwapMode](#aiomql.core.constants.SymbolSwapMode)
  * [DayOfWeek](#aiomql.core.constants.DayOfWeek)
  * [SymbolOrderGTCMode](#aiomql.core.constants.SymbolOrderGTCMode)
  * [SymbolOptionRight](#aiomql.core.constants.SymbolOptionRight)
  * [SymbolOptionMode](#aiomql.core.constants.SymbolOptionMode)
  * [AccountTradeMode](#aiomql.core.constants.AccountTradeMode)
  * [TickFlag](#aiomql.core.constants.TickFlag)
  * [TradeRetcode](#aiomql.core.constants.TradeRetcode)
  * [AccountStopOutMode](#aiomql.core.constants.AccountStopOutMode)
  * [AccountMarginMode](#aiomql.core.constants.AccountMarginMode)

<a id="aiomql.core.constants"></a>

# aiomql.core.constants

<a id="aiomql.core.constants.TradeAction"></a>

## TradeAction Objects

```python
class TradeAction(Repr, IntEnum)
```

TRADE_REQUEST_ACTION Enum.

**Attributes**:

- `DEAL` _int_ - Delete the pending order placed previously Place a trade order for an immediate execution with the
  specified parameters (market order).
- `PENDING` _int_ - Delete the pending order placed previously
- `SLTP` _int_ - Modify Stop Loss and Take Profit values of an opened position
- `MODIFY` _int_ - Modify the parameters of the order placed previously
- `REMOVE` _int_ - Delete the pending order placed previously
- `CLOSE_BY` _int_ - Close a position by an opposite one

<a id="aiomql.core.constants.OrderFilling"></a>

## OrderFilling Objects

```python
class OrderFilling(Repr, IntEnum)
```

ORDER_TYPE_FILLING Enum.

**Attributes**:

- `FOK` _int_ - This execution policy means that an order can be executed only in the specified volume.
  If the necessary amount of a financial instrument is currently unavailable in the market, the order will
  not be executed. The desired volume can be made up of several available offers.
  
- `IOC` _int_ - An agreement to execute a deal at the maximum volume available in the market within the volume
  specified in the order. If the request cannot be filled completely, an order with the available volume will
  be executed, and the remaining volume will be canceled.
  
- `RETURN` _int_ - This policy is used only for market (ORDER_TYPE_BUY and ORDER_TYPE_SELL), limit and stop limit
  orders (ORDER_TYPE_BUY_LIMIT, ORDER_TYPE_SELL_LIMIT,ORDER_TYPE_BUY_STOP_LIMIT and
  ORDER_TYPE_SELL_STOP_LIMIT) and only for the symbols with Market or Exchange execution modes. If filled
  partially, a market or limit order with the remaining volume is not canceled, and is processed further.
  During activation of the ORDER_TYPE_BUY_STOP_LIMIT and ORDER_TYPE_SELL_STOP_LIMIT orders, an appropriate
  limit order ORDER_TYPE_BUY_LIMIT/ORDER_TYPE_SELL_LIMIT with the ORDER_FILLING_RETURN type is created.

<a id="aiomql.core.constants.OrderTime"></a>

## OrderTime Objects

```python
class OrderTime(Repr, IntEnum)
```

ORDER_TIME Enum.

**Attributes**:

- `GTC` _int_ - Good till cancel order
- `DAY` _int_ - Good till current trade day order
- `SPECIFIED` _int_ - The order is active until the specified date
- `SPECIFIED_DAY` _int_ - The order is active until 23:59:59 of the specified day. If this time appears to be out of
  a trading session, the expiration is processed at the nearest trading time.

<a id="aiomql.core.constants.OrderType"></a>

## OrderType Objects

```python
class OrderType(Repr, IntEnum)
```

ORDER_TYPE Enum.

**Attributes**:

- `BUY` _int_ - Market buy order
- `SELL` _int_ - Market sell order
- `BUY_LIMIT` _int_ - Buy Limit pending order
- `SELL_LIMIT` _int_ - Sell Limit pending order
- `BUY_STOP` _int_ - Buy Stop pending order
- `SELL_STOP` _int_ - Sell Stop pending order
- `BUY_STOP_LIMIT` _int_ - Upon reaching the order price, Buy Limit pending order is placed at StopLimit price
- `SELL_STOP_LIMIT` _int_ - Upon reaching the order price, Sell Limit pending order is placed at StopLimit price
- `CLOSE_BY` _int_ - Order for closing a position by an opposite one
  
  Properties:
- `opposite` _int_ - Gets the opposite of an order type

<a id="aiomql.core.constants.OrderType.opposite"></a>

#### opposite

```python
@property
def opposite()
```

Gets the opposite of an order type for closing an open position

**Returns**:

- `int` - integer value of opposite order type

<a id="aiomql.core.constants.BookType"></a>

## BookType Objects

```python
class BookType(Repr, IntEnum)
```

BOOK_TYPE Enum.

**Attributes**:

- `SELL` _int_ - Sell order (Offer)
- `BUY` _int_ - Buy order (Bid)
- `SELL_MARKET` _int_ - Sell order by Market
- `BUY_MARKET` _int_ - Buy order by Market

<a id="aiomql.core.constants.TimeFrame"></a>

## TimeFrame Objects

```python
class TimeFrame(Repr, IntEnum)
```

TIMEFRAME Enum.

**Attributes**:

- `M1` _int_ - One Minute
- `M2` _int_ - Two Minutes
- `M3` _int_ - Three Minutes
- `M4` _int_ - Four Minutes
- `M5` _int_ - Five Minutes
- `M6` _int_ - Six Minutes
- `M10` _int_ - Ten Minutes
- `M15` _int_ - Fifteen Minutes
- `M20` _int_ - Twenty Minutes
- `M30` _int_ - Thirty Minutes
- `H1` _int_ - One Hour
- `H2` _int_ - Two Hours
- `H3` _int_ - Three Hours
- `H4` _int_ - Four Hours
- `H6` _int_ - Six Hours
- `H8` _int_ - Eight Hours
- `D1` _int_ - One Day
- `W1` _int_ - One Week
- `MN1` _int_ - One Month
  
  Properties:
- `time` - return the value of the timeframe object in seconds. Used as a property
  

**Methods**:

- `get` - get a timeframe object from a time value in seconds

<a id="aiomql.core.constants.TimeFrame.time"></a>

#### time

```python
@property
def time()
```

The number of seconds in a TIMEFRAME

**Returns**:

- `int` - The number of seconds in a TIMEFRAME
  

**Examples**:

  >>> t = TimeFrame.H1
  >>> print(t.time)
  3600

<a id="aiomql.core.constants.CopyTicks"></a>

## CopyTicks Objects

```python
class CopyTicks(Repr, IntEnum)
```

COPY_TICKS Enum. This defines the types of ticks that can be requested using the copy_ticks_from() and
copy_ticks_range() functions.

**Attributes**:

- `ALL` _int_ - All ticks
- `INFO` _int_ - Ticks containing Bid and/or Ask price changes
- `TRADE` _int_ - Ticks containing Last and/or Volume price changes

<a id="aiomql.core.constants.PositionType"></a>

## PositionType Objects

```python
class PositionType(Repr, IntEnum)
```

POSITION_TYPE Enum. Direction of an open position (buy or sell)

**Attributes**:

- `BUY` _int_ - Buy
- `SELL` _int_ - Sell

<a id="aiomql.core.constants.PositionReason"></a>

## PositionReason Objects

```python
class PositionReason(Repr, IntEnum)
```

POSITION_REASON Enum. The reason for opening a position is contained in the POSITION_REASON Enum

**Attributes**:

- `CLIENT` _int_ - The position was opened as a result of activation of an order placed from a desktop terminal
- `MOBILE` _int_ - The position was opened as a result of activation of an order placed from a mobile application
- `WEB` _int_ - The position was opened as a result of activation of an order placed from the web platform
- `EXPERT` _int_ - The position was opened as a result of activation of an order placed from an MQL5 program,
  i.e. an Expert Advisor or a script

<a id="aiomql.core.constants.DealType"></a>

## DealType Objects

```python
class DealType(Repr, IntEnum)
```

DEAL_TYPE enum. Each deal is characterized by a type, allowed values are enumerated in this enum

**Attributes**:

- `BUY` _int_ - Buy
- `SELL` _int_ - Sell
- `BALANCE` _int_ - Balance
- `CREDIT` _int_ - Credit
- `CHARGE` _int_ - Additional Charge
- `CORRECTION` _int_ - Correction
- `BONUS` _int_ - Bonus
- `COMMISSION` _int_ - Additional Commission
- `COMMISSION_DAILY` _int_ - Daily Commission
- `COMMISSION_MONTHLY` _int_ - Monthly Commission
- `COMMISSION_AGENT_DAILY` _int_ - Daily Agent Commission
- `COMMISSION_AGENT_MONTHLY` _int_ - Monthly Agent Commission
- `INTEREST` _int_ - Interest Rate
- `DEAL_DIVIDEND` _int_ - Dividend Operations
- `DEAL_DIVIDEND_FRANKED` _int_ - Franked (non-taxable) dividend operations
- `DEAL_TAX` _int_ - Tax Charges
  
- `BUY_CANCELED` _int_ - Canceled buy deal. There can be a situation when a previously executed buy deal is canceled.
  In this case, the type of the previously executed deal (DEAL_TYPE_BUY) is changed to DEAL_TYPE_BUY_CANCELED,
  and its profit/loss is zeroized. Previously obtained profit/loss is charged/withdrawn using a separated
  balance operation
  
- `SELL_CANCELED` _int_ - Canceled sell deal. There can be a situation when a previously executed sell deal is
  canceled. In this case, the type of the previously executed deal (DEAL_TYPE_SELL) is changed to
  DEAL_TYPE_SELL_CANCELED, and its profit/loss is zeroized. Previously obtained profit/loss is
  charged/withdrawn using a separated balance operation.

<a id="aiomql.core.constants.DealEntry"></a>

## DealEntry Objects

```python
class DealEntry(Repr, IntEnum)
```

DEAL_ENTRY Enum. Deals differ not only in their types set in DEAL_TYPE enum, but also in the way they change
positions. This can be a simple position opening, or accumulation of a previously opened position (market entering),
position closing by an opposite deal of a corresponding volume (market exiting), or position reversing, if the
opposite-direction deal covers the volume of the previously opened position.

**Attributes**:

- `IN` _int_ - Entry In
- `OUT` _int_ - Entry Out
- `INOUT` _int_ - Reverse
- `OUT_BY` _int_ - Close a position by an opposite one

<a id="aiomql.core.constants.DealReason"></a>

## DealReason Objects

```python
class DealReason(Repr, IntEnum)
```

DEAL_REASON Enum. The reason for deal execution is contained in the DEAL_REASON property. A deal can be executed
as a result of triggering of an order placed from a mobile application or an MQL5 program, as well as as a result
of the StopOut event, variation margin calculation, etc.

**Attributes**:

- `CLIENT` _int_ - The deal was executed as a result of activation of an order placed from a desktop terminal
- `MOBILE` _int_ - The deal was executed as a result of activation of an order placed from a desktop terminal
- `WEB` _int_ - The deal was executed as a result of activation of an order placed from the web platform
- `EXPERT` _int_ - The deal was executed as a result of activation of an order placed from an MQL5 program, i.e.
  an Expert Advisor or a script
- `SL` _int_ - The deal was executed as a result of Stop Loss activation
- `TP` _int_ - The deal was executed as a result of Take Profit activation
- `SO` _int_ - The deal was executed as a result of the Stop Out event
- `ROLLOVER` _int_ - The deal was executed due to a rollover
- `VMARGIN` _int_ - The deal was executed after charging the variation margin
- `SPLIT` _int_ - The deal was executed after the split (price reduction) of an instrument, which had an open
  position during split announcement

<a id="aiomql.core.constants.OrderReason"></a>

## OrderReason Objects

```python
class OrderReason(Repr, IntEnum)
```

ORDER_REASON Enum.

**Attributes**:

- `CLIENT` _int_ - The order was placed from a desktop terminal
- `MOBILE` _int_ - The order was placed from a mobile application
- `WEB` _int_ - The order was placed from a web platform
- `EXPERT` _int_ - The order was placed from an MQL5-program, i.e. by an Expert Advisor or a script
- `SL` _int_ - The order was placed as a result of Stop Loss activation
- `TP` _int_ - The order was placed as a result of Take Profit activation
- `SO` _int_ - The order was placed as a result of the Stop Out event

<a id="aiomql.core.constants.SymbolChartMode"></a>

## SymbolChartMode Objects

```python
class SymbolChartMode(Repr, IntEnum)
```

SYMBOL_CHART_MODE Enum. A symbol price chart can be based on Bid or Last prices. The price selected for symbol
charts also affects the generation and display of bars in the terminal.
Possible values of the SYMBOL_CHART_MODE property are described in this enum

**Attributes**:

- `BID` _int_ - Bars are based on Bid prices
- `LAST` _int_ - Bars are based on last prices

<a id="aiomql.core.constants.SymbolCalcMode"></a>

## SymbolCalcMode Objects

```python
class SymbolCalcMode(Repr, IntEnum)
```

SYMBOL_CALC_MODE Enum. The SYMBOL_CALC_MODE enumeration is used for obtaining information about how the margin
requirements for a symbol are calculated.

**Attributes**:

- `FOREX` _int_ - Forex mode - calculation of profit and margin for Forex
- `FOREX_NO_LEVERAGE` _int_ - Forex No Leverage mode – calculation of profit and margin for Forex symbols without
  taking into account the leverage
- `FUTURES` _int_ - Futures mode - calculation of margin and profit for futures
- `CFD` _int_ - CFD mode - calculation of margin and profit for CFD
- `CFDINDEX` _int_ - CFD index mode - calculation of margin and profit for CFD by indexes
- `CFDLEVERAGE` _int_ - CFD Leverage mode - calculation of margin and profit for CFD at leverage trading
- `EXCH_STOCKS` _int_ - Calculation of margin and profit for trading securities on a stock exchange
- `EXCH_FUTURES` _int_ - Calculation of margin and profit for trading futures contracts on a stock exchange
- `EXCH_OPTIONS` _int_ - value is 34
- `EXCH_OPTIONS_MARGIN` _int_ - value is 36
- `EXCH_BONDS` _int_ - Exchange Bonds mode – calculation of margin and profit for trading bonds on a stock exchange
- `STOCKS_MOEX` _int_ - Exchange MOEX Stocks mode –calculation of margin and profit for trading securities on MOEX
- `EXCH_BONDS_MOEX` _int_ - Exchange MOEX Bonds mode – calculation of margin and profit for trading bonds on MOEX
  
- `SERV_COLLATERAL` _int_ - Collateral mode - a symbol is used as a non-tradable asset on a trading account.
  The market value of an open position is calculated based on the volume, current market price, contract size
  and liquidity ratio. The value is included into Assets, which are added to Equity. Open positions of such
  symbols increase the Free Margin amount and are used as additional margin (collateral) for open positions

<a id="aiomql.core.constants.SymbolTradeMode"></a>

## SymbolTradeMode Objects

```python
class SymbolTradeMode(Repr, IntEnum)
```

SYMBOL_TRADE_MODE Enum. There are several symbol trading modes. Information about trading modes of a certain
symbol is reflected in the values this enumeration

**Attributes**:

- `DISABLED` _int_ - Trade is disabled for the symbol
- `LONGONLY` _int_ - Allowed only long positions
- `SHORTONLY` _int_ - Allowed only short positions
- `CLOSEONLY` _int_ - Allowed only position close operations
- `FULL` _int_ - No trade restrictions

<a id="aiomql.core.constants.SymbolTradeExecution"></a>

## SymbolTradeExecution Objects

```python
class SymbolTradeExecution(Repr, IntEnum)
```

SYMBOL_TRADE_EXECUTION Enum. The modes, or execution policies, define the rules for cases when the price has
changed or the requested volume cannot be completely fulfilled at the moment.

**Attributes**:

- `REQUEST` _int_ - Executing a market order at the price previously received from the broker. Prices for a certain
  market order are requested from the broker before the order is sent. Upon receiving the prices, order
  execution at the given price can be either confirmed or rejected.
  
- `INSTANT` _int_ - Executing a market order at the specified price immediately. When sending a trade request to be
  executed, the platform automatically adds the current prices to the order.
  - If the broker accepts the price, the order is executed.
  - If the broker does not accept the requested price, a "Requote" is sent — the broker returns prices,
  at which this order can be executed.
  
- `MARKET` _int_ - A broker makes a decision about the order execution price without any additional discussion with the trader.
  Sending the order in such a mode means advance consent to its execution at this price.
  
- `EXCHANGE` _int_ - Trade operations are executed at the prices of the current market offers.

<a id="aiomql.core.constants.SymbolSwapMode"></a>

## SymbolSwapMode Objects

```python
class SymbolSwapMode(Repr, IntEnum)
```

SYMBOL_SWAP_MODE Enum. Methods of swap calculation at position transfer are specified in enumeration
ENUM_SYMBOL_SWAP_MODE. The method of swap calculation determines the units of measure of the SYMBOL_SWAP_LONG and
SYMBOL_SWAP_SHORT parameters. For example, if swaps are charged in the client deposit currency, then the values of
those parameters are specified as an amount of money in the client deposit currency.

**Attributes**:

- `DISABLED` _int_ - Swaps disabled (no swaps)
- `POINTS` _int_ - Swaps are charged in points
- `CURRENCY_SYMBOL` _int_ - Swaps are charged in money in base currency of the symbol
- `CURRENCY_MARGIN` _int_ - Swaps are charged in money in margin currency of the symbol
- `CURRENCY_DEPOSIT` _int_ - Swaps are charged in money, in client deposit currency
  
- `INTEREST_CURRENT` _int_ - Swaps are charged as the specified annual interest from the instrument price at
  calculation of swap (standard bank year is 360 days)
  
- `INTEREST_OPEN` _int_ - Swaps are charged as the specified annual interest from the open price of position
  (standard bank year is 360 days)
  
- `REOPEN_CURRENT` _int_ - Swaps are charged by reopening positions. At the end of a trading day the position is
  closed. Next day it is reopened by the close price +/- specified number of points
  (parameters SYMBOL_SWAP_LONG and SYMBOL_SWAP_SHORT)
  
- `REOPEN_BID` _int_ - Swaps are charged by reopening positions. At the end of a trading day the position is closed.
  Next day it is reopened by the current Bid price +/- specified number of
  points (parameters SYMBOL_SWAP_LONG and SYMBOL_SWAP_SHORT)

<a id="aiomql.core.constants.DayOfWeek"></a>

## DayOfWeek Objects

```python
class DayOfWeek(Repr, IntEnum)
```

DAY_OF_WEEK Enum.

**Attributes**:

- `SUNDAY` _int_ - Sunday
- `MONDAY` _int_ - Monday
- `TUESDAY` _int_ - Tuesday
- `WEDNESDAY` _int_ - Wednesday
- `THURSDAY` _int_ - Thursday
- `FRIDAY` _int_ - Friday
- `SATURDAY` _int_ - Saturday

<a id="aiomql.core.constants.SymbolOrderGTCMode"></a>

## SymbolOrderGTCMode Objects

```python
class SymbolOrderGTCMode(Repr, IntEnum)
```

SYMBOL_ORDER_GTC_MODE Enum. If the SYMBOL_EXPIRATION_MODE property is set to SYMBOL_EXPIRATION_GTC
(good till canceled), the expiration of pending orders, as well as of
Stop Loss/Take Profit orders should be additionally set using the ENUM_SYMBOL_ORDER_GTC_MODE enumeration.

**Attributes**:

- `GTC` _int_ - Pending orders and Stop Loss/Take Profit levels are valid for an unlimited period
  until theirConstants, Enumerations and explicit cancellation
  
- `DAILY` _int_ - Orders are valid during one trading day. At the end of the day, all Stop Loss and
  Take Profit levels, as well as pending orders are deleted.
  
- `DAILY_NO_STOPS` _int_ - When a trade day changes, only pending orders are deleted,
  while Stop Loss and Take Profit levels are preserved

<a id="aiomql.core.constants.SymbolOptionRight"></a>

## SymbolOptionRight Objects

```python
class SymbolOptionRight(Repr, IntEnum)
```

SYMBOL_OPTION_RIGHT Enum. An option is a contract, which gives the right, but not the obligation,
to buy or sell an underlying asset (goods, stocks, futures, etc.) at a specified price on or before a specific date.
The following enumerations describe option properties, including the option type and the right arising from it.

**Attributes**:

- `CALL` _int_ - A call option gives you the right to buy an asset at a specified price.
- `PUT` _int_ - A put option gives you the right to sell an asset at a specified price.

<a id="aiomql.core.constants.SymbolOptionMode"></a>

## SymbolOptionMode Objects

```python
class SymbolOptionMode(Repr, IntEnum)
```

SYMBOL_OPTION_MODE Enum.

**Attributes**:

- `EUROPEAN` _int_ - European option may only be exercised on a specified date (expiration, execution date, delivery date)
- `AMERICAN` _int_ - American option may be exercised on any trading day or before expiry. The period within which
  a buyer can exercise the option is specified for it.

<a id="aiomql.core.constants.AccountTradeMode"></a>

## AccountTradeMode Objects

```python
class AccountTradeMode(Repr, IntEnum)
```

ACCOUNT_TRADE_MODE Enum. There are several types of accounts that can be opened on a trade server.
The type of account on which an MQL5 program is running can be found out using
the ENUM_ACCOUNT_TRADE_MODE enumeration.

**Attributes**:

- `DEMO` - Demo account
- `CONTEST` - Contest account
- `REAL` - Real Account

<a id="aiomql.core.constants.TickFlag"></a>

## TickFlag Objects

```python
class TickFlag(Repr, IntFlag)
```

TICK_FLAG Enum. TICK_FLAG defines possible flags for ticks. These flags are used to describe ticks obtained by the
copy_ticks_from() and copy_ticks_range() functions.

**Attributes**:

- `BID` _int_ - Bid price changed
- `ASK` _int_ - Ask price changed
- `LAST` _int_ - Last price changed
- `VOLUME` _int_ - Volume changed
- `BUY` _int_ - last Buy price changed
- `SELL` _int_ - last Sell price changed

<a id="aiomql.core.constants.TradeRetcode"></a>

## TradeRetcode Objects

```python
class TradeRetcode(Repr, IntEnum)
```

TRADE_RETCODE Enum. Return codes for order send/check operations

**Attributes**:

- `REQUOTE` _int_ - Requote
- `REJECT` _int_ - Request rejected
- `CANCEL` _int_ - Request canceled by trader
- `PLACED` _int_ - Order placed
- `DONE` _int_ - Request completed
- `DONE_PARTIAL` _int_ - Only part of the request was completed
- `ERROR` _int_ - Request processing error
- `TIMEOUT` _int_ - Request canceled by timeout
- `INVALID` _int_ - Invalid request
- `INVALID_VOLUME` _int_ - Invalid volume in the request
- `INVALID_PRICE` _int_ - Invalid price in the request
- `INVALID_STOPS` _int_ - Invalid stops in the request
- `TRADE_DISABLED` _int_ - Trade is disabled
- `MARKET_CLOSED` _int_ - Market is closed
- `NO_MONEY` _int_ - There is not enough money to complete the request
- `PRICE_CHANGED` _int_ - Prices changed
- `PRICE_OFF` _int_ - There are no quotes to process the request
- `INVALID_EXPIRATION` _int_ - Invalid order expiration date in the request
- `ORDER_CHANGED` _int_ - Order state changed
- `TOO_MANY_REQUESTS` _int_ - Too frequent requests
- `NO_CHANGES` _int_ - No changes in request
- `SERVER_DISABLES_AT` _int_ - Autotrading disabled by server
- `CLIENT_DISABLES_AT` _int_ - Autotrading disabled by client terminal
- `LOCKED` _int_ - Request locked for processing
- `FROZEN` _int_ - Order or position frozen
- `INVALID_FILL` _int_ - Invalid order filling type
- `CONNECTION` _int_ - No connection with the trade server
- `ONLY_REAL` _int_ - Operation is allowed only for live accounts
- `LIMIT_ORDERS` _int_ - The number of pending orders has reached the limit
- `LIMIT_VOLUME` _int_ - The volume of orders and positions for the symbol has reached the limit
- `INVALID_ORDER` _int_ - Incorrect or prohibited order type
- `POSITION_CLOSED` _int_ - Position with the specified POSITION_IDENTIFIER has already been closed
- `INVALID_CLOSE_VOLUME` _int_ - A close volume exceeds the current position volume
  
- `CLOSE_ORDER_EXIST` _int_ - A close order already exists for a specified position. This may happen when working in
  the hedging system:
  · when attempting to close a position with an opposite one, while close orders for the position already exist
  · when attempting to fully or partially close a position if the total volume of the already present close
  orders and the newly placed one exceeds the current position volume
  
- `LIMIT_POSITIONS` _int_ - The number of open positions simultaneously present on an account can be limited by the
  server settings.After a limit is reached, the server returns the TRADE_RETCODE_LIMIT_POSITIONS error when
  attempting to place an order. The limitation operates differently depending on the position accounting type:
  · Netting — number of open positions is considered. When a limit is reached, the platform does not let
  placing new orders whose execution may increase the number of open positions. In fact, the platform
  allows placing orders only for the symbols that already have open positions.
  The current pending orders are not considered since their execution may lead to changes in the current
  positions but it cannot increase their number.
  
  · Hedging — pending orders are considered together with open positions, since a pending order activation
  always leads to opening a new position. When a limit is reached, the platform does not allow placing
  both new market orders for opening positions and pending orders.
  
- `REJECT_CANCEL` _int_ - The pending order activation request is rejected, the order is canceled.
- `LONG_ONLY` _int_ - The request is rejected, because the "Only long positions are allowed" rule is set for the
  symbol (POSITION_TYPE_BUY)
- `SHORT_ONLY` _int_ - The request is rejected, because the "Only short positions are allowed" rule is set for the
  symbol (POSITION_TYPE_SELL)
- `CLOSE_ONLY` _int_ - The request is rejected, because the "Only position closing is allowed" rule is set for the
  symbol
- `FIFO_CLOSE` _int_ - The request is rejected, because "Position closing is allowed only by FIFO rule" flag is set
  for the trading account (ACCOUNT_FIFO_CLOSE=true)

<a id="aiomql.core.constants.AccountStopOutMode"></a>

## AccountStopOutMode Objects

```python
class AccountStopOutMode(Repr, IntEnum)
```

ACCOUNT_STOPOUT_MODE Enum.

**Attributes**:

- `PERCENT` _int_ - Account stop out mode in percents
- `MONEY` _int_ - Account stop out mode in money

<a id="aiomql.core.constants.AccountMarginMode"></a>

## AccountMarginMode Objects

```python
class AccountMarginMode(Repr, IntEnum)
```

ACCOUNT_MARGIN_MODE Enum.

**Attributes**:

- `RETAIL_NETTING` _int_ - Used for the OTC markets to interpret positions in the "netting"
  mode (only one position can exist for one symbol). The margin is calculated based on the symbol
  type (SYMBOL_TRADE_CALC_MODE).
  
- `EXCHANGE` _int_ - Used for the exchange markets. Margin is calculated based on the discounts specified in
  symbol settings. Discounts are set by the broker, but not less than the values set by the exchange.
  
- `HEDGING` _int_ - Used for the exchange markets where individual positions are possible
  (hedging, multiple positions can exist for one symbol). The margin is calculated based on the symbol
  type (SYMBOL_TRADE_CALC_MODE) taking into account the hedged margin (SYMBOL_MARGIN_HEDGED).

