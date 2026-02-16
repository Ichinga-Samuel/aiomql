"""Comprehensive tests for the synchronous Positions module.

Tests cover:
- Positions class initialization (BaseMeta metaclass behavior)
- Getting positions with various filters
- Getting positions by ticket and symbol
- Closing positions (individual and all)
- Class methods for position operations
- Edge cases and error handling
"""

import pytest

from aiomql.lib.sync.positions import Positions
from aiomql.core.models import TradePosition, OrderSendResult
from aiomql.core.exceptions import InvalidRequest


class TestPositionsInitialization:
    """Test Positions class initialization."""

    def test_has_mt5_attribute(self):
        """Test Positions has mt5 class attribute."""
        assert hasattr(Positions, 'mt5')

    def test_has_config_attribute(self):
        """Test Positions has config class attribute."""
        assert hasattr(Positions, 'config')

    def test_class_attributes_are_shared(self):
        """Test that class attributes are shared across access points."""
        assert Positions.mt5 is Positions.mt5
        assert Positions.config is Positions.config


class TestGetPositionsLive:
    """Live tests for getting positions."""

    @pytest.fixture(scope="class", autouse=True)
    def init(self, make_buy_sell_orders_sync):
        """Initialize with live trades."""
        cls = type(self)
        cls.positions = Positions.get_positions()

    def test_get_positions_returns_tuple(self):
        """Test get_positions returns a tuple."""
        positions = Positions.get_positions()
        assert isinstance(positions, tuple)

    def test_get_positions_contains_trade_positions(self):
        """Test get_positions contains TradePosition objects."""
        positions = Positions.get_positions()
        for position in positions:
            assert isinstance(position, TradePosition)

    def test_get_positions_by_symbol(self):
        """Test get_positions can filter by symbol."""
        if self.positions:
            symbol = self.positions[0].symbol
            positions = Positions.get_positions(symbol=symbol)
            for position in positions:
                assert position.symbol == symbol

    def test_get_positions_by_ticket(self):
        """Test get_positions can filter by ticket."""
        if self.positions:
            ticket = self.positions[0].ticket
            positions = Positions.get_positions(ticket=ticket)
            assert len(positions) <= 1
            if positions:
                assert positions[0].ticket == ticket

    def test_get_positions_by_group(self):
        """Test get_positions can filter by group."""
        positions = Positions.get_positions(group="*USD*")
        for position in positions:
            assert "USD" in position.symbol

    def test_get_positions_symbol_overrides_ticket(self):
        """Test that symbol filter takes precedence over ticket."""
        if self.positions:
            symbol = self.positions[0].symbol
            # Pass both symbol and ticket, symbol should take precedence
            positions = Positions.get_positions(symbol=symbol, ticket=99999999)
            # Should still return positions for symbol, not error on ticket
            for position in positions:
                assert position.symbol == symbol


class TestGetPositionByTicketLive:
    """Live tests for get_position_by_ticket class method."""

    @pytest.fixture(scope="class", autouse=True)
    def init(self, make_buy_sell_orders_sync):
        """Initialize with live trades."""
        cls = type(self)
        cls.positions = Positions.get_positions()

    def test_get_position_by_ticket_returns_trade_position(self):
        """Test get_position_by_ticket returns TradePosition."""
        if self.positions:
            ticket = self.positions[0].ticket
            position = Positions.get_position_by_ticket(ticket=ticket)
            assert isinstance(position, TradePosition)

    def test_get_position_by_ticket_correct_ticket(self):
        """Test get_position_by_ticket returns position with matching ticket."""
        if self.positions:
            ticket = self.positions[0].ticket
            position = Positions.get_position_by_ticket(ticket=ticket)
            assert position.ticket == ticket

    def test_get_position_by_ticket_nonexistent_returns_none(self):
        """Test get_position_by_ticket returns None for nonexistent ticket."""
        position = Positions.get_position_by_ticket(ticket=999999999999)
        assert position is None

    def test_get_position_by_ticket_has_required_attributes(self):
        """Test returned position has required attributes."""
        if self.positions:
            ticket = self.positions[0].ticket
            position = Positions.get_position_by_ticket(ticket=ticket)
            assert hasattr(position, 'ticket')
            assert hasattr(position, 'symbol')
            assert hasattr(position, 'volume')
            assert hasattr(position, 'type')
            assert hasattr(position, 'price_open')
            assert hasattr(position, 'price_current')
            assert hasattr(position, 'profit')


class TestGetPositionsBySymbolLive:
    """Live tests for get_positions_by_symbol class method."""

    @pytest.fixture(scope="class", autouse=True)
    def init(self, make_buy_sell_orders_sync):
        """Ensure trades exist."""
        pass

    def test_get_positions_by_symbol_returns_tuple(self):
        """Test get_positions_by_symbol returns a tuple."""
        positions = Positions.get_positions_by_symbol(symbol="BTCUSD")
        assert isinstance(positions, tuple)

    def test_get_positions_by_symbol_contains_trade_positions(self):
        """Test get_positions_by_symbol contains TradePosition objects."""
        positions = Positions.get_positions_by_symbol(symbol="BTCUSD")
        for position in positions:
            assert isinstance(position, TradePosition)

    def test_get_positions_by_symbol_correct_symbol(self):
        """Test all returned positions have the requested symbol."""
        positions = Positions.get_positions_by_symbol(symbol="BTCUSD")
        for position in positions:
            assert position.symbol == "BTCUSD"

    def test_get_positions_by_symbol_nonexistent_returns_empty(self):
        """Test get_positions_by_symbol returns empty tuple for nonexistent symbol."""
        positions = Positions.get_positions_by_symbol(symbol="NONEXISTENT123")
        assert positions == ()


class TestGetTotalPositionsLive:
    """Live tests for get_total_positions class method."""

    @pytest.fixture(scope="class", autouse=True)
    def init(self, make_buy_sell_orders_sync):
        """Ensure trades exist."""
        pass

    def test_get_total_positions_returns_int(self):
        """Test get_total_positions returns an integer."""
        total = Positions.get_total_positions()
        assert isinstance(total, int)

    def test_get_total_positions_non_negative(self):
        """Test get_total_positions returns non-negative value."""
        total = Positions.get_total_positions()
        assert total >= 0

    def test_get_total_positions_matches_get_positions(self):
        """Test get_total_positions matches length of get_positions."""
        total = Positions.get_total_positions()
        positions = Positions.get_positions()
        assert total == len(positions)


class TestClosePositionLive:
    """Live tests for closing positions."""

    @pytest.fixture(scope="class", autouse=True)
    def init(self, make_buy_sell_orders_sync):
        """Initialize with live trades."""
        cls = type(self)
        cls.positions = Positions.get_positions()

    def test_close_position_returns_tuple(self):
        """Test close_position returns a tuple of (bool, OrderSendResult)."""
        if self.positions:
            position = self.positions[0]
            result = Positions.close_position(position=position)
            assert isinstance(result, tuple)
            assert len(result) == 2

    def test_close_position_success(self):
        """Test close_position successfully closes a position."""
        # Refresh positions
        positions = Positions.get_positions()
        if positions:
            position = positions[0]
            success, result = Positions.close_position(position=position)
            if success:
                assert isinstance(result, OrderSendResult)
                assert result.retcode == 10009

    def test_close_position_by_ticket_returns_tuple(self):
        """Test close_position_by_ticket returns a tuple."""
        # Refresh positions
        positions = Positions.get_positions()
        if positions:
            ticket = positions[0].ticket
            result = Positions.close_position_by_ticket(ticket=ticket)
            assert isinstance(result, tuple)
            assert len(result) == 2

    def test_close_position_by_ticket_nonexistent_raises(self):
        """Test close_position_by_ticket raises InvalidRequest for nonexistent ticket."""
        with pytest.raises(InvalidRequest):
            Positions.close_position_by_ticket(ticket=999999999999)


class TestCloseStaticMethodLive:
    """Live tests for the static close method."""

    @pytest.fixture(scope="class", autouse=True)
    def init(self, make_buy_sell_orders_sync):
        """Initialize with live trades."""
        cls = type(self)
        cls.positions = Positions.get_positions()

    def test_close_returns_tuple(self):
        """Test close static method returns tuple of (bool, OrderSendResult)."""
        # Refresh positions
        positions = Positions.get_positions()
        if positions:
            position = positions[0]
            result = Positions.close(
                ticket=position.ticket,
                symbol=position.symbol,
                price=position.price_current,
                volume=position.volume,
                order_type=position.type,
            )
            assert isinstance(result, tuple)
            assert len(result) == 2


class TestClosePositionsLive:
    """Live tests for close_positions class method."""

    @pytest.fixture(scope="class", autouse=True)
    def init(self, make_buy_sell_orders_sync):
        """Initialize with live trades."""
        cls = type(self)
        cls.positions = Positions.get_positions()

    def test_close_positions_returns_tuple(self):
        """Test close_positions returns a tuple."""
        positions = Positions.get_positions()
        result = Positions.close_positions(positions=positions)
        assert isinstance(result, tuple)

    def test_close_positions_empty_positions(self):
        """Test close_positions with empty positions returns empty tuple."""
        result = Positions.close_positions(positions=())
        assert result == ()


class TestCloseAllPositionsLive:
    """Live tests for closing all positions."""

    @pytest.fixture(scope="class", autouse=True)
    def init(self, make_buy_sell_orders_sync):
        """Initialize with live trades."""
        pass

    def test_close_all_positions_returns_tuple(self):
        """Test close_all_positions class method returns a tuple."""
        result = Positions.close_all_positions()
        assert isinstance(result, tuple)

    def test_close_all_positions_contains_order_send_results(self):
        """Test close_all_positions returns OrderSendResult objects."""
        result = Positions.close_all_positions()
        for res in result:
            assert isinstance(res, OrderSendResult)


class TestPositionAttributes:
    """Test TradePosition attributes from positions."""

    @pytest.fixture(scope="class", autouse=True)
    def init(self, make_buy_sell_orders_sync):
        """Initialize with live trades."""
        cls = type(self)
        cls.positions = Positions.get_positions()

    def test_position_has_ticket(self):
        """Test position has ticket attribute."""
        if self.positions:
            position = self.positions[0]
            assert hasattr(position, 'ticket')
            assert isinstance(position.ticket, int)

    def test_position_has_symbol(self):
        """Test position has symbol attribute."""
        if self.positions:
            position = self.positions[0]
            assert hasattr(position, 'symbol')
            assert isinstance(position.symbol, str)

    def test_position_has_volume(self):
        """Test position has volume attribute."""
        if self.positions:
            position = self.positions[0]
            assert hasattr(position, 'volume')
            assert isinstance(position.volume, float)

    def test_position_has_type(self):
        """Test position has type attribute."""
        if self.positions:
            position = self.positions[0]
            assert hasattr(position, 'type')

    def test_position_has_price_open(self):
        """Test position has price_open attribute."""
        if self.positions:
            position = self.positions[0]
            assert hasattr(position, 'price_open')
            assert isinstance(position.price_open, float)

    def test_position_has_price_current(self):
        """Test position has price_current attribute."""
        if self.positions:
            position = self.positions[0]
            assert hasattr(position, 'price_current')
            assert isinstance(position.price_current, float)

    def test_position_has_profit(self):
        """Test position has profit attribute."""
        if self.positions:
            position = self.positions[0]
            assert hasattr(position, 'profit')
            assert isinstance(position.profit, float)

    def test_position_has_sl_tp(self):
        """Test position has sl and tp attributes."""
        if self.positions:
            position = self.positions[0]
            assert hasattr(position, 'sl')
            assert hasattr(position, 'tp')


class TestPositionsEdgeCases:
    """Test edge cases and error handling."""

    def test_get_positions_empty_when_no_positions(self):
        """Test get_positions returns empty tuple when no positions exist."""
        # Close all positions first
        Positions.close_all_positions()
        result = Positions.get_positions()
        # Result should be a tuple (possibly empty)
        assert isinstance(result, tuple)

    def test_get_positions_with_invalid_group(self):
        """Test get_positions with nonexistent group returns empty."""
        result = Positions.get_positions(group="NONEXISTENT_GROUP_12345")
        assert result == ()
