"""Sessions allow you to run code at specific times of the day."""
import asyncio
from datetime import time, timedelta, datetime
from asyncio import sleep, iscoroutinefunction
from typing import Literal, Callable
from logging import getLogger

from .positions import Positions

logger = getLogger(__name__)


def delta(obj: time):
    """Get the timedelta of a datetime.time object.

    Args:
        obj (datetime.time): A datetime.time object.
    """
    return timedelta(hours=obj.hour, minutes=obj.minute, seconds=obj.second, microseconds=obj.microsecond)


def seconds(start: time, end: time) -> set[int]:
    if start > end:
        return set(range(delta(start).seconds, 86400)) | set(range(0, delta(end).seconds))
    return set(range(delta(start).seconds, delta(end).seconds))


class Session:
    """A session is a time period between two datetime.time objects specified in utc.

    Attributes:
        start (datetime.time): The start time of the session.
        end (datetime.time): The end time of the session.
        on_start (str): The action to take when the session starts. Default is None.
        on_end (str): The action to take when the session ends. Default is None.
        custom_start (Callable): A custom function to call when the session starts. Default is None.
        custom_end (Callable): A custom function to call when the session ends. Default is None.
        name (str): A name for the session. Default is a combination of start and end.
        seconds (set[int]): A set of seconds between start and end.

    Methods:
        begin: Call the action specified in on_start or custom_start.
        close: Call the action specified in on_end or custom_end.
        action: Used by begin and close to call the action specified.
        delta: Get the timedelta of a datetime.time object.
        until: Get the seconds until the session starts from the current time.
    """
    def __init__(self, *, start: int | time, end: int | time,
                 on_start: Literal['close_all', 'close_win', 'close_loss', 'custom_start'] = None,
                 on_end: Literal['close_all', 'close_win', 'close_loss', 'custom_end'] = None,
                 custom_start: Callable = None, custom_end: Callable = None, name: str = ''):
        """Create a session.

        Keyword Args:
            start (int | datetime.time): The start time of the session in UTC.
            end (int | datetime.time): The end time of the session in UTC.
            on_start (Literal['close_all', 'close_win', 'close_loss', 'custom_start']): The action to take when the
                session starts. Default is None.
            on_end (Literal['close_all', 'close_win', 'close_loss', 'custom_end']): The action to take when the session
                ends. Default is None.
            custom_start (Callable): A custom function to call when the session starts. Default is None.
            custom_end (Callable): A custom function to call when the session ends. Default is None.
            name (str): A name for the session. Default is a combination of start and end.
        """
        self.start = start if isinstance(start, time) else time(hour=start)
        self.end = end if isinstance(end, time) else time(hour=end)
        self.on_start = on_start
        self.on_end = on_end
        self.custom_start = custom_start
        self.custom_end = custom_end
        self.name = name or f'{self.start} - {self.end}'
        self.seconds = seconds(self.start, self.end)

    def __contains__(self, item: time):
        return delta(item).seconds in self.seconds

    def __str__(self):
        return f'{self.start}-->{self.name}-->{self.end}' if self.name else f'{self.start}-->{self.end}'

    def __repr__(self):
        return f'{self.start}-->{self.end}'

    def __len__(self):
        return (delta(self.start) - delta(self.end)).seconds

    async def begin(self):
        """Call the action specified in on_start or custom_start."""
        await self.action(self.on_start)

    async def close(self):
        """Call the action specified in on_end or custom_end."""
        await self.action(self.on_end)

    async def action(self, action):
        """Used by begin and close to call the action specified.

        Args:
            action (Literal['close_all', 'close_win', 'close_loss', 'custom_start', 'custom_end']): The action to take.
        """
        try:
            position = Positions()
            positions = await position.positions_get()

            match action:
                case 'close_all':
                    await asyncio.gather(*(position.close(price=pos.price_current, ticket=pos.ticket,
                                                          order_type=pos.type, volume=pos.volume,
                                                          symbol=pos.symbol) for pos in positions),
                                         return_exceptions=True)

                case 'close_win':
                    await asyncio.gather(
                        *(position.close(price=pos.price_current, ticket=pos.ticket, order_type=pos.type,
                                         volume=pos.volume, symbol=pos.symbol) for pos in positions if pos.profit > 0),
                        return_exceptions=True)

                case 'close_loss':
                    await asyncio.gather(
                        *(position.close(price=pos.price_current, ticket=pos.ticket, order_type=pos.type,
                                         volume=pos.volume, symbol=pos.symbol) for pos in positions if
                          pos.profit < 0), return_exceptions=True)

                case 'custom_end':
                    if iscoroutinefunction(self.custom_end):
                        await self.custom_end()
                    self.custom_end()

                case 'custom_start':
                    if iscoroutinefunction(self.custom_start):
                        await self.custom_start()
                    self.custom_start()

                case _:
                    pass
        except Exception as exe:
            logger.warning(f'Failed to call action {action} due to {exe}')

    def until(self):
        """Get the seconds until the session starts from the current time in seconds."""
        return (delta(self.start) - delta(datetime.utcnow().time())).seconds


class Sessions:
    """Sessions allow you to run code at specific times of the day. It is a collection of Session objects.
    Sessions are sorted by start time. The sessions object is an asynchronous context manager.

    Attributes:
        sessions (list[Session]): A list of Session objects.
        current_session (Session): The current session.

    Methods:
        find: Find a session that contains a datetime.time object.
        find_next: Find the next session that contains a datetime.time object.
        check: Check if the current session has started and if not, wait until it starts.
    """
    def __init__(self, *sessions: Session):
        self.sessions = list(sessions)
        self.sessions.sort(key=lambda x: (x.start, x.end))
        self.current_session = None

    def find(self, obj: time) -> Session | None:
        """Find a session that contains a datetime.time object.

        Args:
            obj (datetime.time): A datetime.time object.

        Returns:
            Session | None: A Session object or None if not found.
        """
        for session in self.sessions:
            if obj in session:
                return session
        return None

    def find_next(self, obj: time) -> Session:
        """Find the next session that contains a datetime.time object.

        Args:
            obj (datetime.time): A datetime.time object.

        Returns:
            Session: A Session object.
        """
        for session in self.sessions:
            if obj < session.start:
                return session
        return self.sessions[0]

    def __contains__(self, item: time):
        return True if self.find(item) is not None else False

    async def __aenter__(self):
        await self.check()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.current_session.close()

    async def check(self):
        """Check if the current session has started and if not, wait until it starts."""
        now = datetime.utcnow().time()
        current_session = self.find(now)
        if current_session:
            if self.current_session:
                if self.current_session == current_session:
                    return
                await self.current_session.close()

            self.current_session = current_session
            await self.current_session.begin()
            return

        await self.current_session.close() if self.current_session else ...
        current_session = self.find_next(now)
        secs = current_session.until() + 10
        print(f'sleeping for {secs} seconds until next {current_session} session')
        await sleep(secs)
        self.current_session = current_session
        await self.current_session.begin()
