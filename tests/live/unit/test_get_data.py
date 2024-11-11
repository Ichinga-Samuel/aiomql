from pathlib import Path
from datetime import datetime, UTC

import pytest

from aiomql.core.backtesting.get_data import GetData
from aiomql.core.constants import TimeFrame


class TestGetData:
    @classmethod
    def setup_class(cls):
        cls.start = datetime(2024, 2, 1, tzinfo=UTC)
        cls.end = datetime(2024, 2, 2, tzinfo=UTC)
        cls.symbols = ["BTCUSD", "ETHUSD"]
        cls.timeframes = [TimeFrame.H1, TimeFrame.H2]
        cls.g_data = GetData(start=cls.start, end=cls.end, symbols=cls.symbols, timeframes=cls.timeframes, name="test_data")

    @pytest.fixture(scope="class", autouse=True)
    async def get_data(self):
        await self.g_data.get_data()
        self.g_data.save_data()

    def test_init(self):
        assert self.g_data.start == self.start
        assert self.g_data.end == self.end
        assert self.g_data.symbols == set(self.symbols)
        assert self.g_data.timeframes == set(self.timeframes)
        assert self.g_data.name == "test_data"
        assert self.g_data.range == range(int((self.end - self.start).total_seconds()))
        assert self.g_data.span == range(int(self.start.timestamp()), int(self.end.timestamp()))

    async def test_get_data(self):
        assert self.g_data.data.fully_loaded is True
        assert len(self.g_data.data.ticks.keys()) == 2
        assert len(self.g_data.data.symbols.keys()) == 2

    async def test_save_data(self):
        file = Path(self.g_data.config.backtest_dir / "test_data.pkl")
        assert file.exists()

    async def test_load_data(self):
        data = GetData.load_data(name="tests/live/backtesting/test_data.pkl")
        assert data.name == "test_data"
        assert data.fully_loaded is True
        assert len(data.ticks.keys()) == 2
        assert len(data.symbols.keys()) == 2
