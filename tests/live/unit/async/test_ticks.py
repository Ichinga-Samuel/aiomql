"""Comprehensive tests for the Tick and Ticks module.

Tests cover:
- Tick initialization with valid and invalid parameters
- Tick comparison and hashing operations
- Tick dictionary-like access and iteration
- Tick data conversion methods
- Ticks initialization from various data sources
- Ticks indexing, slicing, and iteration
- Ticks DataFrame operations
- Ticks technical analysis access
- Ticks addition and merging operations
- Integration tests with live MetaTrader data
"""

from datetime import datetime

import pytest
import pandas as pd
from pandas import DataFrame, Series

from aiomql.lib.ticks import Tick, Ticks
from aiomql.ta_libs import pandas_ta_classic as ta


class TestTickInitialization:
    """Test Tick class initialization."""

    def test_init_with_required_fields(self):
        """Test Tick initialization with all required fields."""
        tick = Tick(bid=1.1234, ask=1.1236, last=1.1235, volume=100.0)
        assert tick.bid == 1.1234
        assert tick.ask == 1.1236
        assert tick.last == 1.1235
        assert tick.volume == 100.0

    def test_init_sets_default_time(self):
        """Test Tick sets default time to current timestamp."""
        before = datetime.now().timestamp()
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        after = datetime.now().timestamp()
        assert before <= tick.time <= after

    def test_init_sets_default_time_msc(self):
        """Test Tick sets default time_msc from time."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        assert tick.time_msc == tick.time * 1000

    def test_init_sets_default_index(self):
        """Test Tick sets default Index to 0."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        assert tick.Index == 0

    def test_init_sets_default_index_as_time_msc(self):
        """Test Tick sets default index to time_msc."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        assert tick.index == tick.time_msc

    def test_init_with_custom_time(self):
        """Test Tick initialization with custom time."""
        custom_time = 1700000000.0
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time=custom_time)
        assert tick.time == custom_time

    def test_init_with_custom_time_msc(self):
        """Test Tick initialization with custom time_msc."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=1700000000000.0)
        assert tick.time_msc == 1700000000000.0

    def test_init_with_custom_index(self):
        """Test Tick initialization with custom Index."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, Index=5)
        assert tick.Index == 5

    def test_init_with_custom_index_lowercase(self):
        """Test Tick initialization with custom index (lowercase)."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, index=99999.0)
        assert tick.index == 99999.0

    def test_init_with_additional_attributes(self):
        """Test Tick initialization with additional custom attributes."""
        tick = Tick(
            bid=1.0, ask=1.1, last=1.05, volume=50.0,
            flags=1, volume_real=50.5, custom_attr="test"
        )
        assert tick.flags == 1
        assert tick.volume_real == 50.5
        assert tick.custom_attr == "test"

    def test_init_missing_bid_raises_error(self):
        """Test Tick initialization without bid raises ValueError."""
        with pytest.raises(ValueError):
            Tick(ask=1.1, last=1.05, volume=50.0)

    def test_init_missing_ask_raises_error(self):
        """Test Tick initialization without ask raises ValueError."""
        with pytest.raises(ValueError):
            Tick(bid=1.0, last=1.05, volume=50.0)

    def test_init_missing_last_raises_error(self):
        """Test Tick initialization without last raises ValueError."""
        with pytest.raises(ValueError):
            Tick(bid=1.0, ask=1.1, volume=50.0)

    def test_init_missing_volume_raises_error(self):
        """Test Tick initialization without volume raises ValueError."""
        with pytest.raises(ValueError):
            Tick(bid=1.0, ask=1.1, last=1.05)

    def test_init_missing_all_required_raises_error(self):
        """Test Tick initialization with no arguments raises ValueError."""
        with pytest.raises(ValueError):
            Tick()


class TestTickRepr:
    """Test Tick __repr__ method."""

    def test_repr_contains_class_name(self):
        """Test repr contains class name."""
        tick = Tick(bid=1.1234, ask=1.1236, last=1.1235, volume=100.0)
        assert "Tick" in repr(tick)

    def test_repr_contains_bid(self):
        """Test repr contains bid value."""
        tick = Tick(bid=1.1234, ask=1.1236, last=1.1235, volume=100.0)
        assert "bid=1.1234" in repr(tick)

    def test_repr_contains_ask(self):
        """Test repr contains ask value."""
        tick = Tick(bid=1.1234, ask=1.1236, last=1.1235, volume=100.0)
        assert "ask=1.1236" in repr(tick)

    def test_repr_contains_last(self):
        """Test repr contains last value."""
        tick = Tick(bid=1.1234, ask=1.1236, last=1.1235, volume=100.0)
        assert "last=1.1235" in repr(tick)

    def test_repr_contains_volume(self):
        """Test repr contains volume value."""
        tick = Tick(bid=1.1234, ask=1.1236, last=1.1235, volume=100.0)
        assert "volume=100.0" in repr(tick)

    def test_repr_contains_index(self):
        """Test repr contains Index value."""
        tick = Tick(bid=1.1234, ask=1.1236, last=1.1235, volume=100.0, Index=5)
        assert "Index=5" in repr(tick)


class TestTickComparison:
    """Test Tick comparison operations."""

    def test_eq_same_time_msc(self):
        """Test equality with same time_msc."""
        tick1 = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=1000.0)
        tick2 = Tick(bid=2.0, ask=2.1, last=2.05, volume=100.0, time_msc=1000.0)
        assert tick1 == tick2

    def test_eq_different_time_msc(self):
        """Test inequality with different time_msc."""
        tick1 = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=1000.0)
        tick2 = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=2000.0)
        assert not (tick1 == tick2)

    def test_lt_earlier_time_msc(self):
        """Test less than with earlier time_msc."""
        tick1 = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=1000.0)
        tick2 = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=2000.0)
        assert tick1 < tick2

    def test_lt_later_time_msc(self):
        """Test not less than with later time_msc."""
        tick1 = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=2000.0)
        tick2 = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=1000.0)
        assert not (tick1 < tick2)

    def test_lt_same_time_msc(self):
        """Test not less than with same time_msc."""
        tick1 = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=1000.0)
        tick2 = Tick(bid=2.0, ask=2.1, last=2.05, volume=100.0, time_msc=1000.0)
        assert not (tick1 < tick2)

    def test_hash_same_time_msc(self):
        """Test same hash for same time_msc."""
        tick1 = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=1000.0)
        tick2 = Tick(bid=2.0, ask=2.1, last=2.05, volume=100.0, time_msc=1000.0)
        assert hash(tick1) == hash(tick2)

    def test_hash_different_time_msc(self):
        """Test different hash for different time_msc."""
        tick1 = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=1000.0)
        tick2 = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=2000.0)
        assert hash(tick1) != hash(tick2)

    def test_tick_can_be_used_in_set(self):
        """Test Tick can be used in a set based on time_msc."""
        tick1 = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=1000.0)
        tick2 = Tick(bid=2.0, ask=2.1, last=2.05, volume=100.0, time_msc=1000.0)
        tick3 = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=2000.0)
        tick_set = {tick1, tick2, tick3}
        assert len(tick_set) == 2

    def test_tick_can_be_sorted(self):
        """Test Tick can be sorted by time_msc."""
        tick1 = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=3000.0)
        tick2 = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=1000.0)
        tick3 = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, time_msc=2000.0)
        sorted_ticks = sorted([tick1, tick2, tick3])
        assert sorted_ticks[0].time_msc == 1000.0
        assert sorted_ticks[1].time_msc == 2000.0
        assert sorted_ticks[2].time_msc == 3000.0


class TestTickDictAccess:
    """Test Tick dictionary-like access."""

    def test_getitem_existing_key(self):
        """Test __getitem__ for existing key."""
        tick = Tick(bid=1.1234, ask=1.1236, last=1.1235, volume=100.0)
        assert tick["bid"] == 1.1234

    def test_getitem_missing_key_raises_error(self):
        """Test __getitem__ for missing key raises KeyError."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        with pytest.raises(KeyError):
            _ = tick["nonexistent"]

    def test_setitem_new_key(self):
        """Test __setitem__ creates new attribute."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        tick["custom"] = "value"
        assert tick["custom"] == "value"
        assert tick.custom == "value"

    def test_setitem_existing_key(self):
        """Test __setitem__ updates existing attribute."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        tick["bid"] = 2.0
        assert tick["bid"] == 2.0
        assert tick.bid == 2.0

    def test_iter_returns_key_value_pairs(self):
        """Test __iter__ returns key-value pairs."""
        tick = Tick(bid=1.1234, ask=1.1236, last=1.1235, volume=100.0)
        items = dict(tick)
        assert "bid" in items
        assert items["bid"] == 1.1234

    def test_keys_returns_attribute_names(self):
        """Test keys() returns attribute names."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        keys = tick.keys()
        assert "bid" in keys
        assert "ask" in keys
        assert "last" in keys
        assert "volume" in keys

    def test_values_returns_attribute_values(self):
        """Test values() returns attribute values."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        values = list(tick.values())
        assert 1.0 in values
        assert 1.1 in values
        assert 1.05 in values
        assert 50.0 in values


class TestTickDict:
    """Test Tick dict() method."""

    def test_dict_returns_all_attributes(self):
        """Test dict() returns all attributes by default."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        d = tick.dict()
        assert "bid" in d
        assert "ask" in d
        assert "last" in d
        assert "volume" in d
        assert "time" in d

    def test_dict_exclude_single(self):
        """Test dict() excludes specified attributes."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        d = tick.dict(exclude={"time", "time_msc"})
        assert "time" not in d
        assert "time_msc" not in d
        assert "bid" in d

    def test_dict_include_only(self):
        """Test dict() includes only specified attributes."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        d = tick.dict(include={"bid", "ask"})
        assert d == {"bid": 1.0, "ask": 1.1}

    def test_dict_include_overrides_exclude(self):
        """Test include takes precedence when both are specified."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        d = tick.dict(exclude={"bid"}, include={"bid", "ask"})
        # include should take precedence
        assert "bid" in d
        assert "ask" in d

    def test_dict_with_empty_exclude(self):
        """Test dict() with empty exclude set."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        d = tick.dict(exclude=set())
        assert "bid" in d

    def test_dict_with_empty_include(self):
        """Test dict() with empty include set returns all."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        d = tick.dict(include=set())
        # Empty include should return all
        assert "bid" in d
        assert "ask" in d


class TestTickSetAttributes:
    """Test Tick set_attributes() method."""

    def test_set_attributes_single(self):
        """Test set_attributes with single attribute."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        tick.set_attributes(custom="value")
        assert tick.custom == "value"

    def test_set_attributes_multiple(self):
        """Test set_attributes with multiple attributes."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        tick.set_attributes(attr1="one", attr2=2, attr3=3.0)
        assert tick.attr1 == "one"
        assert tick.attr2 == 2
        assert tick.attr3 == 3.0

    def test_set_attributes_override_existing(self):
        """Test set_attributes can override existing attributes."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        tick.set_attributes(bid=2.0)
        assert tick.bid == 2.0


class TestTickToSeries:
    """Test Tick to_series() method."""

    def test_to_series_returns_series(self):
        """Test to_series returns pandas Series."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        series = tick.to_series()
        assert isinstance(series, Series)

    def test_to_series_excludes_index(self):
        """Test to_series excludes Index and index."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0, Index=5)
        series = tick.to_series()
        assert "Index" not in series.index
        assert "index" not in series.index

    def test_to_series_contains_data(self):
        """Test to_series contains tick data."""
        tick = Tick(bid=1.0, ask=1.1, last=1.05, volume=50.0)
        series = tick.to_series()
        assert "bid" in series.index
        assert series["bid"] == 1.0


class TestTicksInitialization:
    """Test Ticks class initialization."""

    @pytest.fixture
    def sample_dataframe(self):
        """Create sample tick DataFrame."""
        return DataFrame({
            "time": [1700000000, 1700000001, 1700000002],
            "bid": [1.0, 1.1, 1.2],
            "ask": [1.01, 1.11, 1.21],
            "last": [1.005, 1.105, 1.205],
            "volume": [100.0, 200.0, 300.0],
            "time_msc": [1700000000000, 1700000001000, 1700000002000],
            "flags": [1, 2, 3],
            "volume_real": [100.5, 200.5, 300.5],
        })

    def test_init_from_dataframe(self, sample_dataframe):
        """Test Ticks initialization from DataFrame."""
        ticks = Ticks(data=sample_dataframe)
        assert len(ticks) == 3

    def test_init_from_ticks_instance(self, sample_dataframe):
        """Test Ticks initialization from another Ticks instance."""
        ticks1 = Ticks(data=sample_dataframe)
        ticks2 = Ticks(data=ticks1)
        assert len(ticks2) == 3

    def test_init_from_list_of_dicts(self):
        """Test Ticks initialization from list of dicts."""
        data = [
            {"time": 1, "bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0, "time_msc": 1000},
            {"time": 2, "bid": 1.1, "ask": 1.2, "last": 1.15, "volume": 60.0, "time_msc": 2000},
        ]
        ticks = Ticks(data=data)
        assert len(ticks) == 2

    def test_init_sets_time_msc_as_index(self, sample_dataframe):
        """Test Ticks sets time_msc as DataFrame index."""
        ticks = Ticks(data=sample_dataframe)
        assert list(ticks.data.index) == [1700000000000, 1700000001000, 1700000002000]

    def test_init_with_flip(self, sample_dataframe):
        """Test Ticks initialization with flip=True reverses order."""
        ticks = Ticks(data=sample_dataframe, flip=True)
        assert ticks[0].bid == 1.2  # Originally last row
        assert ticks[-1].bid == 1.0  # Originally first row

    def test_init_without_flip(self, sample_dataframe):
        """Test Ticks initialization without flip maintains order."""
        ticks = Ticks(data=sample_dataframe, flip=False)
        assert ticks[0].bid == 1.0  # First row
        assert ticks[-1].bid == 1.2  # Last row

    def test_init_invalid_type_raises_error(self):
        """Test Ticks initialization with invalid type raises ValueError."""
        with pytest.raises(ValueError):
            Ticks(data="invalid")

    def test_init_from_numpy_array(self):
        """Test Ticks initialization from numpy array (via DataFrame)."""
        import numpy as np
        arr = np.array([
            [1.0, 1.1, 1.05, 50.0, 1000],
            [1.1, 1.2, 1.15, 60.0, 2000],
        ])
        df = DataFrame(arr, columns=["bid", "ask", "last", "volume", "time_msc"])
        ticks = Ticks(data=df)
        assert len(ticks) == 2


class TestTicksLen:
    """Test Ticks __len__ method."""

    def test_len_returns_correct_count(self):
        """Test len returns correct number of ticks."""
        data = [
            {"bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0, "time_msc": 1000},
            {"bid": 1.1, "ask": 1.2, "last": 1.15, "volume": 60.0, "time_msc": 2000},
            {"bid": 1.2, "ask": 1.3, "last": 1.25, "volume": 70.0, "time_msc": 3000},
        ]
        ticks = Ticks(data=data)
        assert len(ticks) == 3

    def test_len_empty_ticks(self):
        """Test len for empty Ticks container."""
        ticks = Ticks(data=DataFrame())
        assert len(ticks) == 0


class TestTicksRepr:
    """Test Ticks __repr__ method."""

    def test_repr_returns_string(self):
        """Test repr returns string representation."""
        data = [{"bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0, "time_msc": 1000}]
        ticks = Ticks(data=data)
        assert isinstance(repr(ticks), str)


class TestTicksContains:
    """Test Ticks __contains__ method."""

    def test_contains_existing_tick(self):
        """Test __contains__ for existing tick."""
        data = [
            {"bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0, "time_msc": 1000},
            {"bid": 1.1, "ask": 1.2, "last": 1.15, "volume": 60.0, "time_msc": 2000},
        ]
        ticks = Ticks(data=data)
        tick = ticks[0]
        assert tick in ticks

    def test_contains_after_modification(self):
        """Test __contains__ after modifying tick time_msc."""
        data = [
            {"bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0, "time_msc": 1000},
        ]
        ticks = Ticks(data=data)
        tick = ticks[0]
        tick.time_msc = 9999  # Modify time_msc
        assert tick not in ticks


class TestTicksGetattr:
    """Test Ticks __getattr__ method."""

    @pytest.fixture
    def sample_ticks(self):
        """Create sample Ticks instance."""
        data = [
            {"bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0, "time_msc": 1000},
            {"bid": 1.1, "ask": 1.2, "last": 1.15, "volume": 60.0, "time_msc": 2000},
        ]
        return Ticks(data=data)

    def test_getattr_column(self, sample_ticks):
        """Test __getattr__ returns column as Series."""
        bids = sample_ticks.bid
        assert isinstance(bids, Series)
        assert list(bids) == [1.0, 1.1]

    def test_getattr_index_lowercase(self, sample_ticks):
        """Test __getattr__ for 'index' returns DataFrame index."""
        index = sample_ticks.index
        assert list(index) == [1000, 2000]

    def test_getattr_index_uppercase(self, sample_ticks):
        """Test __getattr__ for 'Index' returns sequential range."""
        Index = sample_ticks.Index
        assert isinstance(Index, Series)
        assert list(Index) == [0, 1]

    def test_getattr_nonexistent_raises_error(self, sample_ticks):
        """Test __getattr__ for non-existent attribute raises AttributeError."""
        with pytest.raises(AttributeError):
            _ = sample_ticks.nonexistent


class TestTicksGetitem:
    """Test Ticks __getitem__ method."""

    @pytest.fixture
    def sample_ticks(self):
        """Create sample Ticks instance."""
        data = [
            {"bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0, "time_msc": 1000},
            {"bid": 1.1, "ask": 1.2, "last": 1.15, "volume": 60.0, "time_msc": 2000},
            {"bid": 1.2, "ask": 1.3, "last": 1.25, "volume": 70.0, "time_msc": 3000},
        ]
        return Ticks(data=data)

    def test_getitem_positive_int(self, sample_ticks):
        """Test __getitem__ with positive integer returns Tick."""
        tick = sample_ticks[0]
        assert isinstance(tick, Tick)
        assert tick.bid == 1.0
        assert tick.Index == 0

    def test_getitem_negative_int(self, sample_ticks):
        """Test __getitem__ with negative integer returns Tick."""
        tick = sample_ticks[-1]
        assert isinstance(tick, Tick)
        assert tick.bid == 1.2
        assert tick.Index == 2

    def test_getitem_slice(self, sample_ticks):
        """Test __getitem__ with slice returns Ticks."""
        sliced = sample_ticks[1:3]
        assert isinstance(sliced, Ticks)
        assert len(sliced) == 2
        assert sliced[0].bid == 1.1

    def test_getitem_string_column(self, sample_ticks):
        """Test __getitem__ with string returns column Series."""
        bids = sample_ticks["bid"]
        assert isinstance(bids, Series)
        assert list(bids) == [1.0, 1.1, 1.2]

    def test_getitem_string_index(self, sample_ticks):
        """Test __getitem__ with 'index' returns DataFrame index."""
        index = sample_ticks["index"]
        assert list(index) == [1000, 2000, 3000]

    def test_getitem_string_index_uppercase(self, sample_ticks):
        """Test __getitem__ with 'Index' returns sequential range."""
        Index = sample_ticks["Index"]
        assert list(Index) == [0, 1, 2]

    def test_getitem_invalid_type_raises_error(self, sample_ticks):
        """Test __getitem__ with invalid type raises TypeError."""
        with pytest.raises(TypeError):
            _ = sample_ticks[1.5]

    def test_getitem_sets_correct_index_for_tick(self, sample_ticks):
        """Test __getitem__ sets correct index for returned Tick."""
        tick = sample_ticks[1]
        assert tick.index == 2000  # time_msc
        assert tick.Index == 1     # Position


class TestTicksSetitem:
    """Test Ticks __setitem__ method."""

    @pytest.fixture
    def sample_ticks(self):
        """Create sample Ticks instance."""
        data = [
            {"bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0, "time_msc": 1000},
            {"bid": 1.1, "ask": 1.2, "last": 1.15, "volume": 60.0, "time_msc": 2000},
        ]
        return Ticks(data=data)

    def test_setitem_new_column(self, sample_ticks):
        """Test __setitem__ adds new column."""
        sample_ticks["spread"] = Series([0.1, 0.1], index=sample_ticks.index)
        assert "spread" in sample_ticks.data.columns

    def test_setitem_existing_column(self, sample_ticks):
        """Test __setitem__ overwrites existing column."""
        sample_ticks["bid"] = Series([2.0, 2.1], index=sample_ticks.index)
        assert list(sample_ticks.bid) == [2.0, 2.1]

    def test_setitem_non_series_raises_error(self, sample_ticks):
        """Test __setitem__ with non-Series raises TypeError."""
        with pytest.raises(TypeError):
            sample_ticks["spread"] = [0.1, 0.1]


class TestTicksIteration:
    """Test Ticks iteration methods."""

    @pytest.fixture
    def sample_ticks(self):
        """Create sample Ticks instance."""
        data = [
            {"bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0, "time_msc": 1000},
            {"bid": 1.1, "ask": 1.2, "last": 1.15, "volume": 60.0, "time_msc": 2000},
            {"bid": 1.2, "ask": 1.3, "last": 1.25, "volume": 70.0, "time_msc": 3000},
        ]
        return Ticks(data=data)

    def test_iter_yields_ticks(self, sample_ticks):
        """Test __iter__ yields Tick objects."""
        for tick in sample_ticks:
            assert isinstance(tick, Tick)

    def test_iter_chronological_order(self, sample_ticks):
        """Test __iter__ yields ticks in chronological order."""
        bids = [tick.bid for tick in sample_ticks]
        assert bids == [1.0, 1.1, 1.2]

    def test_iter_sets_correct_index(self, sample_ticks):
        """Test __iter__ sets correct Index for each tick."""
        indices = [tick.Index for tick in sample_ticks]
        assert indices == [0, 1, 2]

    def test_reversed_yields_ticks(self, sample_ticks):
        """Test __reversed__ yields Tick objects."""
        for tick in reversed(sample_ticks):
            assert isinstance(tick, Tick)

    def test_reversed_reverse_chronological_order(self, sample_ticks):
        """Test __reversed__ yields ticks in reverse chronological order."""
        bids = [tick.bid for tick in reversed(sample_ticks)]
        assert bids == [1.2, 1.1, 1.0]

    def test_reversed_sets_correct_index(self, sample_ticks):
        """Test __reversed__ sets correct Index for each tick."""
        indices = [tick.Index for tick in reversed(sample_ticks)]
        assert indices == [2, 1, 0]


class TestTicksProperties:
    """Test Ticks properties."""

    @pytest.fixture
    def sample_ticks(self):
        """Create sample Ticks instance."""
        data = [
            {"bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0, "time_msc": 1000},
            {"bid": 1.1, "ask": 1.2, "last": 1.15, "volume": 60.0, "time_msc": 2000},
        ]
        return Ticks(data=data)

    def test_data_property_returns_dataframe(self, sample_ticks):
        """Test data property returns DataFrame."""
        assert isinstance(sample_ticks.data, DataFrame)

    def test_ta_property_access(self, sample_ticks):
        """Test ta property for pandas_ta access."""
        assert hasattr(sample_ticks, "ta")
        assert sample_ticks.ta is sample_ticks.data.ta

    def test_ta_lib_property_returns_ta(self, sample_ticks):
        """Test ta_lib property returns pandas_ta_classic module."""
        assert sample_ticks.ta_lib is ta


class TestTicksRename:
    """Test Ticks rename() method."""

    @pytest.fixture
    def sample_ticks(self):
        """Create sample Ticks instance."""
        data = [
            {"bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0, "time_msc": 1000},
        ]
        return Ticks(data=data)

    def test_rename_inplace(self, sample_ticks):
        """Test rename with inplace=True modifies in place."""
        sample_ticks.rename(inplace=True, bid="bidPrice")
        assert "bidPrice" in sample_ticks.data.columns
        assert "bid" not in sample_ticks.data.columns


class TestTicksAddition:
    """Test Ticks addition operations."""

    @pytest.fixture
    def ticks1(self):
        """Create first Ticks instance."""
        data = [
            {"bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0, "time_msc": 1000},
            {"bid": 1.1, "ask": 1.2, "last": 1.15, "volume": 60.0, "time_msc": 2000},
        ]
        return Ticks(data=data)

    @pytest.fixture
    def ticks2(self):
        """Create second Ticks instance."""
        data = [
            {"bid": 1.2, "ask": 1.3, "last": 1.25, "volume": 70.0, "time_msc": 3000},
            {"bid": 1.3, "ask": 1.4, "last": 1.35, "volume": 80.0, "time_msc": 4000},
        ]
        return Ticks(data=data)

    def test_add_returns_new_ticks(self, ticks1, ticks2):
        """Test __add__ returns new Ticks instance."""
        result = ticks1 + ticks2
        assert isinstance(result, Ticks)
        assert len(result) == 4

    def test_add_preserves_originals(self, ticks1, ticks2):
        """Test __add__ does not modify originals."""
        original_len1 = len(ticks1)
        original_len2 = len(ticks2)
        _ = ticks1 + ticks2
        assert len(ticks1) == original_len1
        assert len(ticks2) == original_len2

    def test_add_sorted_by_index(self, ticks1, ticks2):
        """Test __add__ result is sorted by index."""
        result = ticks1 + ticks2
        indices = list(result.index)
        assert indices == sorted(indices)

    def test_iadd_modifies_in_place(self, ticks1, ticks2):
        """Test __iadd__ modifies in place."""
        original_id = id(ticks1)
        ticks1 += ticks2
        assert id(ticks1) == original_id
        assert len(ticks1) == 4

    def test_iadd_sorted_by_index(self, ticks1, ticks2):
        """Test __iadd__ result is sorted by index."""
        ticks1 += ticks2
        indices = list(ticks1.index)
        assert indices == sorted(indices)

    def test_add_overlapping_indices(self, ticks1):
        """Test __add__ with overlapping indices updates values."""
        ticks_overlap = Ticks(data=[
            {"bid": 9.9, "ask": 9.9, "last": 9.9, "volume": 999.0, "time_msc": 1000},  # Same as first
        ])
        result = ticks1 + ticks_overlap
        # The overlapping entry should be overwritten
        assert result[0].bid == 9.9


class TestTicksAdd:
    """Test Ticks add() method."""

    @pytest.fixture
    def sample_ticks(self):
        """Create sample Ticks instance."""
        data = [
            {"bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0, "time_msc": 1000},
        ]
        return Ticks(data=data)

    def test_add_tick(self, sample_ticks):
        """Test add() with Tick object."""
        tick = Tick(bid=1.1, ask=1.2, last=1.15, volume=60.0, time_msc=2000)
        sample_ticks.add(tick)
        assert len(sample_ticks) == 2

    def test_add_series(self, sample_ticks):
        """Test add() with Series object."""
        series = Series({
            "bid": 1.1, "ask": 1.2, "last": 1.15, "volume": 60.0, "time_msc": 2000
        }, name=2000)  # name is the index
        sample_ticks.add(series)
        assert len(sample_ticks) == 2

    def test_add_dataframe(self, sample_ticks):
        """Test add() with DataFrame object."""
        df = DataFrame([
            {"bid": 1.1, "ask": 1.2, "last": 1.15, "volume": 60.0, "time_msc": 2000},
            {"bid": 1.2, "ask": 1.3, "last": 1.25, "volume": 70.0, "time_msc": 3000},
        ])
        df.index = df["time_msc"]
        sample_ticks.add(df)
        assert len(sample_ticks) == 3

    def test_add_invalid_type_raises_error(self, sample_ticks):
        """Test add() with invalid type raises TypeError."""
        with pytest.raises(TypeError):
            sample_ticks.add("invalid")

    def test_add_returns_self(self, sample_ticks):
        """Test add() returns self for chaining."""
        tick = Tick(bid=1.1, ask=1.2, last=1.15, volume=60.0, time_msc=2000)
        result = sample_ticks.add(tick)
        assert result is sample_ticks

    def test_add_maintains_sorted_order(self, sample_ticks):
        """Test add() maintains sorted order by index."""
        tick = Tick(bid=0.9, ask=1.0, last=0.95, volume=40.0, time_msc=500)  # Earlier than existing
        sample_ticks.add(tick)
        indices = list(sample_ticks.index)
        assert indices == sorted(indices)


class TestTicksLiveData:
    """Integration tests with live MetaTrader data."""

    async def test_tick_from_live_data(self, mt):
        """Test creating Tick from live MetaTrader data."""
        btc_tick = await mt.symbol_info_tick("BTCUSD")
        tick = Tick(**btc_tick._asdict())
        assert isinstance(tick, Tick)
        assert hasattr(tick, "bid")
        assert hasattr(tick, "ask")
        assert hasattr(tick, "last")
        assert hasattr(tick, "volume")

    async def test_tick_dict_with_live_data(self, mt):
        """Test Tick dict() method with live data."""
        btc_tick = await mt.symbol_info_tick("BTCUSD")
        tick = Tick(**btc_tick._asdict())
        tick_dict = tick.dict(include={"ask", "bid", "time", "volume"})
        assert isinstance(tick_dict, dict)
        assert "ask" in tick_dict
        assert "bid" in tick_dict
        assert "volume_real" not in tick_dict

    async def test_ticks_from_live_data(self, mt):
        """Test creating Ticks from live MetaTrader data."""
        start = datetime(year=2026, month=1, day=5)
        ticks_data = await mt.copy_ticks_from("EURUSD", start, 10, mt.COPY_TICKS_ALL)
        ticks = Ticks(data=ticks_data)
        assert isinstance(ticks, Ticks)
        assert len(ticks) == 10

    async def test_ticks_indexing_with_live_data(self, mt):
        """Test Ticks indexing with live data."""
        start = datetime(year=2026, month=1, day=5)
        ticks_data = await mt.copy_ticks_from("EURUSD", start, 10, mt.COPY_TICKS_ALL)
        ticks = Ticks(data=ticks_data)
        assert isinstance(ticks[0], Tick)
        assert isinstance(ticks[-1], Tick)

    async def test_ticks_column_access_with_live_data(self, mt):
        """Test Ticks column access with live data."""
        start = datetime(year=2026, month=1, day=5)
        ticks_data = await mt.copy_ticks_from("EURUSD", start, 10, mt.COPY_TICKS_ALL)
        ticks = Ticks(data=ticks_data)
        bids = ticks["bid"]
        assert len(bids) == 10
        assert isinstance(bids, Series)

    async def test_ticks_slicing_with_live_data(self, mt):
        """Test Ticks slicing with live data."""
        start = datetime(year=2026, month=1, day=5)
        ticks_data = await mt.copy_ticks_from("EURUSD", start, 10, mt.COPY_TICKS_ALL)
        ticks = Ticks(data=ticks_data)
        subset = ticks[5:]
        assert isinstance(subset, Ticks)
        assert len(subset) == 5

    async def test_ticks_iteration_with_live_data(self, mt):
        """Test Ticks iteration with live data."""
        start = datetime(year=2026, month=1, day=5)
        ticks_data = await mt.copy_ticks_from("EURUSD", start, 10, mt.COPY_TICKS_ALL)
        ticks = Ticks(data=ticks_data)
        count = 0
        for tick in ticks:
            assert isinstance(tick, Tick)
            count += 1
        assert count == 10

    async def test_ticks_reversed_with_live_data(self, mt):
        """Test Ticks reversed iteration with live data."""
        start = datetime(year=2026, month=1, day=5)
        ticks_data = await mt.copy_ticks_from("EURUSD", start, 10, mt.COPY_TICKS_ALL)
        ticks = Ticks(data=ticks_data)
        reversed_list = list(reversed(ticks))
        assert len(reversed_list) == 10
        # First in reversed should be last in original
        assert reversed_list[0].time_msc == ticks[-1].time_msc

    async def test_tick_comparison_with_live_data(self, mt):
        """Test Tick comparison with live data."""
        start = datetime(year=2026, month=1, day=5)
        ticks_data = await mt.copy_ticks_from("EURUSD", start, 10, mt.COPY_TICKS_ALL)
        ticks = Ticks(data=ticks_data)
        tick1 = ticks[0]
        tick2 = ticks[1]
        assert tick1 < tick2 or tick1 == tick2  # tick1 should be earlier or same time

    async def test_ticks_data_property_with_live_data(self, mt):
        """Test Ticks data property with live data."""
        start = datetime(year=2026, month=1, day=5)
        ticks_data = await mt.copy_ticks_from("EURUSD", start, 10, mt.COPY_TICKS_ALL)
        ticks = Ticks(data=ticks_data)
        assert isinstance(ticks.data, DataFrame)
        assert "bid" in ticks.data.columns
        assert "ask" in ticks.data.columns

    async def test_tick_contains_with_live_data(self, mt):
        """Test Tick contains check with live data."""
        start = datetime(year=2026, month=1, day=5)
        ticks_data = await mt.copy_ticks_from("EURUSD", start, 10, mt.COPY_TICKS_ALL)
        ticks = Ticks(data=ticks_data)
        tick = ticks[5]
        assert tick in ticks

    async def test_tick_to_series_with_live_data(self, mt):
        """Test Tick to_series with live data."""
        btc_tick = await mt.symbol_info_tick("BTCUSD")
        tick = Tick(**btc_tick._asdict())
        series = tick.to_series()
        assert isinstance(series, Series)
        assert "bid" in series.index
        assert "ask" in series.index

    async def test_ticks_add_tick_with_live_data(self, mt):
        """Test Ticks add() with live Tick data."""
        start = datetime(year=2026, month=1, day=5)
        ticks_data = await mt.copy_ticks_from("EURUSD", start, 10, mt.COPY_TICKS_ALL)
        ticks = Ticks(data=ticks_data)

        # Get another tick
        btc_tick = await mt.symbol_info_tick("EURUSD")
        new_tick = Tick(**btc_tick._asdict())

        original_len = len(ticks)
        ticks.add(new_tick)
        assert len(ticks) == original_len + 1

    async def test_ticks_addition_with_live_data(self, mt):
        """Test Ticks addition with live data."""
        start1 = datetime(year=2026, month=1, day=5)
        start2 = datetime(year=2026, month=1, day=6)
        ticks1_data = await mt.copy_ticks_from("EURUSD", start1, 5, mt.COPY_TICKS_ALL)
        ticks2_data = await mt.copy_ticks_from("EURUSD", start2, 5, mt.COPY_TICKS_ALL)

        ticks1 = Ticks(data=ticks1_data)
        ticks2 = Ticks(data=ticks2_data)

        combined = ticks1 + ticks2
        assert isinstance(combined, Ticks)
        assert len(combined) >= len(ticks1)  # Should have more or equal (depends on overlap)


class TestTickEdgeCases:
    """Test edge cases for Tick class."""

    def test_tick_with_zero_values(self):
        """Test Tick with zero values."""
        tick = Tick(bid=0.0, ask=0.0, last=0.0, volume=0.0)
        assert tick.bid == 0.0
        assert tick.volume == 0.0

    def test_tick_with_negative_values(self):
        """Test Tick with negative values (some markets allow negative prices)."""
        tick = Tick(bid=-1.0, ask=-0.9, last=-0.95, volume=100.0)
        assert tick.bid == -1.0

    def test_tick_with_very_large_values(self):
        """Test Tick with very large values."""
        tick = Tick(bid=1e12, ask=1e12 + 100, last=1e12 + 50, volume=1e10)
        assert tick.bid == 1e12

    def test_tick_with_very_small_decimal_values(self):
        """Test Tick with very small decimal values."""
        tick = Tick(bid=0.00001, ask=0.00002, last=0.000015, volume=0.001)
        assert tick.bid == 0.00001


class TestTicksEdgeCases:
    """Test edge cases for Ticks class."""

    def test_ticks_single_item(self):
        """Test Ticks with single item."""
        data = [{"bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0, "time_msc": 1000}]
        ticks = Ticks(data=data)
        assert len(ticks) == 1
        assert ticks[0].bid == 1.0
        assert ticks[-1].bid == 1.0

    def test_ticks_empty(self):
        """Test empty Ticks container."""
        ticks = Ticks(data=DataFrame())
        assert len(ticks) == 0
        list_ticks = list(ticks)
        assert list_ticks == []

    def test_ticks_slice_empty_result(self):
        """Test Ticks slice that results in empty."""
        data = [{"bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0, "time_msc": 1000}]
        ticks = Ticks(data=data)
        empty_slice = ticks[10:20]
        assert len(empty_slice) == 0

    def test_ticks_without_time_msc_column(self):
        """Test Ticks without time_msc column."""
        data = [{"bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0}]
        ticks = Ticks(data=data)
        assert len(ticks) == 1

    def test_ticks_with_duplicate_time_msc(self):
        """Test Ticks with duplicate time_msc values."""
        data = [
            {"bid": 1.0, "ask": 1.1, "last": 1.05, "volume": 50.0, "time_msc": 1000},
            {"bid": 1.1, "ask": 1.2, "last": 1.15, "volume": 60.0, "time_msc": 1000},  # Same time_msc
        ]
        ticks = Ticks(data=data)
        # Both should be in the data
        assert len(ticks) == 2
