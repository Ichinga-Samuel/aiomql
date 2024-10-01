import asyncio
from datetime import time, timedelta, datetime
from typing import Literal, Callable, Iterable
from logging import getLogger

import pytz

from . import TradePosition
from .core.models import OrderSendResult
from .positions import Positions
from .core.config import Config
from.contrib.backtester.event_manager import EventManager

logger = getLogger(__name__)


def delta(obj: time) -> timedelta:
    """Get the timedelta of a datetime.time object.

    Args:
        obj (datetime.time): A datetime.time object.
    """
    return timedelta(hours=obj.hour, minutes=obj.minute, seconds=obj.second, microseconds=obj.microsecond)


async def backtest_sleep(secs):
    """A custom function to call when the session starts."""
    em = EventManager()
    config = Config()
    sleep = config.backtest_engine.cursor.time + secs
    async with em.condition:
        while sleep > config.backtest_engine.cursor.time:
            await em.wait()


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
        self.start = start if isinstance(start, time) else time(hour=start, tzinfo=pytz.UTC)
        self.end = end if isinstance(end, time) else time(hour=end, tzinfo=pytz.UTC)
        self.on_start = on_start
        self.on_end = on_end
        self.custom_start = custom_start
        self.custom_end = custom_end
        self.name = name or f'{self.start}<-->{self.end}'
        self.positions_manager = Positions()
        self.config = Config()

    def __contains__(self, item: time):
        if self.start > self.end:
            end = timedelta(days=1, hours=self.start.hour, minutes=self.start.minute, seconds=self.start.second,
                            microseconds=self.start.microsecond)
            start = delta(self.start)
            if item < self.start and item < self.end:
                item = timedelta(days=1, hours=item.hour, minutes=item.minute, seconds=item.second,
                                 microseconds=item.microsecond)
            else:
                item = delta(item)
        else:
            start = delta(self.start)
            end = delta(self.end)
        return start <= item < end

    def __str__(self):
        return f'{self.start}<-->{self.end}'

    def __repr__(self):
        return f'{self.start}<-->{self.end}'

    def __len__(self):
        return (delta(self.start) - delta(self.end)).seconds
    
    def in_session(self) -> bool:
        """Check if the current time is within the session."""
        now = datetime.now(tz=pytz.UTC).time() if self.config.mode == 'live'\
            else datetime.fromtimestamp(self.config.backtest_engine.cursor.time, tz=pytz.UTC).time()
        return now in self
    
    async def begin(self):
        """Call the action specified in on_start or custom_start."""
        await self.action(action=self.on_start)

    async def close(self):
        """Call the action specified in on_end or custom_end."""
        await self.action(action=self.on_end)

    async def close_positions(self, *, positions: tuple[TradePosition, ...]):

        results = asyncio.gather(*(self.positions_manager.close_position(pos) for pos in positions),
                                 return_exceptions=True)
        closed = pending = 0
        for result in results:
            if isinstance(result, OrderSendResult) and result.retcode == 10009:
                closed += 1
                continue
            pending += 1
        logger.info(f'Closed {closed} positions')
        logger.warning(f"{pending} positions still pending") if pending else ...

    async def close_all(self):
        open_positions = await self.positions_manager.get_positions()
        await self.close_positions(positions=open_positions)

    async def close_win(self):
        open_positions = await self.positions_manager.get_positions()
        positions = tuple(position for position in open_positions if position.profit >= 0)
        await self.close_positions(positions=positions)

    async def close_loss(self):
        open_positions = await self.positions_manager.get_positions()
        positions = tuple(position for position in open_positions if position.profit < 0)
        await self.close_positions(positions=positions)

    async def action(self, *, action):
        """Used by begin and close to call the action specified.

        Args:
            action (Literal['close_all', 'close_win', 'close_loss', 'custom_start', 'custom_end']): The action to take.
        """
        try:
            match action:
                case 'close_all':
                    await self.close_all()

                case 'close_win':
                    await self.close_win()

                case 'close_loss':
                    await self.close_loss()

                case 'custom_end':
                    await self.custom_end()

                case 'custom_start':
                    await self.custom_start()

                case _:
                    pass
        except Exception as exe:
            logger.warning(f'Failed to call action {action} due to {exe}')

    def until(self):
        """Get the seconds until the session starts from the current time in seconds."""
        if self.config.mode == 'backtest':
            now = datetime.fromtimestamp(self.config.backtest_engine.cursor.time, tz=pytz.UTC).time()
            secs = delta(self.start) - delta(now)
        else:
            secs = (delta(self.start) - delta(datetime.now(tz=pytz.UTC).time())).seconds
        return secs


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
    sessions: list[Session]

    def __init__(self, *, sessions: Iterable[Session]):
        self.sessions = list(sessions)
        self.sessions.sort(key=lambda x: (x.start.hour, x.end.hour))
        self.current_session = None
        self.config = Config()

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
            if delta(obj) < delta(session.start):
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
        if self.current_session is not None and self.current_session.in_session():
            return
        
        if self.config.mode == 'backtest':
            now = datetime.fromtimestamp(self.config.backtest_engine.cursor.time, tz=pytz.UTC).time()
        else:
            now = datetime.now().time()

        next_session = self.find(now)

        if next_session and self.current_session is None:
            self.current_session = next_session
            await self.current_session.begin()
            return

        if next_session and self.current_session is not None:
            await self.current_session.close()
            self.current_session = next_session
            await self.current_session.begin()

        if next_session is None and self.current_session is not None:
            await self.current_session.close()

        next_session = self.find_next(now)
        secs = next_session.until() + 10
        logger.info(f'sleeping for {secs} seconds until next {next_session} session')
        sleep_func = asyncio.sleep if self.config.mode == 'live' else backtest_sleep
        await sleep_func(secs)
        self.current_session = next_session
        await self.current_session.begin()
