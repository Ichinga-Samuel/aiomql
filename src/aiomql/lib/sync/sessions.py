"""Synchronous Sessions module for time-based trading session management.

This module provides synchronous Session and Sessions classes for defining
trading time windows and automating actions at session boundaries (e.g.,
closing positions at end of day) without async/await.

Classes:
    Duration: Named tuple representing session duration in hours, minutes, seconds.
    Session: A trading time window with start/end times and configurable actions.
    Sessions: A collection of Session objects with automatic session management.

Example:
    Defining and using trading sessions synchronously::

        from datetime import time
        from aiomql.lib.sync.sessions import Session, Sessions

        # Create sessions for different trading periods
        morning = Session(start=time(8, 0), end=time(12, 0), name="Morning")
        afternoon = Session(
            start=time(13, 0),
            end=time(17, 0),
            on_end='close_all',
            name="Afternoon"
        )

        sessions = Sessions(sessions=[morning, afternoon])

        # Use as context manager
        with sessions:
            # Trading code here - executes during session hours
            pass
"""

from datetime import time, timedelta, datetime, UTC
from typing import Literal, Callable, Iterable, NamedTuple
from logging import getLogger
from time import sleep

from ...core.models import OrderSendResult, TradePosition
from ...core.config import Config
from .positions import Positions

logger = getLogger(__name__)


class Duration(NamedTuple):
    """Named tuple representing a duration of time.

    Attributes:
        hours: Number of hours.
        minutes: Number of minutes.
        seconds: Number of seconds.
    """
    hours: int
    minutes: int
    seconds: int


def delta(obj: time) -> timedelta:
    """Convert a datetime.time object to a timedelta.

    Args:
        obj: A datetime.time object to convert.

    Returns:
        timedelta: The time represented as a timedelta from midnight.
    """
    return timedelta(hours=obj.hour, minutes=obj.minute, seconds=obj.second, microseconds=obj.microsecond)


class Session:
    """A trading session representing a time period between two UTC times.

    Sessions define trading windows and can execute actions automatically
    at session start and end times. Common actions include closing all
    positions, closing winning positions, or closing losing positions.

    Attributes:
        start: The start time of the session in UTC.
        end: The end time of the session in UTC.
        on_start: Action to take when the session starts.
        on_end: Action to take when the session ends.
        custom_start: Custom function to call when session starts.
        custom_end: Custom function to call when session ends.
        name: Human-readable name for the session.
        positions_manager: Positions instance for managing open positions.
        config: Configuration instance.

    Example:
        Creating a session that closes positions at end of day::

            session = Session(
                start=time(9, 0),
                end=time(17, 0),
                on_end='close_all',
                name="Trading Hours"
            )

            if session.in_session():
                # Execute trading logic
                pass
    """

    def __init__(
        self,
        *,
        start: int | time,
        end: int | time,
        on_start: Literal["close_all", "close_win", "close_loss", "custom_start"] = None,
        on_end: Literal["close_all", "close_win", "close_loss", "custom_end"] = None,
        custom_start: Callable = None,
        custom_end: Callable = None,
        name: str = "",
    ):
        """Initialize a trading session.

        Args:
            start: The start time of the session in UTC. Can be an integer
                (hour) or a datetime.time object.
            end: The end time of the session in UTC. Can be an integer
                (hour) or a datetime.time object.
            on_start: Action to execute when session starts. Options are:
                'close_all', 'close_win', 'close_loss', 'custom_start'.
            on_end: Action to execute when session ends. Options are:
                'close_all', 'close_win', 'close_loss', 'custom_end'.
            custom_start: Custom callable to invoke at session start.
                Used when on_start='custom_start'.
            custom_end: Custom callable to invoke at session end.
                Used when on_end='custom_end'.
            name: Human-readable name for the session. Defaults to
                "{start}<-->{end}" format.
        """
        self.start = start.replace(tzinfo=UTC) if isinstance(start, time) else time(hour=start, tzinfo=UTC)
        self.end = end if isinstance(end, time) else time(hour=end, tzinfo=UTC)
        self.on_start = on_start
        self.on_end = on_end
        self.custom_start = custom_start
        self.custom_end = custom_end
        self.name = name or f"{self.start}<-->{self.end}"
        self.positions_manager = Positions()
        self.config = Config()

    def __contains__(self, item: time) -> bool:
        """Check if a time falls within this session.

        Args:
            item: A datetime.time object to check.

        Returns:
            bool: True if the time is within the session, False otherwise.
        """
        span = (delta(self.end) - delta(self.start)).seconds
        item_span = (delta(self.end) - delta(item)).seconds
        return item_span <= span

    def __str__(self) -> str:
        """Return string representation of the session."""
        return f"{self.start}<-->{self.end}"

    def __repr__(self) -> str:
        """Return detailed string representation of the session."""
        return f"{self.start}<-->{self.end}"

    def __len__(self) -> int:
        """Return the session duration in seconds."""
        return int((delta(self.end) - delta(self.start)).seconds)

    def in_session(self) -> bool:
        """Check if the current time is within the session.

        Returns:
            bool: True if current time is within session bounds.
        """
        now = datetime.now(tz=UTC).time()
        return now in self

    def begin(self):
        """Execute the action specified in on_start when session begins."""
        self.action(action=self.on_start)

    def close(self):
        """Execute the action specified in on_end when session ends."""
        self.action(action=self.on_end)

    def duration(self) -> Duration:
        """Get the duration of the session.

        Returns:
            Duration: Named tuple with hours, minutes, and seconds.
        """
        hours, seconds = divmod(len(self), 3600)
        minutes, seconds = divmod(seconds, 60)
        return Duration(hours=hours, minutes=minutes, seconds=seconds)

    def close_positions(self, *, positions: tuple[TradePosition, ...]):
        """Close multiple positions.

        Args:
            positions: Tuple of TradePosition objects to close.
        """
        closed = pending = 0
        for position in positions:
            try:
                result = self.positions_manager.close_position(position=position)
                if isinstance(result, OrderSendResult) and result.retcode == 10009:
                    closed += 1
                else:
                    pending += 1
            except Exception:
                pending += 1
        logger.info(f"Closed {closed} positions")
        logger.warning(f"{pending} positions still pending") if pending else ...

    def close_all(self):
        """Close all open positions."""
        open_positions = self.positions_manager.get_positions()
        self.close_positions(positions=open_positions)

    def close_win(self):
        """Close all positions with non-negative profit."""
        open_positions = self.positions_manager.get_positions()
        positions = tuple(position for position in open_positions if position.profit >= 0)
        self.close_positions(positions=positions)

    def close_loss(self):
        """Close all positions with negative profit."""
        open_positions = self.positions_manager.get_positions()
        positions = tuple(position for position in open_positions if position.profit < 0)
        self.close_positions(positions=positions)

    def action(self, *, action):
        """Execute the specified action.

        Used internally by begin() and close() to dispatch actions.

        Args:
            action: The action to execute. One of 'close_all', 'close_win',
                'close_loss', 'custom_start', 'custom_end', or None.
        """
        try:
            match action:
                case "close_all":
                    self.close_all()

                case "close_win":
                    self.close_win()

                case "close_loss":
                    self.close_loss()

                case "custom_end":
                    self.custom_end()

                case "custom_start":
                    self.custom_start()

                case _:
                    pass
        except Exception as exe:
            logger.warning(f"Failed to call action {action} due to {exe}")

    def until(self) -> int:
        """Get seconds until the session starts.

        Returns:
            int: Number of seconds until session start time.
        """
        return (delta(self.start) - delta(datetime.now(tz=UTC).time())).seconds

class Sessions:
    """A collection of Session objects with automatic session management.

    Sessions manages multiple trading sessions, automatically handling
    transitions between sessions and waiting for session start times.
    Works as a synchronous context manager.

    Attributes:
        sessions: List of Session objects, sorted by start time.
        current_session: The currently active session, or None.
        config: Configuration instance.

    Example:
        Using Sessions as a context manager::

            morning = Session(start=8, end=12, name="Morning")
            afternoon = Session(start=13, end=17, on_end='close_all', name="Afternoon")

            sessions = Sessions(sessions=[morning, afternoon])

            with sessions:
                # This code runs during session hours
                # Automatically waits for next session if outside hours
                execute_strategy()
    """

    sessions: list[Session]
    current_session: Session | None

    def __init__(self, *, sessions: Iterable[Session]):
        """Initialize the Sessions collection.

        Args:
            sessions: Iterable of Session objects to manage.
                Sessions are automatically sorted by start time.
        """
        self.sessions = list(sessions)
        self.sessions.sort(key=lambda x: (x.start.hour, x.end.hour))
        self.current_session = None
        self.config = Config()

    def find(self, *, moment: time = None) -> Session | None:
        """Find a session containing the specified time.

        Args:
            moment: Time to search for. Uses current time if not provided.

        Returns:
            Session | None: The matching session, or None if not found.
        """
        moment = moment or datetime.now(tz=UTC).time()
        for session in self.sessions:
            if moment in session:
                return session
        return None

    def find_next(self, *, moment: time = None) -> Session:
        """Find the next session after the specified time.

        Args:
            moment: Time to search from. Uses current time if not provided.

        Returns:
            Session: The next session. Wraps to first session if at end of day.
        """
        moment or datetime.now(tz=UTC).time()
        for session in self.sessions:
            if delta(moment) < delta(session.start):
                return session
        return self.sessions[0]

    def __contains__(self, moment: time) -> bool:
        """Check if a time falls within any session.

        Args:
            moment: Time to check.

        Returns:
            bool: True if time is within any session.
        """
        return True if self.find(moment=moment) is not None else False

    def __enter__(self):
        """Enter context manager, checking and waiting for session.

        Returns:
            Sessions: Self reference for context manager use.
        """
        self.check()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager, closing current session if active."""
        self.current_session.close() if self.current_session is not None else ...

    def check(self):
        """Check session state and wait for next session if needed.

        Handles session transitions by:
        - Continuing if already in active session
        - Starting new session if one is found
        - Closing previous session when transitioning
        - Sleeping until next session if outside all sessions
        """
        if self.current_session is not None and self.current_session.in_session():
            return
        now = datetime.now(tz=UTC).time()
        next_session = self.find(moment=now)

        if next_session and self.current_session is None:
            self.current_session = next_session
            self.current_session.begin()
            return

        if next_session and self.current_session is not None:
            self.current_session.close()
            self.current_session = next_session
            self.current_session.begin()
            return

        if next_session is None and self.current_session is not None:
            self.current_session.close()

        next_session = self.find_next(moment=now)
        secs = next_session.until() + 10
        logger.info(f"sleeping for {secs} seconds until next {next_session} session")
        sleep(secs)
        self.current_session = next_session
        self.current_session.begin()
