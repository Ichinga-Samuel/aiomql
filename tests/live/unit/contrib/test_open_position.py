"""Comprehensive tests for the open_position module.

Tests cover:
- PendingOrder dataclass initialization and attributes
- OpenPosition initialization and configuration
- Tracker management (add_tracker, trackers property)
- Position update and status
- Stop loss/take profit modification
- State management (remove_from_state)
- Pending order management
- Hedge and stack management
- Position closing
- Utility methods (update, profit_to_price)
"""

import pytest
from dataclasses import fields
from unittest.mock import MagicMock, AsyncMock, patch

from aiomql.contrib.trackers.open_position import PendingOrder, OpenPosition
from aiomql.core.models import TradePosition, OrderSendResult
from aiomql.core.constants import OrderType


class TestPendingOrder:
    """Tests for PendingOrder dataclass."""

    def test_pending_order_initialization(self):
        """Test PendingOrder can be initialized with required fields."""
        mock_order = MagicMock(spec=OrderSendResult)
        pending = PendingOrder(order=mock_order)
        assert pending.order is mock_order
        assert pending.is_hedge is False
        assert pending.is_stack is False
        assert pending.open_pos_params == {}

    def test_pending_order_as_hedge(self):
        """Test PendingOrder initialized as hedge."""
        mock_order = MagicMock(spec=OrderSendResult)
        pending = PendingOrder(order=mock_order, is_hedge=True)
        assert pending.is_hedge is True
        assert pending.is_stack is False

    def test_pending_order_as_stack(self):
        """Test PendingOrder initialized as stack."""
        mock_order = MagicMock(spec=OrderSendResult)
        pending = PendingOrder(order=mock_order, is_stack=True)
        assert pending.is_hedge is False
        assert pending.is_stack is True

    def test_pending_order_with_open_pos_params(self):
        """Test PendingOrder with custom open_pos_params."""
        mock_order = MagicMock(spec=OrderSendResult)
        params = {"close_hedges_on_close": True}
        pending = PendingOrder(order=mock_order, open_pos_params=params)
        assert pending.open_pos_params == params

    def test_pending_order_is_dataclass(self):
        """Test PendingOrder is a proper dataclass."""
        field_names = [f.name for f in fields(PendingOrder)]
        assert "order" in field_names
        assert "is_hedge" in field_names
        assert "is_stack" in field_names
        assert "open_pos_params" in field_names


class TestOpenPositionInitialization:
    """Tests for OpenPosition initialization."""

    @pytest.fixture
    def mock_symbol(self):
        """Creates a mock Symbol."""
        symbol = MagicMock()
        symbol.name = "EURUSD"
        return symbol

    @pytest.fixture
    def mock_position(self):
        """Creates a mock TradePosition."""
        position = MagicMock(spec=TradePosition)
        position.type = OrderType.BUY
        position.volume = 0.1
        position.price_open = 1.1000
        position.sl = 1.0950
        position.tp = 1.1050
        position.ticket = 12345
        return position

    @pytest.fixture
    def mock_config(self):
        """Mock the Config and state."""
        with patch("aiomql.contrib.trackers.open_position.Config") as mock_cfg:
            mock_cfg_instance = MagicMock()
            mock_cfg_instance.state = MagicMock()
            mock_cfg_instance.state.setdefault = MagicMock(return_value={})
            mock_cfg_instance.state.get = MagicMock(return_value={})
            mock_cfg.return_value = mock_cfg_instance
            yield mock_cfg_instance

    @pytest.fixture
    def mock_positions(self):
        """Mock the Positions class."""
        with patch("aiomql.contrib.trackers.open_position.Positions") as mock_pos:
            mock_pos_instance = MagicMock()
            mock_pos.return_value = mock_pos_instance
            yield mock_pos_instance

    @pytest.fixture
    def mock_position_tracker(self):
        """Mock the PositionTracker class."""
        with patch("aiomql.contrib.trackers.open_position.PositionTracker") as mock_tracker:
            yield mock_tracker

    def test_open_position_initialization(self, mock_symbol, mock_position, mock_config, mock_positions, mock_position_tracker):
        """Test OpenPosition can be initialized."""
        open_pos = OpenPosition(symbol=mock_symbol, ticket=12345, position=mock_position)
        assert open_pos.symbol is mock_symbol
        assert open_pos.ticket == 12345
        assert open_pos.position is mock_position

    def test_open_position_default_values(self, mock_symbol, mock_position, mock_config, mock_positions, mock_position_tracker):
        """Test OpenPosition has correct default values."""
        open_pos = OpenPosition(symbol=mock_symbol, ticket=12345, position=mock_position)
        assert open_pos.is_open is True
        assert open_pos.is_hedged is False
        assert open_pos.is_stacked is False
        assert open_pos.is_a_stack is False
        assert open_pos.is_a_hedge is False
        assert open_pos.hedge is None
        assert open_pos.stack is None
        assert open_pos.pending_orders == {}
        assert open_pos.hedges == {}
        assert open_pos.stacks == {}
        assert open_pos.close_pending_orders_on_close is True
        assert open_pos.remove_from_state_on_close is True
        assert open_pos.auto_track_closed is True
        assert open_pos.close_hedges_on_close is False
        assert open_pos.close_stacks_on_close is False

    def test_open_position_custom_values(self, mock_symbol, mock_position, mock_config, mock_positions, mock_position_tracker):
        """Test OpenPosition with custom values."""
        open_pos = OpenPosition(
            symbol=mock_symbol, 
            ticket=12345, 
            position=mock_position,
            close_hedges_on_close=True,
            close_stacks_on_close=True
        )
        assert open_pos.close_hedges_on_close is True
        assert open_pos.close_stacks_on_close is True

    def test_open_position_as_hedge(self, mock_symbol, mock_position, mock_config, mock_positions, mock_position_tracker):
        """Test OpenPosition initialized as a hedge."""
        parent = MagicMock()
        open_pos = OpenPosition(
            symbol=mock_symbol, 
            ticket=12345, 
            position=mock_position,
            is_a_hedge=True,
            hedge=parent
        )
        assert open_pos.is_a_hedge is True
        assert open_pos.hedge is parent

    def test_open_position_as_stack(self, mock_symbol, mock_position, mock_config, mock_positions, mock_position_tracker):
        """Test OpenPosition initialized as a stack."""
        parent = MagicMock()
        open_pos = OpenPosition(
            symbol=mock_symbol, 
            ticket=12345, 
            position=mock_position,
            is_a_stack=True,
            stack=parent
        )
        assert open_pos.is_a_stack is True
        assert open_pos.stack is parent


class TestOpenPositionTrackers:
    """Tests for OpenPosition tracker management."""

    @pytest.fixture
    def open_position(self):
        """Creates an OpenPosition instance with mocked dependencies."""
        with patch("aiomql.contrib.trackers.open_position.Config") as mock_cfg:
            mock_cfg_instance = MagicMock()
            mock_cfg_instance.state = MagicMock()
            mock_cfg_instance.state.setdefault = MagicMock(return_value={})
            mock_cfg.return_value = mock_cfg_instance
            
            with patch("aiomql.contrib.trackers.open_position.Positions"):
                with patch("aiomql.contrib.trackers.open_position.PositionTracker"):
                    mock_symbol = MagicMock()
                    mock_symbol.name = "EURUSD"
                    mock_position = MagicMock(spec=TradePosition)
                    mock_position.type = OrderType.BUY
                    open_pos = OpenPosition(symbol=mock_symbol, ticket=12345, position=mock_position)
                    open_pos._trackers = {}  # Reset trackers
                    yield open_pos

    def test_add_tracker(self, open_position):
        """Test adding a tracker."""
        mock_tracker = MagicMock()
        mock_tracker.rank = 5
        open_position.add_tracker(tracker=mock_tracker, name="test_tracker")
        assert "test_tracker" in open_position._trackers

    def test_add_tracker_with_custom_rank(self, open_position):
        """Test adding a tracker with custom rank."""
        mock_tracker = MagicMock()
        mock_tracker.rank = 5
        open_position.add_tracker(tracker=mock_tracker, name="test_tracker", rank=10)
        assert mock_tracker.rank == 10

    def test_add_tracker_auto_rank(self, open_position):
        """Test adding tracker with auto-generated rank."""
        mock_tracker = MagicMock()
        mock_tracker.rank = None
        open_position.add_tracker(tracker=mock_tracker, name="test_tracker")
        assert mock_tracker.rank == 1  # First tracker, rank = len(trackers) + 1 = 0 + 1

    def test_trackers_property_yields_in_order(self, open_position):
        """Test trackers property yields trackers in rank order."""
        tracker1 = MagicMock()
        tracker1.rank = 3
        tracker2 = MagicMock()
        tracker2.rank = 1
        tracker3 = MagicMock()
        tracker3.rank = 2
        
        open_position._trackers = {
            "tracker1": tracker1,
            "tracker2": tracker2,
            "tracker3": tracker3
        }
        
        trackers_list = list(open_position.trackers)
        assert trackers_list[0] is tracker2  # rank 1
        assert trackers_list[1] is tracker3  # rank 2
        assert trackers_list[2] is tracker1  # rank 3


class TestOpenPositionUpdate:
    """Tests for OpenPosition update methods."""

    @pytest.fixture
    def open_position(self):
        """Creates an OpenPosition instance with mocked dependencies."""
        with patch("aiomql.contrib.trackers.open_position.Config") as mock_cfg:
            mock_cfg_instance = MagicMock()
            mock_cfg_instance.state = MagicMock()
            mock_cfg_instance.state.setdefault = MagicMock(return_value={})
            mock_cfg.return_value = mock_cfg_instance
            
            with patch("aiomql.contrib.trackers.open_position.Positions") as mock_positions_cls:
                mock_positions = MagicMock()
                mock_positions_cls.return_value = mock_positions
                
                with patch("aiomql.contrib.trackers.open_position.PositionTracker"):
                    mock_symbol = MagicMock()
                    mock_symbol.name = "EURUSD"
                    mock_position = MagicMock(spec=TradePosition)
                    mock_position.type = OrderType.BUY
                    open_pos = OpenPosition(symbol=mock_symbol, ticket=12345, position=mock_position)
                    open_pos.positions = mock_positions
                    yield open_pos

    def test_update_method(self, open_position):
        """Test update method sets attributes."""
        open_position.update(is_hedged=True, is_stacked=True)
        assert open_position.is_hedged is True
        assert open_position.is_stacked is True

    async def test_update_position_when_open(self, open_position):
        """Test update_position when position is still open."""
        new_position = MagicMock(spec=TradePosition)
        open_position.positions.get_position_by_ticket = AsyncMock(return_value=new_position)
        
        result = await open_position.update_position()
        
        assert result is True
        assert open_position.is_open is True
        assert open_position.position is new_position

    async def test_update_position_when_closed(self, open_position):
        """Test update_position when position is closed."""
        open_position.positions.get_position_by_ticket = AsyncMock(return_value=None)
        
        result = await open_position.update_position()
        
        assert result is False
        assert open_position.is_open is False

    async def test_update_position_handles_exception(self, open_position):
        """Test update_position handles exceptions gracefully."""
        open_position.positions.get_position_by_ticket = AsyncMock(side_effect=Exception("Test error"))
        open_position.is_open = True
        
        result = await open_position.update_position()
        
        # Should return current is_open value on exception
        assert result is True


class TestOpenPositionStateManagement:
    """Tests for OpenPosition state management."""

    @pytest.fixture
    def open_position(self):
        """Creates an OpenPosition instance with mocked dependencies."""
        with patch("aiomql.contrib.trackers.open_position.Config") as mock_cfg:
            mock_cfg_instance = MagicMock()
            mock_state = {}
            mock_cfg_instance.state = MagicMock()
            mock_cfg_instance.state.get = MagicMock(side_effect=lambda key, default=None: mock_state.get(key, default if default else {}))
            mock_cfg_instance.state.setdefault = MagicMock(return_value={})
            mock_cfg.return_value = mock_cfg_instance
            
            with patch("aiomql.contrib.trackers.open_position.Positions"):
                with patch("aiomql.contrib.trackers.open_position.PositionTracker"):
                    mock_symbol = MagicMock()
                    mock_symbol.name = "EURUSD"
                    mock_position = MagicMock(spec=TradePosition)
                    mock_position.type = OrderType.BUY
                    open_pos = OpenPosition(symbol=mock_symbol, ticket=12345, position=mock_position)
                    open_pos.config = mock_cfg_instance
                    yield open_pos

    def test_remove_from_state(self, open_position):
        """Test remove_from_state removes position from tracked and archives it."""
        tracked_positions = {12345: open_position}
        archived_positions = {}
        
        open_position.config.state.get = MagicMock(side_effect=lambda key, default=None: 
            tracked_positions if key == "tracked_positions" else archived_positions)
        
        open_position.remove_from_state()
        
        assert 12345 not in tracked_positions
        assert 12345 in archived_positions


class TestOpenPositionPendingOrders:
    """Tests for OpenPosition pending order management."""

    @pytest.fixture
    def open_position(self):
        """Creates an OpenPosition instance with mocked dependencies."""
        with patch("aiomql.contrib.trackers.open_position.Config") as mock_cfg:
            mock_cfg_instance = MagicMock()
            mock_cfg_instance.state = MagicMock()
            mock_cfg_instance.state.setdefault = MagicMock(return_value={})
            mock_cfg.return_value = mock_cfg_instance
            
            with patch("aiomql.contrib.trackers.open_position.Positions"):
                with patch("aiomql.contrib.trackers.open_position.PositionTracker"):
                    mock_symbol = MagicMock()
                    mock_symbol.name = "EURUSD"
                    mock_position = MagicMock(spec=TradePosition)
                    mock_position.type = OrderType.BUY
                    open_pos = OpenPosition(symbol=mock_symbol, ticket=12345, position=mock_position)
                    yield open_pos

    async def test_close_pending_order_success(self, open_position):
        """Test closing a pending order successfully."""
        mock_order_result = MagicMock(spec=OrderSendResult)
        mock_order_result.order = 99999
        mock_order_result.request = MagicMock()
        mock_order_result.request.symbol = "EURUSD"
        
        pending_order = PendingOrder(order=mock_order_result, is_hedge=True)
        open_position.pending_orders[99999] = pending_order
        
        cancel_result = MagicMock()
        cancel_result.retcode = 10009
        
        with patch("aiomql.contrib.trackers.open_position.Order") as mock_order:
            mock_order.cancel_order = AsyncMock(return_value=cancel_result)
            
            success, result = await open_position.close_pending_order(pending_order=pending_order)
            
            assert success is True
            assert 99999 not in open_position.pending_orders

    async def test_close_pending_order_failure(self, open_position):
        """Test closing a pending order with failure."""
        mock_order_result = MagicMock(spec=OrderSendResult)
        mock_order_result.order = 99999
        mock_order_result.request = MagicMock()
        mock_order_result.request.symbol = "EURUSD"
        
        pending_order = PendingOrder(order=mock_order_result, is_hedge=True)
        open_position.pending_orders[99999] = pending_order
        
        cancel_result = MagicMock()
        cancel_result.retcode = 10001  # Not success
        cancel_result.comment = "Order not found"
        
        with patch("aiomql.contrib.trackers.open_position.Order") as mock_order:
            mock_order.cancel_order = AsyncMock(return_value=cancel_result)
            
            success, result = await open_position.close_pending_order(pending_order=pending_order)
            
            assert success is False
            assert result is pending_order

    async def test_close_pending_orders(self, open_position):
        """Test closing all pending orders."""
        mock_order1 = MagicMock(spec=OrderSendResult)
        mock_order1.order = 11111
        mock_order1.request = MagicMock()
        mock_order1.request.symbol = "EURUSD"
        
        mock_order2 = MagicMock(spec=OrderSendResult)
        mock_order2.order = 22222
        mock_order2.request = MagicMock()
        mock_order2.request.symbol = "EURUSD"
        
        pending1 = PendingOrder(order=mock_order1, is_hedge=True)
        pending2 = PendingOrder(order=mock_order2, is_stack=True)
        open_position.pending_orders = {11111: pending1, 22222: pending2}
        
        cancel_result = MagicMock()
        cancel_result.retcode = 10009
        
        with patch("aiomql.contrib.trackers.open_position.Order") as mock_order:
            mock_order.cancel_order = AsyncMock(return_value=cancel_result)
            
            results = await open_position.close_pending_orders()
            
            assert results is not None
            assert len(results) == 2


class TestOpenPositionClosing:
    """Tests for OpenPosition closing functionality."""

    @pytest.fixture
    def open_position(self):
        """Creates an OpenPosition instance with mocked dependencies."""
        with patch("aiomql.contrib.trackers.open_position.Config") as mock_cfg:
            mock_cfg_instance = MagicMock()
            mock_cfg_instance.state = MagicMock()
            mock_cfg_instance.state.setdefault = MagicMock(return_value={})
            mock_cfg_instance.state.get = MagicMock(return_value={})
            mock_cfg.return_value = mock_cfg_instance
            
            with patch("aiomql.contrib.trackers.open_position.Positions") as mock_positions_cls:
                mock_positions = MagicMock()
                mock_positions_cls.return_value = mock_positions
                
                with patch("aiomql.contrib.trackers.open_position.PositionTracker"):
                    mock_symbol = MagicMock()
                    mock_symbol.name = "EURUSD"
                    mock_position = MagicMock(spec=TradePosition)
                    mock_position.type = OrderType.BUY
                    open_pos = OpenPosition(symbol=mock_symbol, ticket=12345, position=mock_position)
                    open_pos.positions = mock_positions
                    open_pos.config = mock_cfg_instance
                    yield open_pos

    async def test_close_position_success(self, open_position):
        """Test closing position successfully."""
        close_result = MagicMock(spec=OrderSendResult)
        open_position.positions.close_position = AsyncMock(return_value=(True, close_result))
        
        success, result = await open_position.close_position()
        
        assert success is True
        assert open_position.is_open is False

    async def test_close_position_failure(self, open_position):
        """Test closing position with failure."""
        close_result = MagicMock(spec=OrderSendResult)
        close_result.comment = "Market closed"
        open_position.positions.close_position = AsyncMock(return_value=(False, close_result))
        
        success, result = await open_position.close_position()
        
        assert success is False
        assert result is close_result

    async def test_close_hedges(self, open_position):
        """Test closing all hedge positions."""
        hedge1 = MagicMock()
        hedge1.close_position = AsyncMock(return_value=(True, MagicMock()))
        hedge2 = MagicMock()
        hedge2.close_position = AsyncMock(return_value=(True, MagicMock()))
        
        open_position.hedges = {111: hedge1, 222: hedge2}
        
        await open_position.close_hedges()
        
        hedge1.close_position.assert_called_once()
        hedge2.close_position.assert_called_once()

    async def test_close_stacks(self, open_position):
        """Test closing all stack positions."""
        stack1 = MagicMock()
        stack1.close_position = AsyncMock(return_value=(True, MagicMock()))
        stack2 = MagicMock()
        stack2.close_position = AsyncMock(return_value=(True, MagicMock()))
        
        open_position.stacks = {111: stack1, 222: stack2}
        
        await open_position.close_stacks()
        
        stack1.close_position.assert_called_once()
        stack2.close_position.assert_called_once()


class TestOpenPositionTrack:
    """Tests for OpenPosition track method."""

    @pytest.fixture
    def open_position(self):
        """Creates an OpenPosition instance with mocked dependencies."""
        with patch("aiomql.contrib.trackers.open_position.Config") as mock_cfg:
            mock_cfg_instance = MagicMock()
            mock_cfg_instance.state = MagicMock()
            mock_cfg_instance.state.setdefault = MagicMock(return_value={})
            mock_cfg.return_value = mock_cfg_instance
            
            with patch("aiomql.contrib.trackers.open_position.Positions"):
                with patch("aiomql.contrib.trackers.open_position.PositionTracker"):
                    mock_symbol = MagicMock()
                    mock_symbol.name = "EURUSD"
                    mock_position = MagicMock(spec=TradePosition)
                    mock_position.type = OrderType.BUY
                    open_pos = OpenPosition(symbol=mock_symbol, ticket=12345, position=mock_position)
                    open_pos._trackers = {}
                    yield open_pos

    async def test_track_executes_all_trackers(self, open_position):
        """Test track executes all trackers in order."""
        tracker1 = AsyncMock()
        tracker1.rank = 1
        tracker2 = AsyncMock()
        tracker2.rank = 2
        
        open_position._trackers = {"t1": tracker1, "t2": tracker2}
        
        await open_position.track()
        
        tracker1.assert_called_once()
        tracker2.assert_called_once()


class TestOpenPositionHedgeAndStack:
    """Tests for OpenPosition hedge and stack methods."""

    @pytest.fixture
    def open_position(self):
        """Creates an OpenPosition instance with mocked dependencies."""
        with patch("aiomql.contrib.trackers.open_position.Config") as mock_cfg:
            mock_cfg_instance = MagicMock()
            mock_cfg_instance.state = MagicMock()
            mock_cfg_instance.state.setdefault = MagicMock(return_value={})
            mock_cfg.return_value = mock_cfg_instance
            
            with patch("aiomql.contrib.trackers.open_position.Positions") as mock_positions_cls:
                mock_positions = MagicMock()
                mock_positions_cls.return_value = mock_positions
                
                with patch("aiomql.contrib.trackers.open_position.PositionTracker"):
                    mock_symbol = MagicMock()
                    mock_symbol.name = "EURUSD"
                    mock_position = MagicMock(spec=TradePosition)
                    mock_position.type = OrderType.BUY
                    mock_position.volume = 0.1
                    open_pos = OpenPosition(symbol=mock_symbol, ticket=12345, position=mock_position)
                    open_pos.positions = mock_positions
                    yield open_pos

    async def test_hedge_order_success(self, open_position):
        """Test placing a hedge order successfully."""
        order_result = MagicMock(spec=OrderSendResult)
        order_result.retcode = 10009
        order_result.order = 99999
        
        with patch("aiomql.contrib.trackers.open_position.Order") as mock_order:
            mock_order_instance = MagicMock()
            mock_order_instance.send = AsyncMock(return_value=order_result)
            mock_order.return_value = mock_order_instance
            
            success, result = await open_position.hedge_order(price=1.0950)
            
            assert success is True
            assert open_position.is_hedged is True
            assert 99999 in open_position.pending_orders

    async def test_hedge_order_failure(self, open_position):
        """Test placing a hedge order with failure."""
        order_result = MagicMock(spec=OrderSendResult)
        order_result.retcode = 10001
        order_result.comment = "Invalid price"
        
        with patch("aiomql.contrib.trackers.open_position.Order") as mock_order:
            mock_order_instance = MagicMock()
            mock_order_instance.send = AsyncMock(return_value=order_result)
            mock_order.return_value = mock_order_instance
            
            success, result = await open_position.hedge_order(price=1.0950)
            
            assert success is False

    async def test_stack_order_success(self, open_position):
        """Test placing a stack order successfully."""
        order_result = MagicMock(spec=OrderSendResult)
        order_result.retcode = 10009
        order_result.order = 88888
        
        with patch("aiomql.contrib.trackers.open_position.Order") as mock_order:
            mock_order_instance = MagicMock()
            mock_order_instance.send = AsyncMock(return_value=order_result)
            mock_order.return_value = mock_order_instance
            
            success, result = await open_position.stack_order(price=1.1050)
            
            assert success is True
            assert open_position.is_stacked is True
            assert 88888 in open_position.pending_orders

    async def test_check_pending_order_creates_hedge(self, open_position):
        """Test check_pending_order creates hedge when filled."""
        mock_order_result = MagicMock(spec=OrderSendResult)
        mock_order_result.order = 99999
        
        pending = PendingOrder(order=mock_order_result, is_hedge=True)
        
        new_position = MagicMock(spec=TradePosition)
        new_position.ticket = 99999
        open_position.positions.get_position_by_ticket = AsyncMock(return_value=new_position)
        
        with patch("aiomql.contrib.trackers.open_position.OpenPosition") as mock_open_pos:
            mock_hedge = MagicMock()
            mock_open_pos.return_value = mock_hedge
            
            await open_position.check_pending_order(pending_order=pending)
            
            assert 99999 in open_position.hedges

    async def test_check_pending_order_creates_stack(self, open_position):
        """Test check_pending_order creates stack when filled."""
        mock_order_result = MagicMock(spec=OrderSendResult)
        mock_order_result.order = 88888
        
        pending = PendingOrder(order=mock_order_result, is_stack=True)
        
        new_position = MagicMock(spec=TradePosition)
        new_position.ticket = 88888
        open_position.positions.get_position_by_ticket = AsyncMock(return_value=new_position)
        
        with patch("aiomql.contrib.trackers.open_position.OpenPosition") as mock_open_pos:
            mock_stack = MagicMock()
            mock_open_pos.return_value = mock_stack
            
            await open_position.check_pending_order(pending_order=pending)
            
            assert 88888 in open_position.stacks

    async def test_check_pending_order_not_filled(self, open_position):
        """Test check_pending_order does nothing when not filled."""
        mock_order_result = MagicMock(spec=OrderSendResult)
        mock_order_result.order = 99999
        
        pending = PendingOrder(order=mock_order_result, is_hedge=True)
        
        open_position.positions.get_position_by_ticket = AsyncMock(return_value=None)
        
        await open_position.check_pending_order(pending_order=pending)
        
        assert 99999 not in open_position.hedges


class TestOpenPositionRemoveClosed:
    """Tests for OpenPosition remove_closed method."""

    @pytest.fixture
    def open_position(self):
        """Creates an OpenPosition instance with mocked dependencies."""
        with patch("aiomql.contrib.trackers.open_position.Config") as mock_cfg:
            mock_cfg_instance = MagicMock()
            mock_cfg_instance.state = MagicMock()
            mock_cfg_instance.state.setdefault = MagicMock(return_value={})
            mock_cfg_instance.state.get = MagicMock(return_value={})
            mock_cfg.return_value = mock_cfg_instance
            
            with patch("aiomql.contrib.trackers.open_position.Positions") as mock_positions_cls:
                mock_positions = MagicMock()
                mock_positions_cls.return_value = mock_positions
                
                with patch("aiomql.contrib.trackers.open_position.PositionTracker"):
                    mock_symbol = MagicMock()
                    mock_symbol.name = "EURUSD"
                    mock_position = MagicMock(spec=TradePosition)
                    mock_position.type = OrderType.BUY
                    open_pos = OpenPosition(symbol=mock_symbol, ticket=12345, position=mock_position)
                    open_pos.positions = mock_positions
                    open_pos.config = mock_cfg_instance
                    yield open_pos

    async def test_remove_closed_when_still_open(self, open_position):
        """Test remove_closed does nothing when position is still open."""
        open_position.positions.get_position_by_ticket = AsyncMock(return_value=MagicMock())
        open_position.remove_from_state = MagicMock()
        
        await open_position.remove_closed()
        
        open_position.remove_from_state.assert_not_called()

    async def test_remove_closed_when_closed(self, open_position):
        """Test remove_closed performs cleanup when position is closed."""
        open_position.positions.get_position_by_ticket = AsyncMock(return_value=None)
        open_position.close_pending_orders = AsyncMock()
        open_position.close_hedges = AsyncMock()
        open_position.close_stacks = AsyncMock()
        open_position.remove_from_state = MagicMock()
        
        open_position.close_pending_orders_on_close = True
        open_position.remove_from_state_on_close = True
        open_position.close_hedges_on_close = False
        open_position.close_stacks_on_close = False
        
        await open_position.remove_closed()
        
        open_position.close_pending_orders.assert_called_once()
        open_position.remove_from_state.assert_called_once()
        open_position.close_hedges.assert_not_called()
        open_position.close_stacks.assert_not_called()
