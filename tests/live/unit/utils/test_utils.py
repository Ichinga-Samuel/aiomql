"""Comprehensive tests for the utils/utils.py module.

Tests cover:
- dict_to_string function
- backoff_decorator async retry decorator
- error_handler async error decorator
- error_handler_sync sync error decorator
- round_down function
- round_up function
- round_off function
- async_cache decorator
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from aiomql.utils.utils import (
    dict_to_string,
    backoff_decorator,
    error_handler,
    error_handler_sync,
    round_down,
    round_up,
    round_off,
    async_cache
)


class TestDictToString:
    """Tests for dict_to_string function."""

    def test_empty_dict(self):
        """Test with empty dict."""
        result = dict_to_string({})
        assert result == ""

    def test_single_item(self):
        """Test with single item dict."""
        result = dict_to_string({"key": "value"})
        assert result == "key: value"

    def test_multiple_items_single_line(self):
        """Test with multiple items, single line."""
        result = dict_to_string({"a": 1, "b": 2})
        assert "a: 1" in result
        assert "b: 2" in result
        assert ", " in result

    def test_multiple_items_multi_line(self):
        """Test with multiple items, multi line."""
        result = dict_to_string({"a": 1, "b": 2}, multi=True)
        assert "a: 1" in result
        assert "b: 2" in result
        assert "\n" in result

    def test_various_value_types(self):
        """Test with various value types."""
        data = {"str": "text", "int": 42, "float": 3.14, "bool": True}
        result = dict_to_string(data)
        assert "str: text" in result
        assert "int: 42" in result
        assert "float: 3.14" in result
        assert "bool: True" in result


class TestBackoffDecorator:
    """Tests for backoff_decorator."""

    async def test_successful_call_no_retry(self):
        """Test successful call does not retry."""
        call_count = 0
        
        @backoff_decorator
        async def success_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await success_func()
        
        assert result == "success"
        assert call_count == 1

    async def test_retry_on_exception(self):
        """Test retries on exception."""
        call_count = 0
        
        @backoff_decorator(max_retries=3)
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Test error")
            return "success"
        
        with patch("aiomql.utils.utils.Config") as mock_config:
            mock_config.return_value.mode = "backtest"  # Skip sleep
            result = await failing_func()
        
        assert result == "success"
        assert call_count == 3

    async def test_max_retries_exceeded(self):
        """Test raises after max retries exceeded."""
        call_count = 0
        
        @backoff_decorator(max_retries=2)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with patch("aiomql.utils.utils.Config") as mock_config:
            mock_config.return_value.mode = "backtest"
            with pytest.raises(ValueError, match="Always fails"):
                await always_fails()
        
        assert call_count == 3  # Initial + 2 retries

    async def test_backoff_delay_in_live_mode(self):
        """Test backoff delay applied in live mode."""
        call_count = 0
        
        @backoff_decorator(max_retries=1)
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Test error")
            return "success"
        
        with patch("aiomql.utils.utils.Config") as mock_config:
            mock_config.return_value.mode = "live"
            with patch("aiomql.utils.utils.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                result = await failing_func()
                mock_sleep.assert_called_once()

    async def test_decorator_without_parentheses(self):
        """Test decorator can be used without parentheses."""
        @backoff_decorator
        async def simple_func():
            return "result"
        
        result = await simple_func()
        assert result == "result"

    async def test_decorator_with_parentheses(self):
        """Test decorator can be used with parentheses."""
        @backoff_decorator()
        async def simple_func():
            return "result"
        
        result = await simple_func()
        assert result == "result"


class TestErrorHandler:
    """Tests for error_handler async decorator."""

    async def test_successful_call(self):
        """Test successful call returns result."""
        @error_handler
        async def success_func():
            return "success"
        
        result = await success_func()
        assert result == "success"

    async def test_exception_returns_response(self):
        """Test exception returns configured response."""
        @error_handler(response="default")
        async def failing_func():
            raise ValueError("Test error")
        
        with patch("aiomql.utils.utils.logger"):
            result = await failing_func()
        
        assert result == "default"

    async def test_exception_returns_none_by_default(self):
        """Test exception returns None by default."""
        @error_handler
        async def failing_func():
            raise ValueError("Test error")
        
        with patch("aiomql.utils.utils.logger"):
            result = await failing_func()
        
        assert result is None

    async def test_custom_exception_type(self):
        """Test catches only specified exception type."""
        @error_handler(exe=ValueError, response="caught")
        async def failing_func():
            raise ValueError("Test error")
        
        with patch("aiomql.utils.utils.logger"):
            result = await failing_func()
        
        assert result == "caught"

    async def test_unmatched_exception_propagates(self):
        """Test unmatched exception propagates."""
        @error_handler(exe=ValueError, response="caught")
        async def failing_func():
            raise TypeError("Wrong type")
        
        with pytest.raises(TypeError):
            await failing_func()

    async def test_logs_error_message(self):
        """Test logs error message."""
        @error_handler
        async def failing_func():
            raise ValueError("Test error")
        
        with patch("aiomql.utils.utils.logger") as mock_logger:
            await failing_func()
            mock_logger.error.assert_called_once()

    async def test_custom_error_message(self):
        """Test custom error message is logged."""
        @error_handler(msg="Custom error message")
        async def failing_func():
            raise ValueError("Test error")
        
        with patch("aiomql.utils.utils.logger") as mock_logger:
            await failing_func()
            mock_logger.error.assert_called_once_with("Custom error message")

    async def test_log_error_msg_false(self):
        """Test no logging when log_error_msg is False."""
        @error_handler(log_error_msg=False)
        async def failing_func():
            raise ValueError("Test error")
        
        with patch("aiomql.utils.utils.logger") as mock_logger:
            await failing_func()
            mock_logger.error.assert_not_called()


class TestErrorHandlerSync:
    """Tests for error_handler_sync decorator."""

    def test_successful_call(self):
        """Test successful call returns result."""
        @error_handler_sync
        def success_func():
            return "success"
        
        result = success_func()
        assert result == "success"

    def test_exception_returns_response(self):
        """Test exception returns configured response."""
        @error_handler_sync(response="default")
        def failing_func():
            raise ValueError("Test error")
        
        with patch("aiomql.utils.utils.logger"):
            result = failing_func()
        
        assert result == "default"

    def test_exception_returns_none_by_default(self):
        """Test exception returns None by default."""
        @error_handler_sync
        def failing_func():
            raise ValueError("Test error")
        
        with patch("aiomql.utils.utils.logger"):
            result = failing_func()
        
        assert result is None

    def test_custom_exception_type(self):
        """Test catches only specified exception type."""
        @error_handler_sync(exe=ValueError, response="caught")
        def failing_func():
            raise ValueError("Test error")
        
        with patch("aiomql.utils.utils.logger"):
            result = failing_func()
        
        assert result == "caught"

    def test_unmatched_exception_propagates(self):
        """Test unmatched exception propagates."""
        @error_handler_sync(exe=ValueError)
        def failing_func():
            raise TypeError("Wrong type")
        
        with pytest.raises(TypeError):
            failing_func()

    def test_logs_error_message(self):
        """Test logs error message."""
        @error_handler_sync
        def failing_func():
            raise ValueError("Test error")
        
        with patch("aiomql.utils.utils.logger") as mock_logger:
            failing_func()
            mock_logger.error.assert_called_once()

    def test_log_error_msg_false(self):
        """Test no logging when log_error_msg is False."""
        @error_handler_sync(log_error_msg=False)
        def failing_func():
            raise ValueError("Test error")
        
        with patch("aiomql.utils.utils.logger") as mock_logger:
            failing_func()
            mock_logger.error.assert_not_called()


class TestRoundDown:
    """Tests for round_down function."""

    def test_exact_multiple(self):
        """Test exact multiple returns same value."""
        assert round_down(10, 5) == 10
        assert round_down(100, 10) == 100

    def test_round_down_integer(self):
        """Test rounding down integer."""
        assert round_down(17, 5) == 15
        assert round_down(23, 10) == 20

    def test_round_down_float(self):
        """Test rounding down float."""
        assert round_down(17.5, 5) == 15
        assert round_down(23.9, 10) == 20

    def test_round_down_to_zero(self):
        """Test rounding down to zero."""
        assert round_down(3, 5) == 0
        assert round_down(9, 10) == 0


class TestRoundUp:
    """Tests for round_up function."""

    def test_exact_multiple(self):
        """Test exact multiple returns same value."""
        assert round_up(10, 5) == 10
        assert round_up(100, 10) == 100

    def test_round_up_integer(self):
        """Test rounding up integer."""
        assert round_up(17, 5) == 20
        assert round_up(23, 10) == 30

    def test_round_up_float(self):
        """Test rounding up float."""
        assert round_up(17.5, 5) == 20
        assert round_up(23.1, 10) == 30

    def test_round_up_small_value(self):
        """Test rounding up small value."""
        assert round_up(1, 5) == 5
        assert round_up(1, 10) == 10


class TestRoundOff:
    """Tests for round_off function."""

    def test_round_up_default(self):
        """Test rounds up by default."""
        assert round_off(1.003, 0.01) == 1.01
        assert round_off(1.001, 0.01) == 1.01

    def test_round_down(self):
        """Test rounds down when specified."""
        assert round_off(1.009, 0.01, round_down=True) == 1.00
        assert round_off(1.019, 0.01, round_down=True) == 1.01

    def test_exact_step(self):
        """Test exact step returns same value."""
        assert round_off(1.00, 0.01) == 1.00
        assert round_off(1.05, 0.05) == 1.05

    def test_larger_step(self):
        """Test with larger step."""
        assert round_off(1.12, 0.1) == 1.2
        assert round_off(1.12, 0.1, round_down=True) == 1.1

    def test_integer_step(self):
        """Test with integer step."""
        assert round_off(5.5, 1) == 6.0
        assert round_off(5.5, 1, round_down=True) == 5.0


class TestAsyncCache:
    """Tests for async_cache decorator."""

    async def test_caches_result(self):
        """Test result is cached."""
        call_count = 0
        
        @async_cache
        async def cached_func():
            nonlocal call_count
            call_count += 1
            return "result"
        
        result1 = await cached_func()
        result2 = await cached_func()
        
        assert result1 == "result"
        assert result2 == "result"
        assert call_count == 1

    async def test_different_args_different_cache(self):
        """Test different args have different cache entries."""
        call_count = 0
        
        @async_cache
        async def cached_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = await cached_func(1)
        result2 = await cached_func(2)
        result3 = await cached_func(1)  # Should be cached
        
        assert result1 == 2
        assert result2 == 4
        assert result3 == 2
        assert call_count == 2

    async def test_kwargs_in_cache_key(self):
        """Test kwargs are included in cache key."""
        call_count = 0
        
        @async_cache
        async def cached_func(x, y=1):
            nonlocal call_count
            call_count += 1
            return x + y
        
        result1 = await cached_func(1, y=2)
        result2 = await cached_func(1, y=3)
        result3 = await cached_func(1, y=2)  # Should be cached
        
        assert result1 == 3
        assert result2 == 4
        assert result3 == 3
        assert call_count == 2

    async def test_cache_has_lock(self):
        """Test cached function has lock attribute."""
        @async_cache
        async def cached_func():
            return "result"
        
        assert hasattr(cached_func, "lock")
        assert hasattr(cached_func, "cache")

    async def test_cache_is_dict(self):
        """Test cache is a dictionary."""
        @async_cache
        async def cached_func():
            return "result"
        
        assert isinstance(cached_func.cache, dict)
