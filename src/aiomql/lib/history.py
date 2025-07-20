import asyncio
from datetime import datetime
from logging import getLogger

import pytz

from ..core.config import Config
from ..core.meta_trader import MetaTrader
from ..core.models import TradeDeal, TradeOrder
from ..core.meta_backtester import MetaBackTester

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
    deals: tuple[TradeDeal, ...]
    orders: tuple[TradeOrder, ...]
    total_deals: int
    total_orders: int
    group: str

    def __init__(
        self, *, date_from: datetime | float, date_to: datetime | float, group: str = "", use_utc: bool = True
    ):
        """
        Args:
            date_from (datetime, float): Date the orders are requested from. Set by the 'datetime' object or as a
                number of seconds elapsed since 1970.01.01. Defaults to twenty-four hours from the current time in 'utc'

            date_to (datetime, float): Date up to which the orders are requested. Set by the 'datetime' object or as a
                number of seconds elapsed since 1970.01.01. Defaults to the current time in "utc"

            group (str): Filter for selecting history by symbols. This defaults to an empty string
        """
        self.config = Config()
        self.mt5 = MetaTrader() if self.config.mode != "backtest" else MetaBackTester()
        date_from = date_from if isinstance(date_from, datetime) else datetime.fromtimestamp(date_from)
        date_to = date_to if isinstance(date_to, datetime) else datetime.fromtimestamp(date_to)
        self.date_from = date_from.astimezone(pytz.UTC) if use_utc else date_from
        self.date_to = date_to.astimezone(pytz.UTC) if use_utc else date_to
        self.group = group
        self.deals: tuple[TradeDeal, ...] = ()
        self.orders: tuple[TradeOrder, ...] = ()
        self.total_deals: int = 0
        self.total_orders: int = 0

    async def initialize(self):
        """Get history deals and orders"""
        deals, orders = await asyncio.gather(self.get_deals(), self.get_orders(), return_exceptions=True)
        self.deals = deals if isinstance(deals, tuple) else ()
        self.orders = orders if isinstance(orders, tuple) else ()
        self.total_deals = len(self.deals)
        self.total_orders = len(self.orders)

    async def get_deals(self) -> tuple[TradeDeal, ...]:
        """Get deals from trading history using the parameters set in the constructor.

        Returns:
            tuple[TradeDeal, ...]: A list of trade deals
        """
        deals = await self.mt5.history_deals_get(date_from=self.date_from, date_to=self.date_to, group=self.group)
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
        return tuple(sorted((deal for deal in self.deals if deal.order == ticket), key=lambda x: x.time_msc))

    def get_deals_by_position(self, *, position: int = None) -> tuple[TradeDeal, ...]:
        """
        Get all deals with the specified position ticket in the DEAL_POSITION_ID property
        Args:
            position (int): The position ticket

        Returns:
            tuple[TradeDeal]: A tuple of all deals with the position ticket
        """
        return tuple(sorted((deal for deal in self.deals if deal.position_id == position), key=lambda x: x.time_msc))

    async def get_orders(self) -> tuple[TradeOrder, ...]:
        """Get orders from trading history using the parameters set in the constructor or the method arguments.

        Returns:
            list[TradeOrder]: A list of trade orders
        """
        orders = await self.mt5.history_orders_get(date_from=self.date_from, date_to=self.date_to, group=self.group)

        if orders is not None:
            return tuple(TradeOrder(**order._asdict()) for order in orders)

        logger.warning(f"Failed to get orders")
        return tuple()

    def get_orders_by_ticket(self, *, ticket: int) -> tuple[TradeOrder, ...]:
        """filter orders by ticket"""
        return tuple(sorted((order for order in self.orders if order.ticket == ticket), key=lambda x: x.time_done_msc))

    def get_orders_by_position(self, *, position: int) -> tuple[TradeOrder, ...]:
        """filter orders by position"""
        return tuple(
            sorted((order for order in self.orders if order.position_id == position), key=lambda x: x.time_done_msc)
        )
