"""Comprehensive tests for the strategy_tracker module.

Tests cover:
- StrategyTracker dataclass initialization
- Default values
- time and timestamp properties
- update method with various kwargs
- trend state updates (ranging, bullish, bearish)
"""

import pytest
from dataclasses import fields
from unittest.mock import patch
from datetime import datetime

from aiomql.contrib.utils.strategy_tracker import StrategyTracker
from aiomql.core.constants import OrderType


class TestStrategyTrackerInitialization:
    """Tests for StrategyTracker initialization."""

    def test_default_initialization(self):
        """Test StrategyTracker with default values."""
        tracker = StrategyTracker()
        
        assert tracker.trend == "ranging"
        assert tracker.bullish is False
        assert tracker.bearish is False
        assert tracker.ranging is True
        assert tracker.snooze == 0
        assert tracker.trend_time == 0
        assert tracker.entry_time == 0
        assert tracker.last_trend_price == 0
        assert tracker.last_entry_price == 0
        assert tracker.new is True
        assert tracker.order_type is None
        assert tracker.sl == 0
        assert tracker.tp == 0

    def test_custom_initialization(self):
        """Test StrategyTracker with custom values."""
        tracker = StrategyTracker(
            trend="bullish",
            bullish=True,
            bearish=False,
            ranging=False,
            snooze=5.0,
            trend_time=1000.0,
            entry_time=1001.0,
            last_trend_price=1.1000,
            last_entry_price=1.1005,
            new=False,
            order_type=OrderType.BUY,
            sl=1.0950,
            tp=1.1100
        )
        
        assert tracker.trend == "bullish"
        assert tracker.bullish is True
        assert tracker.bearish is False
        assert tracker.ranging is False
        assert tracker.snooze == 5.0
        assert tracker.order_type == OrderType.BUY
        assert tracker.sl == 1.0950
        assert tracker.tp == 1.1100

    def test_is_dataclass(self):
        """Test StrategyTracker is a proper dataclass."""
        field_names = [f.name for f in fields(StrategyTracker)]
        
        assert "trend" in field_names
        assert "bullish" in field_names
        assert "bearish" in field_names
        assert "ranging" in field_names
        assert "snooze" in field_names
        assert "order_type" in field_names
        assert "sl" in field_names
        assert "tp" in field_names


class TestStrategyTrackerProperties:
    """Tests for StrategyTracker properties."""

    def test_time_property_returns_datetime(self):
        """Test time property returns current datetime."""
        tracker = StrategyTracker()
        
        result = tracker.time
        
        assert isinstance(result, datetime)

    def test_timestamp_property_returns_float(self):
        """Test timestamp property returns float timestamp."""
        tracker = StrategyTracker()
        
        result = tracker.timestamp
        
        assert isinstance(result, float)

    def test_timestamp_equals_time_timestamp(self):
        """Test timestamp equals time.timestamp()."""
        tracker = StrategyTracker()
        
        # Mock datetime.now to ensure consistency
        fixed_time = datetime(2026, 2, 3, 12, 0, 0)
        with patch.object(StrategyTracker, 'time', fixed_time):
            result = tracker.timestamp
            
            assert result == fixed_time.timestamp()


class TestStrategyTrackerUpdate:
    """Tests for StrategyTracker update method."""

    def test_update_single_field(self):
        """Test update with a single field."""
        tracker = StrategyTracker()
        
        tracker.update(snooze=10.0)
        
        assert tracker.snooze == 10.0

    def test_update_multiple_fields(self):
        """Test update with multiple fields."""
        tracker = StrategyTracker()
        
        tracker.update(sl=1.0950, tp=1.1100, new=False)
        
        assert tracker.sl == 1.0950
        assert tracker.tp == 1.1100
        assert tracker.new is False

    def test_update_ignores_unknown_fields(self):
        """Test update ignores fields not in dataclass."""
        tracker = StrategyTracker()
        
        # Should not raise, just ignore unknown field
        tracker.update(unknown_field="value", sl=1.0950)
        
        assert tracker.sl == 1.0950
        assert not hasattr(tracker, "unknown_field") or tracker.__dict__.get("unknown_field") is None

    def test_update_trend_to_ranging(self):
        """Test update trend to ranging sets correct flags."""
        tracker = StrategyTracker(trend="bullish", bullish=True)
        
        tracker.update(trend="ranging")
        
        assert tracker.trend == "ranging"
        assert tracker.ranging is True
        assert tracker.bullish is False
        assert tracker.bearish is False

    def test_update_trend_to_bullish(self):
        """Test update trend to bullish sets correct flags."""
        tracker = StrategyTracker()
        
        tracker.update(trend="bullish")
        
        assert tracker.trend == "bullish"
        assert tracker.bullish is True
        assert tracker.ranging is False
        assert tracker.bearish is False

    def test_update_trend_to_bearish(self):
        """Test update trend to bearish sets correct flags."""
        tracker = StrategyTracker()
        
        tracker.update(trend="bearish")
        
        assert tracker.trend == "bearish"
        assert tracker.bearish is True
        assert tracker.bullish is False
        assert tracker.ranging is False

    def test_update_order_type(self):
        """Test update order_type."""
        tracker = StrategyTracker()
        
        tracker.update(order_type=OrderType.SELL)
        
        assert tracker.order_type == OrderType.SELL

    def test_update_trend_and_other_fields(self):
        """Test update trend along with other fields."""
        tracker = StrategyTracker()
        
        tracker.update(trend="bearish", sl=1.1050, tp=1.0900)
        
        assert tracker.trend == "bearish"
        assert tracker.bearish is True
        assert tracker.sl == 1.1050
        assert tracker.tp == 1.0900

    def test_update_price_fields(self):
        """Test update price tracking fields."""
        tracker = StrategyTracker()
        
        tracker.update(
            last_trend_price=1.1000,
            last_entry_price=1.1005,
            trend_time=1609459200.0,
            entry_time=1609459201.0
        )
        
        assert tracker.last_trend_price == 1.1000
        assert tracker.last_entry_price == 1.1005
        assert tracker.trend_time == 1609459200.0
        assert tracker.entry_time == 1609459201.0


class TestStrategyTrackerTrendTransitions:
    """Tests for trend state transitions."""

    def test_ranging_to_bullish_to_bearish(self):
        """Test full trend transition cycle."""
        tracker = StrategyTracker()
        
        # Start ranging
        assert tracker.ranging is True
        assert tracker.bullish is False
        assert tracker.bearish is False
        
        # To bullish
        tracker.update(trend="bullish")
        assert tracker.ranging is False
        assert tracker.bullish is True
        assert tracker.bearish is False
        
        # To bearish
        tracker.update(trend="bearish")
        assert tracker.ranging is False
        assert tracker.bullish is False
        assert tracker.bearish is True
        
        # Back to ranging
        tracker.update(trend="ranging")
        assert tracker.ranging is True
        assert tracker.bullish is False
        assert tracker.bearish is False

    def test_bearish_to_bullish_direct(self):
        """Test direct transition from bearish to bullish."""
        tracker = StrategyTracker(trend="bearish", bearish=True, ranging=False)
        
        tracker.update(trend="bullish")
        
        assert tracker.bullish is True
        assert tracker.bearish is False
        assert tracker.ranging is False
