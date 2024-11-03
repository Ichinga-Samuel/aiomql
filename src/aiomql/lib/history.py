import asyncio
from datetime import datetime
from logging import getLogger

import pytz
from pandas import DataFrame
import pandas as pd

from ..core.config import Config
from ..core.meta_trader import MetaTrader, CopyTicks, OrderType
from ..core.models import TradeDeal, TradeOrder
from ..core.meta_backtester import MetaBackTester
from .._utils import backoff_decorator

logger = getLogger(__name__)


class History:
    """The history class handles completed trade deals and trade orders in the trading history of an account.

    Attributes:
        deals (list[TradeDeal]): Iterable of trade deals
        orders (list[TradeOrder]): Iterable of trade orders
        total_deals: Total number of deals
        total_orders (int): Total number orders
        group (str): Filter for selecting history by symbols.
        mt5 (MetaTrader): MetaTrader instance
        config (Config): Config instance
    """

    mt5: MetaTrader | MetaBackTester
    config: Config

    def __init__(
        self,
        *,
        date_from: datetime | int,
        date_to: datetime | int,
        group: str = "",
        use_utc: bool = True,
    ):
        """
        Args:
            date_from (datetime, int): Date the orders are requested from. Set by the 'datetime' object or as a
                number of seconds elapsed since 1970.01.01. Defaults to twenty-four hours from the current time in 'utc'

            date_to (datetime, int): Date up to which the orders are requested. Set by the 'datetime' object or as a
                number of seconds elapsed since 1970.01.01. Defaults to the current time in "utc"

            group (str): Filter for selecting history by symbols. Defaults to an empty string
        """
        self.config = Config()
        self.mt5 = MetaTrader() if self.config.mode != "backtest" else MetaBackTester()
        date_from = (
            date_from
            if isinstance(date_from, datetime)
            else datetime.fromtimestamp(date_from)
        )
        date_to = (
            date_to
            if isinstance(date_to, datetime)
            else datetime.fromtimestamp(date_to)
        )
        self.date_from = date_from.astimezone(pytz.UTC) if use_utc else date_from
        self.date_to = date_to.astimezone(pytz.UTC) if use_utc else date_to
        self.group = group
        self.deals: tuple[TradeDeal, ...] = ()
        self.orders: tuple[TradeOrder, ...] = ()
        self.total_deals: int = 0
        self.total_orders: int = 0

    async def initialize(self):
        """Get history deals and orders"""
        deals, orders = await asyncio.gather(
            self.get_deals(), self.get_orders(), return_exceptions=True
        )
        self.deals = deals if isinstance(deals, tuple) else ()
        self.orders = orders if isinstance(orders, tuple) else ()
        self.total_deals = len(self.deals)
        self.total_orders = len(self.orders)

    @backoff_decorator
    async def get_deals(self) -> tuple[TradeDeal, ...]:
        """Get deals from trading history using the parameters set in the constructor.
        Returns:
            tuple[TradeDeal]: A list of trade deals
        """
        deals = await self.mt5.history_deals_get(
            date_from=self.date_from, date_to=self.date_to, group=self.group
        )
        if deals is not None:
            return tuple(TradeDeal(**deal._asdict()) for deal in deals)
        logger.warning(f"Failed to get deals")
        return tuple()

    def get_deals_by_ticket(self, *, ticket: int) -> tuple[TradeDeal, ...]:
        """Call specifying the order ticket. Return all deals having the specified order ticket in the DEAL_ORDER
        property.

        Args:
            ticket (int): The order ticket

        Returns:
            tuple[TradeDeal]: A tuple of all deals with the order ticket
        """
        return tuple(
            sorted(
                (deal for deal in self.deals if deal.order == ticket),
                key=lambda x: x.time_msc,
            )
        )

    def get_deals_by_position(self, *, position: int = None) -> tuple[TradeDeal, ...]:
        """
        Get all deals with the specified position ticket in the DEAL_POSITION_ID property
        Args:
            position (int): The position ticket

        Returns:
            tuple[TradeDeal]: A tuple of all deals with the position ticket
        """
        return tuple(
            sorted(
                (deal for deal in self.deals if deal.position_id == position),
                key=lambda x: x.time_msc,
            )
        )

    @backoff_decorator
    async def get_orders(self) -> tuple[TradeOrder, ...]:
        """Get orders from trading history using the parameters set in the constructor or the method arguments.

        Returns:
            list[TradeOrder]: A list of trade orders
        """
        orders = await self.mt5.history_orders_get(
            date_from=self.date_from, date_to=self.date_to, group=self.group
        )

        if orders is not None:
            return tuple(TradeOrder(**order._asdict()) for order in orders)

        logger.warning(f"Failed to get orders")
        return tuple()

    def get_orders_by_ticket(self, *, ticket: int) -> tuple[TradeOrder, ...]:
        """filter orders by ticket"""
        return tuple(
            sorted(
                (order for order in self.orders if order.ticket == ticket),
                key=lambda x: x.time_done_msc,
            )
        )

    def get_orders_by_position(self, *, position: int) -> tuple[TradeOrder, ...]:
        """filter orders by position"""
        return tuple(
            sorted(
                (order for order in self.orders if order.position_id == position),
                key=lambda x: x.time_done_msc,
            )
        )

    async def track_order(
        self, *, position: int = None, end_time: datetime = None
    ) -> DataFrame:
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
        orders = self.get_orders_by_position(position=position)
        deals = self.get_deals_by_position(position=position)
        open_order = orders[0]
        open_deal = deals[0]
        close_deal = deals[-1]
        time_done = (
            datetime.timestamp(end_time) if end_time is not None else close_deal.time
        )
        time_done_msc = int(time_done * 1000)
        open_order.set_attributes(
            time_done_msc=time_done_msc, time_done=time_done, price_open=open_deal.price
        )
        ticks = await self.mt5.copy_ticks_range(
            open_order.symbol,
            open_order.time_setup,
            open_order.time_done,
            CopyTicks.ALL,
        )
        data = pd.DataFrame(ticks)
        profit = lambda x: self.mt5._order_calc_profit(
            open_order.type,
            open_order.symbol,
            open_order.volume_initial,
            open_order.price_open,
            x.ask if open_order.type == OrderType.BUY else x.bid,
        )
        data["profits"] = data.apply(profit, axis=1)
        data["time"] = pd.to_datetime(data["time"], unit="s")
        data.set_index("time", inplace=True)
        return data
