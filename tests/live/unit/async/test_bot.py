"""Comprehensive tests for the Bot module.

Tests cover:
- Bot initialization
- process_pool class method
- start_terminal async method
- start_terminal_sync method
- initialize async method
- initialize_sync method
- add_function method
- add_coroutine method
- execute method
- start method
- add_strategy method
- add_strategies method
- add_strategy_all method
- init_strategy async method
- init_strategies async method
- init_strategy_sync method
- init_strategies_sync method
- Integration tests
"""

import asyncio
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Type
from unittest.mock import MagicMock, AsyncMock, patch, call

import pytest

from aiomql.lib.bot import Bot
from aiomql.lib.executor import Executor
from aiomql.lib.strategy import Strategy
from aiomql.lib.symbol import Symbol
from aiomql.core.config import Config
from aiomql.core.meta_trader import MetaTrader


class MockStrategy:
    """Mock strategy for testing."""

    def __init__(self, symbol=None, params=None, **kwargs):
        self.symbol = symbol
        self.params = params or {}
        self.kwargs = kwargs
        self.running = True

    async def initialize(self):
        """Async initialize method."""
        return True

    def initialize_sync(self):
        """Sync initialize method."""
        return True

    async def run_strategy(self):
        """Async run_strategy method."""
        pass


class MockFailingStrategy:
    """Mock strategy that fails initialization."""

    def __init__(self, symbol=None, params=None, **kwargs):
        self.symbol = symbol
        self.params = params or {}
        self.running = True

    async def initialize(self):
        """Async initialize method that fails."""
        return False

    def initialize_sync(self):
        """Sync initialize method that fails."""
        return False


class TestBotInitialization:
    """Test Bot class initialization."""

    @patch('aiomql.lib.executor.signal')
    @patch.object(Config, '__new__')
    @patch('aiomql.lib.bot.MetaTrader')
    def test_init_creates_config(self, mock_metatrader, mock_config_new, mock_signal):
        """Test Bot init creates config instance."""
        mock_config = MagicMock()
        mock_config_new.return_value = mock_config

        bot = Bot()

        assert bot.config is not None

    @patch('aiomql.lib.executor.signal')
    @patch.object(Config, '__new__')
    @patch('aiomql.lib.bot.MetaTrader')
    def test_init_creates_executor(self, mock_metatrader, mock_config_new, mock_signal):
        """Test Bot init creates executor instance."""
        mock_config = MagicMock()
        mock_config_new.return_value = mock_config

        bot = Bot()

        assert bot.executor is not None
        assert isinstance(bot.executor, Executor)

    @patch('aiomql.lib.executor.signal')
    @patch.object(Config, '__new__')
    @patch('aiomql.lib.bot.MetaTrader')
    def test_init_creates_empty_strategies_list(self, mock_metatrader, mock_config_new, mock_signal):
        """Test Bot init creates empty strategies list."""
        mock_config = MagicMock()
        mock_config_new.return_value = mock_config

        bot = Bot()

        assert bot.strategies == []

    @patch('aiomql.lib.executor.signal')
    @patch.object(Config, '__new__')
    @patch('aiomql.lib.bot.MetaTrader')
    def test_init_sets_initialized_false(self, mock_metatrader, mock_config_new, mock_signal):
        """Test Bot init sets initialized to False."""
        mock_config = MagicMock()
        mock_config_new.return_value = mock_config

        bot = Bot()

        assert bot.initialized is False

    @patch('aiomql.lib.executor.signal')
    @patch.object(Config, '__new__')
    @patch('aiomql.lib.bot.MetaTrader')
    def test_init_sets_login_false(self, mock_metatrader, mock_config_new, mock_signal):
        """Test Bot init sets login to False."""
        mock_config = MagicMock()
        mock_config_new.return_value = mock_config

        bot = Bot()

        assert bot.login is False

    @patch('aiomql.lib.executor.signal')
    @patch.object(Config, '__new__')
    @patch('aiomql.lib.bot.MetaTrader')
    def test_init_creates_metatrader_instance(self, mock_metatrader, mock_config_new, mock_signal):
        """Test Bot init creates MetaTrader instance."""
        mock_config = MagicMock()
        mock_config_new.return_value = mock_config
        mock_mt = MagicMock()
        mock_metatrader.return_value = mock_mt

        bot = Bot()

        mock_metatrader.assert_called_once()
        assert bot.mt5 == mock_mt

    @patch('aiomql.lib.executor.signal')
    @patch.object(Config, '__new__')
    @patch('aiomql.lib.bot.MetaTrader')
    def test_init_passes_bot_to_config(self, mock_metatrader, mock_config_new, mock_signal):
        """Test Bot init passes itself to Config constructor."""
        mock_config = MagicMock()
        mock_config_new.return_value = mock_config

        bot = Bot()

        # Config is called with bot=self
        mock_config_new.assert_called()


class TestProcessPool:
    """Test Bot process_pool class method."""

    def test_process_pool_with_processes(self):
        """Test process_pool runs processes in parallel."""
        call_tracker = {"called": False}

        def mock_process(**kwargs):
            call_tracker["called"] = True
            call_tracker["kwargs"] = kwargs

        with patch.object(ProcessPoolExecutor, '__init__', return_value=None):
            with patch.object(ProcessPoolExecutor, '__enter__') as mock_enter:
                mock_executor = MagicMock()
                mock_enter.return_value = mock_executor
                with patch.object(ProcessPoolExecutor, '__exit__', return_value=None):
                    Bot.process_pool(processes={mock_process: {"arg1": "value1"}}, num_workers=2)

                    mock_executor.submit.assert_called_once_with(mock_process, arg1="value1")

    def test_process_pool_uses_default_workers(self):
        """Test process_pool calculates workers from processes count."""
        def mock_process1(**kwargs):
            pass

        def mock_process2(**kwargs):
            pass

        with patch('aiomql.lib.bot.ProcessPoolExecutor') as mock_pool:
            mock_executor = MagicMock()
            mock_pool.return_value.__enter__.return_value = mock_executor
            mock_pool.return_value.__exit__ = MagicMock(return_value=None)

            processes = {mock_process1: {}, mock_process2: {}}
            Bot.process_pool(processes=processes)

            # Workers should be len(processes) + 1 = 3
            mock_pool.assert_called_once_with(max_workers=3)

    def test_process_pool_with_custom_workers(self):
        """Test process_pool uses custom worker count."""
        def mock_process(**kwargs):
            pass

        with patch('aiomql.lib.bot.ProcessPoolExecutor') as mock_pool:
            mock_executor = MagicMock()
            mock_pool.return_value.__enter__.return_value = mock_executor
            mock_pool.return_value.__exit__ = MagicMock(return_value=None)

            Bot.process_pool(processes={mock_process: {}}, num_workers=5)

            mock_pool.assert_called_once_with(max_workers=5)

    def test_process_pool_multiple_processes(self):
        """Test process_pool submits all processes."""
        def mock_process1(**kwargs):
            pass

        def mock_process2(**kwargs):
            pass

        def mock_process3(**kwargs):
            pass

        with patch.object(ProcessPoolExecutor, '__init__', return_value=None):
            with patch.object(ProcessPoolExecutor, '__enter__') as mock_enter:
                mock_executor = MagicMock()
                mock_enter.return_value = mock_executor
                with patch.object(ProcessPoolExecutor, '__exit__', return_value=None):
                    processes = {
                        mock_process1: {"x": 1},
                        mock_process2: {"y": 2},
                        mock_process3: {},
                    }
                    Bot.process_pool(processes=processes, num_workers=4)

                    assert mock_executor.submit.call_count == 3


class TestStartTerminal:
    """Test Bot start_terminal and start_terminal_sync methods."""

    @pytest.fixture
    def bot(self):
        """Create a Bot instance for testing."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config_new:
                mock_config = MagicMock()
                mock_config_new.return_value = mock_config
                with patch('aiomql.lib.bot.MetaTrader') as mock_mt:
                    mock_mt_instance = MagicMock()
                    mock_mt.return_value = mock_mt_instance
                    bot = Bot()
                    bot.mt5 = mock_mt_instance
                    return bot

    async def test_start_terminal_success(self, bot):
        """Test start_terminal with successful login."""
        bot.mt5.initialize = AsyncMock(return_value=True)
        bot.mt5.login = AsyncMock(return_value=True)

        result = await bot.start_terminal()

        assert result is True
        assert bot.initialized is True
        assert bot.login is True

    async def test_start_terminal_initialize_fails(self, bot):
        """Test start_terminal when initialize fails."""
        bot.mt5.initialize = AsyncMock(return_value=False)

        result = await bot.start_terminal()

        assert result is False
        assert bot.initialized is False
        assert bot.login is False

    async def test_start_terminal_login_fails(self, bot):
        """Test start_terminal when login fails."""
        bot.mt5.initialize = AsyncMock(return_value=True)
        bot.mt5.login = AsyncMock(return_value=False)

        result = await bot.start_terminal()

        assert result is False
        assert bot.initialized is True
        assert bot.login is False

    async def test_start_terminal_calls_initialize_then_login(self, bot):
        """Test start_terminal calls initialize before login."""
        call_order = []
        bot.mt5.initialize = AsyncMock(return_value=True, side_effect=lambda: call_order.append("init") or True)
        bot.mt5.login = AsyncMock(return_value=True, side_effect=lambda: call_order.append("login") or True)

        await bot.start_terminal()

        assert call_order == ["init", "login"]

    async def test_start_terminal_skips_login_when_init_fails(self, bot):
        """Test start_terminal does not call login when initialize fails."""
        bot.mt5.initialize = AsyncMock(return_value=False)
        bot.mt5.login = AsyncMock(return_value=True)

        await bot.start_terminal()

        bot.mt5.login.assert_not_called()

    def test_start_terminal_sync_success(self, bot):
        """Test start_terminal_sync with successful login."""
        bot.mt5.initialize_sync = MagicMock(return_value=True)
        bot.mt5.login_sync = MagicMock(return_value=True)

        result = bot.start_terminal_sync()

        assert result is True
        assert bot.initialized is True
        assert bot.login is True

    def test_start_terminal_sync_initialize_fails(self, bot):
        """Test start_terminal_sync when initialize fails."""
        bot.mt5.initialize_sync = MagicMock(return_value=False)

        result = bot.start_terminal_sync()

        assert result is False
        assert bot.initialized is False
        assert bot.login is False

    def test_start_terminal_sync_login_fails(self, bot):
        """Test start_terminal_sync when login fails."""
        bot.mt5.initialize_sync = MagicMock(return_value=True)
        bot.mt5.login_sync = MagicMock(return_value=False)

        result = bot.start_terminal_sync()

        assert result is False
        assert bot.initialized is True
        assert bot.login is False

    def test_start_terminal_sync_skips_login_when_init_fails(self, bot):
        """Test start_terminal_sync does not call login_sync when initialize fails."""
        bot.mt5.initialize_sync = MagicMock(return_value=False)
        bot.mt5.login_sync = MagicMock(return_value=True)

        bot.start_terminal_sync()

        bot.mt5.login_sync.assert_not_called()


class TestInitialize:
    """Test Bot initialize and initialize_sync methods."""

    @pytest.fixture
    def bot(self):
        """Create a Bot instance for testing."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config_new:
                mock_config = MagicMock()
                mock_config.shutdown = False
                mock_config.task_queue = MagicMock()
                mock_config.task_queue.run = AsyncMock()
                mock_config_new.return_value = mock_config
                with patch('aiomql.lib.bot.MetaTrader') as mock_mt:
                    mock_mt_instance = MagicMock()
                    mock_mt.return_value = mock_mt_instance
                    bot = Bot()
                    bot.mt5 = mock_mt_instance
                    return bot

    async def test_initialize_successful_login(self, bot):
        """Test initialize with successful login."""
        bot.mt5.initialize = AsyncMock(return_value=True)
        bot.mt5.login = AsyncMock(return_value=True)

        await bot.initialize()

        assert bot.login is True

    async def test_initialize_failed_login_raises_system_exit(self, bot):
        """Test initialize raises SystemExit on failed login."""
        bot.mt5.initialize = AsyncMock(return_value=False)

        with pytest.raises(SystemExit):
            await bot.initialize()

    async def test_initialize_adds_task_queue_coroutine(self, bot):
        """Test initialize adds task_queue.run to executor."""
        bot.mt5.initialize = AsyncMock(return_value=True)
        bot.mt5.login = AsyncMock(return_value=True)

        with patch.object(bot.executor, 'add_coroutine') as mock_add_coro:
            await bot.initialize()

            # Check that task_queue.run was added
            assert mock_add_coro.called

    async def test_initialize_adds_exit_function(self, bot):
        """Test initialize adds executor.exit to functions."""
        bot.mt5.initialize = AsyncMock(return_value=True)
        bot.mt5.login = AsyncMock(return_value=True)

        with patch.object(bot.executor, 'add_function') as mock_add_func:
            await bot.initialize()

            mock_add_func.assert_called()

    async def test_initialize_no_strategies_sets_shutdown(self, bot):
        """Test initialize sets shutdown when no strategies."""
        bot.mt5.initialize = AsyncMock(return_value=True)
        bot.mt5.login = AsyncMock(return_value=True)
        bot.executor.strategy_runners = []

        await bot.initialize()

        assert bot.config.shutdown is True

    async def test_initialize_with_strategies(self, bot):
        """Test initialize with strategies does not shutdown."""
        bot.mt5.initialize = AsyncMock(return_value=True)
        bot.mt5.login = AsyncMock(return_value=True)

        mock_strategy = MockStrategy()
        bot.strategies.append(mock_strategy)

        await bot.initialize()

        assert bot.config.shutdown is False

    async def test_initialize_calls_init_strategies(self, bot):
        """Test initialize calls init_strategies."""
        bot.mt5.initialize = AsyncMock(return_value=True)
        bot.mt5.login = AsyncMock(return_value=True)

        with patch.object(bot, 'init_strategies', new_callable=AsyncMock) as mock_init_strats:
            await bot.initialize()

            mock_init_strats.assert_called_once()

    def test_initialize_sync_successful_login(self, bot):
        """Test initialize_sync with successful login."""
        bot.mt5.initialize_sync = MagicMock(return_value=True)
        bot.mt5.login_sync = MagicMock(return_value=True)

        bot.initialize_sync()

        assert bot.login is True

    def test_initialize_sync_failed_login_raises_system_exit(self, bot):
        """Test initialize_sync raises SystemExit on failed login."""
        bot.mt5.initialize_sync = MagicMock(return_value=False)

        with pytest.raises(SystemExit):
            bot.initialize_sync()

    def test_initialize_sync_adds_task_queue_coroutine(self, bot):
        """Test initialize_sync adds task_queue.run to executor."""
        bot.mt5.initialize_sync = MagicMock(return_value=True)
        bot.mt5.login_sync = MagicMock(return_value=True)

        with patch.object(bot.executor, 'add_coroutine') as mock_add_coro:
            bot.initialize_sync()

            assert mock_add_coro.called

    def test_initialize_sync_adds_exit_function(self, bot):
        """Test initialize_sync adds executor.exit to functions."""
        bot.mt5.initialize_sync = MagicMock(return_value=True)
        bot.mt5.login_sync = MagicMock(return_value=True)

        with patch.object(bot.executor, 'add_function') as mock_add_func:
            bot.initialize_sync()

            mock_add_func.assert_called()

    def test_initialize_sync_no_strategies_sets_shutdown(self, bot):
        """Test initialize_sync sets shutdown when no strategies."""
        bot.mt5.initialize_sync = MagicMock(return_value=True)
        bot.mt5.login_sync = MagicMock(return_value=True)
        bot.executor.strategy_runners = []

        bot.initialize_sync()

        assert bot.config.shutdown is True

    def test_initialize_sync_calls_init_strategies_sync(self, bot):
        """Test initialize_sync calls init_strategies_sync."""
        bot.mt5.initialize_sync = MagicMock(return_value=True)
        bot.mt5.login_sync = MagicMock(return_value=True)

        with patch.object(bot, 'init_strategies_sync') as mock_init_strats:
            bot.initialize_sync()

            mock_init_strats.assert_called_once()


class TestAddFunctionAndCoroutine:
    """Test Bot add_function and add_coroutine methods."""

    @pytest.fixture
    def bot(self):
        """Create a Bot instance for testing."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config_new:
                mock_config = MagicMock()
                mock_config_new.return_value = mock_config
                with patch('aiomql.lib.bot.MetaTrader'):
                    return Bot()

    def test_add_function_without_kwargs(self, bot):
        """Test add_function without kwargs."""
        def my_function():
            pass

        with patch.object(bot.executor, 'add_function') as mock_add:
            bot.add_function(function=my_function)

            mock_add.assert_called_once_with(function=my_function, kwargs={})

    def test_add_function_with_kwargs(self, bot):
        """Test add_function with kwargs."""
        def my_function(a, b):
            pass

        with patch.object(bot.executor, 'add_function') as mock_add:
            bot.add_function(function=my_function, a=1, b=2)

            mock_add.assert_called_once_with(function=my_function, kwargs={"a": 1, "b": 2})

    def test_add_coroutine_without_kwargs(self, bot):
        """Test add_coroutine without kwargs."""
        async def my_coroutine():
            pass

        with patch.object(bot.executor, 'add_coroutine') as mock_add:
            bot.add_coroutine(coroutine=my_coroutine)

            mock_add.assert_called_once_with(coroutine=my_coroutine, kwargs={}, on_separate_thread=False)

    def test_add_coroutine_with_kwargs(self, bot):
        """Test add_coroutine with kwargs."""
        async def my_coroutine(a, b):
            pass

        with patch.object(bot.executor, 'add_coroutine') as mock_add:
            bot.add_coroutine(coroutine=my_coroutine, a=1, b=2)

            mock_add.assert_called_once_with(coroutine=my_coroutine, kwargs={"a": 1, "b": 2}, on_separate_thread=False)

    def test_add_coroutine_on_separate_thread(self, bot):
        """Test add_coroutine with on_separate_thread=True."""
        async def my_coroutine():
            pass

        with patch.object(bot.executor, 'add_coroutine') as mock_add:
            bot.add_coroutine(coroutine=my_coroutine, on_separate_thread=True)

            mock_add.assert_called_once_with(coroutine=my_coroutine, kwargs={}, on_separate_thread=True)


class TestExecuteAndStart:
    """Test Bot execute and start methods."""

    @pytest.fixture
    def bot(self):
        """Create a Bot instance for testing."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config_new:
                mock_config = MagicMock()
                mock_config.shutdown = False
                mock_config.task_queue = MagicMock()
                mock_config.task_queue.run = AsyncMock()
                mock_config_new.return_value = mock_config
                with patch('aiomql.lib.bot.MetaTrader') as mock_mt:
                    mock_mt_instance = MagicMock()
                    mock_mt.return_value = mock_mt_instance
                    bot = Bot()
                    bot.mt5 = mock_mt_instance
                    return bot

    def test_execute_calls_initialize_sync(self, bot):
        """Test execute calls initialize_sync."""
        bot.mt5.initialize_sync = MagicMock(return_value=True)
        bot.mt5.login_sync = MagicMock(return_value=True)

        with patch.object(bot, 'initialize_sync') as mock_init:
            with patch.object(bot.executor, 'execute'):
                bot.config.shutdown = True  # Exit immediately
                bot.execute()

                mock_init.assert_called_once()

    def test_execute_calls_executor_execute_when_not_shutdown(self, bot):
        """Test execute calls executor.execute when not shutdown."""
        bot.mt5.initialize_sync = MagicMock(return_value=True)
        bot.mt5.login_sync = MagicMock(return_value=True)

        with patch.object(bot, 'initialize_sync'):
            with patch.object(bot.executor, 'execute') as mock_exec:
                bot.config.shutdown = False
                bot.execute()

                mock_exec.assert_called_once()

    def test_execute_skips_executor_when_shutdown(self, bot):
        """Test execute skips executor.execute when shutdown."""
        bot.mt5.initialize_sync = MagicMock(return_value=True)
        bot.mt5.login_sync = MagicMock(return_value=True)

        with patch.object(bot, 'initialize_sync'):
            with patch.object(bot.executor, 'execute') as mock_exec:
                bot.config.shutdown = True
                bot.execute()

                mock_exec.assert_not_called()

    async def test_start_calls_initialize(self, bot):
        """Test start calls initialize."""
        bot.mt5.initialize = AsyncMock(return_value=True)
        bot.mt5.login = AsyncMock(return_value=True)

        with patch.object(bot, 'initialize', new_callable=AsyncMock) as mock_init:
            with patch.object(bot.executor, 'execute'):
                bot.config.shutdown = True  # Exit immediately
                await bot.start()

                mock_init.assert_called_once()

    async def test_start_calls_executor_execute_when_not_shutdown(self, bot):
        """Test start calls executor.execute when not shutdown."""
        bot.mt5.initialize = AsyncMock(return_value=True)
        bot.mt5.login = AsyncMock(return_value=True)

        with patch.object(bot, 'initialize', new_callable=AsyncMock):
            with patch.object(bot.executor, 'execute') as mock_exec:
                bot.config.shutdown = False
                await bot.start()

                mock_exec.assert_called_once()

    async def test_start_skips_executor_when_shutdown(self, bot):
        """Test start skips executor.execute when shutdown."""
        bot.mt5.initialize = AsyncMock(return_value=True)
        bot.mt5.login = AsyncMock(return_value=True)

        with patch.object(bot, 'initialize', new_callable=AsyncMock):
            with patch.object(bot.executor, 'execute') as mock_exec:
                bot.config.shutdown = True
                await bot.start()

                mock_exec.assert_not_called()


class TestAddStrategy:
    """Test Bot add_strategy, add_strategies, and add_strategy_all methods."""

    @pytest.fixture
    def bot(self):
        """Create a Bot instance for testing."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config_new:
                mock_config = MagicMock()
                mock_config_new.return_value = mock_config
                with patch('aiomql.lib.bot.MetaTrader'):
                    return Bot()

    def test_add_strategy_appends_to_list(self, bot):
        """Test add_strategy appends strategy to list."""
        strategy = MockStrategy()

        bot.add_strategy(strategy=strategy)

        assert len(bot.strategies) == 1
        assert strategy in bot.strategies

    def test_add_strategy_multiple(self, bot):
        """Test adding multiple strategies one by one."""
        strategy1 = MockStrategy()
        strategy2 = MockStrategy()

        bot.add_strategy(strategy=strategy1)
        bot.add_strategy(strategy=strategy2)

        assert len(bot.strategies) == 2
        assert strategy1 in bot.strategies
        assert strategy2 in bot.strategies

    def test_add_strategies_batch(self, bot):
        """Test add_strategies adds multiple strategies at once."""
        strategy1 = MockStrategy()
        strategy2 = MockStrategy()
        strategy3 = MockStrategy()

        bot.add_strategies(strategies=[strategy1, strategy2, strategy3])

        assert len(bot.strategies) == 3
        assert strategy1 in bot.strategies
        assert strategy2 in bot.strategies
        assert strategy3 in bot.strategies

    def test_add_strategies_extends_existing(self, bot):
        """Test add_strategies extends existing strategies."""
        strategy1 = MockStrategy()
        strategy2 = MockStrategy()

        bot.add_strategy(strategy=strategy1)
        bot.add_strategies(strategies=[strategy2])

        assert len(bot.strategies) == 2

    def test_add_strategies_with_tuple(self, bot):
        """Test add_strategies works with tuple input."""
        strategy1 = MockStrategy()
        strategy2 = MockStrategy()

        bot.add_strategies(strategies=(strategy1, strategy2))

        assert len(bot.strategies) == 2

    def test_add_strategies_with_generator(self, bot):
        """Test add_strategies works with generator input."""
        def strategy_gen():
            yield MockStrategy()
            yield MockStrategy()

        bot.add_strategies(strategies=strategy_gen())

        assert len(bot.strategies) == 2

    def test_add_strategy_all_creates_strategy_per_symbol(self, bot):
        """Test add_strategy_all creates strategy for each symbol."""
        mock_symbol1 = MagicMock(spec=Symbol)
        mock_symbol2 = MagicMock(spec=Symbol)
        mock_symbol3 = MagicMock(spec=Symbol)

        bot.add_strategy_all(
            strategy=MockStrategy,
            params={"param1": "value1"},
            symbols=[mock_symbol1, mock_symbol2, mock_symbol3]
        )

        assert len(bot.strategies) == 3

    def test_add_strategy_all_passes_params(self, bot):
        """Test add_strategy_all passes params to each strategy."""
        mock_symbol = MagicMock(spec=Symbol)

        bot.add_strategy_all(
            strategy=MockStrategy,
            params={"param1": "value1"},
            symbols=[mock_symbol]
        )

        assert bot.strategies[0].params == {"param1": "value1"}

    def test_add_strategy_all_passes_kwargs(self, bot):
        """Test add_strategy_all passes additional kwargs."""
        mock_symbol = MagicMock(spec=Symbol)

        bot.add_strategy_all(
            strategy=MockStrategy,
            symbols=[mock_symbol],
            extra_arg="extra_value"
        )

        assert bot.strategies[0].kwargs.get("extra_arg") == "extra_value"

    def test_add_strategy_all_assigns_correct_symbols(self, bot):
        """Test add_strategy_all assigns the correct symbol to each strategy."""
        mock_symbol1 = MagicMock(spec=Symbol)
        mock_symbol1.name = "EURUSD"
        mock_symbol2 = MagicMock(spec=Symbol)
        mock_symbol2.name = "GBPUSD"

        bot.add_strategy_all(
            strategy=MockStrategy,
            symbols=[mock_symbol1, mock_symbol2]
        )

        assert bot.strategies[0].symbol == mock_symbol1
        assert bot.strategies[1].symbol == mock_symbol2


class TestInitStrategy:
    """Test Bot init_strategy, init_strategies, init_strategy_sync, and init_strategies_sync methods."""

    @pytest.fixture
    def bot(self):
        """Create a Bot instance for testing."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config_new:
                mock_config = MagicMock()
                mock_config_new.return_value = mock_config
                with patch('aiomql.lib.bot.MetaTrader'):
                    return Bot()

    async def test_init_strategy_success_adds_to_executor(self, bot):
        """Test init_strategy adds successful strategy to executor."""
        strategy = MockStrategy()

        with patch.object(bot.executor, 'add_strategy') as mock_add:
            result = await bot.init_strategy(strategy=strategy)

            assert result is True
            mock_add.assert_called_once_with(strategy=strategy)

    async def test_init_strategy_failure_does_not_add(self, bot):
        """Test init_strategy does not add failing strategy."""
        strategy = MockFailingStrategy()

        with patch.object(bot.executor, 'add_strategy') as mock_add:
            result = await bot.init_strategy(strategy=strategy)

            assert result is False
            mock_add.assert_not_called()

    async def test_init_strategy_returns_bool(self, bot):
        """Test init_strategy returns boolean result."""
        strategy = MockStrategy()

        with patch.object(bot.executor, 'add_strategy'):
            result = await bot.init_strategy(strategy=strategy)

            assert isinstance(result, bool)

    async def test_init_strategies_initializes_all(self, bot):
        """Test init_strategies initializes all strategies."""
        strategy1 = MockStrategy()
        strategy2 = MockStrategy()

        bot.strategies = [strategy1, strategy2]

        with patch.object(bot.executor, 'add_strategy'):
            await bot.init_strategies()

            # Both strategies should be in executor
            assert bot.executor.add_strategy.call_count == 2

    async def test_init_strategies_handles_failures(self, bot):
        """Test init_strategies handles failing strategies."""
        strategy1 = MockStrategy()
        strategy2 = MockFailingStrategy()

        bot.strategies = [strategy1, strategy2]

        with patch.object(bot.executor, 'add_strategy'):
            await bot.init_strategies()

            # Only successful strategy should be added
            assert bot.executor.add_strategy.call_count == 1

    async def test_init_strategies_uses_gather(self, bot):
        """Test init_strategies uses asyncio.gather for concurrent initialization."""
        strategy1 = MockStrategy()
        strategy2 = MockStrategy()
        strategy3 = MockStrategy()

        bot.strategies = [strategy1, strategy2, strategy3]

        with patch.object(bot.executor, 'add_strategy'):
            with patch('aiomql.lib.bot.asyncio.gather', new_callable=AsyncMock, return_value=[True, True, True]) as mock_gather:
                await bot.init_strategies()

                mock_gather.assert_called_once()

    def test_init_strategy_sync_success_adds_to_executor(self, bot):
        """Test init_strategy_sync adds successful strategy to executor."""
        strategy = MockStrategy()

        with patch.object(bot.executor, 'add_strategy') as mock_add:
            result = bot.init_strategy_sync(strategy=strategy)

            assert result is True
            mock_add.assert_called_once_with(strategy=strategy)

    def test_init_strategy_sync_failure_does_not_add(self, bot):
        """Test init_strategy_sync does not add failing strategy."""
        strategy = MockFailingStrategy()

        with patch.object(bot.executor, 'add_strategy') as mock_add:
            result = bot.init_strategy_sync(strategy=strategy)

            assert result is False
            mock_add.assert_not_called()

    def test_init_strategies_sync_initializes_all(self, bot):
        """Test init_strategies_sync initializes all strategies."""
        strategy1 = MockStrategy()
        strategy2 = MockStrategy()

        bot.strategies = [strategy1, strategy2]

        with patch.object(bot.executor, 'add_strategy'):
            bot.init_strategies_sync()

            # Both strategies should be in executor
            assert bot.executor.add_strategy.call_count == 2

    def test_init_strategies_sync_handles_failures(self, bot):
        """Test init_strategies_sync handles failing strategies."""
        strategy1 = MockStrategy()
        strategy2 = MockFailingStrategy()

        bot.strategies = [strategy1, strategy2]

        with patch.object(bot.executor, 'add_strategy'):
            bot.init_strategies_sync()

            # Only successful strategy should be added
            assert bot.executor.add_strategy.call_count == 1

    def test_init_strategies_sync_sequential(self, bot):
        """Test init_strategies_sync initializes strategies sequentially."""
        strategy1 = MockStrategy()
        strategy2 = MockStrategy()

        bot.strategies = [strategy1, strategy2]

        with patch.object(bot.executor, 'add_strategy') as mock_add:
            bot.init_strategies_sync()

            # Verify both were added
            calls = mock_add.call_args_list
            assert len(calls) == 2
            assert calls[0] == call(strategy=strategy1)
            assert calls[1] == call(strategy=strategy2)


class TestIntegration:
    """Integration tests for Bot."""

    @pytest.fixture
    def bot(self):
        """Create a Bot instance for testing."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config_new:
                mock_config = MagicMock()
                mock_config.shutdown = False
                mock_config.task_queue = MagicMock()
                mock_config.task_queue.run = AsyncMock()
                mock_config_new.return_value = mock_config
                with patch('aiomql.lib.bot.MetaTrader') as mock_mt:
                    mock_mt_instance = MagicMock()
                    mock_mt.return_value = mock_mt_instance
                    bot = Bot()
                    bot.mt5 = mock_mt_instance
                    return bot

    def test_full_setup_with_strategies_functions_coroutines(self, bot):
        """Test complete bot setup with strategies, functions, and coroutines."""
        # Add strategies
        strategy1 = MockStrategy()
        strategy2 = MockStrategy()
        bot.add_strategies(strategies=[strategy1, strategy2])

        # Add functions
        def my_func(x):
            pass
        bot.add_function(function=my_func, x=1)

        # Add coroutines
        async def my_coro():
            pass
        bot.add_coroutine(coroutine=my_coro)

        async def my_thread_coro():
            pass
        bot.add_coroutine(coroutine=my_thread_coro, on_separate_thread=True)

        assert len(bot.strategies) == 2
        assert my_func in bot.executor.functions
        assert my_coro in bot.executor.coroutines
        assert my_thread_coro in bot.executor.coroutine_threads

    async def test_full_async_workflow(self, bot):
        """Test complete async workflow."""
        bot.mt5.initialize = AsyncMock(return_value=True)
        bot.mt5.login = AsyncMock(return_value=True)

        strategy = MockStrategy()
        bot.add_strategy(strategy=strategy)

        await bot.init_strategies()

        assert len(bot.executor.strategy_runners) == 1

    def test_full_sync_workflow(self, bot):
        """Test complete sync workflow."""
        strategy = MockStrategy()
        bot.add_strategy(strategy=strategy)

        bot.init_strategies_sync()

        assert len(bot.executor.strategy_runners) == 1

    def test_add_strategy_all_workflow(self, bot):
        """Test add_strategy_all creates proper strategies."""
        mock_symbol1 = MagicMock(spec=Symbol)
        mock_symbol1.name = "EURUSD"
        mock_symbol2 = MagicMock(spec=Symbol)
        mock_symbol2.name = "GBPUSD"

        bot.add_strategy_all(
            strategy=MockStrategy,
            params={"risk": 0.01},
            symbols=[mock_symbol1, mock_symbol2]
        )

        assert len(bot.strategies) == 2
        assert bot.strategies[0].symbol == mock_symbol1
        assert bot.strategies[1].symbol == mock_symbol2
        assert bot.strategies[0].params == {"risk": 0.01}
        assert bot.strategies[1].params == {"risk": 0.01}

    async def test_mixed_strategy_initialization(self, bot):
        """Test initialization with mix of successful and failing strategies."""
        success_strategy = MockStrategy()
        failure_strategy = MockFailingStrategy()

        bot.add_strategy(strategy=success_strategy)
        bot.add_strategy(strategy=failure_strategy)

        await bot.init_strategies()

        # Only successful strategy should be added to executor
        assert len(bot.executor.strategy_runners) == 1

    def test_bot_always_uses_metatrader(self):
        """Test bot always creates MetaTrader instance."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config_new:
                mock_config = MagicMock()
                mock_config_new.return_value = mock_config
                with patch('aiomql.lib.bot.MetaTrader') as mock_mt:
                    mock_mt_instance = MagicMock()
                    mock_mt.return_value = mock_mt_instance

                    bot = Bot()

                    mock_mt.assert_called_once()
                    assert bot.mt5 == mock_mt_instance


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def bot(self):
        """Create a Bot instance for testing."""
        with patch('aiomql.lib.executor.signal'):
            with patch.object(Config, '__new__') as mock_config_new:
                mock_config = MagicMock()
                mock_config.shutdown = False
                mock_config.task_queue = MagicMock()
                mock_config.task_queue.run = AsyncMock()
                mock_config_new.return_value = mock_config
                with patch('aiomql.lib.bot.MetaTrader') as mock_mt:
                    mock_mt_instance = MagicMock()
                    mock_mt.return_value = mock_mt_instance
                    bot = Bot()
                    bot.mt5 = mock_mt_instance
                    return bot

    def test_add_strategies_empty_list(self, bot):
        """Test add_strategies with empty list."""
        bot.add_strategies(strategies=[])

        assert len(bot.strategies) == 0

    def test_add_strategy_all_empty_symbols(self, bot):
        """Test add_strategy_all with empty symbols list."""
        bot.add_strategy_all(strategy=MockStrategy, symbols=[])

        assert len(bot.strategies) == 0

    def test_add_strategy_all_none_params(self, bot):
        """Test add_strategy_all with None params."""
        mock_symbol = MagicMock(spec=Symbol)

        bot.add_strategy_all(strategy=MockStrategy, params=None, symbols=[mock_symbol])

        assert len(bot.strategies) == 1
        assert bot.strategies[0].params is None or bot.strategies[0].params == {}

    async def test_init_strategies_empty_list(self, bot):
        """Test init_strategies with no strategies."""
        bot.strategies = []

        await bot.init_strategies()

        assert len(bot.executor.strategy_runners) == 0

    def test_init_strategies_sync_empty_list(self, bot):
        """Test init_strategies_sync with no strategies."""
        bot.strategies = []

        bot.init_strategies_sync()

        assert len(bot.executor.strategy_runners) == 0

    async def test_initialize_exception_handling(self, bot):
        """Test initialize handles exceptions properly."""
        bot.mt5.initialize = AsyncMock(side_effect=Exception("Test error"))

        with pytest.raises(SystemExit):
            await bot.initialize()

    def test_initialize_sync_exception_handling(self, bot):
        """Test initialize_sync handles exceptions properly."""
        bot.mt5.initialize_sync = MagicMock(side_effect=Exception("Test error"))

        with pytest.raises(SystemExit):
            bot.initialize_sync()

    async def test_multiple_strategy_initialization_all_fail(self, bot):
        """Test init_strategies when all strategies fail."""
        strategy1 = MockFailingStrategy()
        strategy2 = MockFailingStrategy()

        bot.strategies = [strategy1, strategy2]

        await bot.init_strategies()

        assert len(bot.executor.strategy_runners) == 0

    def test_multiple_strategy_sync_initialization_all_fail(self, bot):
        """Test init_strategies_sync when all strategies fail."""
        strategy1 = MockFailingStrategy()
        strategy2 = MockFailingStrategy()

        bot.strategies = [strategy1, strategy2]

        bot.init_strategies_sync()

        assert len(bot.executor.strategy_runners) == 0

    async def test_start_terminal_return_value_propagated(self, bot):
        """Test start_terminal return value is the result of the last operation."""
        bot.mt5.initialize = AsyncMock(return_value=True)
        bot.mt5.login = AsyncMock(return_value=True)

        result = await bot.start_terminal()

        assert result is True

    def test_execute_checks_shutdown_after_initialize(self, bot):
        """Test execute checks config.shutdown after initialize_sync."""
        call_order = []

        def mock_init():
            call_order.append("init")
            bot.config.shutdown = True  # Set shutdown during init

        with patch.object(bot, 'initialize_sync', side_effect=mock_init):
            with patch.object(bot.executor, 'execute') as mock_exec:
                bot.execute()

                # initialize_sync should be called but executor.execute should not
                assert call_order == ["init"]
                mock_exec.assert_not_called()
