"""Comprehensive tests for the core utils module.

Tests cover:
- sleep async function
- sleep_sync function
- auto_commit function
"""

import time
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


from aiomql.core.utils import sleep, sleep_sync, auto_commit


class TestSleepAsync:
    """Tests for async sleep function."""

    @pytest.mark.asyncio
    async def test_sleep_calls_asyncio_sleep(self):
        """Test sleep delegates to asyncio.sleep."""
        with patch("aiomql.core.utils.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await sleep(1.5)
            mock_sleep.assert_called_once_with(1.5)

    @pytest.mark.asyncio
    async def test_sleep_with_zero_seconds(self):
        """Test sleep with zero seconds."""
        with patch("aiomql.core.utils.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await sleep(0)
            mock_sleep.assert_called_once_with(0)

    @pytest.mark.asyncio
    async def test_sleep_with_integer_seconds(self):
        """Test sleep with integer seconds."""
        with patch("aiomql.core.utils.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await sleep(5)
            mock_sleep.assert_called_once_with(5)

    @pytest.mark.asyncio
    async def test_sleep_with_float_seconds(self):
        """Test sleep with float seconds."""
        with patch("aiomql.core.utils.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await sleep(0.5)
            mock_sleep.assert_called_once_with(0.5)

    @pytest.mark.asyncio
    async def test_sleep_actually_delays_execution(self):
        """Test sleep actually delays execution."""
        start_time = time.time()
        await sleep(0.1)
        elapsed = time.time() - start_time
        assert elapsed >= 0.1


class TestSleepSync:
    """Tests for sync sleep function."""

    def test_sleep_sync_calls_time_sleep(self):
        """Test sleep_sync delegates to time.sleep."""
        with patch("aiomql.core.utils.time.sleep") as mock_sleep:
            sleep_sync(1.5)
            mock_sleep.assert_called_once_with(1.5)

    def test_sleep_sync_with_zero_seconds(self):
        """Test sleep_sync with zero seconds."""
        with patch("aiomql.core.utils.time.sleep") as mock_sleep:
            sleep_sync(0)
            mock_sleep.assert_called_once_with(0)

    def test_sleep_sync_with_integer_seconds(self):
        """Test sleep_sync with integer seconds."""
        with patch("aiomql.core.utils.time.sleep") as mock_sleep:
            sleep_sync(5)
            mock_sleep.assert_called_once_with(5)

    def test_sleep_sync_with_float_seconds(self):
        """Test sleep_sync with float seconds."""
        with patch("aiomql.core.utils.time.sleep") as mock_sleep:
            sleep_sync(0.5)
            mock_sleep.assert_called_once_with(0.5)

    def test_sleep_sync_actually_delays_execution(self):
        """Test sleep_sync actually delays execution."""
        start_time = time.time()
        sleep_sync(0.1)
        elapsed = time.time() - start_time
        assert elapsed >= 0.1


class TestAutoCommit:
    """Tests for auto_commit function."""

    @pytest.mark.asyncio
    async def test_auto_commit_stops_on_shutdown(self):
        """Test auto_commit stops when shutdown is True immediately."""
        mock_config = MagicMock()
        mock_config.shutdown = True  # Start with shutdown True
        mock_config.db_commit_interval = 0.1
        mock_conn = MagicMock()
        mock_state = MagicMock()
        mock_state.conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_state.conn.__exit__ = MagicMock(return_value=False)
        mock_state.acommit = AsyncMock()
        mock_config.state = mock_state

        with patch("aiomql.core.utils.Config", return_value=mock_config):
            with patch("aiomql.core.utils.sleep", new_callable=AsyncMock):
                await auto_commit()

        # Should not have called acommit since shutdown was True immediately
        mock_state.acommit.assert_not_called()

    @pytest.mark.asyncio
    async def test_auto_commit_uses_config_interval(self):
        """Test auto_commit uses db_commit_interval from config."""
        call_count = 0

        async def mock_sleep(secs):
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                mock_config.shutdown = True

        mock_config = MagicMock()
        mock_config.shutdown = False
        mock_config.db_commit_interval = 5.0
        mock_conn = MagicMock()
        mock_state = MagicMock()
        mock_state.conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_state.conn.__exit__ = MagicMock(return_value=False)
        mock_state.acommit = AsyncMock()
        mock_config.state = mock_state

        with patch("aiomql.core.utils.Config", return_value=mock_config):
            with patch("aiomql.core.utils.sleep", side_effect=mock_sleep) as patched_sleep:
                await auto_commit()

        # Verify sleep was called with the config interval
        patched_sleep.assert_called_with(5.0)

    @pytest.mark.asyncio
    async def test_auto_commit_calls_acommit(self):
        """Test auto_commit calls state.acommit with correct args."""
        call_count = 0

        async def mock_sleep(secs):
            nonlocal call_count
            call_count += 1
            if call_count >= 1:
                mock_config.shutdown = True

        mock_config = MagicMock()
        mock_config.shutdown = False
        mock_config.db_commit_interval = 0.1
        mock_conn = MagicMock()
        mock_state = MagicMock()
        mock_state.conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_state.conn.__exit__ = MagicMock(return_value=False)
        mock_state.acommit = AsyncMock()
        mock_config.state = mock_state

        with patch("aiomql.core.utils.Config", return_value=mock_config):
            with patch("aiomql.core.utils.sleep", side_effect=mock_sleep):
                await auto_commit()

        # Verify acommit was called with connection and close=False
        mock_state.acommit.assert_called_with(conn=mock_conn, close=False)

    @pytest.mark.asyncio
    async def test_auto_commit_loops_multiple_times(self):
        """Test auto_commit performs multiple commit cycles before shutdown."""
        call_count = 0

        async def mock_sleep(secs):
            nonlocal call_count
            call_count += 1
            if call_count >= 3:
                mock_config.shutdown = True

        mock_config = MagicMock()
        mock_config.shutdown = False
        mock_config.db_commit_interval = 0.1
        mock_conn = MagicMock()
        mock_state = MagicMock()
        mock_state.conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_state.conn.__exit__ = MagicMock(return_value=False)
        mock_state.acommit = AsyncMock()
        mock_config.state = mock_state

        with patch("aiomql.core.utils.Config", return_value=mock_config):
            with patch("aiomql.core.utils.sleep", side_effect=mock_sleep):
                await auto_commit()

        # acommit should be called 3 times (once per loop iteration)
        assert mock_state.acommit.call_count == 3

    @pytest.mark.asyncio
    async def test_auto_commit_handles_exception(self):
        """Test auto_commit handles exceptions gracefully."""
        mock_config = MagicMock()
        mock_config.shutdown = False
        mock_state = MagicMock()
        mock_state.conn.__enter__ = MagicMock(side_effect=Exception("Test error"))
        mock_state.conn.__exit__ = MagicMock(return_value=False)
        mock_config.state = mock_state

        with patch("aiomql.core.utils.Config", return_value=mock_config):
            with patch("aiomql.core.utils.logger") as mock_logger:
                # Should not raise, just log the error
                await auto_commit()
                mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_auto_commit_handles_acommit_exception(self):
        """Test auto_commit handles exception during acommit."""
        mock_config = MagicMock()
        mock_config.shutdown = False
        mock_config.db_commit_interval = 0.1
        mock_conn = MagicMock()
        mock_state = MagicMock()
        mock_state.conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_state.conn.__exit__ = MagicMock(return_value=False)
        mock_state.acommit = AsyncMock(side_effect=Exception("Commit failed"))
        mock_config.state = mock_state

        with patch("aiomql.core.utils.Config", return_value=mock_config):
            with patch("aiomql.core.utils.sleep", new_callable=AsyncMock):
                with patch("aiomql.core.utils.logger") as mock_logger:
                    await auto_commit()
                    mock_logger.error.assert_called_once()
