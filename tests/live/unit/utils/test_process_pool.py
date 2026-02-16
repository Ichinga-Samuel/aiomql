"""Comprehensive tests for the process_pool module.

Tests cover:
- process_pool function with various process configurations
"""

import pytest
from unittest.mock import patch, MagicMock, call

from aiomql.utils.process_pool import process_pool


class TestProcessPool:
    """Tests for process_pool function."""

    def test_process_pool_submits_processes(self):
        """Test process_pool submits all processes."""
        mock_func1 = MagicMock()
        mock_func2 = MagicMock()
        
        processes = {
            mock_func1: {"arg1": "value1"},
            mock_func2: {"arg2": "value2"}
        }
        
        with patch("aiomql.utils.process_pool.ProcessPoolExecutor") as mock_executor_cls:
            mock_executor = MagicMock()
            mock_executor.__enter__ = MagicMock(return_value=mock_executor)
            mock_executor.__exit__ = MagicMock(return_value=False)
            mock_executor_cls.return_value = mock_executor
            
            process_pool(processes)
            
            # Verify submit was called for each process
            assert mock_executor.submit.call_count == 2

    def test_process_pool_passes_kwargs(self):
        """Test process_pool passes kwargs to processes."""
        mock_func = MagicMock()
        
        processes = {
            mock_func: {"key1": "val1", "key2": "val2"}
        }
        
        with patch("aiomql.utils.process_pool.ProcessPoolExecutor") as mock_executor_cls:
            mock_executor = MagicMock()
            mock_executor.__enter__ = MagicMock(return_value=mock_executor)
            mock_executor.__exit__ = MagicMock(return_value=False)
            mock_executor_cls.return_value = mock_executor
            
            process_pool(processes)
            
            mock_executor.submit.assert_called_once_with(mock_func, key1="val1", key2="val2")

    def test_process_pool_default_num_workers(self):
        """Test process_pool uses len(processes) + 1 as default workers."""
        mock_func1 = MagicMock()
        mock_func2 = MagicMock()
        
        processes = {
            mock_func1: {},
            mock_func2: {}
        }
        
        with patch("aiomql.utils.process_pool.ProcessPoolExecutor") as mock_executor_cls:
            mock_executor = MagicMock()
            mock_executor.__enter__ = MagicMock(return_value=mock_executor)
            mock_executor.__exit__ = MagicMock(return_value=False)
            mock_executor_cls.return_value = mock_executor
            
            process_pool(processes)
            
            # Default should be len(processes) + 1 = 3
            mock_executor_cls.assert_called_once_with(max_workers=3)

    def test_process_pool_custom_num_workers(self):
        """Test process_pool uses custom num_workers."""
        mock_func = MagicMock()
        
        processes = {
            mock_func: {}
        }
        
        with patch("aiomql.utils.process_pool.ProcessPoolExecutor") as mock_executor_cls:
            mock_executor = MagicMock()
            mock_executor.__enter__ = MagicMock(return_value=mock_executor)
            mock_executor.__exit__ = MagicMock(return_value=False)
            mock_executor_cls.return_value = mock_executor
            
            process_pool(processes, num_workers=10)
            
            mock_executor_cls.assert_called_once_with(max_workers=10)

    def test_process_pool_empty_kwargs(self):
        """Test process_pool with empty kwargs for a process."""
        mock_func = MagicMock()
        
        processes = {
            mock_func: {}
        }
        
        with patch("aiomql.utils.process_pool.ProcessPoolExecutor") as mock_executor_cls:
            mock_executor = MagicMock()
            mock_executor.__enter__ = MagicMock(return_value=mock_executor)
            mock_executor.__exit__ = MagicMock(return_value=False)
            mock_executor_cls.return_value = mock_executor
            
            process_pool(processes)
            
            mock_executor.submit.assert_called_once_with(mock_func)

    def test_process_pool_multiple_processes_with_different_kwargs(self):
        """Test process_pool with multiple processes having different kwargs."""
        mock_func1 = MagicMock()
        mock_func2 = MagicMock()
        mock_func3 = MagicMock()
        
        processes = {
            mock_func1: {"config": "config1"},
            mock_func2: {"symbol": "EURUSD", "volume": 0.1},
            mock_func3: {}
        }
        
        with patch("aiomql.utils.process_pool.ProcessPoolExecutor") as mock_executor_cls:
            mock_executor = MagicMock()
            mock_executor.__enter__ = MagicMock(return_value=mock_executor)
            mock_executor.__exit__ = MagicMock(return_value=False)
            mock_executor_cls.return_value = mock_executor
            
            process_pool(processes)
            
            assert mock_executor.submit.call_count == 3
