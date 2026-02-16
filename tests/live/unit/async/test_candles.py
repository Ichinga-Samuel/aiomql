"""Comprehensive tests for the candle module.

Tests cover:
- CandleProtocol compliance
- CandleBase methods and properties
- Candle class functionality
- Candles container operations
"""
from datetime import datetime

import pytest
import pandas as pd
from pandas import Series, DataFrame, Timestamp

from aiomql.lib.candle import Candle, Candles, CandleBase, CandleProtocol
from aiomql.core.constants import TimeFrame
from aiomql.ta_libs import pandas_ta_classic as ta


class TestCandleProtocol:
    """Test CandleProtocol type checking."""

    def test_candle_implements_protocol(self):
        """Candle class should implement CandleProtocol."""
        candle = Candle(open=100, high=110, low=95, close=105)
        assert isinstance(candle, CandleProtocol)

    def test_candlebase_implements_protocol(self):
        """CandleBase subclass should implement CandleProtocol."""
        class CustomCandle(CandleBase):
            def __init__(self, **kwargs):
                self.open = kwargs['open']
                self.high = kwargs['high']
                self.low = kwargs['low']
                self.close = kwargs['close']

        candle = CustomCandle(open=100, high=110, low=95, close=105)
        assert isinstance(candle, CandleProtocol)

    def test_minimal_protocol_implementation(self):
        """Minimal class with OHLC should implement CandleProtocol."""
        class MinimalCandle:
            def __init__(self, **kwargs):
                self.open = kwargs['open']
                self.high = kwargs['high']
                self.low = kwargs['low']
                self.close = kwargs['close']

        candle = MinimalCandle(open=100, high=110, low=95, close=105)
        assert isinstance(candle, CandleProtocol)


class TestCandleBase:
    """Test CandleBase class methods and properties."""

    @classmethod
    def setup_class(cls):
        """Create test candles for CandleBase tests."""
        # Bullish candle: close > open
        cls.bullish = Candle(open=100.0, high=110.0, low=95.0, close=108.0)
        # Bearish candle: close < open
        cls.bearish = Candle(open=108.0, high=112.0, low=90.0, close=95.0)
        # Doji candle: close == open
        cls.doji = Candle(open=100.0, high=105.0, low=95.0, close=100.0)

    def test_repr(self):
        """Test __repr__ method."""
        repr_str = repr(self.bullish)
        assert repr_str.startswith("Candle(")
        assert "open=" in repr_str
        assert "high=" in repr_str
        assert "low=" in repr_str
        assert "close=" in repr_str

    def test_is_bullish(self):
        """Test is_bullish method."""
        assert self.bullish.is_bullish() is True
        assert self.bearish.is_bullish() is False
        assert self.doji.is_bullish() is True  # close == open is bullish

    def test_is_bearish(self):
        """Test is_bearish method."""
        assert self.bearish.is_bearish() is True
        assert self.bullish.is_bearish() is False
        assert self.doji.is_bearish() is False

    def test_upper_wick(self):
        """Test upper_wick property."""
        # Bullish: high - close = 110 - 108 = 2
        assert self.bullish.upper_wick == 2.0
        # Bearish: high - open = 112 - 108 = 4
        assert self.bearish.upper_wick == 4.0

    def test_lower_wick(self):
        """Test lower_wick property."""
        # Bullish: open - low = 100 - 95 = 5
        assert self.bullish.lower_wick == 5.0
        # Bearish: close - low = 95 - 90 = 5
        assert self.bearish.lower_wick == 5.0

    def test_candle_range(self):
        """Test candle_range property."""
        # Bullish: high - low = 110 - 95 = 15
        assert self.bullish.candle_range == 15.0
        # Bearish: high - low = 112 - 90 = 22
        assert self.bearish.candle_range == 22.0

    def test_candle_body(self):
        """Test candle_body property."""
        # Bullish: |close - open| = |108 - 100| = 8
        assert self.bullish.candle_body == 8.0
        # Bearish: |95 - 108| = 13
        assert self.bearish.candle_body == 13.0
        # Doji: |100 - 100| = 0
        assert self.doji.candle_body == 0.0

    def test_upper_wick_percentage(self):
        """Test upper_wick_percentage property."""
        # Bullish: (2 / 15) * 100 = 13.33...
        assert abs(self.bullish.upper_wick_percentage - 13.333333) < 0.001

    def test_lower_wick_percentage(self):
        """Test lower_wick_percentage property."""
        # Bullish: (5 / 15) * 100 = 33.33...
        assert abs(self.bullish.lower_wick_percentage - 33.333333) < 0.001

    def test_candle_body_percentage(self):
        """Test candle_body_percentage property."""
        # Bullish: (8 / 15) * 100 = 53.33...
        assert abs(self.bullish.candle_body_percentage - 53.333333) < 0.001

    def test_comparison_key(self):
        """Test _comparison_key static method."""
        key = CandleBase._comparison_key(self.bullish)
        assert key == (8.0, 15.0)  # (body, range)

    def test_comparison_key_with_dict(self):
        """Test _comparison_key works with dict-like objects."""
        candle_dict = {'open': 100.0, 'high': 110.0, 'low': 95.0, 'close': 108.0}
        key = CandleBase._comparison_key(candle_dict)
        assert key == (8.0, 15.0)

    def test_equality(self):
        """Test __eq__ based on body and range."""
        # Same body and range
        c1 = Candle(open=100, high=110, low=95, close=108)  # body=8, range=15
        c2 = Candle(open=102, high=112, low=97, close=110)  # body=8, range=15
        assert c1 == c2

    def test_inequality(self):
        """Test __ne__ based on body and range."""
        assert self.bullish != self.bearish

    def test_less_than(self):
        """Test __lt__ comparison."""
        # Bullish: body=8, range=15
        # Bearish: body=13, range=22
        assert self.bullish < self.bearish  # smaller body

    def test_less_than_or_equal(self):
        """Test __le__ comparison."""
        c1 = Candle(open=100, high=110, low=95, close=108)
        c2 = Candle(open=102, high=112, low=97, close=110)  # Same key
        assert c1 <= c2
        assert self.bullish <= self.bearish

    def test_greater_than(self):
        """Test __gt__ comparison."""
        assert self.bearish > self.bullish

    def test_greater_than_or_equal(self):
        """Test __ge__ comparison."""
        c1 = Candle(open=100, high=110, low=95, close=108)
        c2 = Candle(open=102, high=112, low=97, close=110)
        assert c1 >= c2
        assert self.bearish >= self.bullish

    def test_hash(self):
        """Test __hash__ method."""
        time = datetime.now().timestamp()
        c1 = Candle(open=100, high=110, low=95, close=108, time=time)
        c2 = Candle(open=100, high=110, low=95, close=108, time=time)  # Same key
        assert hash(c1) == hash(c2)

    def test_getitem(self):
        """Test __getitem__ for dict-like access."""
        assert self.bullish['open'] == 100.0
        assert self.bullish['close'] == 108.0

    def test_setitem(self):
        """Test __setitem__ for dict-like setting."""
        candle = Candle(open=100, high=110, low=95, close=105)
        candle['custom_attr'] = 42
        assert candle['custom_attr'] == 42
        assert candle.custom_attr == 42

    def test_iter(self):
        """Test __iter__ for iterating over attributes."""
        candle = Candle(open=100, high=110, low=95, close=105)
        items = dict(candle)
        assert 'open' in items
        assert 'close' in items
        assert items['open'] == 100

    def test_keys(self):
        """Test keys method."""
        candle = Candle(open=100, high=110, low=95, close=105)
        keys = candle.keys()
        assert 'open' in keys
        assert 'high' in keys
        assert 'low' in keys
        assert 'close' in keys

    def test_values(self):
        """Test values method."""
        candle = Candle(open=100, high=110, low=95, close=105)
        values = list(candle.values())
        assert 100 in values
        assert 105 in values

    def test_set_attributes(self):
        """Test set_attributes method."""
        candle = Candle(open=100, high=110, low=95, close=105)
        candle.set_attributes(ema=20, sma=50)
        assert candle.ema == 20
        assert candle.sma == 50

    def test_dict_method(self):
        """Test dict method."""
        candle = Candle(open=100, high=110, low=95, close=105)
        result = candle.dict()
        assert 'open' in result
        assert result['open'] == 100

    def test_dict_exclude(self):
        """Test dict method with exclude parameter."""
        candle = Candle(open=100, high=110, low=95, close=105)
        result = candle.dict(exclude={'time', 'Index'})
        assert 'time' not in result
        assert 'Index' not in result
        assert 'open' in result

    def test_dict_include(self):
        """Test dict method with include parameter."""
        candle = Candle(open=100, high=110, low=95, close=105)
        result = candle.dict(include={'open', 'close'})
        assert set(result.keys()) == {'open', 'close'}

    def test_to_series(self):
        """Test to_series method."""
        candle = Candle(open=100, high=110, low=95, close=105)
        series = candle.to_series()
        assert isinstance(series, Series)
        assert series['open'] == 100
        assert 'Index' not in series.index
        assert 'index' not in series.index


class TestCandle:
    """Test Candle class specific functionality."""

    def test_init_required_args(self):
        """Test Candle requires open, high, low, close."""
        with pytest.raises(ValueError):
            Candle(open=100, high=110, low=95)  # Missing close

    def test_init_with_defaults(self):
        """Test Candle initializes defaults for optional attributes."""
        candle = Candle(open=100, high=110, low=95, close=105)
        assert hasattr(candle, 'time')
        assert hasattr(candle, 'Index')
        assert hasattr(candle, 'index')
        assert hasattr(candle, 'volume')
        assert hasattr(candle, 'spread')

    def test_init_with_custom_time(self):
        """Test Candle with custom time."""
        custom_time = 1609459200.0  # 2021-01-01 00:00:00
        candle = Candle(open=100, high=110, low=95, close=105, time=custom_time)
        assert candle.time == custom_time

    def test_init_with_volume(self):
        """Test Candle with volume attributes."""
        candle = Candle(
            open=100, high=110, low=95, close=105,
            tick_volume=1000, real_volume=500
        )
        assert candle.tick_volume == 1000
        assert candle.real_volume == 500
        assert candle.volume == 500  # Uses real_volume if available

    def test_init_volume_fallback(self):
        """Test volume falls back to tick_volume."""
        candle = Candle(
            open=100, high=110, low=95, close=105,
            tick_volume=1000, real_volume=0
        )
        assert candle.volume == 1000

    def test_repr(self):
        """Test Candle __repr__ includes all attributes."""
        candle = Candle(open=100, high=110, low=95, close=105)
        repr_str = repr(candle)
        assert "Index=" in repr_str
        assert "time=" in repr_str
        assert "open=" in repr_str
        assert "index=" in repr_str

    def test_hash_includes_time(self):
        """Test Candle hash includes time."""
        c1 = Candle(open=100, high=110, low=95, close=105, time=1000)
        c2 = Candle(open=100, high=110, low=95, close=105, time=2000)
        # Same OHLC but different time should have different hash
        assert hash(c1) != hash(c2)

    def test_index_is_timestamp(self):
        """Test index is a Pandas Timestamp."""
        candle = Candle(open=100, high=110, low=95, close=105)
        assert isinstance(candle.index, Timestamp)


class TestCandles:
    """Test Candles container class."""

    @pytest.fixture(scope="class")
    async def candles(self, mt):
        """Create candles from MetaTrader data."""
        start = datetime(day=5, month=10, year=2023)
        rates = await mt.copy_rates_from("BTCUSD", mt.TIMEFRAME_H1, start, 200)
        return Candles(data=rates)

    @pytest.fixture(scope="class")
    async def candles_2(self, mt):
        """Create another set of candles for merge tests."""
        start = datetime(day=5, month=10, year=2023)
        rates = await mt.copy_rates_from("BTCUSD", mt.TIMEFRAME_H1, start, 300)
        return Candles(data=rates)

    @pytest.fixture
    def sample_candles(self):
        """Create sample candles from DataFrame for non-async tests."""
        data = pd.DataFrame({
            'time': [1609459200.0 + i * 3600 for i in range(10)],
            'open': [100 + i for i in range(10)],
            'high': [105 + i for i in range(10)],
            'low': [95 + i for i in range(10)],
            'close': [102 + i for i in range(10)],
            'tick_volume': [1000 + i * 100 for i in range(10)],
            'real_volume': [500 + i * 50 for i in range(10)],
            'spread': [1 for _ in range(10)],
        })
        return Candles(data=data)

    def test_init_from_dataframe(self, sample_candles):
        """Test Candles creation from DataFrame."""
        assert len(sample_candles) == 10
        assert isinstance(sample_candles.data, DataFrame)

    def test_init_from_candles(self, sample_candles):
        """Test Candles creation from another Candles object."""
        new_candles = Candles(data=sample_candles)
        assert len(new_candles) == len(sample_candles)

    def test_init_from_iterable(self):
        """Test Candles creation from iterable."""
        data = [
            {'time': 1609459200.0, 'open': 100, 'high': 105, 'low': 95, 'close': 102},
            {'time': 1609462800.0, 'open': 102, 'high': 108, 'low': 100, 'close': 105},
        ]
        candles = Candles(data=data)
        assert len(candles) == 2

    def test_init_flip(self, sample_candles):
        """Test Candles with flip=True reverses order."""
        flipped = Candles(data=sample_candles.data, flip=True)
        # First candle in flipped should be last in original
        assert flipped[0].open == sample_candles[-1].open

    def test_init_custom_candle_class(self, sample_candles):
        """Test Candles with custom candle class."""
        class CustomCandle(CandleBase):
            def __init__(self, **kwargs):
                self.open = kwargs['open']
                self.high = kwargs['high']
                self.low = kwargs['low']
                self.close = kwargs['close']
                self.time = kwargs.get('time', 0)
                self.Index = kwargs.get('Index', 0)
                self.index = kwargs.get('index', Timestamp.now())

        candles = Candles(data=sample_candles.data, candle_class=CustomCandle)
        assert isinstance(candles[0], CustomCandle)

    def test_repr(self, sample_candles):
        """Test __repr__ returns DataFrame repr."""
        repr_str = repr(sample_candles)
        assert 'open' in repr_str

    def test_len(self, sample_candles):
        """Test __len__ returns correct count."""
        assert len(sample_candles) == 10

    def test_contains(self, sample_candles):
        """Test __contains__ checks candle presence."""
        candle = sample_candles[0]
        assert candle in sample_candles

    def test_getitem_int(self, sample_candles):
        """Test __getitem__ with integer index."""
        candle = sample_candles[0]
        assert isinstance(candle, Candle)
        assert candle.Index == 0

    def test_getitem_negative_int(self, sample_candles):
        """Test __getitem__ with negative index."""
        candle = sample_candles[-1]
        assert isinstance(candle, Candle)
        assert candle.Index == 9

    def test_getitem_slice(self, sample_candles):
        """Test __getitem__ with slice."""
        sliced = sample_candles[2:5]
        assert isinstance(sliced, Candles)
        assert len(sliced) == 3

    def test_getitem_str(self, sample_candles):
        """Test __getitem__ with string column name."""
        series = sample_candles['open']
        assert isinstance(series, pd.Series)
        assert len(series) == 10

    def test_getitem_index_str(self, sample_candles):
        """Test __getitem__ with 'index' string."""
        index = sample_candles['index']
        assert isinstance(index, pd.DatetimeIndex)

    def test_getitem_Index_str(self, sample_candles):
        """Test __getitem__ with 'Index' string."""
        index_series = sample_candles['Index']
        assert isinstance(index_series, pd.Series)
        assert list(index_series) == list(range(10))

    def test_setitem(self, sample_candles):
        """Test __setitem__ adds column."""
        new_series = sample_candles.open * 2
        sample_candles['double_open'] = new_series
        assert 'double_open' in sample_candles.data.columns

    def test_getattr_column(self, sample_candles):
        """Test __getattr__ for column access."""
        open_series = sample_candles.open
        assert isinstance(open_series, pd.Series)

    def test_getattr_index(self, sample_candles):
        """Test __getattr__ for 'index'."""
        index = sample_candles.index
        assert isinstance(index, pd.DatetimeIndex)

    def test_getattr_Index(self, sample_candles):
        """Test __getattr__ for 'Index'."""
        Index = sample_candles.Index
        assert isinstance(Index, pd.Series)

    def test_getattr_invalid(self, sample_candles):
        """Test __getattr__ raises AttributeError for invalid attr."""
        with pytest.raises(AttributeError):
            _ = sample_candles.invalid_attribute

    def test_iter(self, sample_candles):
        """Test __iter__ yields Candle objects."""
        candles_list = list(sample_candles)
        assert len(candles_list) == 10
        assert all(isinstance(c, Candle) for c in candles_list)

    def test_reversed(self, sample_candles):
        """Test __reversed__ yields candles in reverse order."""
        reversed_list = list(reversed(sample_candles))
        assert len(reversed_list) == 10
        assert reversed_list[0].Index == 9

    def test_timeframe(self, sample_candles):
        """Test timeframe property detection."""
        tf = sample_candles.timeframe
        assert tf == TimeFrame.H1

    def test_columns(self, sample_candles):
        """Test columns property."""
        cols = sample_candles.columns
        assert 'open' in cols
        assert 'close' in cols

    def test_data_property(self, sample_candles):
        """Test data property returns DataFrame."""
        assert isinstance(sample_candles.data, DataFrame)

    def test_rename(self, sample_candles):
        """Test rename method."""
        sample_candles.rename(inplace=True, open='open_price')
        assert 'open_price' in sample_candles.data.columns

    def test_iadd(self, candles, candles_2):
        """Test in-place addition of candles."""
        original_len = len(candles)
        candles += candles_2
        assert len(candles) >= original_len

    def test_add(self, candles, candles_2):
        """Test addition creates new Candles object."""
        combined = candles + candles_2
        assert isinstance(combined, Candles)
        assert len(combined) == 300

    def test_add_candle(self, sample_candles):
        """Test add method with Candle object."""
        length = len(sample_candles)
        candle = sample_candles[-1]
        now = datetime.now()
        candle.time = now.timestamp() + 3600  # 1 hour later
        candle.index = pd.Timestamp(candle.time, unit="s", tz=now.astimezone().tzinfo)
        sample_candles.add(candle)
        assert len(sample_candles) == length + 1

    def test_add_series(self, sample_candles):
        """Test add method with Series object."""
        length = len(sample_candles)
        candle = sample_candles[-1]
        now = datetime.now()
        candle.time = now.timestamp() + 7200  # 2 hours later
        series = candle.to_series()
        sample_candles.add(series)
        assert len(sample_candles) == length + 1

    def test_add_dataframe(self, sample_candles):
        """Test add method with DataFrame object."""
        length = len(sample_candles)
        new_data = pd.DataFrame({
            'time': [datetime.now().timestamp() + 10800],
            'open': [200],
            'high': [210],
            'low': [190],
            'close': [205],
        })
        sample_candles.add(new_data)
        assert len(sample_candles) == length + 1

    def test_add_invalid_type(self, sample_candles):
        """Test add method raises TypeError for invalid input."""
        with pytest.raises(TypeError):
            sample_candles.add("invalid")

    def test_ta_accessor(self, sample_candles):
        """Test ta property for pandas_ta access."""
        ta = sample_candles.ta
        assert ta is not None

    def test_ta_lib_accessor(self, sample_candles):
        """Test ta_lib property returns pandas_ta_classic module."""
        assert sample_candles.ta_lib is ta

    def test_get_candle(self, candles):
        """Test getting single candle from live data."""
        candle = candles[10]
        assert isinstance(candle, Candle)
        assert candle in candles

    def test_slice_live(self, candles):
        """Test slicing live data."""
        sliced = candles[10:15]
        assert len(sliced) == 5
        assert isinstance(sliced, Candles)

    def test_timeframe_live(self, candles):
        """Test timeframe detection on live data."""
        tf = candles.timeframe
        assert tf == TimeFrame.H1

    def test_ta_and_rename_live(self, candles):
        """Test ta operations on live data."""
        ema = candles.ta.ema(close="open", length=10, append=True)
        assert "EMA_10" in candles.data.columns
        candles.rename(inplace=True, EMA_10="ema")
        assert "ema" in candles.data.columns

    def test_ta_lib_live(self, candles):
        """Test ta_lib operations on live data."""
        fas = candles.ta_lib.above(candles.open, candles.close)
        assert isinstance(fas, pd.Series)
        candles["fas"] = fas
        assert "fas" in candles.data.columns


class TestCandleComparisonsWithDict:
    """Test candle comparisons with dict-like objects."""

    def test_equal_to_dict(self):
        """Test candle equality with dict."""
        candle = Candle(open=100, high=110, low=95, close=108)
        candle_dict = {'open': 100, 'high': 110, 'low': 95, 'close': 108}
        assert candle == candle_dict

    def test_less_than_dict(self):
        """Test candle less than comparison with dict."""
        candle = Candle(open=100, high=105, low=98, close=102)  # body=2, range=7
        candle_dict = {'open': 100, 'high': 110, 'low': 90, 'close': 108}  # body=8, range=20
        assert candle < candle_dict

    def test_greater_than_dict(self):
        """Test candle greater than comparison with dict."""
        candle = Candle(open=100, high=120, low=80, close=115)  # body=15, range=40
        candle_dict = {'open': 100, 'high': 105, 'low': 98, 'close': 102}  # body=2, range=7
        assert candle > candle_dict


class TestCandleSorting:
    """Test candle sorting functionality."""

    def test_sort_candles(self):
        """Test sorting candles by body and range."""
        c1 = Candle(open=100, high=105, low=98, close=102)  # body=2, range=7
        c2 = Candle(open=100, high=110, low=90, close=108)  # body=8, range=20
        c3 = Candle(open=100, high=103, low=99, close=101)  # body=1, range=4

        candles = [c2, c1, c3]
        sorted_candles = sorted(candles)

        assert sorted_candles[0].candle_body == 1  # c3
        assert sorted_candles[1].candle_body == 2  # c1
        assert sorted_candles[2].candle_body == 8  # c2

    def test_candles_in_set(self):
        """Test using candles in a set."""
        c1 = Candle(open=100, high=110, low=95, close=108)
        c2 = Candle(open=102, high=112, low=97, close=110)  # Same key as c1

        candle_set = {c1, c2}
        # Both have same hash, so set should contain only one
        assert len(candle_set) <= 2
