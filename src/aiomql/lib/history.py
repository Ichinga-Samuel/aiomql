"""History module for accessing trade history.

This module provides the History class for retrieving completed trade
deals and orders from the trading account history within a specified
date range.

Example:
    Getting trade history::

        history = History(date_from=datetime(2024, 1, 1), date_to=datetime.now())
        await history.initialize()
        for deal in history.deals:
            print(f"Deal {deal.ticket}: {deal.profit}")
"""

import asyncio
from typing import ClassVar
from datetime import datetime, UTC
from logging import getLogger

from ..core.config import Config
from ..core.meta_trader import MetaTrader
from ..core.models import TradeDeal, TradeOrder
from ..core.base import BaseMeta
from ..core.exceptions import InvalidRequest

logger = getLogger(__name__)


class History(metaclass=BaseMeta):
    """Handles completed trade deals and orders from account history.

    Provides methods to retrieve and filter historical trade deals and orders
    within a specified date range. Supports filtering by symbol group, order
    ticket, and position ID.

    Attributes:
        deals: Tuple of trade deals retrieved from history.
        orders: Tuple of trade orders retrieved from history.
        total_deals: Total number of deals retrieved.
        total_orders: Total number of orders retrieved.
        group: Symbol filter pattern for selecting history.
        date_from: Start date for history query.
        date_to: End date for history query.
        mt5: MetaTrader (class variable).
        config: Config instance (class variable).

    Example:
        Basic usage::

            from datetime import datetime
            from aiomql.lib.history import History

            history = History(
                date_from=datetime(2024, 1, 1),
                date_to=datetime.now()
            )
            await history.initialize()

            # Access deals and orders
            print(f"Total deals: {history.total_deals}")
            print(f"Total orders: {history.total_orders}")

            # Filter by position
            position_deals = history.get_deals_by_position(position=12345)
    """
    mt5: ClassVar[MetaTrader]
    config: ClassVar[Config]
    deals: tuple[TradeDeal, ...]
    orders: tuple[TradeOrder, ...]
    total_deals: int
    total_orders: int
    group: str

    def __init__(self, *, date_from: datetime | float, date_to: datetime | float, group: str = "", use_utc: bool = False):
        """Initialize a History instance with date range and filters.

        Args:
            date_from: Start date for history query. Can be a datetime object
                or Unix timestamp (seconds since 1970-01-01).
            date_to: End date for history query. Can be a datetime object
                or Unix timestamp (seconds since 1970-01-01).
            group: Symbol filter pattern for selecting history. Use '*' as
                wildcard. Defaults to empty string (all symbols).
            use_utc: If True, convert date_from and date_to to UTC timezone.
                Defaults to False.

        Example:
            Create history for specific date range::

                # Using datetime objects
                history = History(
                    date_from=datetime(2024, 1, 1),
                    date_to=datetime(2024, 12, 31)
                )

                # Using timestamps
                history = History(
                    date_from=1704067200.0,  # 2024-01-01
                    date_to=1735689600.0     # 2024-12-31
                )

                # With symbol filter
                history = History(
                    date_from=datetime(2024, 1, 1),
                    date_to=datetime.now(),
                    group="*USD*"  # Only USD pairs
                )
        """
        date_from = date_from if isinstance(date_from, datetime) else datetime.fromtimestamp(date_from)
        date_to = date_to if isinstance(date_to, datetime) else datetime.fromtimestamp(date_to)
        self.date_from = date_from.astimezone(UTC) if use_utc else date_from
        self.date_to = date_to.astimezone(UTC) if use_utc else date_to
        self.group = group
        self.deals: tuple[TradeDeal, ...] = ()
        self.orders: tuple[TradeOrder, ...] = ()
        self.total_deals: int = 0
        self.total_orders: int = 0

    async def initialize(self) -> None:
        """Fetch history deals and orders from the trading account.

        Retrieves both deals and orders concurrently and stores them in
        the instance attributes. Must be called before accessing deals
        or orders.

        Note:
            This method handles exceptions gracefully. If fetching deals
            or orders fails, the corresponding attribute will be an empty tuple.

        Example:
            Initialize and access history::

                history = History(date_from=start, date_to=end)
                await history.initialize()
                print(f"Found {history.total_deals} deals")
        """
        deals, orders = await asyncio.gather(self.get_deals(), self.get_orders(), return_exceptions=True)
        self.deals = deals if isinstance(deals, tuple) else ()
        self.orders = orders if isinstance(orders, tuple) else ()
        self.total_deals = len(self.deals)
        self.total_orders = len(self.orders)

    async def get_deals(self) -> tuple[TradeDeal, ...]:
        """Retrieve trade deals from history.

        Fetches deals from the trading history using the date range and
        group filter set in the constructor.

        Returns:
            tuple[TradeDeal, ...]: Tuple of TradeDeal objects. Returns empty
                tuple if no deals found or on error.

        Note:
            Logs a warning if fetching deals fails.
        """
        deals = await self.mt5.history_deals_get(date_from=self.date_from, date_to=self.date_to, group=self.group)
        return tuple(TradeDeal(**deal._asdict()) for deal in deals)

    async def get_orders(self) -> tuple[TradeOrder, ...]:
        """Retrieve trade orders from history.

        Fetches orders from the trading history using the date range and
        group filter set in the constructor.

        Returns:
            tuple[TradeOrder, ...]: Tuple of TradeOrder objects. Returns empty
                tuple if no orders found or on error.

        Note:
            Logs a warning if fetching orders fails.
        """
        orders = await self.mt5.history_orders_get(date_from=self.date_from, date_to=self.date_to, group=self.group)
        return tuple(TradeOrder(**order._asdict()) for order in orders)

    def filter_deals_by_ticket(self, *, ticket: int) -> tuple[TradeDeal, ...]:
        """Filters cached deals by ticket number.

        Args:
            ticket: The deal ticket number to filter by.

        Returns:
            tuple[TradeDeal, ...]: Deals matching the specified ticket.
        """
        return tuple(deal for deal in self.deals if deal.ticket == ticket)

    def filter_deals_by_position(self, *, position: int) -> tuple[TradeDeal, ...]:
        """Filters cached deals by position identifier.

        Args:
            position: The position ID to filter by.

        Returns:
            tuple[TradeDeal, ...]: Deals matching the specified position.
        """
        return tuple(deal for deal in self.deals if deal.position_id == position)

    def filter_orders_by_ticket(self, *, ticket: int) -> tuple[TradeOrder, ...]:
        """Filters cached orders by ticket number.

        Args:
            ticket: The order ticket number to filter by.

        Returns:
            tuple[TradeOrder, ...]: Orders matching the specified ticket.
        """
        return tuple(order for order in self.orders if order.ticket == ticket)

    def filter_orders_by_position(self, *, position: int) -> tuple[TradeOrder, ...]:
        """Filters cached orders by position identifier.

        Args:
            position: The position ID to filter by.

        Returns:
            tuple[TradeOrder, ...]: Orders matching the specified position.
        """
        return tuple(order for order in self.orders if order.position_id == position)

    @classmethod
    async def get_deal_by_ticket(cls, *, ticket: int) -> TradeDeal:
        """Fetches a single deal from history by its ticket number.

        Args:
            ticket: The deal ticket number.

        Returns:
            TradeDeal: The matching deal.

        Raises:
            InvalidRequest: If no deal matches the given ticket.
        """
        deals = await cls.mt5.history_deals_get(ticket=ticket)
        if (deal := deals[0]).ticket == ticket:
            return TradeDeal(**deal._asdict())
        raise InvalidRequest("Ticket not found")

    @classmethod
    async def get_deals_by_position(cls, *, position: int = None) -> tuple[TradeDeal, ...]:
        """Fetches deals from history by position identifier.

        Args:
            position: The position ID to filter by.

        Returns:
            tuple[TradeDeal, ...]: Deals associated with the position.
        """
        deals = await cls.mt5.history_deals_get(position=position)
        return tuple(TradeDeal(**deal._asdict()) for deal in deals if deal.position_id == position)

    @classmethod
    async def get_order_by_ticket(cls, *, ticket: int) -> TradeOrder:
        """Fetches a single order from history by its ticket number.

        Args:
            ticket: The order ticket number.

        Returns:
            TradeOrder: The matching order.

        Raises:
            InvalidRequest: If no order matches the given ticket.
        """
        orders = await cls.mt5.history_orders_get(ticket=ticket)
        if (order := orders[0]).ticket == ticket:
            return TradeOrder(**order._asdict())
        raise InvalidRequest("Ticket not found")

    @classmethod
    async def get_orders_by_position(cls, *, position: int) -> tuple[TradeOrder, ...]:
        """Fetches orders from history by position identifier.

        Args:
            position: The position ID to filter by.

        Returns:
            tuple[TradeOrder, ...]: Orders associated with the position.
        """
        orders = await cls.mt5.history_orders_get(position=position)
        return tuple(TradeOrder(**order._asdict()) for order in orders)
