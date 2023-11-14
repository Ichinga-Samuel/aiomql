"""Trader class module. Handles the creation of an order and the placing of trades"""

from datetime import datetime
from typing import TypeVar
from logging import getLogger
from zoneinfo import ZoneInfo

from .order import Order
from .symbol import Symbol as _Symbol
from .ram import RAM
from .core.models import OrderType, OrderSendResult
from .core.config import Config
from .utils import dict_to_string
from .result import Result

logger = getLogger(__name__)
Symbol = TypeVar('Symbol', bound=_Symbol)


class Trader:
    """Base class for creating a Trader object. Handles the creation of an order and the placing of trades

    Attributes:
        symbol (Symbol): Financial instrument class Symbol class or any subclass of it.
        ram (RAM): RAM instance
        order (Order): Trade order

    Class Attributes:
        name (str): A name for the strategy.
        account (Account): Account instance.
        mt5 (MetaTrader): MetaTrader instance.
        config (Config): Config instance.
    """
    config = Config()

    def __init__(self, *, symbol: Symbol, ram: RAM = None):
        """Initializes the order object and RAM instance

        Args:
            symbol (Symbol): Financial instrument
            ram (RAM): Risk Assessment and Management instance
        """
        self.symbol = symbol
        self.order = Order(symbol=symbol.name)
        self.ram = ram or RAM()
        self.params = {}

    async def create_order(self, *, order_type: OrderType, **kwargs):
        """Complete the order object with the required values. Creates a simple order.

        Args:
            order_type (OrderType): Type of order
            kwargs: keyword arguments as required for the specific trader
        """
        points = kwargs.get('points', self.symbol.trade_stops_level+self.symbol.spread)
        self.order.volume = await self.symbol.compute_volume()
        self.order.type = order_type
        await self.set_trade_stop_levels(points=points)

    async def set_order_limits(self, pips: float):
        """Sets the stop loss and take profit for the order. This method uses pips as defined for forex instruments.

        Args:
            pips: Target pips
        """
        pips = pips * self.symbol.pip
        sl, tp = pips, pips * self.ram.risk_to_reward
        tick = await self.symbol.info_tick()
        if self.order.type == OrderType.BUY:
            self.order.sl, self.order.tp = tick.ask - sl, tick.ask + tp
            self.order.price = tick.ask
        elif self.order.type == OrderType.SELL:
            self.order.sl, self.order.tp = tick.bid + sl, tick.bid - tp
            self.order.price = tick.bid
        else:
            raise ValueError(f"Invalid order type: {self.order.type}")

    async def set_trade_stop_levels(self, *, points):
        """Set the stop loss and take profit levels of the order based on the points."""
        points = points * self.symbol.point
        sl, tp = points, points * self.ram.risk_to_reward
        tick = await self.symbol.info_tick()
        if self.order.type == OrderType.BUY:
            self.order.sl, self.order.tp = tick.ask - sl, tick.ask + tp
            self.order.price = tick.ask
        else:
            self.order.sl, self.order.tp = tick.bid + sl, tick.bid - tp
            self.order.price = tick.bid

    async def check_order(self) -> bool:
        """Check order before sending it to the broker.

        Returns:
            bool: True if order can go through else false
        """
        check = await self.order.check()
        if check.retcode != 0:
            logger.warning(
                f"Symbol: {self.order.symbol}\nResult:\n{dict_to_string(check.get_dict(include={'comment', 'retcode'}), multi=True)}")
            return False
        return True

    async def send_order(self):
        result = await self.order.send()
        if result.retcode != 10009:
            logger.warning(
                f"Symbol: {self.order.symbol}\nResult:\n{dict_to_string(result.get_dict(include={'comment', 'retcode'}), multi=True)}")
            return
        logger.info(f"Symbol: {self.order.symbol}\nOrder: {dict_to_string(result.dict, multi=True)}\n")
        await self.record_trade(result)

    async def record_trade(self, result: OrderSendResult):
        """
        Record the trade in a csv file.
        Args:
            result (OrderSendResult): Result of the order send
        """
        if result.retcode != 10009 or not self.config.record_trades:
            return
        profit = await self.order.calc_profit()
        params = self.params
        params['expected_profit'] = profit
        date = datetime.utcnow()
        date = date.replace(tzinfo=ZoneInfo('UTC'))
        params['date'] = date
        params['time'] = date.timestamp()
        res = Result(result=result, parameters=params)
        await res.save_csv()

    async def place_trade(self, order_type: OrderType, params: dict = None, **kwargs):
        """Places a trade based on the order_type.

        Args:
            order_type (OrderType): Type of order
            params: parameters of the trading strategy used to place the trade
            kwargs: keyword arguments as required for the specific trader
        """
        try:
            await self.create_order(order_type=order_type, **kwargs)
            if not await self.check_order():
                return
            self.params |= params or {}
            await self.send_order()
        except Exception as err:
            logger.error(f"{err}. Symbol: {self.order.symbol}\n {self.__class__.__name__}.place_trade")
