import asyncio
from datetime import datetime
from logging import getLogger

from pandas import DataFrame
import pandas as pd

from .core.config import Config
from .core.meta_trader import MetaTrader, CopyTicks, OrderType
from .core.models import TradeDeal, TradeOrder

logger = getLogger(__name__)


class History:
    """The history class handles completed trade deals and trade orders in the trading history of an account.

    Attributes:
        deals (list[TradeDeal]): Iterable of trade deals
        orders (list[TradeOrder]): Iterable of trade orders
        total_deals: Total number of deals
        total_orders (int): Total number orders
        group (str): Filter for selecting history by symbols.
        ticket (int): Filter for selecting history by ticket number
        position (int): Filter for selecting history deals by position
        initialized (bool): check if initial request has been sent to the terminal to get history.
        mt5 (MetaTrader): MetaTrader instance
        config (Config): Config instance
    """
    mt5: MetaTrader
    config: Config

    def __init__(self, *, date_from: datetime | int = None, date_to: datetime | int = None,
                 group: str = "", ticket: int = None, position: int = None):
        """
        Args:
            date_from (datetime, float): Date the orders are requested from. Set by the 'datetime' object or as a
                number of seconds elapsed since 1970.01.01. Defaults to twenty-four hours from the current time in 'utc'

            date_to (datetime, float): Date up to which the orders are requested. Set by the 'datetime' object or as a
                number of seconds elapsed since 1970.01.01. Defaults to the current time in "utc"

            group (str): Filter for selecting history by symbols.
            ticket (int): Filter for selecting history by ticket number
            position (int): Filter for selecting history deals by position
        """
        self.config = Config()
        self.mt5 = MetaTrader()
        self.date_from = date_from
        self.date_to = date_to
        self.group = group
        self.ticket = ticket
        self.position = position
        self.deals: list[TradeDeal] = []
        self.orders: list[TradeOrder] = []
        self.total_deals: int = 0
        self.total_orders: int = 0
        self.initialized = False

    async def init(self, deals=True, orders=True) -> bool:
        """Get history deals and orders

        Keyword Args:
            deals (bool): If true get history deals during initial request to terminal
            orders (bool): If true get history orders during initial request to terminal

        Returns:
            bool: True if all requests were successful else False
        """
        tasks = []
        tasks.append(self.get_deals()) if deals else ...
        tasks.append(self.get_orders()) if orders else ...
        res = await asyncio.gather(*tasks)
        self.initialized = all(res)
        return self.initialized

    async def get_deals(self, *, date_from: datetime | int = None, date_to: datetime | int = None, group: str = '',
                        retries: int = 3) -> tuple[TradeDeal, ...]:
        """Get deals from trading history using the parameters set in the constructor.

        Returns:
            tuple[TradeDeal]: A list of trade deals
        """
        if retries < 1:
            logger.warning(f'Failed to get deals: {self.mt5.error}')
            return tuple()

        date_from, date_to, group = date_from or self.date_from, date_to or self.date_to, group or self.group
        deals = await self.mt5.history_deals_get(date_from=date_from, date_to=date_to, group=group)

        if deals is not None:
            self.deals = tuple(TradeDeal(**deal._asdict()) for deal in deals)
            self.total_deals = len(self.deals)
            return self.deals

        if self.mt5.error.is_connection_error():
            await asyncio.sleep(retries)
            return await self.get_deals(date_from=date_from, date_to=date_to, group=group, retries=retries-1)

        logger.warning(f'Failed to get deals: {self.mt5.error}')
        return tuple()

    async def get_deals_ticket(self, *, ticket: int = None) -> tuple[TradeDeal, ...]:
        """Call specifying the order ticket. Return all deals having the specified order ticket in the DEAL_ORDER
        property.

        Args:
            ticket (int): The order ticket

        Returns:
            tuple[TradeDeal]: A tuple of all deals with the order ticket
        """
        ticket = ticket or self.ticket
        assert ticket is not None, 'ticket not provided'
        deals = await self.mt5.history_deals_get(ticket=ticket)
        return tuple(sorted([TradeDeal(**deal._asdict()) for deal in deals], key=lambda x: x.time_msc))

    async def get_deals_position(self, *, position: int = None) -> tuple[TradeDeal, ...]:
        """
        Get all deals with the specified position ticket in the DEAL_POSITION_ID property
        Args:
            position (int): The position ticket

        Returns:
            tuple[TradeDeal]: A tuple of all deals with the position ticket
        """
        position = position or self.position
        assert position is not None, 'position not provided'
        deals = await self.mt5.history_deals_get(position=position)
        return tuple(sorted([TradeDeal(**deal._asdict()) for deal in deals], key=lambda x: x.time_msc))

    async def deals_total(self, *, date_from: int | datetime = None, date_to: int | datetime = None) -> int:
        """Get total number of deals within the specified period in the constructor.
        Args:
            date_from (int|datetime): Date the orders are requested from. Set by the 'datetime' object or as a number of
                seconds elapsed since 1970.01.01.
            date_to (int|datetime): Date up to which the orders are requested. Set by the 'datetime' object or as a
                number of seconds elapsed since 1970.01.01.
        Returns:
            int: Total number of Deals
        """
        date_from, date_to = date_from or self.date_from, date_to or self.date_to
        assert date_from is not None and date_to is not None, 'date_from and/or date_to not provided'
        total_deals = await self.mt5.history_deals_total(date_from, date_to)
        return total_deals

    async def get_orders(self, *, date_from: datetime | int = None, date_to: datetime | int = None, group: str = '',
                         retries: int = 3) -> tuple[TradeOrder, ...]:
        """Get orders from trading history using the parameters set in the constructor or the method arguments.

        Returns:
            list[TradeOrder]: A list of trade orders
        """
        if retries < 1:
            logger.warning(f'Failed to get orders: {self.mt5.error}')
            return tuple()

        date_from, date_to, group = date_from or self.date_from, date_to or self.date_to, group or self.group
        orders = await self.mt5.history_orders_get(date_from=date_from, date_to=date_to, group=group)
        if orders is not None:
            return tuple(TradeOrder(**order._asdict()) for order in orders)

        if self.mt5.error.is_connection_error():
            await asyncio.sleep(retries)
            return await self.get_orders(date_from=date_from, date_to=date_to, group=group, retries=retries - 1)

        logger.warning(f'Failed to get orders: {self.mt5.error}')
        return tuple()

    async def get_order_ticket(self, ticket: int | None = None) -> TradeOrder:
        ticket = ticket or self.ticket
        assert isinstance(ticket, int), 'ticket not provided'
        orders = await self.mt5.history_orders_get(ticket=ticket)
        order = orders[0]
        assert order.ticket == ticket
        return TradeOrder(**order._asdict())

    async def get_orders_position(self, position: int = None) -> tuple[TradeOrder, ...]:
        """
        Call specifying the position ticket. Return all orders with a position ticket specified in the
        ORDER_POSITION_ID property

        Args:
            position: The position ticket

        Returns:
            tuple[TradeOrder]: A tuple of all orders with the position ticket
        """
        position = position or self.position
        assert isinstance(position, int), 'position not provided'
        orders = await self.mt5.history_orders_get(position=position)
        return tuple(sorted([TradeOrder(**order._asdict()) for order in orders], key=lambda x: x.time_done_msc))

    async def orders_total(self, date_from: int | datetime = None, date_to: int | datetime = None) -> int:
        """Get total number of orders within the specified period in the constructor.

        Returns:
            int: Total number of orders
        """
        date_from, date_to = date_from or self.date_from, date_to or self.date_to
        assert date_from is not None and date_to is not None, 'date_from and/or date_to not provided'
        total_orders = await self.mt5.history_orders_total(date_from, date_to)
        return total_orders

    async def track_order(self, *, position: int = None, end_time: datetime = None) -> DataFrame:
        """
        Track an order from the time it was opened to the time it was closed or any given time.
         The tracking is done by getting the ticks
        for the order symbol from the time the order was opened to the time it was closed. The profit for each tick is
        calculated using the order type, symbol, initial volume, open price and the bid or ask price of the tick
        depending on the order type.
        Args:
            end_time (datetime): The time to stop tracking the order. If not provided, the tracking will continue until
                the order is closed.
            position (int): The position ticket
            end_time (int): The time to stop tracking the order in seconds. If not provided, the tracking will continue
             until the order is closed.
        Returns:
            DataFrame: A pandas DataFrame of the ticks and profit for the order.
        """
        orders = await self.get_orders_position(position=position)
        deals = await self.get_deals_position(position=position)
        open_order = orders[0]
        open_deal = deals[0]
        close_deal = deals[-1]
        time_done = datetime.timestamp(end_time) if end_time is not None else close_deal.time
        time_done_msc = int(time_done * 1000)
        open_order.set_attributes(time_done_msc=time_done_msc, time_done=time_done, price_open=open_deal.price)
        ticks = await self.mt5.copy_ticks_range(open_order.symbol, open_order.time_setup, open_order.time_done,
                                                CopyTicks.ALL)
        data = pd.DataFrame(ticks)
        profit = lambda x: self.mt5._order_calc_profit(open_order.type, open_order.symbol, open_order.volume_initial,
                                                       open_order.price_open,
                                                       x.ask if open_order.type == OrderType.BUY else x.bid)
        data['profits'] = data.apply(profit, axis=1)
        data['time'] = pd.to_datetime(data['time'], unit='s')
        data.set_index('time', inplace=True)
        return data
