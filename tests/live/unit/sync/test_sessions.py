"""Comprehensive tests for the synchronous Sessions module.

Tests cover:
- Duration NamedTuple
- delta helper function
- Session initialization and attributes
- Session __contains__, __str__, __repr__, __len__
- Session in_session method
- Session begin and close methods
- Session duration method
- Session close_positions, close_all, close_win, close_loss methods
- Session action method
- Session until method
- Sessions initialization
- Sessions find and find_next methods
- Sessions __contains__
- Sessions context manager
- Sessions check method
- Integration tests
"""

from datetime import time, datetime, timedelta, UTC
from unittest.mock import MagicMock, patch
import pytest

from aiomql.lib.sync.sessions import Session, Sessions, Duration, delta
from aiomql.core.config import Config
from aiomql.core.models import TradePosition, OrderSendResult


class TestDuration:
    """Test Duration NamedTuple."""

    def test_duration_creation(self):
        """Test creating Duration with values."""
        d = Duration(hours=2, minutes=30, seconds=45)
        assert d.hours == 2
        assert d.minutes == 30
        assert d.seconds == 45

    def test_duration_unpacking(self):
        """Test Duration can be unpacked."""
        d = Duration(hours=1, minutes=15, seconds=30)
        hours, minutes, seconds = d
        assert hours == 1
        assert minutes == 15
        assert seconds == 30

    def test_duration_is_tuple(self):
        """Test Duration is a tuple subclass."""
        d = Duration(hours=1, minutes=0, seconds=0)
        assert isinstance(d, tuple)


class TestDeltaFunction:
    """Test delta helper function."""

    def test_delta_basic_time(self):
        """Test delta with basic time."""
        t = time(hour=2, minute=30, second=45)
        result = delta(t)
        expected = timedelta(hours=2, minutes=30, seconds=45)
        assert result == expected

    def test_delta_midnight(self):
        """Test delta with midnight."""
        t = time(hour=0, minute=0, second=0)
        result = delta(t)
        assert result == timedelta(0)

    def test_delta_with_microseconds(self):
        """Test delta includes microseconds."""
        t = time(hour=1, minute=2, second=3, microsecond=456789)
        result = delta(t)
        expected = timedelta(hours=1, minutes=2, seconds=3, microseconds=456789)
        assert result == expected

    def test_delta_end_of_day(self):
        """Test delta with end of day time."""
        t = time(hour=23, minute=59, second=59)
        result = delta(t)
        expected = timedelta(hours=23, minutes=59, seconds=59)
        assert result == expected


class TestSessionInitialization:
    """Test Session class initialization."""

    def test_init_with_time_objects(self):
        """Test Session init with datetime.time objects."""
        start = time(8, 0)
        end = time(16, 0)
        session = Session(start=start, end=end)

        assert session.start.hour == 8
        assert session.end.hour == 16
        assert session.start.tzinfo == UTC

    def test_init_with_integers(self):
        """Test Session init with integer hours."""
        session = Session(start=9, end=17)

        assert session.start.hour == 9
        assert session.end.hour == 17
        assert session.start.tzinfo == UTC

    def test_init_with_on_start(self):
        """Test Session init with on_start action."""
        session = Session(start=8, end=16, on_start="close_all")
        assert session.on_start == "close_all"

    def test_init_with_on_end(self):
        """Test Session init with on_end action."""
        session = Session(start=8, end=16, on_end="close_loss")
        assert session.on_end == "close_loss"

    def test_init_with_custom_functions(self):
        """Test Session init with custom start/end functions."""
        def my_start():
            pass

        def my_end():
            pass

        session = Session(start=8, end=16, custom_start=my_start, custom_end=my_end)
        assert session.custom_start == my_start
        assert session.custom_end == my_end

    def test_init_with_name(self):
        """Test Session init with custom name."""
        session = Session(start=8, end=16, name="Morning Session")
        assert session.name == "Morning Session"

    def test_init_default_name(self):
        """Test Session generates default name."""
        session = Session(start=8, end=16)
        assert "<-->" in session.name

    def test_init_creates_positions_manager(self):
        """Test Session creates positions manager."""
        session = Session(start=8, end=16)
        assert session.positions_manager is not None

    def test_init_creates_config(self):
        """Test Session creates config."""
        session = Session(start=8, end=16)
        assert isinstance(session.config, Config)


class TestSessionContains:
    """Test Session __contains__ method."""

    def test_contains_time_in_session(self):
        """Test time within session returns True."""
        session = Session(start=8, end=16)
        test_time = time(12, 0)
        assert test_time in session

    def test_contains_time_at_start(self):
        """Test time at start of session."""
        session = Session(start=8, end=16)
        test_time = time(8, 0)
        assert test_time in session

    def test_contains_time_at_end(self):
        """Test time at end of session."""
        session = Session(start=8, end=16)
        test_time = time(16, 0)
        assert test_time in session

    def test_contains_time_before_session(self):
        """Test time before session returns False."""
        session = Session(start=8, end=16)
        test_time = time(7, 0)
        assert test_time not in session

    def test_contains_time_after_session(self):
        """Test time after session returns False."""
        session = Session(start=8, end=16)
        test_time = time(17, 0)
        assert test_time not in session


class TestSessionStringMethods:
    """Test Session string representation methods."""

    def test_str(self):
        """Test __str__ returns formatted string."""
        session = Session(start=8, end=16)
        result = str(session)
        assert "<-->" in result

    def test_repr(self):
        """Test __repr__ returns formatted string."""
        session = Session(start=8, end=16)
        result = repr(session)
        assert "<-->" in result


class TestSessionLen:
    """Test Session __len__ method."""

    def test_len_full_hours(self):
        """Test __len__ returns duration in seconds."""
        session = Session(start=8, end=16)
        expected = 8 * 3600  # 8 hours in seconds
        assert len(session) == expected

    def test_len_partial_hours(self):
        """Test __len__ with partial hours."""
        session = Session(start=time(8, 30), end=time(16, 45))
        expected = 8 * 3600 + 15 * 60  # 8 hours 15 minutes
        assert len(session) == expected


class TestSessionDuration:
    """Test Session duration method."""

    def test_duration_returns_duration_tuple(self):
        """Test duration returns Duration NamedTuple."""
        session = Session(start=8, end=16)
        result = session.duration()
        assert isinstance(result, Duration)

    def test_duration_values(self):
        """Test duration returns correct values."""
        session = Session(start=8, end=16)
        result = session.duration()
        assert result.hours == 8
        assert result.minutes == 0
        assert result.seconds == 0

    def test_duration_with_partial_hours(self):
        """Test duration with non-full hours."""
        session = Session(start=time(8, 0), end=time(10, 30, 45))
        result = session.duration()
        assert result.hours == 2
        assert result.minutes == 30
        assert result.seconds == 45


class TestSessionInSession:
    """Test Session in_session method."""

    @patch.object(Config, '__new__')
    def test_in_session_live_mode(self, mock_config):
        """Test in_session in live mode."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        # Test depends on current time, just verify it runs
        session = Session(start=0, end=23)
        result = session.in_session()
        assert isinstance(result, bool)


class TestSessionActions:
    """Test Session action methods."""

    @pytest.fixture
    def session(self):
        """Create a session for testing."""
        return Session(start=8, end=16)

    def test_begin_calls_action(self, session):
        """Test begin calls action with on_start."""
        session.on_start = "close_all"
        session.close_all = MagicMock()
        session.begin()
        session.close_all.assert_called_once()

    def test_close_calls_action(self, session):
        """Test close calls action with on_end."""
        session.on_end = "close_loss"
        session.close_loss = MagicMock()
        session.close()
        session.close_loss.assert_called_once()

    def test_action_close_all(self, session):
        """Test action dispatches to close_all."""
        session.close_all = MagicMock()
        session.action(action="close_all")
        session.close_all.assert_called_once()

    def test_action_close_win(self, session):
        """Test action dispatches to close_win."""
        session.close_win = MagicMock()
        session.action(action="close_win")
        session.close_win.assert_called_once()

    def test_action_close_loss(self, session):
        """Test action dispatches to close_loss."""
        session.close_loss = MagicMock()
        session.action(action="close_loss")
        session.close_loss.assert_called_once()

    def test_action_custom_start(self, session):
        """Test action calls custom_start."""
        session.custom_start = MagicMock()
        session.action(action="custom_start")
        session.custom_start.assert_called_once()

    def test_action_custom_end(self, session):
        """Test action calls custom_end."""
        session.custom_end = MagicMock()
        session.action(action="custom_end")
        session.custom_end.assert_called_once()

    def test_action_none_does_nothing(self, session):
        """Test action with None does nothing."""
        # Should not raise
        session.action(action=None)

    def test_action_handles_exception(self, session):
        """Test action handles exceptions gracefully."""
        session.close_all = MagicMock(side_effect=Exception("Test error"))
        # Should not raise, just log warning
        session.action(action="close_all")


class TestSessionClosePositions:
    """Test Session position closing methods."""

    @pytest.fixture
    def session(self):
        """Create a session for testing."""
        return Session(start=8, end=16)

    def test_close_positions(self, session):
        """Test close_positions calls positions manager."""
        position = MagicMock(spec=TradePosition)
        result = MagicMock(spec=OrderSendResult)
        result.retcode = 10009

        session.positions_manager.close_position = MagicMock(return_value=result)
        session.close_positions(positions=(position,))
        session.positions_manager.close_position.assert_called_once_with(position=position)

    def test_close_all(self, session):
        """Test close_all gets and closes all positions."""
        positions = (MagicMock(spec=TradePosition),)
        session.positions_manager.get_positions = MagicMock(return_value=positions)
        session.close_positions = MagicMock()

        session.close_all()
        session.positions_manager.get_positions.assert_called_once()
        session.close_positions.assert_called_once_with(positions=positions)

    def test_close_win_filters_profit(self, session):
        """Test close_win only closes profitable positions."""
        win_pos = MagicMock(spec=TradePosition)
        win_pos.profit = 100
        loss_pos = MagicMock(spec=TradePosition)
        loss_pos.profit = -50

        session.positions_manager.get_positions = MagicMock(return_value=(win_pos, loss_pos))
        session.close_positions = MagicMock()

        session.close_win()
        session.close_positions.assert_called_once()
        closed_positions = session.close_positions.call_args[1]["positions"]
        assert win_pos in closed_positions
        assert loss_pos not in closed_positions

    def test_close_loss_filters_loss(self, session):
        """Test close_loss only closes losing positions."""
        win_pos = MagicMock(spec=TradePosition)
        win_pos.profit = 100
        loss_pos = MagicMock(spec=TradePosition)
        loss_pos.profit = -50

        session.positions_manager.get_positions = MagicMock(return_value=(win_pos, loss_pos))
        session.close_positions = MagicMock()

        session.close_loss()
        session.close_positions.assert_called_once()
        closed_positions = session.close_positions.call_args[1]["positions"]
        assert loss_pos in closed_positions
        assert win_pos not in closed_positions


class TestSessionUntil:
    """Test Session until method."""

    @patch.object(Config, '__new__')
    def test_until_returns_seconds(self, mock_config):
        """Test until returns seconds until session start."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        session = Session(start=23, end=0)  # Future session
        result = session.until()
        assert isinstance(result, int)
        assert result >= 0


class TestSessionsInitialization:
    """Test Sessions class initialization."""

    def test_init_with_sessions(self):
        """Test Sessions init with list of Session objects."""
        s1 = Session(start=8, end=12)
        s2 = Session(start=13, end=17)
        sessions = Sessions(sessions=[s1, s2])

        assert len(sessions.sessions) == 2
        assert sessions.current_session is None

    def test_init_sorts_sessions(self):
        """Test Sessions sorts by start time."""
        s1 = Session(start=13, end=17)
        s2 = Session(start=8, end=12)
        sessions = Sessions(sessions=[s1, s2])

        assert sessions.sessions[0].start.hour == 8
        assert sessions.sessions[1].start.hour == 13

    def test_init_creates_config(self):
        """Test Sessions creates config."""
        s1 = Session(start=8, end=12)
        sessions = Sessions(sessions=[s1])
        assert isinstance(sessions.config, Config)


class TestSessionsFind:
    """Test Sessions find method."""

    @pytest.fixture
    def sessions(self):
        """Create Sessions for testing."""
        s1 = Session(start=8, end=12)
        s2 = Session(start=13, end=17)
        return Sessions(sessions=[s1, s2])

    def test_find_returns_session(self, sessions):
        """Test find returns matching session."""
        result = sessions.find(moment=time(10, 0))
        assert result is not None
        assert result.start.hour == 8

    def test_find_returns_none_when_not_found(self, sessions):
        """Test find returns None when no match."""
        result = sessions.find(moment=time(12, 30))
        assert result is None

    def test_find_second_session(self, sessions):
        """Test find can find second session."""
        result = sessions.find(moment=time(15, 0))
        assert result is not None
        assert result.start.hour == 13


class TestSessionsFindNext:
    """Test Sessions find_next method."""

    @pytest.fixture
    def sessions(self):
        """Create Sessions for testing."""
        s1 = Session(start=8, end=12)
        s2 = Session(start=13, end=17)
        return Sessions(sessions=[s1, s2])

    def test_find_next_returns_next_session(self, sessions):
        """Test find_next returns next session."""
        result = sessions.find_next(moment=time(7, 0))
        assert result.start.hour == 8

    def test_find_next_between_sessions(self, sessions):
        """Test find_next when between sessions."""
        result = sessions.find_next(moment=time(12, 30))
        assert result.start.hour == 13

    def test_find_next_wraps_to_first(self, sessions):
        """Test find_next wraps to first session at end of day."""
        result = sessions.find_next(moment=time(18, 0))
        assert result.start.hour == 8


class TestSessionsContains:
    """Test Sessions __contains__ method."""

    @pytest.fixture
    def sessions(self):
        """Create Sessions for testing."""
        s1 = Session(start=8, end=12)
        s2 = Session(start=13, end=17)
        return Sessions(sessions=[s1, s2])

    def test_contains_time_in_session(self, sessions):
        """Test time within any session returns True."""
        assert time(10, 0) in sessions

    def test_contains_time_between_sessions(self, sessions):
        """Test time between sessions returns False."""
        assert time(12, 30) not in sessions

    def test_contains_time_outside_sessions(self, sessions):
        """Test time outside all sessions returns False."""
        assert time(18, 0) not in sessions


class TestSessionsContextManager:
    """Test Sessions sync context manager."""

    @pytest.fixture
    def sessions(self):
        """Create Sessions for testing."""
        s1 = Session(start=0, end=23)  # All day session
        return Sessions(sessions=[s1])

    def test_enter_calls_check(self, sessions):
        """Test __enter__ calls check."""
        sessions.check = MagicMock()
        with sessions:
            sessions.check.assert_called_once()

    def test_exit_closes_session(self, sessions):
        """Test __exit__ closes current session."""
        sessions.check = MagicMock()
        mock_session = MagicMock()

        with sessions:
            sessions.current_session = mock_session

        mock_session.close.assert_called_once()


class TestSessionsCheck:
    """Test Sessions check method."""

    @pytest.fixture
    def sessions(self):
        """Create Sessions for testing."""
        s1 = Session(start=8, end=12)
        s2 = Session(start=13, end=17)
        return Sessions(sessions=[s1, s2])

    def test_check_returns_if_in_session(self, sessions):
        """Test check returns early if already in session."""
        mock_session = MagicMock()
        mock_session.in_session.return_value = True
        sessions.current_session = mock_session

        sessions.check()
        # Should return without changing current_session
        assert sessions.current_session == mock_session

    def test_check_starts_new_session(self, sessions):
        """Test check starts new session when found."""
        sessions.find = MagicMock(return_value=sessions.sessions[0])
        sessions.sessions[0].begin = MagicMock()

        sessions.check()
        assert sessions.current_session == sessions.sessions[0]
        sessions.sessions[0].begin.assert_called_once()

    def test_check_transitions_session(self, sessions):
        """Test check handles session transition."""
        old_session = MagicMock()
        old_session.in_session.return_value = False
        old_session.close = MagicMock()
        sessions.current_session = old_session

        new_session = sessions.sessions[0]
        new_session.begin = MagicMock()
        sessions.find = MagicMock(return_value=new_session)

        sessions.check()
        old_session.close.assert_called_once()
        assert sessions.current_session == new_session


class TestIntegration:
    """Integration tests for Sessions."""

    def test_create_multiple_sessions(self):
        """Test creating multiple sessions."""
        morning = Session(start=8, end=12, name="Morning", on_end="close_loss")
        afternoon = Session(start=13, end=17, name="Afternoon", on_end="close_all")
        evening = Session(start=18, end=22, name="Evening")

        sessions = Sessions(sessions=[morning, afternoon, evening])

        assert len(sessions.sessions) == 3
        assert sessions.sessions[0].name == "Morning"
        assert sessions.sessions[1].name == "Afternoon"
        assert sessions.sessions[2].name == "Evening"

    def test_session_duration_calculations(self):
        """Test session duration calculations are correct."""
        session = Session(start=time(9, 30), end=time(16, 45))
        duration = session.duration()

        assert duration.hours == 7
        assert duration.minutes == 15
        assert duration.seconds == 0

    def test_custom_action_functions(self):
        """Test custom action functions work."""
        called = {"start": False, "end": False}

        def on_start():
            called["start"] = True

        def on_end():
            called["end"] = True

        session = Session(
            start=8, end=16,
            on_start="custom_start", on_end="custom_end",
            custom_start=on_start, custom_end=on_end
        )

        session.begin()
        session.close()

        assert called["start"] is True
        assert called["end"] is True
