from enum import IntEnum, IntFlag

import MetaTrader5 as mt5

"""
MetaTrader5 constants as IntEnum types with Python style class names and nice string representation

Examples:
    >>> from aiomql import OrderFilling 
    >>> fok = OrderFilling.FOK
    >>> print(fok)
    "ORDER_FILLING_FOK"
"""


class Repr:
    __enum_name__ = ""

    def __str__(self):
        return f"{self.__enum_name__}_{self.name}"


class TradeAction(Repr, IntEnum):
    """TRADE_REQUEST_ACTION Enum.
    
    Attributes:
        DEAL (int): Delete the pending order placed previously Place a trade order for an immediate execution with the
            specified parameters (market order).
        PENDING (int): Delete the pending order placed previously
        SLTP (int): Modify Stop Loss and Take Profit values of an opened position
        MODIFY (int): Modify the parameters of the order placed previously
        REMOVE (int): Delete the pending order placed previously
        CLOSE_BY (int): Close a position by an opposite one 
    """
    __enum_name__ = "TRADE_ACTION"
    DEAL = mt5.TRADE_ACTION_DEAL
    PENDING = mt5.TRADE_ACTION_PENDING
    SLTP = mt5.TRADE_ACTION_SLTP
    MODIFY = mt5.TRADE_ACTION_MODIFY
    REMOVE = mt5.TRADE_ACTION_MODIFY
    CLOSE_BY = mt5.TRADE_ACTION_CLOSE_BY


class OrderFilling(Repr, IntEnum):
    """ORDER_TYPE_FILLING Enum.
    
    Attributes:
        FOK (int): This execution policy means that an order can be executed only in the specified volume.
            If the necessary amount of a financial instrument is currently unavailable in the market, the order will
            not be executed. The desired volume can be made up of several available offers.

        IOC (int): An agreement to execute a deal at the maximum volume available in the market within the volume
            specified in the order. If the request cannot be filled completely, an order with the available volume will
            be executed, and the remaining volume will be canceled.

        RETURN (int): This policy is used only for market (ORDER_TYPE_BUY and ORDER_TYPE_SELL), limit and stop limit
            orders (ORDER_TYPE_BUY_LIMIT, ORDER_TYPE_SELL_LIMIT,ORDER_TYPE_BUY_STOP_LIMIT and
            ORDER_TYPE_SELL_STOP_LIMIT) and only for the symbols with Market or Exchange execution modes. If filled
            partially, a market or limit order with the remaining volume is not canceled, and is processed further.
            During activation of the ORDER_TYPE_BUY_STOP_LIMIT and ORDER_TYPE_SELL_STOP_LIMIT orders, an appropriate
            limit order ORDER_TYPE_BUY_LIMIT/ORDER_TYPE_SELL_LIMIT with the ORDER_FILLING_RETURN type is created.
    """
    __enum_name__ = "ORDER_FILLING"
    FOK = mt5.ORDER_FILLING_FOK
    IOC = mt5.ORDER_FILLING_IOC
    RETURN = mt5.ORDER_FILLING_RETURN


class OrderTime(Repr, IntEnum):
    """ORDER_TIME Enum.
    
    Attributes:
        GTC (int): Good till cancel order 
        DAY (int): Good till current trade day order 
        SPECIFIED (int): The order is active until the specified date 
        SPECIFIED_DAY (int): The order is active until 23:59:59 of the specified day. If this time appears to be out of
            a trading session, the expiration is processed at the nearest trading time.
    """
    __enum_name__ = "ORDER_TIME"
    GTC = mt5.ORDER_TIME_GTC
    DAY = mt5.ORDER_TIME_DAY
    SPECIFIED = mt5.ORDER_TIME_SPECIFIED
    SPECIFIED_DAY = mt5.ORDER_TIME_SPECIFIED_DAY


class OrderType(Repr, IntEnum):
    """ORDER_TYPE Enum.
    
    Attributes:
        BUY (int): Market buy order 
        SELL (int): Market sell order 
        BUY_LIMIT (int): Buy Limit pending order 
        SELL_LIMIT (int): Sell Limit pending order 
        BUY_STOP (int): Buy Stop pending order 
        SELL_STOP (int): Sell Stop pending order 
        BUY_STOP_LIMIT (int): Upon reaching the order price, Buy Limit pending order is placed at StopLimit price 
        SELL_STOP_LIMIT (int): Upon reaching the order price, Sell Limit pending order is placed at StopLimit price 
        CLOSE_BY (int): Order for closing a position by an opposite one 

    Properties:
        opposite (int): Gets the opposite of an order type
    """
    __enum_name__ = "ORDER_TYPE"
    BUY = mt5.ORDER_TYPE_BUY
    SELL = mt5.ORDER_TYPE_SELL
    BUY_LIMIT = mt5.ORDER_TYPE_BUY_LIMIT
    SELL_LIMIT = mt5.ORDER_TYPE_SELL_LIMIT
    BUY_STOP = mt5.ORDER_TYPE_BUY_STOP
    SELL_STOP = mt5.ORDER_TYPE_SELL_STOP
    BUY_STOP_LIMIT = mt5.ORDER_TYPE_BUY_STOP_LIMIT
    SELL_STOP_LIMIT = mt5.ORDER_TYPE_SELL_STOP_LIMIT
    CLOSE_BY = mt5.ORDER_TYPE_CLOSE_BY

    @property
    def opposite(self):
        """Gets the opposite of an order type for closing an open position

        Returns:
            int: integer value of opposite order type
        """
        return {0: 1, 1: 0, 2: 3, 3: 2, 4: 5, 5: 4, 6: 7, 7: 6, 8: 8}[self]


class BookType(Repr, IntEnum):
    """BOOK_TYPE Enum.

    Attributes:
        SELL (int): Sell order (Offer) 
        BUY (int): Buy order (Bid) 
        SELL_MARKET (int): Sell order by Market 
        BUY_MARKET (int): Buy order by Market 
    """
    __enum_name__ = "BOOK_TYPE"
    SELL = mt5.BOOK_TYPE_SELL
    BUY = mt5.BOOK_TYPE_BUY
    SELL_MARKET = mt5.BOOK_TYPE_SELL_MARKET
    BUY_MARKET = mt5.BOOK_TYPE_BUY_MARKET


class TimeFrame(Repr, IntEnum):
    """TIMEFRAME Enum.

    Attributes:
        M1 (int): One Minute
        M2 (int): Two Minutes
        M3 (int): Three Minutes
        M4 (int): Four Minutes
        M5 (int): Five Minutes
        M6 (int): Six Minutes
        M10 (int): Ten Minutes
        M15 (int): Fifteen Minutes
        M20 (int): Twenty Minutes
        M30 (int): Thirty Minutes
        H1 (int): One Hour
        H2 (int): Two Hours
        H3 (int): Three Hours
        H4 (int): Four Hours
        H6 (int): Six Hours
        H8 (int): Eight Hours
        D1 (int): One Day
        W1 (int): One Week
        MN1 (int): One Month

    Properties:
        time: return the value of the timeframe object in seconds. Used as a property

    Methods:
        get: get a timeframe object from a time value in seconds
    """
    __enum_name__ = "TIMEFRAME"

    def __str__(self):
        return self.name

    M1 = mt5.TIMEFRAME_M1
    M2 = mt5.TIMEFRAME_M2
    M3 = mt5.TIMEFRAME_M3
    M4 = mt5.TIMEFRAME_M4
    M5 = mt5.TIMEFRAME_M5
    M6 = mt5.TIMEFRAME_M6
    M10 = mt5.TIMEFRAME_M10
    M15 = mt5.TIMEFRAME_M15
    M20 = mt5.TIMEFRAME_M20
    M30 = mt5.TIMEFRAME_M30
    H1 = mt5.TIMEFRAME_H1
    H2 = mt5.TIMEFRAME_H2
    H3 = mt5.TIMEFRAME_H3
    H4 = mt5.TIMEFRAME_H4
    H6 = mt5.TIMEFRAME_H6
    H8 = mt5.TIMEFRAME_H8
    H12 = mt5.TIMEFRAME_H12
    D1 = mt5.TIMEFRAME_D1
    W1 = mt5.TIMEFRAME_W1
    MN1 = mt5.TIMEFRAME_MN1

    @property
    def time(self):
        """The number of seconds in a TIMEFRAME

        Returns:
            int: The number of seconds in a TIMEFRAME

        Examples:
            >>> t = TimeFrame.H1
            >>> print(t.time)
            3600
        """
        times = {1: 60, 2: 120, 3: 180, 4: 240, 5: 300, 6: 360, 10: 600, 15: 900, 20: 1200, 30: 1800, 16385: 3600,
                 16386: 7200, 16387: 10800, 16388: 14400, 16390: 21600, 16392: 28800, 16396: 43200, 16408: 86400,
                 32769: 604800, 49153: 2592000}
        return times[self]

    @classmethod
    def get(cls, time: int):
        times = {60: 1, 120: 2, 180: 3, 240: 4, 300: 5, 360: 6, 600: 10, 900: 15, 1200: 20, 1800: 30, 3600: 16385,
                 7200: 16386, 10800: 16387, 14400: 16388, 21600: 16390, 28800: 16392, 43200: 16396, 86400: 16408,
                 604800: 32769, 2592000: 49153}
        return TimeFrame(times[int(time)])


class CopyTicks(Repr, IntEnum):
    """COPY_TICKS Enum. This defines the types of ticks that can be requested using the copy_ticks_from() and
    copy_ticks_range() functions.

    Attributes:
        ALL (int): All ticks 
        INFO (int): Ticks containing Bid and/or Ask price changes 
        TRADE (int): Ticks containing Last and/or Volume price changes 
    """
    __enum_name__ = "COPY_TICKS"
    ALL = mt5.COPY_TICKS_ALL
    INFO = mt5.COPY_TICKS_INFO
    TRADE = mt5.COPY_TICKS_TRADE


class PositionType(Repr, IntEnum):
    """POSITION_TYPE Enum. Direction of an open position (buy or sell)

    Attributes:
        BUY (int): Buy 
        SELL (int): Sell
    """
    __enum_name__ = "POSITION_TYPE"
    BUY = mt5.POSITION_TYPE_BUY
    SELL = mt5.POSITION_TYPE_SELL


class PositionReason(Repr, IntEnum):
    """POSITION_REASON Enum. The reason for opening a position is contained in the POSITION_REASON Enum

    Attributes:
       CLIENT (int): The position was opened as a result of activation of an order placed from a desktop terminal
       MOBILE (int): The position was opened as a result of activation of an order placed from a mobile application
       WEB (int): The position was opened as a result of activation of an order placed from the web platform
       EXPERT (int): The position was opened as a result of activation of an order placed from an MQL5 program,
           i.e. an Expert Advisor or a script
    """
    __enum_name__ = "POSITION_REASON"
    CLIENT = mt5.POSITION_REASON_CLIENT
    MOBILE = mt5.POSITION_REASON_MOBILE
    WEB = mt5.POSITION_REASON_WEB
    EXPERT = mt5.POSITION_REASON_EXPERT


class DealType(Repr, IntEnum):
    """DEAL_TYPE enum. Each deal is characterized by a type, allowed values are enumerated in this enum

    Attributes:
        BUY (int): Buy
        SELL (int): Sell
        BALANCE (int): Balance
        CREDIT (int): Credit
        CHARGE (int): Additional Charge
        CORRECTION (int): Correction
        BONUS (int): Bonus
        COMMISSION (int): Additional Commission
        COMMISSION_DAILY (int): Daily Commission
        COMMISSION_MONTHLY (int): Monthly Commission
        COMMISSION_AGENT_DAILY (int): Daily Agent Commission
        COMMISSION_AGENT_MONTHLY (int): Monthly Agent Commission
        INTEREST (int): Interest Rate
        DEAL_DIVIDEND (int): Dividend Operations
        DEAL_DIVIDEND_FRANKED (int): Franked (non-taxable) dividend operations
        DEAL_TAX (int): Tax Charges

        BUY_CANCELED (int): Canceled buy deal. There can be a situation when a previously executed buy deal is canceled.
            In this case, the type of the previously executed deal (DEAL_TYPE_BUY) is changed to DEAL_TYPE_BUY_CANCELED,
            and its profit/loss is zeroized. Previously obtained profit/loss is charged/withdrawn using a separated
            balance operation

        SELL_CANCELED (int): Canceled sell deal. There can be a situation when a previously executed sell deal is
            canceled. In this case, the type of the previously executed deal (DEAL_TYPE_SELL) is changed to
            DEAL_TYPE_SELL_CANCELED, and its profit/loss is zeroized. Previously obtained profit/loss is
            charged/withdrawn using a separated balance operation.
    """
    __enum_name__ = "DEAL_TYPE"
    BUY = mt5.DEAL_TYPE_BUY
    SELL = mt5.DEAL_TYPE_SELL
    BALANCE = mt5.DEAL_TYPE_BALANCE
    CREDIT = mt5.DEAL_TYPE_CREDIT
    CHARGE = mt5.DEAL_TYPE_CHARGE
    CORRECTION = mt5.DEAL_TYPE_CORRECTION
    BONUS = mt5.DEAL_TYPE_BONUS
    COMMISSION = mt5.DEAL_TYPE_COMMISSION
    COMMISSION_DAILY = mt5.DEAL_TYPE_COMMISSION_DAILY
    COMMISSION_MONTHLY = mt5.DEAL_TYPE_COMMISSION_MONTHLY
    COMMISSION_AGENT_DAILY = mt5.DEAL_TYPE_COMMISSION_AGENT_DAILY
    COMMISSION_AGENT_MONTHLY = mt5.DEAL_TYPE_COMMISSION_AGENT_MONTHLY
    INTEREST = mt5.DEAL_TYPE_INTEREST
    BUY_CANCELED = mt5.DEAL_TYPE_BUY_CANCELED
    SELL_CANCELED = mt5.DEAL_TYPE_SELL_CANCELED
    DEAL_DIVIDEND = mt5.DEAL_DIVIDEND
    DEAL_DIVIDEND_FRANKED = mt5.DEAL_DIVIDEND_FRANKED
    DEAL_TAX = mt5.DEAL_TAX

    def __str__(self):
        if self.name in ('DEAL_DIVIDEND', 'DEAL_DIVIDEND_FRANKED', 'DEAL_TAX'):
            return self.name
        return super().__str__()


class DealEntry(Repr, IntEnum):
    """DEAL_ENTRY Enum. Deals differ not only in their types set in DEAL_TYPE enum, but also in the way they change
    positions. This can be a simple position opening, or accumulation of a previously opened position (market entering),
    position closing by an opposite deal of a corresponding volume (market exiting), or position reversing, if the
    opposite-direction deal covers the volume of the previously opened position.

    Attributes:
        IN (int): Entry In
        OUT (int): Entry Out
        INOUT (int): Reverse
        OUT_BY (int): Close a position by an opposite one
    """
    __enum_name__ = "DEAL_ENTRY"
    IN = mt5.DEAL_ENTRY_IN
    OUT = mt5.DEAL_ENTRY_OUT
    INOUT = mt5.DEAL_ENTRY_INOUT
    OUT_BY = mt5.DEAL_ENTRY_OUT_BY


class DealReason(Repr, IntEnum):
    """DEAL_REASON Enum. The reason for deal execution is contained in the DEAL_REASON property. A deal can be executed
    as a result of triggering of an order placed from a mobile application or an MQL5 program, as well as as a result
    of the StopOut event, variation margin calculation, etc.

    Attributes:
        CLIENT (int): The deal was executed as a result of activation of an order placed from a desktop terminal
        MOBILE (int): The deal was executed as a result of activation of an order placed from a desktop terminal
        WEB (int): The deal was executed as a result of activation of an order placed from the web platform
        EXPERT (int): The deal was executed as a result of activation of an order placed from an MQL5 program, i.e.
            an Expert Advisor or a script
        SL (int): The deal was executed as a result of Stop Loss activation
        TP (int): The deal was executed as a result of Take Profit activation
        SO (int): The deal was executed as a result of the Stop Out event
        ROLLOVER (int): The deal was executed due to a rollover
        VMARGIN (int): The deal was executed after charging the variation margin
        SPLIT (int): The deal was executed after the split (price reduction) of an instrument, which had an open
            position during split announcement
    """
    __enum_name__ = "DEAL_REASON"
    CLIENT = mt5.DEAL_REASON_CLIENT
    MOBILE = mt5.DEAL_REASON_MOBILE
    WEB = mt5.DEAL_REASON_WEB
    EXPERT = mt5.DEAL_REASON_EXPERT
    SL = mt5.DEAL_REASON_SL
    TP = mt5.DEAL_REASON_TP
    SO = mt5.DEAL_REASON_SO
    ROLLOVER = mt5.DEAL_REASON_ROLLOVER
    VMARGIN = mt5.DEAL_REASON_VMARGIN
    SPLIT = mt5.DEAL_REASON_SPLIT


class OrderReason(Repr, IntEnum):
    """ORDER_REASON Enum.

    Attributes:
        CLIENT (int): The order was placed from a desktop terminal
        MOBILE (int): The order was placed from a mobile application
        WEB (int): The order was placed from a web platform
        EXPERT (int): The order was placed from an MQL5-program, i.e. by an Expert Advisor or a script
        SL (int): The order was placed as a result of Stop Loss activation
        TP (int): The order was placed as a result of Take Profit activation
        SO (int): The order was placed as a result of the Stop Out event
    """
    __enum_name__ = "ORDER_REASON"
    CLIENT = mt5.ORDER_REASON_CLIENT
    MOBILE = mt5.ORDER_REASON_MOBILE
    WEB = mt5.ORDER_REASON_WEB
    EXPERT = mt5.ORDER_REASON_EXPERT
    SL = mt5.ORDER_REASON_SL
    TP = mt5.ORDER_REASON_TP
    SO = mt5.ORDER_REASON_SO


class SymbolChartMode(Repr, IntEnum):
    """SYMBOL_CHART_MODE Enum. A symbol price chart can be based on Bid or Last prices. The price selected for symbol
    charts also affects the generation and display of bars in the terminal.
    Possible values of the SYMBOL_CHART_MODE property are described in this enum

    Attributes:
        BID (int): Bars are based on Bid prices
        LAST (int): Bars are based on last prices
    """
    __enum_name__ = "SYMBOL_CHART_MODE"
    BID = mt5.SYMBOL_CHART_MODE_BID
    LAST = mt5.SYMBOL_CHART_MODE_LAST


class SymbolCalcMode(Repr, IntEnum):
    """SYMBOL_CALC_MODE Enum. The SYMBOL_CALC_MODE enumeration is used for obtaining information about how the margin
    requirements for a symbol are calculated.

    Attributes:
        FOREX (int): Forex mode - calculation of profit and margin for Forex
        FOREX_NO_LEVERAGE (int): Forex No Leverage mode – calculation of profit and margin for Forex symbols without
            taking into account the leverage
        FUTURES (int): Futures mode - calculation of margin and profit for futures
        CFD (int): CFD mode - calculation of margin and profit for CFD
        CFDINDEX (int): CFD index mode - calculation of margin and profit for CFD by indexes
        CFDLEVERAGE (int): CFD Leverage mode - calculation of margin and profit for CFD at leverage trading
        EXCH_STOCKS (int): Calculation of margin and profit for trading securities on a stock exchange
        EXCH_FUTURES (int): Calculation of margin and profit for trading futures contracts on a stock exchange
        EXCH_OPTIONS (int): value is 34
        EXCH_OPTIONS_MARGIN (int): value is 36
        EXCH_BONDS (int): Exchange Bonds mode – calculation of margin and profit for trading bonds on a stock exchange
        STOCKS_MOEX (int): Exchange MOEX Stocks mode –calculation of margin and profit for trading securities on MOEX
        EXCH_BONDS_MOEX (int): Exchange MOEX Bonds mode – calculation of margin and profit for trading bonds on MOEX

        SERV_COLLATERAL (int): Collateral mode - a symbol is used as a non-tradable asset on a trading account.
            The market value of an open position is calculated based on the volume, current market price, contract size
            and liquidity ratio. The value is included into Assets, which are added to Equity. Open positions of such
            symbols increase the Free Margin amount and are used as additional margin (collateral) for open positions
    """
    __enum_name__ = "SYMBOL_CALC_MODE"
    FOREX = mt5.SYMBOL_CALC_MODE_FOREX
    FOREX_NO_LEVERAGE = mt5.SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE
    FUTURES = mt5.SYMBOL_CALC_MODE_FUTURES
    CFD = mt5.SYMBOL_CALC_MODE_CFD
    CFDINDEX = mt5.SYMBOL_CALC_MODE_CFDINDEX
    CFDLEVERAGE = mt5.SYMBOL_CALC_MODE_CFDLEVERAGE
    EXCH_STOCKS = mt5.SYMBOL_CALC_MODE_EXCH_STOCKS
    EXCH_FUTURES = mt5.SYMBOL_CALC_MODE_EXCH_FUTURES
    EXCH_OPTIONS = mt5.SYMBOL_CALC_MODE_EXCH_OPTIONS
    EXCH_OPTIONS_MARGIN = mt5.SYMBOL_CALC_MODE_EXCH_OPTIONS_MARGIN
    EXCH_BONDS = mt5.SYMBOL_CALC_MODE_EXCH_BONDS
    EXCH_STOCKS_MOEX = mt5.SYMBOL_CALC_MODE_EXCH_STOCKS_MOEX
    EXCH_BONDS_MOEX = mt5.SYMBOL_CALC_MODE_EXCH_BONDS_MOEX
    SERV_COLLATERAL = mt5.SYMBOL_CALC_MODE_SERV_COLLATERAL


class SymbolTradeMode(Repr, IntEnum):
    """SYMBOL_TRADE_MODE Enum. There are several symbol trading modes. Information about trading modes of a certain
    symbol is reflected in the values this enumeration

    Attributes:
        DISABLED (int): Trade is disabled for the symbol
        LONGONLY (int): Allowed only long positions
        SHORTONLY (int): Allowed only short positions
        CLOSEONLY (int): Allowed only position close operations
        FULL (int): No trade restrictions
    """

    __enum_name__ = "SYMBOL_TRADE_MODE"
    DISABLED = mt5.SYMBOL_TRADE_MODE_DISABLED
    LONGONLY = mt5.SYMBOL_TRADE_MODE_LONGONLY
    SHORTONLY = mt5.SYMBOL_TRADE_MODE_SHORTONLY
    CLOSEONLY = mt5.SYMBOL_TRADE_MODE_CLOSEONLY
    FULL = mt5.SYMBOL_TRADE_MODE_FULL


class SymbolTradeExecution(Repr, IntEnum):
    """SYMBOL_TRADE_EXECUTION Enum. The modes, or execution policies, define the rules for cases when the price has
    changed or the requested volume cannot be completely fulfilled at the moment.

    Attributes:
        REQUEST (int): Executing a market order at the price previously received from the broker. Prices for a certain
            market order are requested from the broker before the order is sent. Upon receiving the prices, order
            execution at the given price can be either confirmed or rejected.

        INSTANT (int): Executing a market order at the specified price immediately. When sending a trade request to be
            executed, the platform automatically adds the current prices to the order.
            - If the broker accepts the price, the order is executed.
            - If the broker does not accept the requested price, a "Requote" is sent — the broker returns prices,
            at which this order can be executed.

        MARKET (int): A broker makes a decision about the order execution price without any additional discussion with the trader.
            Sending the order in such a mode means advance consent to its execution at this price.

        EXCHANGE (int): Trade operations are executed at the prices of the current market offers.
    """

    __enum_name__ = "SYMBOL_TRADE_EXECUTION"
    REQUEST = mt5.SYMBOL_TRADE_EXECUTION_REQUEST
    INSTANT = mt5.SYMBOL_TRADE_EXECUTION_INSTANT
    MARKET = mt5.SYMBOL_TRADE_EXECUTION_MARKET
    EXCHANGE = mt5.SYMBOL_TRADE_EXECUTION_EXCHANGE


class SymbolSwapMode(Repr, IntEnum):
    """SYMBOL_SWAP_MODE Enum. Methods of swap calculation at position transfer are specified in enumeration
    ENUM_SYMBOL_SWAP_MODE. The method of swap calculation determines the units of measure of the SYMBOL_SWAP_LONG and
    SYMBOL_SWAP_SHORT parameters. For example, if swaps are charged in the client deposit currency, then the values of
    those parameters are specified as an amount of money in the client deposit currency.

    Attributes:
        DISABLED (int): Swaps disabled (no swaps)
        POINTS (int): Swaps are charged in points
        CURRENCY_SYMBOL (int): Swaps are charged in money in base currency of the symbol
        CURRENCY_MARGIN (int): Swaps are charged in money in margin currency of the symbol
        CURRENCY_DEPOSIT (int): Swaps are charged in money, in client deposit currency

        INTEREST_CURRENT (int): Swaps are charged as the specified annual interest from the instrument price at
            calculation of swap (standard bank year is 360 days)

        INTEREST_OPEN (int): Swaps are charged as the specified annual interest from the open price of position
            (standard bank year is 360 days)

        REOPEN_CURRENT (int): Swaps are charged by reopening positions. At the end of a trading day the position is
            closed. Next day it is reopened by the close price +/- specified number of points
            (parameters SYMBOL_SWAP_LONG and SYMBOL_SWAP_SHORT)

        REOPEN_BID (int): Swaps are charged by reopening positions. At the end of a trading day the position is closed.
            Next day it is reopened by the current Bid price +/- specified number of
            points (parameters SYMBOL_SWAP_LONG and SYMBOL_SWAP_SHORT)
    """
    __enum_name__ = "SYMBOL_SWAP_MODE"
    DISABLED = mt5.SYMBOL_SWAP_MODE_DISABLED
    POINTS = mt5.SYMBOL_SWAP_MODE_POINTS
    CURRENCY_SYMBOL = mt5.SYMBOL_SWAP_MODE_CURRENCY_SYMBOL
    CURRENCY_MARGIN = mt5.SYMBOL_SWAP_MODE_CURRENCY_MARGIN
    CURRENCY_DEPOSIT = mt5.SYMBOL_SWAP_MODE_CURRENCY_DEPOSIT
    INTEREST_CURRENT = mt5.SYMBOL_SWAP_MODE_INTEREST_CURRENT
    INTEREST_OPEN = mt5.SYMBOL_SWAP_MODE_INTEREST_OPEN
    REOPEN_CURRENT = mt5.SYMBOL_SWAP_MODE_REOPEN_CURRENT
    REOPEN_BID = mt5.SYMBOL_SWAP_MODE_REOPEN_BID


class DayOfWeek(Repr, IntEnum):
    """DAY_OF_WEEK Enum.

    Attributes:
        SUNDAY (int): Sunday
        MONDAY (int): Monday
        TUESDAY (int): Tuesday
        WEDNESDAY (int): Wednesday
        THURSDAY (int): Thursday
        FRIDAY (int): Friday
        SATURDAY (int): Saturday
    """
    __enum__name__ = "DAY_OF_WEEK"
    SUNDAY = mt5.DAY_OF_WEEK_SUNDAY
    MONDAY = mt5.DAY_OF_WEEK_MONDAY
    TUESDAY = mt5.DAY_OF_WEEK_TUESDAY
    WEDNESDAY = mt5.DAY_OF_WEEK_WEDNESDAY
    THURSDAY = mt5.DAY_OF_WEEK_THURSDAY
    FRIDAY = mt5.DAY_OF_WEEK_FRIDAY
    SATURDAY = mt5.DAY_OF_WEEK_SATURDAY


class SymbolOrderGTCMode(Repr, IntEnum):
    """SYMBOL_ORDER_GTC_MODE Enum. If the SYMBOL_EXPIRATION_MODE property is set to SYMBOL_EXPIRATION_GTC
        (good till canceled), the expiration of pending orders, as well as of
        Stop Loss/Take Profit orders should be additionally set using the ENUM_SYMBOL_ORDER_GTC_MODE enumeration.

    Attributes:
        GTC (int): Pending orders and Stop Loss/Take Profit levels are valid for an unlimited period
            until theirConstants, Enumerations and explicit cancellation

        DAILY (int): Orders are valid during one trading day. At the end of the day, all Stop Loss and
            Take Profit levels, as well as pending orders are deleted.

        DAILY_NO_STOPS (int): When a trade day changes, only pending orders are deleted,
            while Stop Loss and Take Profit levels are preserved
    """
    __enum_name__ = "SYMBOL_ORDERS"
    GTC = mt5.SYMBOL_ORDERS_GTC
    DAILY = mt5.SYMBOL_ORDERS_DAILY
    DAILY_NO_STOPS = mt5.SYMBOL_ORDERS_DAILY_NO_STOPS


class SymbolOptionRight(Repr, IntEnum):
    """SYMBOL_OPTION_RIGHT Enum. An option is a contract, which gives the right, but not the obligation,
    to buy or sell an underlying asset (goods, stocks, futures, etc.) at a specified price on or before a specific date.
    The following enumerations describe option properties, including the option type and the right arising from it.

    Attributes:
        CALL (int): A call option gives you the right to buy an asset at a specified price.
        PUT (int): A put option gives you the right to sell an asset at a specified price.
    """
    __enum_name__ = "SYMBOL_OPTION_RIGHT"
    CALL = mt5.SYMBOL_OPTION_RIGHT_CALL
    PUT = mt5.SYMBOL_OPTION_RIGHT_PUT


class SymbolOptionMode(Repr, IntEnum):
    """SYMBOL_OPTION_MODE Enum.

    Attributes:
        EUROPEAN (int): European option may only be exercised on a specified date (expiration, execution date, delivery date)
        AMERICAN (int): American option may be exercised on any trading day or before expiry. The period within which
        a buyer can exercise the option is specified for it.
    """
    __enum_name__ = "SYMBOL_OPTION_MODE"
    EUROPEAN = mt5.SYMBOL_OPTION_MODE_EUROPEAN
    AMERICAN = mt5.SYMBOL_OPTION_MODE_AMERICAN


class AccountTradeMode(Repr, IntEnum):
    """ACCOUNT_TRADE_MODE Enum. There are several types of accounts that can be opened on a trade server.
    The type of account on which an MQL5 program is running can be found out using
    the ENUM_ACCOUNT_TRADE_MODE enumeration.

    Attributes:
        DEMO: Demo account
        CONTEST: Contest account
        REAL: Real Account
    """
    __enum_name__ = "ACCOUNT_TRADE_MODE"
    DEMO = mt5.ACCOUNT_TRADE_MODE_DEMO
    CONTEST = mt5.ACCOUNT_TRADE_MODE_CONTEST
    REAL = mt5.ACCOUNT_TRADE_MODE_REAL


class TickFlag(Repr, IntFlag):
    """TICK_FLAG Enum. TICK_FLAG defines possible flags for ticks. These flags are used to describe ticks obtained by the
    copy_ticks_from() and copy_ticks_range() functions.

    Attributes:
        BID (int): Bid price changed
        ASK (int): Ask price changed
        LAST (int): Last price changed
        VOLUME (int): Volume changed
        BUY (int): last Buy price changed
        SELL (int): last Sell price changed
        """
    __enum_name__ = "TICK_FLAG"
    BID = mt5.TICK_FLAG_BID
    ASK = mt5.TICK_FLAG_ASK
    LAST = mt5.TICK_FLAG_LAST
    VOLUME = mt5.TICK_FLAG_VOLUME
    BUY = mt5.TICK_FLAG_BUY
    SELL = mt5.TICK_FLAG_SELL


class TradeRetcode(Repr, IntEnum):
    """TRADE_RETCODE Enum. Return codes for order send/check operations

    Attributes:
        REQUOTE (int): Requote
        REJECT (int): Request rejected
        CANCEL (int): Request canceled by trader
        PLACED (int): Order placed
        DONE (int): Request completed
        DONE_PARTIAL (int): Only part of the request was completed
        ERROR (int): Request processing error
        TIMEOUT (int): Request canceled by timeout
        INVALID (int): Invalid request
        INVALID_VOLUME (int): Invalid volume in the request
        INVALID_PRICE (int): Invalid price in the request
        INVALID_STOPS (int): Invalid stops in the request
        TRADE_DISABLED (int): Trade is disabled
        MARKET_CLOSED (int): Market is closed
        NO_MONEY (int): There is not enough money to complete the request
        PRICE_CHANGED (int): Prices changed
        PRICE_OFF (int): There are no quotes to process the request
        INVALID_EXPIRATION (int): Invalid order expiration date in the request
        ORDER_CHANGED (int): Order state changed
        TOO_MANY_REQUESTS (int): Too frequent requests
        NO_CHANGES (int): No changes in request
        SERVER_DISABLES_AT (int): Autotrading disabled by server
        CLIENT_DISABLES_AT (int): Autotrading disabled by client terminal
        LOCKED (int): Request locked for processing
        FROZEN (int): Order or position frozen
        INVALID_FILL (int): Invalid order filling type
        CONNECTION (int): No connection with the trade server
        ONLY_REAL (int): Operation is allowed only for live accounts
        LIMIT_ORDERS (int): The number of pending orders has reached the limit
        LIMIT_VOLUME (int): The volume of orders and positions for the symbol has reached the limit
        INVALID_ORDER (int): Incorrect or prohibited order type
        POSITION_CLOSED (int): Position with the specified POSITION_IDENTIFIER has already been closed
        INVALID_CLOSE_VOLUME (int): A close volume exceeds the current position volume

        CLOSE_ORDER_EXIST (int): A close order already exists for a specified position. This may happen when working in
            the hedging system:
            · when attempting to close a position with an opposite one, while close orders for the position already exist
            · when attempting to fully or partially close a position if the total volume of the already present close
                orders and the newly placed one exceeds the current position volume

        LIMIT_POSITIONS (int): The number of open positions simultaneously present on an account can be limited by the
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

        REJECT_CANCEL (int): The pending order activation request is rejected, the order is canceled.
        LONG_ONLY (int): The request is rejected, because the "Only long positions are allowed" rule is set for the
            symbol (POSITION_TYPE_BUY)
        SHORT_ONLY (int): The request is rejected, because the "Only short positions are allowed" rule is set for the
            symbol (POSITION_TYPE_SELL)
        CLOSE_ONLY (int): The request is rejected, because the "Only position closing is allowed" rule is set for the
            symbol
        FIFO_CLOSE (int): The request is rejected, because "Position closing is allowed only by FIFO rule" flag is set
            for the trading account (ACCOUNT_FIFO_CLOSE=true)
    """
    __enum_name__ = "TRADE_RETCODE"
    REQUOTE = mt5.TRADE_RETCODE_REQUOTE
    REJECT = mt5.TRADE_RETCODE_REJECT
    CANCEL = mt5.TRADE_RETCODE_CANCEL
    PLACED = mt5.TRADE_RETCODE_PLACED
    DONE = mt5.TRADE_RETCODE_DONE
    DONE_PARTIAL = mt5.TRADE_RETCODE_DONE_PARTIAL
    ERROR = mt5.TRADE_RETCODE_ERROR
    TIMEOUT = mt5.TRADE_RETCODE_TIMEOUT
    INVALID = mt5.TRADE_RETCODE_INVALID
    INVALID_VOLUME = mt5.TRADE_RETCODE_INVALID_VOLUME
    INVALID_PRICE = mt5.TRADE_RETCODE_INVALID_PRICE
    INVALID_STOPS = mt5.TRADE_RETCODE_INVALID_STOPS
    TRADE_DISABLED = mt5.TRADE_RETCODE_TRADE_DISABLED
    MARKET_CLOSED = mt5.TRADE_RETCODE_MARKET_CLOSED
    NO_MONEY = mt5.TRADE_RETCODE_NO_MONEY 
    PRICE_CHANGED = mt5.TRADE_RETCODE_PRICE_CHANGED
    PRICE_OFF = mt5.TRADE_RETCODE_PRICE_OFF
    INVALID_EXPIRATION = mt5.TRADE_RETCODE_INVALID_EXPIRATION
    ORDER_CHANGED = mt5.TRADE_RETCODE_ORDER_CHANGED
    TOO_MANY_REQUESTS = mt5.TRADE_RETCODE_TOO_MANY_REQUESTS
    NO_CHANGES = mt5.TRADE_RETCODE_NO_CHANGES
    SERVER_DISABLES_AT = mt5.TRADE_RETCODE_SERVER_DISABLES_AT
    CLIENT_DISABLES_AT = mt5.TRADE_RETCODE_CLIENT_DISABLES_AT
    LOCKED = mt5.TRADE_RETCODE_LOCKED
    FROZEN = mt5.TRADE_RETCODE_FROZEN
    INVALID_FILL = mt5.TRADE_RETCODE_INVALID_FILL
    CONNECTION = mt5.TRADE_RETCODE_CONNECTION
    ONLY_REAL = mt5.TRADE_RETCODE_ONLY_REAL
    LIMIT_ORDERS = mt5.TRADE_RETCODE_LIMIT_ORDERS
    LIMIT_VOLUME = mt5.TRADE_RETCODE_LIMIT_VOLUME
    INVALID_ORDER = mt5.TRADE_RETCODE_INVALID_ORDER
    POSITION_CLOSED = mt5.TRADE_RETCODE_POSITION_CLOSED
    INVALID_CLOSE_VOLUME = mt5.TRADE_RETCODE_INVALID_CLOSE_VOLUME
    CLOSE_ORDER_EXIST = mt5.TRADE_RETCODE_CLOSE_ORDER_EXIST
    LIMIT_POSITIONS = mt5.TRADE_RETCODE_LIMIT_POSITIONS
    REJECT_CANCEL = mt5.TRADE_RETCODE_REJECT_CANCEL
    LONG_ONLY = mt5.TRADE_RETCODE_LONG_ONLY
    SHORT_ONLY = mt5.TRADE_RETCODE_SHORT_ONLY
    CLOSE_ONLY = mt5.TRADE_RETCODE_CLOSE_ONLY
    FIFO_CLOSE = mt5.TRADE_RETCODE_FIFO_CLOSE
    

class AccountStopOutMode(Repr, IntEnum):
    """ACCOUNT_STOPOUT_MODE Enum.

    Attributes:
        PERCENT (int): Account stop out mode in percents
        MONEY (int): Account stop out mode in money
    """

    __enum_name__ = "ACCOUNT_STOPOUT_MODE"
    PERCENT = mt5.ACCOUNT_STOPOUT_MODE_PERCENT
    MONEY = mt5.ACCOUNT_STOPOUT_MODE_MONEY


class AccountMarginMode(Repr, IntEnum):
    """ACCOUNT_MARGIN_MODE Enum.

    Attributes:
        RETAIL_NETTING (int): Used for the OTC markets to interpret positions in the "netting"
            mode (only one position can exist for one symbol). The margin is calculated based on the symbol
            type (SYMBOL_TRADE_CALC_MODE).

        EXCHANGE (int): Used for the exchange markets. Margin is calculated based on the discounts specified in
            symbol settings. Discounts are set by the broker, but not less than the values set by the exchange.

        HEDGING (int): Used for the exchange markets where individual positions are possible
            (hedging, multiple positions can exist for one symbol). The margin is calculated based on the symbol
            type (SYMBOL_TRADE_CALC_MODE) taking into account the hedged margin (SYMBOL_MARGIN_HEDGED).
    """
    __enum_name__ = "ACCOUNT_MARGIN_MODE"
    RETAIL_NETTING = mt5.ACCOUNT_MARGIN_MODE_RETAIL_NETTING
    EXCHANGE = mt5.ACCOUNT_MARGIN_MODE_EXCHANGE
    RETAIL_HEDGING = mt5.ACCOUNT_MARGIN_MODE_RETAIL_HEDGING
