"""Comprehensive tests for the percentages module.

Tests cover:
- get_price_diff_pct
- get_price_in_range_pct
- get_price_at_pct
- extend_interval_by_percentage
- get_price_change_pct
- increase_value_by_pct
- decrease_value_by_pct
"""

import pytest

from aiomql.utils.price_utils import (
    get_price_diff_pct,
    get_price_in_range_pct,
    get_price_at_pct,
    extend_interval_by_percentage,
    get_price_change_pct,
    increase_value_by_pct,
    decrease_value_by_pct
)


class TestCalculatePercentageDifference:
    """Tests for get_price_diff_pct function."""

    def test_equal_values(self):
        """Test equal values returns 0."""
        assert get_price_diff_pct(50, 50) == 0.0
        assert get_price_diff_pct(100, 100) == 0.0

    def test_different_values(self):
        """Test different values returns correct percentage."""
        result = get_price_diff_pct(100, 110)
        assert abs(result - 9.523809523809524) < 0.0001

    def test_large_difference(self):
        """Test large difference."""
        result = get_price_diff_pct(200, 100)
        assert abs(result - 66.66666666666666) < 0.0001

    def test_order_independent(self):
        """Test result is same regardless of order."""
        result1 = get_price_diff_pct(100, 200)
        result2 = get_price_diff_pct(200, 100)
        assert result1 == result2

    def test_decimal_values(self):
        """Test with decimal values."""
        result = get_price_diff_pct(1.5, 1.0)
        assert result > 0


class TestCalculatePercentagePosition:
    """Tests for get_price_in_range_pct function."""

    def test_value_at_start(self):
        """Test value at start returns 0%."""
        assert get_price_in_range_pct(0, 100, 0) == 0.0
        assert get_price_in_range_pct(10, 20, 10) == 0.0

    def test_value_at_end(self):
        """Test value at end returns 100%."""
        assert get_price_in_range_pct(0, 100, 100) == 100.0
        assert get_price_in_range_pct(10, 20, 20) == 100.0

    def test_value_in_middle(self):
        """Test value in middle returns 50%."""
        assert get_price_in_range_pct(0, 100, 50) == 50.0
        assert get_price_in_range_pct(10, 20, 15) == 50.0

    def test_quarter_position(self):
        """Test 25% position."""
        assert get_price_in_range_pct(0, 100, 25) == 25.0

    def test_value_beyond_end(self):
        """Test value beyond end returns > 100%."""
        result = get_price_in_range_pct(0, 100, 150)
        assert result == 150.0

    def test_value_before_start(self):
        """Test value before start returns negative."""
        result = get_price_in_range_pct(0, 100, -50)
        assert result == -50.0


class TestCalculateValueAtPercentage:
    """Tests for get_price_at_pct function."""

    def test_zero_percent(self):
        """Test 0% returns start value."""
        assert get_price_at_pct(0, 100, 0) == 0.0
        assert get_price_at_pct(10, 20, 0) == 10.0

    def test_hundred_percent(self):
        """Test 100% returns end value."""
        assert get_price_at_pct(0, 100, 100) == 100.0
        assert get_price_at_pct(10, 20, 100) == 20.0

    def test_fifty_percent(self):
        """Test 50% returns middle value."""
        assert get_price_at_pct(0, 100, 50) == 50.0
        assert get_price_at_pct(10, 20, 50) == 15.0

    def test_quarter_percent(self):
        """Test 25% position."""
        assert get_price_at_pct(0, 200, 25) == 50.0

    def test_beyond_hundred_percent(self):
        """Test > 100% extends beyond end."""
        assert get_price_at_pct(0, 100, 150) == 150.0


class TestExtendIntervalByPercentage:
    """Tests for extend_interval_by_percentage function."""

    def test_fifty_percent_extension(self):
        """Test 50% extension."""
        assert extend_interval_by_percentage(0, 100, 50) == 150.0

    def test_hundred_percent_extension(self):
        """Test 100% extension (doubles interval)."""
        assert extend_interval_by_percentage(10, 20, 100) == 30.0

    def test_twenty_percent_extension(self):
        """Test 20% extension."""
        assert extend_interval_by_percentage(0, 50, 20) == 60.0

    def test_zero_percent_extension(self):
        """Test 0% extension returns original end."""
        assert extend_interval_by_percentage(0, 100, 0) == 100.0

    def test_small_interval(self):
        """Test with small interval."""
        result = extend_interval_by_percentage(1.0, 1.1, 50)
        assert abs(result - 1.15) < 0.0001


class TestCalculatePercentageChange:
    """Tests for get_price_change_pct function."""

    def test_no_change(self):
        """Test no change returns 0%."""
        assert get_price_change_pct(50, 50) == 0.0
        assert get_price_change_pct(100, 100) == 0.0

    def test_positive_change(self):
        """Test positive change (increase)."""
        assert get_price_change_pct(100, 150) == 50.0
        assert get_price_change_pct(100, 200) == 100.0

    def test_negative_change(self):
        """Test negative change (decrease)."""
        assert get_price_change_pct(200, 100) == -50.0
        assert get_price_change_pct(100, 50) == -50.0

    def test_double_value(self):
        """Test doubling returns 100%."""
        assert get_price_change_pct(50, 100) == 100.0

    def test_half_value(self):
        """Test halving returns -50%."""
        assert get_price_change_pct(100, 50) == -50.0


class TestIncreaseByPercentage:
    """Tests for increase_value_by_pct function."""

    def test_ten_percent_increase(self):
        """Test 10% increase."""
        result = increase_value_by_pct(100, 10)
        assert result == 110.0

    def test_twenty_percent_increase(self):
        """Test 20% increase."""
        assert increase_value_by_pct(50, 20) == 60.0

    def test_fifty_percent_increase(self):
        """Test 50% increase."""
        assert increase_value_by_pct(200, 50) == 300.0

    def test_zero_percent_increase(self):
        """Test 0% increase returns original."""
        assert increase_value_by_pct(100, 0) == 100.0

    def test_hundred_percent_increase(self):
        """Test 100% increase doubles value."""
        assert increase_value_by_pct(50, 100) == 100.0

    def test_decimal_value(self):
        """Test with decimal value."""
        result = increase_value_by_pct(1.1000, 10)
        assert abs(result - 1.21) < 0.0001


class TestDecreaseByPercentage:
    """Tests for decrease_value_by_pct function."""

    def test_ten_percent_decrease(self):
        """Test 10% decrease."""
        assert decrease_value_by_pct(100, 10) == 90.0

    def test_twenty_percent_decrease(self):
        """Test 20% decrease."""
        assert decrease_value_by_pct(50, 20) == 40.0

    def test_fifty_percent_decrease(self):
        """Test 50% decrease."""
        assert decrease_value_by_pct(200, 50) == 100.0

    def test_zero_percent_decrease(self):
        """Test 0% decrease returns original."""
        assert decrease_value_by_pct(100, 0) == 100.0

    def test_hundred_percent_decrease(self):
        """Test 100% decrease returns 0."""
        assert decrease_value_by_pct(100, 100) == 0.0

    def test_decimal_value(self):
        """Test with decimal value."""
        result = decrease_value_by_pct(1.1000, 10)
        assert abs(result - 0.99) < 0.0001
