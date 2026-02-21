"""Comprehensive tests for the price_utils module.

Tests cover all 8 pure utility functions:
- get_price_diff_pct
- get_price_in_range_pct
- get_price_at_pct
- extend_range_by_pct
- get_price_change_pct
- increase_value_by_pct
- decrease_value_by_pct
"""

import pytest

from aiomql.utils.price_utils import (
    get_price_diff_pct,
    get_price_in_range_pct,
    get_price_at_pct,
    extend_range_by_pct,
    get_price_change_pct,
    increase_value_by_pct,
    decrease_value_by_pct,
)


class TestGetPriceDiffPct:
    """Tests for get_price_diff_pct function."""

    def test_equal_values(self):
        """Test zero difference when values are equal."""
        assert get_price_diff_pct(50, 50) == 0.0

    def test_small_difference(self):
        """Test small percentage difference."""
        result = get_price_diff_pct(100, 110)
        assert pytest.approx(result, rel=1e-6) == 9.523809523809524

    def test_large_difference(self):
        """Test large percentage difference."""
        result = get_price_diff_pct(200, 100)
        assert pytest.approx(result, rel=1e-6) == 66.66666666666666

    def test_order_does_not_matter(self):
        """Test that argument order gives same result (symmetric)."""
        assert get_price_diff_pct(100, 110) == get_price_diff_pct(110, 100)

    def test_with_decimals(self):
        """Test with decimal values (common in forex pricing)."""
        result = get_price_diff_pct(1.1000, 1.1050)
        assert result > 0

    def test_very_close_values(self):
        """Test with very close values."""
        result = get_price_diff_pct(1.10000, 1.10001)
        assert result > 0
        assert result < 0.01  # Very small percentage


class TestGetPriceInRangePct:
    """Tests for get_price_in_range_pct function."""

    def test_midpoint(self):
        """Test value at midpoint returns 50%."""
        assert get_price_in_range_pct(0, 100, 50) == 50.0

    def test_start_value(self):
        """Test value at start returns 0%."""
        assert get_price_in_range_pct(0, 100, 0) == 0.0

    def test_end_value(self):
        """Test value at end returns 100%."""
        assert get_price_in_range_pct(0, 100, 100) == 100.0

    def test_quarter(self):
        """Test value at 25%."""
        assert get_price_in_range_pct(0, 100, 25) == 25.0

    def test_offset_range(self):
        """Test with non-zero start."""
        assert get_price_in_range_pct(10, 20, 15) == 50.0

    def test_beyond_range(self):
        """Test value beyond the range returns > 100%."""
        result = get_price_in_range_pct(0, 100, 150)
        assert result == 150.0

    def test_below_range(self):
        """Test value below the range returns negative."""
        result = get_price_in_range_pct(10, 20, 5)
        assert result == -50.0

    def test_forex_prices(self):
        """Test with realistic forex price ranges."""
        # Price at 80% of move from 1.1000 to 1.1100
        result = get_price_in_range_pct(1.1000, 1.1100, 1.1080)
        assert pytest.approx(result, rel=1e-6) == 80.0


class TestGetPriceAtPct:
    """Tests for get_price_at_pct function."""

    def test_zero_percent(self):
        """Test 0% returns start value."""
        assert get_price_at_pct(0, 100, 0) == 0.0

    def test_hundred_percent(self):
        """Test 100% returns end value."""
        assert get_price_at_pct(0, 100, 100) == 100.0

    def test_fifty_percent(self):
        """Test 50% returns midpoint."""
        assert get_price_at_pct(0, 100, 50) == 50.0

    def test_offset_range(self):
        """Test with non-zero start."""
        assert get_price_at_pct(10, 20, 50) == 15.0

    def test_twenty_five_percent(self):
        """Test 25%."""
        assert get_price_at_pct(0, 200, 25) == 50.0

    def test_over_hundred_percent(self):
        """Test beyond 100% extends past end."""
        result = get_price_at_pct(0, 100, 150)
        assert result == 150.0

    def test_inverse_of_get_price_in_range_pct(self):
        """Test that get_price_at_pct is the inverse of get_price_in_range_pct."""
        start, end = 1.1000, 1.1100
        pct = 75.0
        value = get_price_at_pct(start, end, pct)
        recovered_pct = get_price_in_range_pct(start, end, value)
        assert pytest.approx(recovered_pct, rel=1e-6) == pct


class TestExtendRangeByPct:
    """Tests for extend_range_by_pct function."""

    def test_extend_by_fifty_percent(self):
        """Test extending range by 50%."""
        assert extend_range_by_pct(0, 100, 50) == 150.0

    def test_extend_by_hundred_percent(self):
        """Test extending range by 100% (doubles the span beyond end)."""
        assert extend_range_by_pct(10, 20, 100) == 30.0

    def test_extend_by_twenty_percent(self):
        """Test extending range by 20%."""
        assert extend_range_by_pct(0, 50, 20) == 60.0

    def test_extend_by_zero(self):
        """Test extending by 0% returns original end."""
        assert extend_range_by_pct(0, 100, 0) == 100.0

    def test_forex_take_profit_extension(self):
        """Test realistic forex TP extension scenario."""
        # Extend TP from 1.1100 (opened at 1.1000) by 20%
        new_tp = extend_range_by_pct(1.1000, 1.1100, 20)
        expected = 1.1100 + (0.0100 * 0.20)  # 1.1120
        assert pytest.approx(new_tp, rel=1e-6) == expected

    def test_small_extension(self):
        """Test small percentage extension."""
        result = extend_range_by_pct(100, 200, 10)
        assert result == 210.0


class TestGetPriceChangePct:
    """Tests for get_price_change_pct function."""

    def test_no_change(self):
        """Test zero change."""
        assert get_price_change_pct(50, 50) == 0.0

    def test_increase(self):
        """Test positive price change."""
        assert get_price_change_pct(100, 150) == 50.0

    def test_decrease(self):
        """Test negative price change."""
        assert get_price_change_pct(200, 100) == -50.0

    def test_double(self):
        """Test 100% increase (doubling)."""
        assert get_price_change_pct(100, 200) == 100.0

    def test_small_change(self):
        """Test small forex-like price change."""
        result = get_price_change_pct(1.1000, 1.1010)
        assert pytest.approx(result, abs=0.01) == pytest.approx(0.0909, abs=0.01)

    def test_negative_values(self):
        """Test with signed values (e.g. profit going more negative)."""
        result = get_price_change_pct(-100, -50)
        assert result == -50.0


class TestIncreaseValueByPct:
    """Tests for increase_value_by_pct function."""

    def test_increase_by_ten_percent(self):
        """Test 10% increase."""
        assert round(increase_value_by_pct(100, 10), 2) == 110.0

    def test_increase_by_twenty_percent(self):
        """Test 20% increase."""
        assert increase_value_by_pct(50, 20) == 60.0

    def test_increase_by_fifty_percent(self):
        """Test 50% increase."""
        assert increase_value_by_pct(200, 50) == 300.0

    def test_increase_by_zero(self):
        """Test 0% increase returns original value."""
        assert increase_value_by_pct(100, 0) == 100.0

    def test_increase_by_hundred_percent(self):
        """Test 100% increase doubles the value."""
        assert increase_value_by_pct(100, 100) == 200.0

    def test_increase_with_decimals(self):
        """Test increase with decimal input."""
        result = increase_value_by_pct(1.1000, 5)
        assert pytest.approx(result, rel=1e-6) == 1.155


class TestDecreaseValueByPct:
    """Tests for decrease_value_by_pct function."""

    def test_decrease_by_ten_percent(self):
        """Test 10% decrease."""
        assert decrease_value_by_pct(100, 10) == 90.0

    def test_decrease_by_twenty_percent(self):
        """Test 20% decrease."""
        assert decrease_value_by_pct(50, 20) == 40.0

    def test_decrease_by_fifty_percent(self):
        """Test 50% decrease halves the value."""
        assert decrease_value_by_pct(200, 50) == 100.0

    def test_decrease_by_zero(self):
        """Test 0% decrease returns original value."""
        assert decrease_value_by_pct(100, 0) == 100.0

    def test_decrease_by_hundred_percent(self):
        """Test 100% decrease returns zero."""
        assert decrease_value_by_pct(100, 100) == 0.0

    def test_decrease_with_decimals(self):
        """Test decrease with decimal input."""
        result = decrease_value_by_pct(1.1000, 5)
        assert pytest.approx(result, rel=1e-6) == 1.045


class TestFunctionInteractions:
    """Tests verifying relationships between price utility functions."""

    def test_increase_then_decrease_returns_original(self):
        """Test that increase then decrease by same rate does NOT return original
        (this is expected due to compounding)."""
        original = 100.0
        increased = increase_value_by_pct(original, 10)
        result = decrease_value_by_pct(increased, 10)
        # 100 * 1.1 * 0.9 = 99.0, NOT 100 (compounding effect)
        assert pytest.approx(result, rel=1e-6) == 99.0

    def test_extend_range_consistent_with_range_pct(self):
        """Test that extended range position is beyond 100%."""
        start, end = 0, 100
        extended = extend_range_by_pct(start, end, 50)
        pct = get_price_in_range_pct(start, end, extended)
        assert pct == 150.0

    def test_price_change_consistent_with_increase(self):
        """Test that increase_value_by_pct result matches get_price_change_pct."""
        original = 100.0
        rate = 25.0
        increased = increase_value_by_pct(original, rate)
        change = get_price_change_pct(original, increased)
        assert pytest.approx(change, rel=1e-6) == rate
