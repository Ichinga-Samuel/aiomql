from datetime import datetime

import pytest
import pytz
import pandas as pd
from aiomql.lib.candle import Candle, Candles
from aiomql.core.meta_trader import MetaTrader
from aiomql.core.constants import TimeFrame


class TestCandle:
    @classmethod
    def setup_class(cls):
        cls.bullish_candle = Candle(open=1.3421, high=1.3462, low=1.3405, close=1.3452, time=0, Index=0)
        cls.bearish_candle = Candle(open=1.3452, high=1.3405, low=1.3462, close=1.3421, time=1, Index=1)

    def test_repr(self):
        repr_str = repr(self.bearish_candle)
        assert repr_str.startswith("Candle(")
        assert "open=" in repr_str
        assert "high=" in repr_str
        assert "low=" in repr_str
        assert "close=" in repr_str

    def test_set_attributes(self):
        self.bearish_candle.set_attributes(ema=10)
        assert self.bearish_candle.ema == 10

    def test_compare(self):
        assert self.bearish_candle > self.bullish_candle
        assert self.bullish_candle != self.bearish_candle
        assert self.bullish_candle < self.bearish_candle

    def test_dict(self):
        self.bearish_candle.set_attributes(ema=10)
        result = self.bearish_candle.dict(exclude={"time"})
        result2 = self.bearish_candle.dict(include={"close", "high"})
        assert result["open"] == 1.3452
        assert result["ema"] == 10
        assert "time" not in result
        assert set(result2.keys()) == {"close", "high"}

    def test_dictionary_properties(self):
        self.bearish_candle["ema"] = 4
        assert self.bearish_candle["ema"] == 4

    def test_candle_type(self):
        assert self.bearish_candle.is_bearish()
        assert self.bullish_candle.is_bullish()


class TestCandles:
    @pytest.fixture(scope="class")
    async def candles(self):
        mt = MetaTrader()
        start = datetime(day=5, month=10, year=2023)
        rates = await mt.copy_rates_from("BTCUSD", mt.TIMEFRAME_H1, start, 200)
        return Candles(data=rates)

    def test_get_series(self, candles):
        series = candles["open"]
        assert isinstance(series, pd.Series)
        assert len(series) == 200

    def test_get_candle(self, candles):
        candle = candles[10]
        assert isinstance(candle, Candle)
        assert candle in candles
        assert candle.Index == 10

    def test_slice(self, candles):
        sliced = candles[10:15]
        assert len(sliced) == 5
        assert isinstance(sliced, Candles)

    def test_setitem(self, candles):
        new_series = candles.open
        new_series = new_series * 2
        candles["double_open"] = new_series
        assert "double_open" in candles.data.columns

    def test_getattr(self, candles):
        open_series = candles.open
        assert isinstance(open_series, pd.Series)
        assert open_series.equals(candles.data["open"])

    def test_iter(self, candles):
        l_5 = candles[-5:]
        assert all(isinstance(candle, Candle) for candle in l_5)

    def test_timeframe(self, candles):
        tf = candles.timeframe
        assert tf == TimeFrame.H1

    def test_ta_and_rename(self, candles):
        ema = candles.ta.ema(close="open", length=10, append=True)
        assert "EMA_10" in candles.data.columns
        candles.rename(inplace=True, EMA_10="ema")
        assert "ema" in candles.data.columns

    def test_ta_lib(self, candles):
        fas = candles.ta_lib.above(candles.open, candles.close)
        assert isinstance(fas, pd.Series)
        candles["fas"] = fas
        assert "fas" in candles.data.columns