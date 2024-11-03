from datetime import datetime, time, UTC

import pytest

from aiomql.lib.sessions import Session, Sessions, delta


class TestSessions:
    @pytest.fixture(scope="class")
    def make_sessions(self, make_session):
        london, all_day, over_night = make_session
        return Sessions(sessions=[london, all_day, over_night])

    @pytest.fixture(scope="class")
    def make_session(self):
        end = time(hour=16, minute=59, second=59, microsecond=999_999, tzinfo=UTC)
        london = Session(start=8, end=end, name="London", on_end="close_all")
        start, end = time(hour=0, tzinfo=UTC), time(
            hour=23, minute=59, second=59, tzinfo=UTC
        )
        all_day = Session(start=start, end=end, name="AllDay", on_end="close_all")
        end = time(hour=6, minute=59, second=59, microsecond=999_999, tzinfo=UTC)
        over_night = Session(start=18, end=end, name="OverNight", on_end="close_all")
        return london, all_day, over_night

    def test_session_attributes(self, make_session):
        london, all_day, over_night = make_session
        period = over_night.duration()
        assert london.name == "London"
        assert london.start == time(hour=8, tzinfo=UTC)
        assert london.end.hour == 16
        assert period.hours == 12
        assert period.minutes == period.seconds == 59

    def test_session_intervals(self, make_session):
        london, all_day, over_night = make_session
        two_am = time(hour=2, tzinfo=UTC)
        noon = time(hour=12, tzinfo=UTC)
        now = datetime.now(UTC).time()
        hours_till_london_starts = (delta(london.start) - delta(now)).seconds // 3600
        assert hours_till_london_starts == london.until() // 3600
        assert two_am in over_night
        assert noon in london
        assert two_am not in london
        assert noon not in over_night
        # all_day session is always open
        assert all_day.in_session()

    async def test_sessions(self, make_session):
        london, all_day, over_night = make_session
        sessions = Sessions(sessions=[london, over_night])
        now = time(hour=21, tzinfo=UTC)
        noon = time(hour=12, tzinfo=UTC)
        mid_nite = time(hour=0, tzinfo=UTC)
        next_sess = sessions.find_next(moment=now)
        noon_sess = sessions.find(moment=noon)
        no_sess = sessions.find(moment=time(hour=17, tzinfo=UTC))
        mid_nite_sess = sessions.find(moment=mid_nite)
        current_sess = sessions.find(moment=now)
        assert current_sess.name == "OverNight"
        assert noon_sess.name == "London"
        assert no_sess is None
        assert next_sess.name == "London"
        assert mid_nite_sess.name == "OverNight"
        current = datetime.now(UTC).time()
        if current.hour not in (7, 17):
            await sessions.check()
            assert sessions.current_session is not None
            assert sessions.current_session.name in ("London", "OverNight")
