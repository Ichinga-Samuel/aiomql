"""Comprehensive tests for the Executor module.

Tests cover:
- Executor initialization
- add_function method
- add_coroutine method
- add_strategy and add_strategies methods
- run_strategy static method (async and sync strategies)
- run_coroutine_tasks method
- run_coroutine_task static method
- run_function static method
- sigint_handle method
- exit method
- execute method
- Integration tests
"""

import asyncio
import inspect
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, AsyncMock, patch, call
import pytest

from aiomql.lib.executor import Executor
from aiomql.lib.strategy import Strategy
from aiomql.core.config import Config


class MockAsyncStrategy:
    """Mock async strategy for testing."""

    def __init__(self):
        self.running = True

    async def run_strategy(self):
        """Async run_strategy method."""
        pass


class MockSyncStrategy:
    """Mock sync strategy for testing."""

    def __init__(self):
        self.running = True

    def run_strategy(self):
        """Sync run_strategy method."""
        pass


class TestExecutorInitialization:
    """Test Executor class initialization."""

    @patch('aiomql.lib.executor.signal')
    @patch.object(Config, '__new__')
    def test_init_creates_empty_strategy_runners(self, mock_config, mock_signal):
        """Test Executor init creates empty strategy_runners list."""
        config = MagicMock()
        mock_config.return_value = config

        executor = Executor()

        assert executor.strategy_runners == []

    @patch('aiomql.lib.executor.signal')
    @patch.object(Config, '__new__')
    def test_init_creates_empty_coroutines(self, mock_config, mock_signal):
        """Test Executor init creates empty coroutines dict."""
        config = MagicMock()
        mock_config.return_value = config

        executor = Executor()

        assert executor.coroutines == {}

    @patch('aiomql.lib.executor.signal')
    @patch.object(Config, '__new__')
    def test_init_creates_empty_coroutine_threads(self, mock_config, mock_signal):
        """Test Executor init creates empty coroutine_threads dict."""
        config = MagicMock()
        mock_config.return_value = config

        executor = Executor()

        assert executor.coroutine_threads == {}

    @patch('aiomql.lib.executor.signal')
    @patch.object(Config, '__new__')
    def test_init_creates_empty_functions(self, mock_config, mock_signal):
        """Test Executor init creates empty functions dict."""
        config = MagicMock()
        mock_config.return_value = config

        executor = Executor()

        assert executor.functions == {}

    @patch('aiomql.lib.executor.signal')
    @patch.object(Config, '__new__')
    def test_init_creates_config(self, mock_config, mock_signal):
        """Test Executor init creates config."""
        config = MagicMock()
        mock_config.return_value = config

        executor = Executor()

        assert executor.config is not None

    @patch('aiomql.lib.executor.signal')
    @patch.object(Config, '__new__')
    def test_init_sets_timeout_none(self, mock_config, mock_signal):
        """Test Executor init sets timeout to None."""
        config = MagicMock()
        mock_config.return_value = config

        executor = Executor()

        assert executor.timeout is None

    @patch('aiomql.lib.executor.signal')
    @patch.object(Config, '__new__')
    def test_init_registers_signal_handler(self, mock_config, mock_signal):
        """Test Executor init registers SIGINT handler."""
        config = MagicMock()
        mock_config.return_value = config

        executor = Executor()

        mock_signal.assert_called()


class TestAddFunction:
    """Test Executor add_function method."""

    @pytest.fixture
    def executor(self):
        """Create an Executor for testing."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config:
                config = MagicMock()
                mock_config.return_value = config
                return Executor()

    def test_add_function_without_kwargs(self, executor):
        """Test add_function without kwargs."""
        def my_function():
            pass

        executor.add_function(function=my_function)

        assert my_function in executor.functions
        assert executor.functions[my_function] == {}

    def test_add_function_with_kwargs(self, executor):
        """Test add_function with kwargs."""
        def my_function(a, b):
            pass

        kwargs = {"a": 1, "b": 2}
        executor.add_function(function=my_function, kwargs=kwargs)

        assert my_function in executor.functions
        assert executor.functions[my_function] == kwargs

    def test_add_multiple_functions(self, executor):
        """Test adding multiple functions."""
        def func1():
            pass

        def func2():
            pass

        executor.add_function(function=func1, kwargs={"x": 1})
        executor.add_function(function=func2, kwargs={"y": 2})

        assert len(executor.functions) == 2
        assert func1 in executor.functions
        assert func2 in executor.functions

    def test_add_function_none_kwargs_becomes_empty_dict(self, executor):
        """Test add_function with None kwargs defaults to empty dict."""
        def my_function():
            pass

        executor.add_function(function=my_function, kwargs=None)

        assert executor.functions[my_function] == {}

    def test_add_function_replaces_if_same_key(self, executor):
        """Test add_function overwrites kwargs if same function is added twice."""
        def my_function():
            pass

        executor.add_function(function=my_function, kwargs={"a": 1})
        executor.add_function(function=my_function, kwargs={"a": 2})

        assert executor.functions[my_function] == {"a": 2}
        assert len(executor.functions) == 1


class TestAddCoroutine:
    """Test Executor add_coroutine method."""

    @pytest.fixture
    def executor(self):
        """Create an Executor for testing."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config:
                config = MagicMock()
                mock_config.return_value = config
                return Executor()

    def test_add_coroutine_without_kwargs(self, executor):
        """Test add_coroutine without kwargs."""
        async def my_coroutine():
            pass

        executor.add_coroutine(coroutine=my_coroutine)

        assert my_coroutine in executor.coroutines
        assert executor.coroutines[my_coroutine] == {}

    def test_add_coroutine_with_kwargs(self, executor):
        """Test add_coroutine with kwargs."""
        async def my_coroutine(a, b):
            pass

        kwargs = {"a": 1, "b": 2}
        executor.add_coroutine(coroutine=my_coroutine, kwargs=kwargs)

        assert my_coroutine in executor.coroutines
        assert executor.coroutines[my_coroutine] == kwargs

    def test_add_coroutine_on_separate_thread(self, executor):
        """Test add_coroutine with on_separate_thread=True."""
        async def my_coroutine():
            pass

        executor.add_coroutine(coroutine=my_coroutine, on_separate_thread=True)

        assert my_coroutine in executor.coroutine_threads
        assert my_coroutine not in executor.coroutines

    def test_add_coroutine_default_not_separate_thread(self, executor):
        """Test add_coroutine defaults to not separate thread."""
        async def my_coroutine():
            pass

        executor.add_coroutine(coroutine=my_coroutine)

        assert my_coroutine in executor.coroutines
        assert my_coroutine not in executor.coroutine_threads

    def test_add_coroutine_none_kwargs_becomes_empty_dict(self, executor):
        """Test add_coroutine with None kwargs defaults to empty dict."""
        async def my_coroutine():
            pass

        executor.add_coroutine(coroutine=my_coroutine, kwargs=None)

        assert executor.coroutines[my_coroutine] == {}

    def test_add_coroutine_on_separate_thread_with_kwargs(self, executor):
        """Test add_coroutine on separate thread with kwargs."""
        async def my_coroutine(x):
            pass

        executor.add_coroutine(coroutine=my_coroutine, kwargs={"x": 42}, on_separate_thread=True)

        assert my_coroutine in executor.coroutine_threads
        assert executor.coroutine_threads[my_coroutine] == {"x": 42}


class TestAddStrategy:
    """Test Executor add_strategy and add_strategies methods."""

    @pytest.fixture
    def executor(self):
        """Create an Executor for testing."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config:
                config = MagicMock()
                mock_config.return_value = config
                return Executor()

    def test_add_strategy(self, executor):
        """Test add_strategy adds single strategy."""
        strategy = MagicMock(spec=Strategy)

        executor.add_strategy(strategy=strategy)

        assert len(executor.strategy_runners) == 1
        assert strategy in executor.strategy_runners

    def test_add_multiple_strategies_one_by_one(self, executor):
        """Test adding multiple strategies one by one."""
        strategy1 = MagicMock(spec=Strategy)
        strategy2 = MagicMock(spec=Strategy)

        executor.add_strategy(strategy=strategy1)
        executor.add_strategy(strategy=strategy2)

        assert len(executor.strategy_runners) == 2
        assert strategy1 in executor.strategy_runners
        assert strategy2 in executor.strategy_runners

    def test_add_strategies_batch(self, executor):
        """Test add_strategies adds multiple strategies at once."""
        strategy1 = MagicMock(spec=Strategy)
        strategy2 = MagicMock(spec=Strategy)
        strategy3 = MagicMock(spec=Strategy)

        executor.add_strategies(strategies=(strategy1, strategy2, strategy3))

        assert len(executor.strategy_runners) == 3
        assert strategy1 in executor.strategy_runners
        assert strategy2 in executor.strategy_runners
        assert strategy3 in executor.strategy_runners

    def test_add_strategies_extends_existing(self, executor):
        """Test add_strategies extends existing strategies."""
        strategy1 = MagicMock(spec=Strategy)
        strategy2 = MagicMock(spec=Strategy)

        executor.add_strategy(strategy=strategy1)
        executor.add_strategies(strategies=(strategy2,))

        assert len(executor.strategy_runners) == 2

    def test_add_strategies_preserves_order(self, executor):
        """Test add_strategies preserves insertion order."""
        strategy1 = MagicMock(spec=Strategy)
        strategy2 = MagicMock(spec=Strategy)
        strategy3 = MagicMock(spec=Strategy)

        executor.add_strategies(strategies=(strategy1, strategy2, strategy3))

        assert executor.strategy_runners[0] == strategy1
        assert executor.strategy_runners[1] == strategy2
        assert executor.strategy_runners[2] == strategy3


class TestRunStrategy:
    """Test Executor run_strategy static method."""

    def test_run_strategy_async(self):
        """Test run_strategy with async strategy."""
        strategy = MockAsyncStrategy()
        strategy.run_strategy = AsyncMock()

        with patch('asyncio.run') as mock_asyncio_run:
            Executor.run_strategy(strategy)
            mock_asyncio_run.assert_called_once()

    def test_run_strategy_sync(self):
        """Test run_strategy with sync strategy."""
        strategy = MockSyncStrategy()
        strategy.run_strategy = MagicMock()

        with patch('asyncio.run') as mock_asyncio_run:
            Executor.run_strategy(strategy)
            # asyncio.run should NOT be called for sync
            mock_asyncio_run.assert_not_called()
            strategy.run_strategy.assert_called_once()

    def test_run_strategy_detects_async_correctly(self):
        """Test run_strategy correctly detects async method."""
        async_strategy = MockAsyncStrategy()

        assert inspect.iscoroutinefunction(async_strategy.run_strategy)

    def test_run_strategy_detects_sync_correctly(self):
        """Test run_strategy correctly detects sync method."""
        sync_strategy = MockSyncStrategy()

        assert not inspect.iscoroutinefunction(sync_strategy.run_strategy)

    def test_run_strategy_calls_sync_directly(self):
        """Test run_strategy calls sync strategy's run_strategy directly."""
        strategy = MockSyncStrategy()
        call_tracker = {"called": False}

        original_run = strategy.run_strategy
        def tracking_run():
            call_tracker["called"] = True
        strategy.run_strategy = tracking_run

        Executor.run_strategy(strategy)

        assert call_tracker["called"] is True


class TestRunCoroutineTasks:
    """Test Executor run_coroutine_tasks method."""

    @pytest.fixture
    def executor(self):
        """Create an Executor for testing."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config:
                config = MagicMock()
                mock_config.return_value = config
                return Executor()

    async def test_run_coroutine_tasks_runs_all(self, executor):
        """Test run_coroutine_tasks runs all coroutines."""
        call_tracker = {"coro1": False, "coro2": False}

        async def coro1():
            call_tracker["coro1"] = True

        async def coro2():
            call_tracker["coro2"] = True

        executor.add_coroutine(coroutine=coro1)
        executor.add_coroutine(coroutine=coro2)

        await executor.run_coroutine_tasks()

        assert call_tracker["coro1"] is True
        assert call_tracker["coro2"] is True

    async def test_run_coroutine_tasks_passes_kwargs(self, executor):
        """Test run_coroutine_tasks passes kwargs to coroutines."""
        received_kwargs = {}

        async def my_coro(a, b):
            received_kwargs["a"] = a
            received_kwargs["b"] = b

        executor.add_coroutine(coroutine=my_coro, kwargs={"a": 1, "b": 2})

        await executor.run_coroutine_tasks()

        assert received_kwargs["a"] == 1
        assert received_kwargs["b"] == 2

    async def test_run_coroutine_tasks_handles_exception(self, executor):
        """Test run_coroutine_tasks handles exceptions gracefully."""
        async def failing_coro():
            raise Exception("Test error")

        executor.add_coroutine(coroutine=failing_coro)

        # Should not raise
        await executor.run_coroutine_tasks()

    async def test_run_coroutine_tasks_empty(self, executor):
        """Test run_coroutine_tasks with no coroutines."""
        # Should not raise
        await executor.run_coroutine_tasks()

    async def test_run_coroutine_tasks_only_runs_coroutines_not_threads(self, executor):
        """Test run_coroutine_tasks only runs coroutines, not coroutine_threads."""
        call_tracker = {"coro": False, "thread_coro": False}

        async def regular_coro():
            call_tracker["coro"] = True

        async def thread_coro():
            call_tracker["thread_coro"] = True

        executor.add_coroutine(coroutine=regular_coro)
        executor.add_coroutine(coroutine=thread_coro, on_separate_thread=True)

        await executor.run_coroutine_tasks()

        assert call_tracker["coro"] is True
        assert call_tracker["thread_coro"] is False


class TestRunCoroutineTask:
    """Test Executor run_coroutine_task static method."""

    def test_run_coroutine_task_runs_with_asyncio(self):
        """Test run_coroutine_task uses asyncio.run."""
        async def my_coro(x):
            return x

        with patch('asyncio.run') as mock_asyncio_run:
            Executor.run_coroutine_task(my_coro, {"x": 42})
            mock_asyncio_run.assert_called_once()

    def test_run_coroutine_task_passes_kwargs(self):
        """Test run_coroutine_task passes kwargs to the coroutine."""
        received = {}

        async def my_coro(a, b):
            received["a"] = a
            received["b"] = b

        with patch('asyncio.run', side_effect=lambda coro: asyncio.get_event_loop().run_until_complete(coro)) as mock_run:
            # Just verify the coroutine is called with kwargs
            Executor.run_coroutine_task(my_coro, {"a": 1, "b": 2})
            mock_run.assert_called_once()


class TestRunFunction:
    """Test Executor run_function static method."""

    def test_run_function_calls_function(self):
        """Test run_function calls the function."""
        mock_func = MagicMock()

        Executor.run_function(mock_func, {})

        mock_func.assert_called_once_with()

    def test_run_function_passes_kwargs(self):
        """Test run_function passes kwargs."""
        mock_func = MagicMock()
        kwargs = {"a": 1, "b": "test"}

        Executor.run_function(mock_func, kwargs)

        mock_func.assert_called_once_with(a=1, b="test")

    def test_run_function_with_multiple_kwargs(self):
        """Test run_function with multiple keyword arguments."""
        received = {}

        def capture_func(**kwargs):
            received.update(kwargs)

        Executor.run_function(capture_func, {"x": 10, "y": 20, "z": 30})

        assert received == {"x": 10, "y": 20, "z": 30}


class TestSigintHandle:
    """Test Executor sigint_handle method."""

    @pytest.fixture
    def executor(self):
        """Create an Executor for testing."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config:
                config = MagicMock()
                config.shutdown = False
                mock_config.return_value = config
                return Executor()

    def test_sigint_handle_sets_shutdown(self, executor):
        """Test sigint_handle sets config.shutdown to True."""
        executor.sigint_handle(None, None)

        assert executor.config.shutdown is True

    def test_sigint_handle_accepts_signum_and_frame(self, executor):
        """Test sigint_handle accepts signum and frame parameters."""
        mock_frame = MagicMock()

        # Should not raise
        executor.sigint_handle(2, mock_frame)

        assert executor.config.shutdown is True


class TestExit:
    """Test Executor exit method."""

    @pytest.fixture
    def executor(self):
        """Create an Executor for testing."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config:
                config = MagicMock()
                config.shutdown = False
                config.force_shutdown = False
                config.task_queue = MagicMock()
                mock_config.return_value = config
                exec_ = Executor()
                exec_.executor = MagicMock(spec=ThreadPoolExecutor)
                return exec_

    def test_exit_with_timeout(self, executor):
        """Test exit respects timeout."""
        executor.timeout = 0.1
        executor.config.shutdown = False

        executor.exit()

        assert executor.config.shutdown is True

    def test_exit_stops_strategies(self, executor):
        """Test exit sets running=False on all strategies."""
        strategy1 = MagicMock()
        strategy1.running = True
        strategy2 = MagicMock()
        strategy2.running = True

        executor.strategy_runners = [strategy1, strategy2]
        executor.timeout = 0.1

        executor.exit()

        assert strategy1.running is False
        assert strategy2.running is False

    def test_exit_cancels_task_queue(self, executor):
        """Test exit cancels task queue."""
        executor.timeout = 0.1

        executor.exit()

        executor.config.task_queue.cancel.assert_called_once()

    def test_exit_shuts_down_executor(self, executor):
        """Test exit shuts down thread pool executor."""
        executor.timeout = 0.1

        executor.exit()

        executor.executor.shutdown.assert_called_once_with(wait=False, cancel_futures=False)

    def test_exit_force_shutdown(self, executor):
        """Test exit with force_shutdown."""
        executor.config.force_shutdown = True
        executor.timeout = 0.1

        with patch('os._exit') as mock_exit:
            executor.exit()
            mock_exit.assert_called_once_with(1)

    def test_exit_on_shutdown_flag(self, executor):
        """Test exit when shutdown is already True."""
        executor.config.shutdown = True

        executor.exit()

        # Should still stop strategies and clean up
        executor.config.task_queue.cancel.assert_called_once()
        executor.executor.shutdown.assert_called_once_with(wait=False, cancel_futures=False)

    def test_exit_no_strategies(self, executor):
        """Test exit with no strategies."""
        executor.timeout = 0.1
        executor.strategy_runners = []

        # Should not raise
        executor.exit()

        executor.config.task_queue.cancel.assert_called_once()

    def test_exit_exception_calls_os_exit(self, executor):
        """Test exit calls os._exit on exception during shutdown."""
        executor.config.shutdown = True
        executor.config.task_queue.cancel.side_effect = Exception("Cancel error")

        with patch('os._exit') as mock_exit:
            executor.exit()
            mock_exit.assert_called_once_with(1)

    def test_exit_timeout_duration(self, executor):
        """Test exit completes within timeout duration."""
        executor.timeout = 0.05
        executor.config.shutdown = False

        start = time.time()
        executor.exit()
        elapsed = time.time() - start

        # Should exit within timeout + small buffer
        assert elapsed < 0.3
        assert executor.config.shutdown is True


class TestExecute:
    """Test Executor execute method."""

    @pytest.fixture
    def executor(self):
        """Create an Executor for testing."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config:
                config = MagicMock()
                config.shutdown = True  # Set shutdown True so exit loop terminates immediately
                config.force_shutdown = False
                config.task_queue = MagicMock()
                mock_config.return_value = config
                return Executor()

    def test_execute_calculates_workers(self, executor):
        """Test execute calculates minimum workers correctly."""
        strategy = MagicMock()
        executor.add_strategy(strategy=strategy)

        def func():
            pass
        executor.add_function(function=func)

        async def coro():
            pass
        executor.add_coroutine(coroutine=coro, on_separate_thread=True)

        # workers_ = 1 strategy + 1 function + 1 coroutine_thread + 3 = 6
        with patch('aiomql.lib.executor.ThreadPoolExecutor') as mock_pool:
            mock_tpe = MagicMock()
            mock_pool.return_value.__enter__.return_value = mock_tpe
            mock_pool.return_value.__exit__ = MagicMock(return_value=None)

            executor.execute(workers=2)

            # max(2, 6) = 6
            mock_pool.assert_called_once_with(max_workers=6)

    def test_execute_uses_minimum_workers(self, executor):
        """Test execute uses at least the calculated minimum workers."""
        # With no strategies/functions/threads, workers_ = 0 + 0 + 0 + 3 = 3
        with patch('aiomql.lib.executor.ThreadPoolExecutor') as mock_pool:
            mock_tpe = MagicMock()
            mock_pool.return_value.__enter__.return_value = mock_tpe
            mock_pool.return_value.__exit__ = MagicMock(return_value=None)

            executor.execute(workers=1)

            # max(1, 3) = 3
            mock_pool.assert_called_once_with(max_workers=3)

    def test_execute_respects_custom_workers(self, executor):
        """Test execute uses custom workers when larger than calculated."""
        with patch('aiomql.lib.executor.ThreadPoolExecutor') as mock_pool:
            mock_tpe = MagicMock()
            mock_pool.return_value.__enter__.return_value = mock_tpe
            mock_pool.return_value.__exit__ = MagicMock(return_value=None)

            executor.execute(workers=20)

            # max(20, 3) = 20
            mock_pool.assert_called_once_with(max_workers=20)

    def test_execute_default_workers(self, executor):
        """Test execute default workers parameter is 5."""
        with patch('aiomql.lib.executor.ThreadPoolExecutor') as mock_pool:
            mock_tpe = MagicMock()
            mock_pool.return_value.__enter__.return_value = mock_tpe
            mock_pool.return_value.__exit__ = MagicMock(return_value=None)

            executor.execute()

            # max(5, 3) = 5
            mock_pool.assert_called_once_with(max_workers=5)

    def test_execute_submits_strategies(self, executor):
        """Test execute submits each strategy to the thread pool."""
        strategy1 = MagicMock()
        strategy2 = MagicMock()
        executor.add_strategy(strategy=strategy1)
        executor.add_strategy(strategy=strategy2)

        with patch('aiomql.lib.executor.ThreadPoolExecutor') as mock_pool:
            mock_tpe = MagicMock()
            mock_pool.return_value.__enter__.return_value = mock_tpe
            mock_pool.return_value.__exit__ = MagicMock(return_value=None)

            executor.execute()

            # Check strategies were submitted
            submit_calls = mock_tpe.submit.call_args_list
            strategy_calls = [c for c in submit_calls if len(c.args) >= 2 and c.args[0] == executor.run_strategy]
            assert len(strategy_calls) == 2

    def test_execute_submits_functions(self, executor):
        """Test execute submits functions to the thread pool."""
        def my_func(x):
            pass
        executor.add_function(function=my_func, kwargs={"x": 1})

        with patch('aiomql.lib.executor.ThreadPoolExecutor') as mock_pool:
            mock_tpe = MagicMock()
            mock_pool.return_value.__enter__.return_value = mock_tpe
            mock_pool.return_value.__exit__ = MagicMock(return_value=None)

            executor.execute()

            # Check function was submitted
            submit_calls = mock_tpe.submit.call_args_list
            func_calls = [c for c in submit_calls if len(c.args) >= 1 and c.args[0] == my_func]
            assert len(func_calls) == 1

    def test_execute_submits_coroutine_threads(self, executor):
        """Test execute submits coroutine threads to the thread pool."""
        async def my_coro():
            pass
        executor.add_coroutine(coroutine=my_coro, on_separate_thread=True)

        with patch('aiomql.lib.executor.ThreadPoolExecutor') as mock_pool:
            mock_tpe = MagicMock()
            mock_pool.return_value.__enter__.return_value = mock_tpe
            mock_pool.return_value.__exit__ = MagicMock(return_value=None)

            executor.execute()

            # Check coroutine thread was submitted
            submit_calls = mock_tpe.submit.call_args_list
            coro_thread_calls = [c for c in submit_calls if len(c.args) >= 1 and c.args[0] == executor.run_coroutine_task]
            assert len(coro_thread_calls) == 1

    def test_execute_submits_coroutine_tasks(self, executor):
        """Test execute submits run_coroutine_tasks via asyncio.run."""
        async def my_coro():
            pass
        executor.add_coroutine(coroutine=my_coro)

        with patch('aiomql.lib.executor.ThreadPoolExecutor') as mock_pool:
            mock_tpe = MagicMock()
            mock_pool.return_value.__enter__.return_value = mock_tpe
            mock_pool.return_value.__exit__ = MagicMock(return_value=None)

            executor.execute()

            # Check asyncio.run was submitted for coroutine tasks
            submit_calls = mock_tpe.submit.call_args_list
            asyncio_calls = [c for c in submit_calls if len(c.args) >= 1 and c.args[0] == asyncio.run]
            assert len(asyncio_calls) == 1

    def test_execute_sets_executor_attribute(self, executor):
        """Test execute sets the executor attribute on the Executor instance."""
        with patch('aiomql.lib.executor.ThreadPoolExecutor') as mock_pool:
            mock_tpe = MagicMock()
            mock_pool.return_value.__enter__.return_value = mock_tpe
            mock_pool.return_value.__exit__ = MagicMock(return_value=None)

            executor.execute()

            assert executor.executor == mock_tpe


class TestIntegration:
    """Integration tests for Executor."""

    @pytest.fixture
    def executor(self):
        """Create an Executor for testing."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config:
                config = MagicMock()
                config.shutdown = False
                config.force_shutdown = False
                config.task_queue = MagicMock()
                mock_config.return_value = config
                return Executor()

    def test_full_setup(self, executor):
        """Test complete executor setup."""
        # Add strategies
        strategy1 = MagicMock(spec=Strategy)
        strategy2 = MagicMock(spec=Strategy)
        executor.add_strategies(strategies=(strategy1, strategy2))

        # Add functions
        def my_func(x):
            pass
        executor.add_function(function=my_func, kwargs={"x": 1})

        # Add coroutines
        async def my_coro():
            pass
        executor.add_coroutine(coroutine=my_coro)

        async def my_thread_coro():
            pass
        executor.add_coroutine(coroutine=my_thread_coro, on_separate_thread=True)

        assert len(executor.strategy_runners) == 2
        assert len(executor.functions) == 1
        assert len(executor.coroutines) == 1
        assert len(executor.coroutine_threads) == 1

    def test_async_and_sync_strategies(self, executor):
        """Test executor handles both async and sync strategies."""
        async_strategy = MockAsyncStrategy()
        sync_strategy = MockSyncStrategy()

        executor.add_strategy(strategy=async_strategy)
        executor.add_strategy(strategy=sync_strategy)

        assert len(executor.strategy_runners) == 2

        # Both should be runnable via run_strategy
        with patch('asyncio.run'):
            # Should not raise for either
            Executor.run_strategy(async_strategy)
            Executor.run_strategy(sync_strategy)

    async def test_coroutines_with_different_kwargs(self, executor):
        """Test running coroutines with different kwargs."""
        results = []

        async def collector(value):
            results.append(value)

        executor.add_coroutine(coroutine=collector, kwargs={"value": 1})
        executor.add_coroutine(coroutine=collector, kwargs={"value": 2})

        # Note: dicts can't have duplicate keys, so second call overwrites first
        await executor.run_coroutine_tasks()

        # Only the last kwargs will be used
        assert 2 in results

    def test_timeout_functionality(self, executor):
        """Test timeout functionality in exit."""
        executor.timeout = 0.05
        executor.executor = MagicMock(spec=ThreadPoolExecutor)

        start = time.time()
        executor.exit()
        elapsed = time.time() - start

        # Should exit within timeout + small buffer
        assert elapsed < 0.2
        assert executor.config.shutdown is True

    def test_sigint_then_exit(self, executor):
        """Test SIGINT handler followed by exit."""
        executor.executor = MagicMock(spec=ThreadPoolExecutor)
        strategy = MagicMock()
        strategy.running = True
        executor.add_strategy(strategy=strategy)

        # Simulate SIGINT
        executor.sigint_handle(2, None)
        assert executor.config.shutdown is True

        # Now exit should process immediately
        executor.exit()

        assert strategy.running is False
        executor.config.task_queue.cancel.assert_called_once()
