from datetime import time, timedelta, datetime
from asyncio import sleep


class Session:

    def __init__(self, start: int | time, end: int | time):
        self.start = start if isinstance(start, time) else time(hour=start)
        self.end = end if isinstance(end, time) else time(hour=end)
        self.__from = self.delta(self.start)
        self.__to = self.delta(self.end)

    def __contains__(self, item: time):
        return self.start <= item < self.end

    def delta(self, obj):
        return timedelta(hours=obj.hour, minutes=obj.minute, seconds=obj.second, microseconds=obj.microsecond)

    def __len__(self):
        return (self.__to - self.__from).seconds

    def until(self):
        now = lambda: datetime.utcnow().time()
        return (self.__from - self.delta(now())).seconds


class Sessions:
    def __init__(self, *sessions: Session):
        self.sessions = list(sessions)
        self.sessions.sort(key=lambda x: x.start)

    def find(self, obj):
        for session in self.sessions:
            if obj in session:
                return session
        return None

    def find_next(self, obj):
        for session in self.sessions:
            if obj < session.start:
                return session
        return self.sessions[-1]

    def __contains__(self, item: time):
        return True if self.find(item) is not None else False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def check(self):
        now = datetime.utcnow().time()
        if now in self:
            return
        next_session = self.find_next(now)
        secs = next_session.until()
        print(f'sleeping for {secs} seconds')
        await sleep(secs)
