"""Comprehensive tests for the position_trackers module.

Tests cover:
- PositionTracker initialization and configuration
- PositionTracker callable behavior
- PositionTracker set_tracker method
- OpenPositionsTracker initialization
- OpenPositionsTracker track loop
- OpenPositionsTracker remove_closed_positions
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from aiomql.contrib.trackers.position_trackers import PositionTracker, OpenPositionsTracker


class TestPositionTrackerInitialization:
    """Tests for PositionTracker initialization."""

    def test_init_with_required_args(self):
        """Test PositionTracker can be initialized with required args."""
        mock_open_position = MagicMock()
        mock_open_position.add_tracker = MagicMock()
        mock_function = MagicMock()
        mock_function.__name__ = "test_function"
        
        tracker = PositionTracker(mock_open_position, mock_function)
        
        assert tracker.open_position is mock_open_position
        assert tracker.function is mock_function
        assert tracker.name == "test_function"
        assert tracker.rank is None
        assert tracker.params == {}

    def test_init_with_custom_name(self):
        """Test PositionTracker with custom name."""
        mock_open_position = MagicMock()
        mock_open_position.add_tracker = MagicMock()
        mock_function = MagicMock()
        mock_function.__name__ = "original_name"
        
        tracker = PositionTracker(mock_open_position, mock_function, name="custom_tracker")
        
        assert tracker.name == "custom_tracker"

    def test_init_with_rank(self):
        """Test PositionTracker with rank."""
        mock_open_position = MagicMock()
        mock_open_position.add_tracker = MagicMock()
        mock_function = MagicMock()
        mock_function.__name__ = "test_function"
        
        tracker = PositionTracker(mock_open_position, mock_function, rank=5)
        
        assert tracker.rank == 5

    def test_init_with_function_params(self):
        """Test PositionTracker with function parameters."""
        mock_open_position = MagicMock()
        mock_open_position.add_tracker = MagicMock()
        mock_function = MagicMock()
        mock_function.__name__ = "test_function"
        params = {"sl": 1.0950, "tp": 1.1050}
        
        tracker = PositionTracker(mock_open_position, mock_function, function_params=params)
        
        assert tracker.params == params

    def test_init_calls_set_tracker(self):
        """Test PositionTracker calls set_tracker on init."""
        mock_open_position = MagicMock()
        mock_open_position.add_tracker = MagicMock()
        mock_function = MagicMock()
        mock_function.__name__ = "test_function"
        
        tracker = PositionTracker(mock_open_position, mock_function, name="my_tracker", rank=3)
        
        mock_open_position.add_tracker.assert_called_once_with(
            tracker=tracker, name="my_tracker", rank=3
        )


class TestPositionTrackerCall:
    """Tests for PositionTracker __call__ method."""

    async def test_call_executes_function(self):
        """Test __call__ executes the tracking function."""
        mock_open_position = MagicMock()
        mock_open_position.add_tracker = MagicMock()
        mock_open_position.symbol = MagicMock()
        mock_open_position.symbol.name = "EURUSD"
        mock_open_position.ticket = 12345
        mock_function = AsyncMock()
        mock_function.__name__ = "test_function"
        
        tracker = PositionTracker(mock_open_position, mock_function)
        await tracker()
        
        mock_function.assert_called_once_with(mock_open_position)

    async def test_call_with_params(self):
        """Test __call__ passes configured params."""
        mock_open_position = MagicMock()
        mock_open_position.add_tracker = MagicMock()
        mock_function = AsyncMock()
        mock_function.__name__ = "test_function"
        params = {"sl": 1.0950, "tp": 1.1050}
        
        tracker = PositionTracker(mock_open_position, mock_function, function_params=params)
        await tracker()
        
        mock_function.assert_called_once_with(mock_open_position, sl=1.0950, tp=1.1050)

    async def test_call_with_kwargs(self):
        """Test __call__ accepts additional kwargs."""
        mock_open_position = MagicMock()
        mock_open_position.add_tracker = MagicMock()
        mock_function = AsyncMock()
        mock_function.__name__ = "test_function"
        
        tracker = PositionTracker(mock_open_position, mock_function)
        await tracker(extra_param="value")
        
        mock_function.assert_called_once_with(mock_open_position, extra_param="value")

    async def test_call_kwargs_override_params(self):
        """Test __call__ kwargs override configured params."""
        mock_open_position = MagicMock()
        mock_open_position.add_tracker = MagicMock()
        mock_function = AsyncMock()
        mock_function.__name__ = "test_function"
        params = {"sl": 1.0950}
        
        tracker = PositionTracker(mock_open_position, mock_function, function_params=params)
        await tracker(sl=1.0900)  # Override sl
        
        mock_function.assert_called_once_with(mock_open_position, sl=1.0900)

    async def test_call_handles_exception(self):
        """Test __call__ handles exceptions gracefully."""
        mock_open_position = MagicMock()
        mock_open_position.add_tracker = MagicMock()
        mock_open_position.symbol = MagicMock()
        mock_open_position.symbol.name = "EURUSD"
        mock_open_position.ticket = 12345
        mock_function = AsyncMock(side_effect=Exception("Test error"))
        mock_function.__name__ = "test_function"
        
        tracker = PositionTracker(mock_open_position, mock_function)
        
        # Should not raise, just log
        await tracker()


class TestPositionTrackerSetTracker:
    """Tests for PositionTracker set_tracker method."""

    def test_set_tracker_adds_to_open_position(self):
        """Test set_tracker adds tracker to open position."""
        mock_open_position = MagicMock()
        mock_open_position.add_tracker = MagicMock()
        mock_function = MagicMock()
        mock_function.__name__ = "test_function"
        
        tracker = PositionTracker(mock_open_position, mock_function)
        mock_open_position.add_tracker.reset_mock()
        
        tracker.set_tracker()
        
        mock_open_position.add_tracker.assert_called_once_with(
            tracker=tracker, name="test_function", rank=None
        )

    def test_set_tracker_with_new_name_and_rank(self):
        """Test set_tracker with new name and rank."""
        mock_open_position = MagicMock()
        mock_open_position.add_tracker = MagicMock()
        mock_function = MagicMock()
        mock_function.__name__ = "test_function"
        
        tracker = PositionTracker(mock_open_position, mock_function)
        mock_open_position.add_tracker.reset_mock()
        
        tracker.set_tracker(name="new_name", rank=10)
        
        mock_open_position.add_tracker.assert_called_once_with(
            tracker=tracker, name="new_name", rank=10
        )


class TestOpenPositionsTrackerInitialization:
    """Tests for OpenPositionsTracker initialization."""

    @pytest.fixture(autouse=True)
    def reset_class_attributes(self):
        """Reset class attributes before each test."""
        if hasattr(OpenPositionsTracker, "config"):
            delattr(OpenPositionsTracker, "config")
        if hasattr(OpenPositionsTracker, "positions"):
            delattr(OpenPositionsTracker, "positions")
        if hasattr(OpenPositionsTracker, "state"):
            delattr(OpenPositionsTracker, "state")
        yield

    def test_init_default_values(self):
        """Test OpenPositionsTracker with default values."""
        with patch("aiomql.contrib.trackers.position_trackers.Config"):
            with patch("aiomql.contrib.trackers.position_trackers.Positions"):
                with patch("aiomql.contrib.trackers.position_trackers.State"):
                    tracker = OpenPositionsTracker()
                    
                    assert tracker.interval == 10
                    assert tracker.state_key == "tracked_positions"
                    assert tracker.autocommit is False
                    assert tracker.auto_remove_closed is False

    def test_init_custom_values(self):
        """Test OpenPositionsTracker with custom values."""
        with patch("aiomql.contrib.trackers.position_trackers.Config"):
            with patch("aiomql.contrib.trackers.position_trackers.Positions"):
                with patch("aiomql.contrib.trackers.position_trackers.State"):
                    tracker = OpenPositionsTracker(
                        interval=30,
                        state_key="my_positions",
                        autocommit=True,
                        auto_remove_closed=True
                    )
                    
                    assert tracker.interval == 30
                    assert tracker.state_key == "my_positions"
                    assert tracker.autocommit is True
                    assert tracker.auto_remove_closed is True

    def test_new_initializes_class_attributes(self):
        """Test __new__ initializes class-level config, positions, state."""
        with patch("aiomql.contrib.trackers.position_trackers.Config") as mock_cfg:
            with patch("aiomql.contrib.trackers.position_trackers.Positions") as mock_pos:
                with patch("aiomql.contrib.trackers.position_trackers.State") as mock_state:
                    tracker = OpenPositionsTracker()
                    
                    mock_cfg.assert_called()
                    mock_pos.assert_called()
                    mock_state.assert_called()


class TestOpenPositionsTrackerTrack:
    """Tests for OpenPositionsTracker track method."""

    @pytest.fixture(autouse=True)
    def reset_class_attributes(self):
        """Reset class attributes before each test."""
        if hasattr(OpenPositionsTracker, "config"):
            delattr(OpenPositionsTracker, "config")
        if hasattr(OpenPositionsTracker, "positions"):
            delattr(OpenPositionsTracker, "positions")
        if hasattr(OpenPositionsTracker, "state"):
            delattr(OpenPositionsTracker, "state")
        yield

    async def test_track_executes_trackers_on_positions(self):
        """Test track executes all trackers on all positions."""
        mock_config = MagicMock()
        mock_config.shutdown = False
        
        call_count = 0
        async def mock_sleep(secs):
            nonlocal call_count
            call_count += 1
            if call_count >= 1:
                mock_config.shutdown = True
        
        mock_position1 = MagicMock()
        mock_position1.track = AsyncMock()
        mock_position2 = MagicMock()
        mock_position2.track = AsyncMock()
        
        mock_state = MagicMock()
        mock_state.conn = MagicMock()
        mock_state.conn.close = MagicMock()
        mock_state.get = MagicMock(return_value={1: mock_position1, 2: mock_position2})
        
        with patch("aiomql.contrib.trackers.position_trackers.Config", return_value=mock_config):
            with patch("aiomql.contrib.trackers.position_trackers.Positions"):
                with patch("aiomql.contrib.trackers.position_trackers.State", return_value=mock_state):
                    with patch("aiomql.contrib.trackers.position_trackers.sleep", side_effect=mock_sleep):
                        tracker = OpenPositionsTracker()
                        tracker.config = mock_config
                        tracker.state = mock_state
                        
                        await tracker.track()
                        
                        mock_position1.track.assert_called()
                        mock_position2.track.assert_called()

    async def test_track_stops_on_shutdown(self):
        """Test track stops when shutdown is True."""
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        
        mock_config_state = MagicMock()
        mock_config_state.conn = mock_conn
        
        mock_config = MagicMock()
        mock_config.shutdown = True  # Start with shutdown True
        mock_config.state = mock_config_state
        
        mock_state = MagicMock()
        
        with patch("aiomql.contrib.trackers.position_trackers.Config", return_value=mock_config):
            with patch("aiomql.contrib.trackers.position_trackers.Positions"):
                with patch("aiomql.contrib.trackers.position_trackers.State", return_value=mock_state):
                    tracker = OpenPositionsTracker()
                    tracker.config = mock_config
                    tracker.state = mock_state
                    
                    await tracker.track()
                    
                    # Should have closed the connection
                    mock_conn.close.assert_called_once()

    async def test_track_auto_remove_closed(self):
        """Test track calls remove_closed_positions when enabled."""
        mock_config = MagicMock()
        mock_config.shutdown = False
        
        call_count = 0
        async def mock_sleep(secs):
            nonlocal call_count
            call_count += 1
            if call_count >= 1:
                mock_config.shutdown = True
        
        mock_state = MagicMock()
        mock_state.conn = MagicMock()
        mock_state.conn.close = MagicMock()
        mock_state.get = MagicMock(return_value={})
        
        with patch("aiomql.contrib.trackers.position_trackers.Config", return_value=mock_config):
            with patch("aiomql.contrib.trackers.position_trackers.Positions"):
                with patch("aiomql.contrib.trackers.position_trackers.State", return_value=mock_state):
                    with patch("aiomql.contrib.trackers.position_trackers.sleep", side_effect=mock_sleep):
                        tracker = OpenPositionsTracker(auto_remove_closed=True)
                        tracker.config = mock_config
                        tracker.state = mock_state
                        tracker.remove_closed_positions = AsyncMock()
                        
                        await tracker.track()
                        
                        tracker.remove_closed_positions.assert_called()

    async def test_track_autocommit(self):
        """Test track calls acommit when autocommit enabled."""
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        
        mock_config_state = MagicMock()
        mock_config_state.conn = mock_conn
        
        mock_config = MagicMock()
        mock_config.shutdown = False
        mock_config.state = mock_config_state
        
        call_count = 0
        async def mock_sleep(secs):
            nonlocal call_count
            call_count += 1
            if call_count >= 1:
                mock_config.shutdown = True
        
        mock_state = MagicMock()
        mock_state.get = MagicMock(return_value={})
        mock_state.acommit = AsyncMock()
        
        with patch("aiomql.contrib.trackers.position_trackers.Config", return_value=mock_config):
            with patch("aiomql.contrib.trackers.position_trackers.Positions"):
                with patch("aiomql.contrib.trackers.position_trackers.State", return_value=mock_state):
                    with patch("aiomql.contrib.trackers.position_trackers.sleep", side_effect=mock_sleep):
                        tracker = OpenPositionsTracker(autocommit=True)
                        tracker.config = mock_config
                        tracker.state = mock_state
                        
                        await tracker.track()
                        
                        mock_state.acommit.assert_called_with(conn=mock_conn, close=False)


class TestOpenPositionsTrackerRemoveClosed:
    """Tests for OpenPositionsTracker remove_closed_positions method."""

    @pytest.fixture(autouse=True)
    def reset_class_attributes(self):
        """Reset class attributes before each test."""
        if hasattr(OpenPositionsTracker, "config"):
            delattr(OpenPositionsTracker, "config")
        if hasattr(OpenPositionsTracker, "positions"):
            delattr(OpenPositionsTracker, "positions")
        if hasattr(OpenPositionsTracker, "state"):
            delattr(OpenPositionsTracker, "state")
        yield

    async def test_remove_closed_positions_keeps_open(self):
        """Test remove_closed_positions keeps only open positions."""
        mock_positions = MagicMock()
        
        # Simulate two open positions from broker
        broker_pos1 = MagicMock()
        broker_pos1.ticket = 111
        broker_pos2 = MagicMock()
        broker_pos2.ticket = 222
        mock_positions.get_positions = AsyncMock(return_value=(broker_pos1, broker_pos2))
        
        # Tracked positions include one closed position
        tracked_pos1 = MagicMock()
        tracked_pos1.ticket = 111
        tracked_pos2 = MagicMock()
        tracked_pos2.ticket = 222
        tracked_pos3 = MagicMock()  # This one is closed
        tracked_pos3.ticket = 333
        
        tracked_positions = {111: tracked_pos1, 222: tracked_pos2, 333: tracked_pos3}
        
        mock_state = MagicMock()
        mock_state.__setitem__ = MagicMock()
        
        with patch("aiomql.contrib.trackers.position_trackers.Config"):
            with patch("aiomql.contrib.trackers.position_trackers.Positions", return_value=mock_positions):
                with patch("aiomql.contrib.trackers.position_trackers.State", return_value=mock_state):
                    tracker = OpenPositionsTracker(state_key="tracked_positions")
                    tracker.positions = mock_positions
                    tracker.state = mock_state
                    
                    await tracker.remove_closed_positions(tracked_positions)
                    
                    # Should have set state with only open positions
                    call_args = mock_state.__setitem__.call_args
                    assert call_args[0][0] == "tracked_positions"
                    # Position 333 should be removed
                    result_dict = call_args[0][1]
                    assert 111 in result_dict
                    assert 222 in result_dict
                    assert 333 not in result_dict

    async def test_remove_closed_positions_removes_all_when_none_open(self):
        """Test remove_closed_positions removes all when no positions open."""
        mock_positions = MagicMock()
        mock_positions.get_positions = AsyncMock(return_value=())  # No open positions
        
        tracked_pos1 = MagicMock()
        tracked_pos1.ticket = 111
        tracked_positions = {111: tracked_pos1}
        
        mock_state = MagicMock()
        mock_state.__setitem__ = MagicMock()
        
        with patch("aiomql.contrib.trackers.position_trackers.Config"):
            with patch("aiomql.contrib.trackers.position_trackers.Positions", return_value=mock_positions):
                with patch("aiomql.contrib.trackers.position_trackers.State", return_value=mock_state):
                    tracker = OpenPositionsTracker(state_key="tracked_positions")
                    tracker.positions = mock_positions
                    tracker.state = mock_state
                    
                    await tracker.remove_closed_positions(tracked_positions)
                    
                    call_args = mock_state.__setitem__.call_args
                    result_dict = call_args[0][1]
                    assert result_dict == {}
