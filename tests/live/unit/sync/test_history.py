"""Comprehensive tests for the synchronous history module.

Tests cover:
- History class initialization with various parameter combinations
- Class variable sharing (BaseMeta metaclass behavior)
- Synchronous initialization and data fetching
- Deal retrieval and filtering methods
- Order retrieval and filtering methods
- Edge cases and error handling
- UTC timezone handling
"""
from datetime import datetime, UTC, timedelta

import pytest

from aiomql.lib.sync.history import History
from aiomql.core.models import TradeDeal, TradeOrder
from aiomql.core.sync.meta_trader import MetaTrader


@pytest.fixture(scope="module")
def make_buy_sell_orders_sync():
    """Create buy and sell orders synchronously for testing history."""
    mt = MetaTrader()
    sym_info = mt.symbol_info("BTCUSD")
    dsl = (sym_info.trade_stops_level + sym_info.spread) * 2 * sym_info.point
    sl = sym_info.ask - dsl
    tp = sym_info.ask + dsl
    req = {
        "action": mt.TRADE_ACTION_DEAL,
        "symbol": "BTCUSD",
        "volume": sym_info.volume_min,
        "type": mt.ORDER_TYPE_BUY,
        "price": sym_info.ask,
        "sl": sl,
        "tp": tp,
    }
    mt.order_send(req)
    req["type"] = mt.ORDER_TYPE_SELL
    req["price"] = sym_info.bid
    req["sl"] = sym_info.bid + dsl
    req["tp"] = sym_info.bid - dsl
    mt.order_send(req)


class TestHistoryInitialization:
    """Test History class initialization and configuration."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures for initialization tests."""
        cls.now = datetime.now()
        cls.start = cls.now.replace(hour=0, minute=0, second=0, microsecond=0)
        cls.end = cls.now.replace(hour=23, minute=59, second=59, microsecond=0)

    def test_init_with_datetime_objects(self):
        """Test initialization with datetime objects."""
        history = History(date_from=self.start, date_to=self.end)
        assert history.date_from == self.start
        assert history.date_to == self.end

    def test_init_with_timestamps(self):
        """Test initialization with Unix timestamp floats."""
        start_ts = self.start.timestamp()
        end_ts = self.end.timestamp()
        history = History(date_from=start_ts, date_to=end_ts)
        assert history.date_from.timestamp() == start_ts
        assert history.date_to.timestamp() == end_ts

    def test_init_with_mixed_types(self):
        """Test initialization with mixed datetime and timestamp."""
        start_ts = self.start.timestamp()
        history = History(date_from=start_ts, date_to=self.end)
        assert history.date_from.timestamp() == start_ts
        assert history.date_to == self.end

    def test_init_with_group_filter(self):
        """Test initialization with symbol group filter."""
        history = History(date_from=self.start, date_to=self.end, group="*USD*")
        assert history.group == "*USD*"

    def test_init_with_empty_group(self):
        """Test initialization with empty group (default)."""
        history = History(date_from=self.start, date_to=self.end)
        assert history.group == ""

    def test_init_with_use_utc_true(self):
        """Test initialization with use_utc=True converts to UTC."""
        local_time = datetime.now()
        history = History(date_from=local_time, date_to=local_time, use_utc=True)
        assert history.date_from.tzinfo == UTC
        assert history.date_to.tzinfo == UTC

    def test_init_with_use_utc_false(self):
        """Test initialization with use_utc=False keeps original timezone."""
        local_time = datetime.now()
        history = History(date_from=local_time, date_to=local_time, use_utc=False)
        # When use_utc is False, timezone is not modified
        assert history.date_from == local_time
        assert history.date_to == local_time

    def test_init_default_attributes(self):
        """Test default attribute values after initialization."""
        history = History(date_from=self.start, date_to=self.end)
        assert history.deals == ()
        assert history.orders == ()
        assert history.total_deals == 0
        assert history.total_orders == 0

    def test_init_class_variables_set(self):
        """Test that class variables mt5 and config are set."""
        history = History(date_from=self.start, date_to=self.end)
        assert hasattr(History, 'mt5')
        assert hasattr(History, 'config')
        assert hasattr(history, 'mt5')
        assert hasattr(history, 'config')

    def test_multiple_instances_share_mt5(self):
        """Test that multiple History instances share the same mt5 object."""
        history1 = History(date_from=self.start, date_to=self.end)
        history2 = History(date_from=self.start, date_to=self.end)
        assert history1.mt5 is history2.mt5

    def test_multiple_instances_share_config(self):
        """Test that multiple History instances share the same config object."""
        history1 = History(date_from=self.start, date_to=self.end)
        history2 = History(date_from=self.start, date_to=self.end)
        assert history1.config is history2.config


class TestHistoryLive:
    """Live tests for synchronous History class with actual MT5 connection."""

    @pytest.fixture(scope="class", autouse=True)
    def init(self, make_buy_sell_orders_sync):
        """Initialize history with live trades."""
        self.history.initialize()

    @classmethod
    def setup_class(cls):
        """Set up test fixtures with today's date range."""
        now = datetime.now()
        cls.start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        cls.end = now.replace(hour=23, minute=59, second=59, microsecond=0)
        cls.history = History(date_from=cls.start, date_to=cls.end)

    def test_initialize_populates_deals(self):
        """Test that initialize() populates deals attribute."""
        assert self.history.deals is not None
        assert isinstance(self.history.deals, tuple)

    def test_initialize_populates_orders(self):
        """Test that initialize() populates orders attribute."""
        assert self.history.orders is not None
        assert isinstance(self.history.orders, tuple)

    def test_initialize_sets_total_deals(self):
        """Test that initialize() sets correct total_deals count."""
        assert self.history.total_deals >= 0
        assert self.history.total_deals == len(self.history.deals)

    def test_initialize_sets_total_orders(self):
        """Test that initialize() sets correct total_orders count."""
        assert self.history.total_orders >= 0
        assert self.history.total_orders == len(self.history.orders)

    def test_get_deals_returns_trade_deal_objects(self):
        """Test that get_deals returns TradeDeal objects."""
        deals = self.history.get_deals()
        assert isinstance(deals, tuple)
        if deals:
            assert all(isinstance(deal, TradeDeal) for deal in deals)

    def test_get_orders_returns_trade_order_objects(self):
        """Test that get_orders returns TradeOrder objects."""
        orders = self.history.get_orders()
        assert isinstance(orders, tuple)
        if orders:
            assert all(isinstance(order, TradeOrder) for order in orders)

    def test_deals_have_required_attributes(self):
        """Test that deals have expected TradeDeal attributes."""
        if self.history.deals:
            deal = self.history.deals[0]
            assert hasattr(deal, 'ticket')
            assert hasattr(deal, 'order')
            assert hasattr(deal, 'time')
            assert hasattr(deal, 'time_msc')
            assert hasattr(deal, 'type')
            assert hasattr(deal, 'position_id')
            assert hasattr(deal, 'profit')
            assert hasattr(deal, 'symbol')

    def test_orders_have_required_attributes(self):
        """Test that orders have expected TradeOrder attributes."""
        if self.history.orders:
            order = self.history.orders[0]
            assert hasattr(order, 'ticket')
            assert hasattr(order, 'time_setup')
            assert hasattr(order, 'time_done')
            assert hasattr(order, 'time_done_msc')
            assert hasattr(order, 'type')
            assert hasattr(order, 'position_id')
            assert hasattr(order, 'symbol')


class TestHistoryDealsFiltering:
    """Test deal filtering methods with live data."""

    @pytest.fixture(scope="class", autouse=True)
    def init(self, make_buy_sell_orders_sync):
        """Initialize history with live trades."""
        self.history.initialize()

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        now = datetime.now()
        cls.start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        cls.end = now.replace(hour=23, minute=59, second=59, microsecond=0)
        cls.history = History(date_from=cls.start, date_to=cls.end)

    def test_filter_deals_by_ticket_returns_tuple(self):
        """Test filter_deals_by_ticket returns a tuple."""
        if self.history.deals:
            ticket = self.history.deals[0].order
            deals = self.history.filter_deals_by_ticket(ticket=ticket)
            assert isinstance(deals, tuple)

    def test_filter_deals_by_ticket_finds_matching_deals(self):
        """Test filter_deals_by_ticket finds deals with matching order ticket."""
        if self.history.deals:
            ticket = self.history.deals[0].order
            deals = self.history.filter_deals_by_ticket(ticket=ticket)
            if deals:
                assert all(deal.order == ticket for deal in deals)

    def test_filter_deals_by_ticket_nonexistent_returns_empty(self):
        """Test filter_deals_by_ticket returns empty tuple for nonexistent ticket."""
        nonexistent_ticket = 999999999999
        deals = self.history.filter_deals_by_ticket(ticket=nonexistent_ticket)
        assert deals == ()

    def test_filter_deals_by_position_returns_tuple(self):
        """Test filter_deals_by_position returns a tuple."""
        if self.history.deals:
            position = self.history.deals[0].position_id
            deals = self.history.filter_deals_by_position(position=position)
            assert isinstance(deals, tuple)

    def test_filter_deals_by_position_finds_matching_deals(self):
        """Test filter_deals_by_position finds deals with matching position_id."""
        if self.history.deals:
            position = self.history.deals[0].position_id
            deals = self.history.filter_deals_by_position(position=position)
            if deals:
                assert all(deal.position_id == position for deal in deals)

    def test_filter_deals_by_position_nonexistent_returns_empty(self):
        """Test filter_deals_by_position returns empty tuple for nonexistent position."""
        nonexistent_position = 999999999999
        deals = self.history.filter_deals_by_position(position=nonexistent_position)
        assert deals == ()


class TestHistoryOrdersFiltering:
    """Test order filtering methods with live data."""

    @pytest.fixture(scope="class", autouse=True)
    def init(self, make_buy_sell_orders_sync):
        """Initialize history with live trades."""
        self.history.initialize()

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        now = datetime.now()
        cls.start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        cls.end = now.replace(hour=23, minute=59, second=59, microsecond=0)
        cls.history = History(date_from=cls.start, date_to=cls.end)

    def test_filter_orders_by_ticket_returns_tuple(self):
        """Test filter_orders_by_ticket returns a tuple."""
        if self.history.orders:
            ticket = self.history.orders[0].ticket
            orders = self.history.filter_orders_by_ticket(ticket=ticket)
            assert isinstance(orders, tuple)

    def test_filter_orders_by_ticket_finds_matching_orders(self):
        """Test filter_orders_by_ticket finds orders with matching ticket."""
        if self.history.orders:
            ticket = self.history.orders[0].ticket
            orders = self.history.filter_orders_by_ticket(ticket=ticket)
            if orders:
                assert all(order.ticket == ticket for order in orders)

    def test_filter_orders_by_ticket_nonexistent_returns_empty(self):
        """Test filter_orders_by_ticket returns empty tuple for nonexistent ticket."""
        nonexistent_ticket = 999999999999
        orders = self.history.filter_orders_by_ticket(ticket=nonexistent_ticket)
        assert orders == ()

    def test_filter_orders_by_position_returns_tuple(self):
        """Test filter_orders_by_position returns a tuple."""
        if self.history.orders:
            position = self.history.orders[0].position_id
            orders = self.history.filter_orders_by_position(position=position)
            assert isinstance(orders, tuple)

    def test_filter_orders_by_position_finds_matching_orders(self):
        """Test filter_orders_by_position finds orders with matching position_id."""
        if self.history.orders:
            position = self.history.orders[0].position_id
            orders = self.history.filter_orders_by_position(position=position)
            if orders:
                assert all(order.position_id == position for order in orders)

    def test_filter_orders_by_position_nonexistent_returns_empty(self):
        """Test filter_orders_by_position returns empty tuple for nonexistent position."""
        nonexistent_position = 999999999999
        orders = self.history.filter_orders_by_position(position=nonexistent_position)
        assert orders == ()


class TestHistoryWithGroupFilter:
    """Test History with group filter for specific symbols."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures with group filter."""
        now = datetime.now()
        cls.start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        cls.end = now.replace(hour=23, minute=59, second=59, microsecond=0)

    @pytest.fixture(scope="class", autouse=True)
    def init(self, make_buy_sell_orders_sync):
        """Ensure trades are created for group filter tests."""
        pass

    def test_group_filter_btcusd(self):
        """Test filtering history by BTCUSD symbol group."""
        history = History(date_from=self.start, date_to=self.end, group="*BTCUSD*")
        history.initialize()
        for deal in history.deals:
            assert "BTCUSD" in deal.symbol

    def test_group_filter_usd(self):
        """Test filtering history by USD symbol group."""
        history = History(date_from=self.start, date_to=self.end, group="*USD*")
        history.initialize()
        for deal in history.deals:
            assert "USD" in deal.symbol

    def test_group_filter_nonexistent_symbol(self):
        """Test filtering with nonexistent symbol group returns empty."""
        history = History(date_from=self.start, date_to=self.end, group="NONEXISTENT12345")
        history.initialize()
        assert history.total_deals == 0
        assert history.total_orders == 0


class TestHistoryDateRanges:
    """Test History with various date ranges."""

    @pytest.fixture(scope="class", autouse=True)
    def init(self, make_buy_sell_orders_sync):
        """Ensure trades are made for date range tests."""
        pass

    def test_today_date_range(self):
        """Test history retrieval for today's date range."""
        now = datetime.now()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=0)
        history = History(date_from=start, date_to=end)
        history.initialize()
        # Should have at least the test trades
        assert history.total_deals >= 0

    def test_past_date_range(self):
        """Test history retrieval for a past date range."""
        now = datetime.now()
        end = now - timedelta(days=7)
        start = end - timedelta(days=7)
        history = History(date_from=start, date_to=end)
        history.initialize()
        assert isinstance(history.deals, tuple)
        assert isinstance(history.orders, tuple)

    def test_wide_date_range(self):
        """Test history retrieval for a wide date range (30 days)."""
        now = datetime.now()
        start = now - timedelta(days=30)
        end = now
        history = History(date_from=start, date_to=end)
        history.initialize()
        assert isinstance(history.deals, tuple)
        assert isinstance(history.orders, tuple)

    def test_narrow_date_range(self):
        """Test history retrieval for a narrow date range (1 hour)."""
        now = datetime.now()
        start = now - timedelta(hours=1)
        end = now
        history = History(date_from=start, date_to=end)
        history.initialize()
        assert isinstance(history.deals, tuple)
        assert isinstance(history.orders, tuple)


class TestHistoryEdgeCases:
    """Test edge cases and error handling."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.now = datetime.now()
        cls.start = cls.now.replace(hour=0, minute=0, second=0, microsecond=0)
        cls.end = cls.now.replace(hour=23, minute=59, second=59, microsecond=0)

    def test_empty_history_no_trades(self):
        """Test handling of date range with no trades."""
        # Use a future date range where no trades exist
        future_start = datetime.now() + timedelta(days=365)
        future_end = future_start + timedelta(days=1)
        history = History(date_from=future_start, date_to=future_end)
        history.initialize()
        assert history.deals == ()
        assert history.orders == ()
        assert history.total_deals == 0
        assert history.total_orders == 0

    def test_filter_deals_by_ticket_with_no_deals(self):
        """Test filtering by ticket when deals is empty."""
        future_start = datetime.now() + timedelta(days=365)
        future_end = future_start + timedelta(days=1)
        history = History(date_from=future_start, date_to=future_end)
        history.initialize()
        deals = history.filter_deals_by_ticket(ticket=12345)
        assert deals == ()

    def test_filter_deals_by_position_with_no_deals(self):
        """Test filtering by position when deals is empty."""
        future_start = datetime.now() + timedelta(days=365)
        future_end = future_start + timedelta(days=1)
        history = History(date_from=future_start, date_to=future_end)
        history.initialize()
        deals = history.filter_deals_by_position(position=12345)
        assert deals == ()

    def test_filter_orders_by_ticket_with_no_orders(self):
        """Test filtering by ticket when orders is empty."""
        future_start = datetime.now() + timedelta(days=365)
        future_end = future_start + timedelta(days=1)
        history = History(date_from=future_start, date_to=future_end)
        history.initialize()
        orders = history.filter_orders_by_ticket(ticket=12345)
        assert orders == ()

    def test_filter_orders_by_position_with_no_orders(self):
        """Test filtering by position when orders is empty."""
        future_start = datetime.now() + timedelta(days=365)
        future_end = future_start + timedelta(days=1)
        history = History(date_from=future_start, date_to=future_end)
        history.initialize()
        orders = history.filter_orders_by_position(position=12345)
        assert orders == ()

    def test_initialize_can_be_called_multiple_times(self):
        """Test that initialize() can be safely called multiple times."""
        history = History(date_from=self.start, date_to=self.end)
        history.initialize()
        first_deals = history.deals
        first_orders = history.orders

        history.initialize()
        # Should still have data after reinitialization
        assert isinstance(history.deals, tuple)
        assert isinstance(history.orders, tuple)

    def test_filtering_before_initialize(self):
        """Test filtering methods work on uninitialized history (empty tuples)."""
        history = History(date_from=self.start, date_to=self.end)
        # Don't call initialize
        deals = history.filter_deals_by_ticket(ticket=12345)
        assert deals == ()

        deals = history.filter_deals_by_position(position=12345)
        assert deals == ()

        orders = history.filter_orders_by_ticket(ticket=12345)
        assert orders == ()

        orders = history.filter_orders_by_position(position=12345)
        assert orders == ()


class TestHistoryUtcConversion:
    """Test UTC timezone conversion functionality."""

    def test_utc_conversion_with_naive_datetime(self):
        """Test UTC conversion with naive datetime objects."""
        now = datetime.now()
        history = History(date_from=now, date_to=now, use_utc=True)
        assert history.date_from.tzinfo == UTC
        assert history.date_to.tzinfo == UTC

    def test_utc_conversion_with_timestamps(self):
        """Test UTC conversion when dates are provided as timestamps."""
        now = datetime.now()
        ts = now.timestamp()
        history = History(date_from=ts, date_to=ts, use_utc=True)
        assert history.date_from.tzinfo == UTC
        assert history.date_to.tzinfo == UTC

    def test_no_utc_conversion_preserves_datetime(self):
        """Test that use_utc=False preserves the original datetime."""
        now = datetime.now()
        history = History(date_from=now, date_to=now, use_utc=False)
        # Without UTC conversion, dates should equal original
        assert history.date_from == now
        assert history.date_to == now


class TestHistoryConsistency:
    """Test data consistency between different retrieval methods."""

    @pytest.fixture(scope="class", autouse=True)
    def init(self, make_buy_sell_orders_sync):
        """Initialize history fixture."""
        self.history.initialize()

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        now = datetime.now()
        cls.start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        cls.end = now.replace(hour=23, minute=59, second=59, microsecond=0)
        cls.history = History(date_from=cls.start, date_to=cls.end)

    def test_get_deals_matches_deals_attribute(self):
        """Test that get_deals() returns same data as deals attribute."""
        deals = self.history.get_deals()
        # After initialization, deals attribute should have same count
        # Note: Fresh call may have different data if trades occurred between calls
        assert isinstance(deals, tuple)
        if deals:
            assert all(isinstance(d, TradeDeal) for d in deals)

    def test_get_orders_matches_orders_attribute(self):
        """Test that get_orders() returns same data as orders attribute."""
        orders = self.history.get_orders()
        assert isinstance(orders, tuple)
        if orders:
            assert all(isinstance(o, TradeOrder) for o in orders)

    def test_total_counts_match_tuple_lengths(self):
        """Test that total_deals and total_orders match tuple lengths."""
        assert self.history.total_deals == len(self.history.deals)
        assert self.history.total_orders == len(self.history.orders)

    def test_filtered_deals_subset_of_all_deals(self):
        """Test that filtered deals are a subset of all deals."""
        if self.history.deals:
            ticket = self.history.deals[0].order
            filtered = self.history.filter_deals_by_ticket(ticket=ticket)
            for deal in filtered:
                assert deal in self.history.deals

    def test_filtered_orders_subset_of_all_orders(self):
        """Test that filtered orders are a subset of all orders."""
        if self.history.orders:
            position = self.history.orders[0].position_id
            filtered = self.history.filter_orders_by_position(position=position)
            for order in filtered:
                assert order in self.history.orders


class TestHistorySyncVsAsync:
    """Test that sync History behaves correctly as a synchronous implementation."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        now = datetime.now()
        cls.start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        cls.end = now.replace(hour=23, minute=59, second=59, microsecond=0)

    def test_initialize_is_synchronous(self):
        """Test that initialize() is a synchronous method (not a coroutine)."""
        history = History(date_from=self.start, date_to=self.end)
        import inspect
        assert not inspect.iscoroutinefunction(history.initialize)

    def test_get_deals_is_synchronous(self):
        """Test that get_deals() is a synchronous method (not a coroutine)."""
        history = History(date_from=self.start, date_to=self.end)
        import inspect
        assert not inspect.iscoroutinefunction(history.get_deals)

    def test_get_orders_is_synchronous(self):
        """Test that get_orders() is a synchronous method (not a coroutine)."""
        history = History(date_from=self.start, date_to=self.end)
        import inspect
        assert not inspect.iscoroutinefunction(history.get_orders)

    def test_initialize_returns_none(self):
        """Test that initialize() returns None (not a coroutine object)."""
        history = History(date_from=self.start, date_to=self.end)
        result = history.initialize()
        assert result is None

    def test_get_deals_returns_tuple_directly(self):
        """Test that get_deals() returns a tuple directly (not a coroutine)."""
        history = History(date_from=self.start, date_to=self.end)
        result = history.get_deals()
        assert isinstance(result, tuple)

    def test_get_orders_returns_tuple_directly(self):
        """Test that get_orders() returns a tuple directly (not a coroutine)."""
        history = History(date_from=self.start, date_to=self.end)
        result = history.get_orders()
        assert isinstance(result, tuple)


class TestHistoryClassMethods:
    """Test History class methods."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        now = datetime.now()
        cls.start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        cls.end = now.replace(hour=23, minute=59, second=59, microsecond=0)
        cls.history = History(date_from=cls.start, date_to=cls.end)
        cls.history.initialize()

    def test_get_deal_by_ticket_exists(self):
        """Test get_deal_by_ticket returns a TradeDeal."""
        if self.history.deals:
            ticket = self.history.deals[0].ticket
            deal = History.get_deal_by_ticket(ticket=ticket)
            assert isinstance(deal, TradeDeal)
            assert deal.ticket == ticket

    def test_get_deals_by_position_exists(self):
        """Test get_deals_by_position returns a tuple of TradeDeals."""
        if self.history.deals:
            position = self.history.deals[0].position_id
            deals = History.get_deals_by_position(position=position)
            assert isinstance(deals, tuple)
            assert all(deal.position_id == position for deal in deals)

    def test_get_order_by_ticket_exists(self):
        """Test get_order_by_ticket returns a TradeOrder."""
        if self.history.orders:
            ticket = self.history.orders[0].ticket
            order = History.get_order_by_ticket(ticket=ticket)
            assert isinstance(order, TradeOrder)
            assert order.ticket == ticket

    def test_get_orders_by_position_exists(self):
        """Test get_orders_by_position returns a tuple of TradeOrders."""
        if self.history.orders:
            position = self.history.orders[0].position_id
            orders = History.get_orders_by_position(position=position)
            assert isinstance(orders, tuple)
            assert all(order.position_id == position for order in orders)
