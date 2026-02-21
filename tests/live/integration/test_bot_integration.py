"""Full integration tests for the Bot class with live MetaTrader 5 connection.

Tests cover the complete Bot lifecycle including:
- Bot initialization and default state
- Strategy management (add_strategy, add_strategies, add_strategy_all)
- Terminal connection (async and sync)
- Strategy initialization (async and sync, including failures)
- Full execution lifecycle with Executor timeout
- add_function and add_coroutine integration
"""

import asyncio
import time
import threading
import pytest

from aiomql.lib.bot import Bot
from aiomql.lib.strategy import Strategy
from aiomql.lib.executor import Executor
from aiomql.lib.symbol import Symbol
from aiomql.core.config import Config
from aiomql.core.meta_trader import MetaTrader
from aiomql.core.exceptions import StopTrading


# ---------------------------------------------------------------------------
# Test Strategies
# ---------------------------------------------------------------------------

class TickLoggerStrategy(Strategy):
    """Strategy that logs the current tick and self-terminates."""

    async def trade(self):
        tick = await self.mt5.symbol_info_tick(self.symbol.name)
        if tick is not None:
            self.parameters["last_bid"] = tick.bid
            self.parameters["last_ask"] = tick.ask
            self.parameters["executed"] = True
        self.running = False


class CandleFetchStrategy(Strategy):
    """Strategy that fetches the last 5 candles and self-terminates."""

    async def trade(self):
        rates = await self.mt5.copy_rates_from_pos(self.symbol.name, self.mt5.TIMEFRAME_M1, 0, 5)
        if rates is not None:
            self.parameters["candle_count"] = len(rates)
            self.parameters["executed"] = True
        self.running = False


class FailingStrategy(Strategy):
    """Strategy that raises StopTrading to test graceful shutdown."""

    async def trade(self):
        self.parameters["executed"] = True
        raise StopTrading("Intentional stop for testing")


# ---------------------------------------------------------------------------
# Bot Initialization
# ---------------------------------------------------------------------------

class TestBotInitialization:
    """Test Bot class creation and default state."""

    def test_bot_creates_executor(self):
        """Test Bot creates an Executor on init."""
        bot = Bot()
        assert isinstance(bot.executor, Executor)

    def test_bot_default_flags(self):
        """Test Bot has correct default flags."""
        bot = Bot()
        assert bot.initialized is False
        assert bot.login is False
        assert bot.strategies == []

    def test_bot_config_reference(self):
        """Test Bot holds a Config reference pointing back to itself."""
        bot = Bot()
        assert isinstance(bot.config, Config)
        assert bot.config.bot is bot

    def test_bot_has_mt5(self):
        """Test Bot creates a MetaTrader instance."""
        bot = Bot()
        assert isinstance(bot.mt5, MetaTrader)


# ---------------------------------------------------------------------------
# Strategy Management
# ---------------------------------------------------------------------------

class TestBotStrategyManagement:
    """Test adding strategies to the Bot."""

    def test_add_strategy(self):
        """Test adding a single strategy."""
        bot = Bot()
        sym = Symbol(name="BTCUSD")
        strategy = TickLoggerStrategy(symbol=sym)
        bot.add_strategy(strategy=strategy)
        assert len(bot.strategies) == 1
        assert bot.strategies[0] is strategy

    def test_add_strategies(self):
        """Test adding multiple strategies at once."""
        bot = Bot()
        strategies = [
            TickLoggerStrategy(symbol=Symbol(name="BTCUSD")),
            CandleFetchStrategy(symbol=Symbol(name="ETHUSD")),
        ]
        bot.add_strategies(strategies=strategies)
        assert len(bot.strategies) == 2

    def test_add_strategy_all(self):
        """Test adding one strategy type across multiple symbols."""
        bot = Bot()
        symbols = [Symbol(name="BTCUSD"), Symbol(name="ETHUSD")]
        bot.add_strategy_all(strategy=TickLoggerStrategy, symbols=symbols)
        assert len(bot.strategies) == 2
        assert all(isinstance(s, TickLoggerStrategy) for s in bot.strategies)
        names = {s.symbol.name for s in bot.strategies}
        assert names == {"BTCUSD", "ETHUSD"}

    def test_add_strategy_all_with_params(self):
        """Test add_strategy_all passes params to each instance."""
        bot = Bot()
        symbols = [Symbol(name="BTCUSD")]
        bot.add_strategy_all(
            strategy=TickLoggerStrategy,
            symbols=symbols,
            params={"risk": 0.02},
        )
        assert bot.strategies[0].parameters["risk"] == 0.02

    def test_add_strategy_preserves_order(self):
        """Test strategies are added in order."""
        bot = Bot()
        s1 = TickLoggerStrategy(symbol=Symbol(name="BTCUSD"), name="first")
        s2 = CandleFetchStrategy(symbol=Symbol(name="ETHUSD"), name="second")
        bot.add_strategy(strategy=s1)
        bot.add_strategy(strategy=s2)
        assert bot.strategies[0].name == "first"
        assert bot.strategies[1].name == "second"


# ---------------------------------------------------------------------------
# Terminal Connection
# ---------------------------------------------------------------------------

class TestBotTerminalConnection:
    """Test terminal initialization and login."""

    async def test_start_terminal_async(self):
        """Test async terminal start sets initialized and login flags."""
        bot = Bot()
        result = await bot.start_terminal()
        assert result is True
        assert bot.initialized is True
        assert bot.login is True

    def test_start_terminal_sync(self):
        """Test sync terminal start sets initialized and login flags."""
        bot = Bot()
        result = bot.start_terminal_sync()
        assert result is True
        assert bot.initialized is True
        assert bot.login is True


# ---------------------------------------------------------------------------
# Strategy Initialization
# ---------------------------------------------------------------------------

class TestBotStrategyInitialization:
    """Test strategy initialization through the Bot."""

    async def test_init_strategy_async(self):
        """Test async init_strategy initializes and registers a strategy."""
        bot = Bot()
        await bot.start_terminal()
        strategy = TickLoggerStrategy(symbol=Symbol(name="BTCUSD"))
        result = await bot.init_strategy(strategy=strategy)
        assert result is True
        assert strategy in bot.executor.strategy_runners

    async def test_init_strategies_async(self):
        """Test async init_strategies initializes all strategies."""
        bot = Bot()
        await bot.start_terminal()
        s1 = TickLoggerStrategy(symbol=Symbol(name="BTCUSD"))
        s2 = CandleFetchStrategy(symbol=Symbol(name="ETHUSD"))
        bot.add_strategy(strategy=s1)
        bot.add_strategy(strategy=s2)
        await bot.init_strategies()
        assert len(bot.executor.strategy_runners) == 2

    def test_init_strategy_sync(self):
        """Test sync init_strategy_sync initializes and registers a strategy."""
        bot = Bot()
        bot.start_terminal_sync()
        strategy = TickLoggerStrategy(symbol=Symbol(name="BTCUSD"))
        result = bot.init_strategy_sync(strategy=strategy)
        assert result is True
        assert strategy in bot.executor.strategy_runners

    async def test_init_strategy_invalid_symbol(self):
        """Test init_strategy with an invalid symbol returns False."""
        bot = Bot()
        await bot.start_terminal()
        strategy = TickLoggerStrategy(symbol=Symbol(name="INVALID_SYMBOL_XYZ"))
        result = await bot.init_strategy(strategy=strategy)
        assert result is False
        assert strategy not in bot.executor.strategy_runners

    async def test_init_strategies_partial_failure(self):
        """Test init_strategies handles mix of valid and invalid symbols."""
        bot = Bot()
        await bot.start_terminal()
        s_good = TickLoggerStrategy(symbol=Symbol(name="BTCUSD"))
        s_bad = CandleFetchStrategy(symbol=Symbol(name="INVALID_SYMBOL_XYZ"))
        bot.add_strategy(strategy=s_good)
        bot.add_strategy(strategy=s_bad)
        await bot.init_strategies()
        # Only the valid strategy should be in the executor
        assert len(bot.executor.strategy_runners) == 1
        assert s_good in bot.executor.strategy_runners


# ---------------------------------------------------------------------------
# Full Lifecycle – Synchronous (execute)
# ---------------------------------------------------------------------------

class TestBotFullLifecycle:
    """Test full bot execution lifecycle using executor.timeout."""

    def test_execute_with_tick_logger(self):
        """Test execute() runs a TickLoggerStrategy to completion."""
        bot = Bot()
        strategy = TickLoggerStrategy(
            symbol=Symbol(name="BTCUSD"),
            params={"executed": False},
        )
        bot.add_strategy(strategy=strategy)
        bot.executor.timeout = 3
        bot.execute()
        assert strategy.parameters["executed"] is True
        assert "last_bid" in strategy.parameters
        assert "last_ask" in strategy.parameters

    def test_execute_with_multiple_strategies(self):
        """Test execute() runs multiple strategies."""
        bot = Bot()
        s1 = TickLoggerStrategy(
            symbol=Symbol(name="BTCUSD"),
            params={"executed": False},
        )
        s2 = CandleFetchStrategy(
            symbol=Symbol(name="ETHUSD"),
            params={"executed": False},
        )
        bot.add_strategy(strategy=s1)
        bot.add_strategy(strategy=s2)
        bot.executor.timeout = 5
        bot.execute()
        assert s1.parameters["executed"] is True
        assert s2.parameters["executed"] is True
        assert s2.parameters["candle_count"] == 5

    def test_execute_with_failing_strategy(self):
        """Test execute() handles a strategy that raises StopTrading."""
        bot = Bot()
        strategy = FailingStrategy(
            symbol=Symbol(name="BTCUSD"),
            params={"executed": False},
        )
        bot.add_strategy(strategy=strategy)
        bot.executor.timeout = 3
        bot.execute()
        # Strategy should have run and set executed before raising
        assert strategy.parameters["executed"] is True
        # Strategy should have stopped running
        assert strategy.running is False

    def test_execute_no_strategies_sets_shutdown(self):
        """Test execute() with no strategies triggers shutdown flag."""
        bot = Bot()
        bot.executor.timeout = 2
        bot.execute()
        assert bot.config.shutdown is True


# ---------------------------------------------------------------------------
# Full Lifecycle – Asynchronous (start)
# ---------------------------------------------------------------------------

class TestBotAsyncLifecycle:
    """Test full async bot lifecycle using executor.timeout."""

    async def test_start_with_tick_logger(self):
        """Test start() runs a TickLoggerStrategy to completion."""
        bot = Bot()
        strategy = TickLoggerStrategy(
            symbol=Symbol(name="BTCUSD"),
            params={"executed": False},
        )
        bot.add_strategy(strategy=strategy)
        bot.executor.timeout = 3
        await bot.start()
        assert strategy.parameters["executed"] is True

    async def test_start_with_candle_fetcher(self):
        """Test start() runs a CandleFetchStrategy to completion."""
        bot = Bot()
        strategy = CandleFetchStrategy(
            symbol=Symbol(name="BTCUSD"),
            params={"executed": False},
        )
        bot.add_strategy(strategy=strategy)
        bot.executor.timeout = 3
        await bot.start()
        assert strategy.parameters["executed"] is True
        assert strategy.parameters["candle_count"] == 5


# ---------------------------------------------------------------------------
# add_function / add_coroutine
# ---------------------------------------------------------------------------

class TestBotAddFunctionCoroutine:
    """Test add_function and add_coroutine execute during bot lifecycle."""

    def test_add_function_runs(self):
        """Test a function added via add_function is executed."""
        result_holder = {"called": False}

        def mark_called():
            result_holder["called"] = True

        bot = Bot()
        strategy = TickLoggerStrategy(
            symbol=Symbol(name="BTCUSD"),
            params={"executed": False},
        )
        bot.add_strategy(strategy=strategy)
        bot.add_function(function=mark_called)
        bot.executor.timeout = 3
        bot.execute()
        assert result_holder["called"] is True

    def test_add_coroutine_runs(self):
        """Test a coroutine added via add_coroutine is executed."""
        result_holder = {"called": False}

        async def async_mark():
            result_holder["called"] = True

        bot = Bot()
        strategy = TickLoggerStrategy(
            symbol=Symbol(name="BTCUSD"),
            params={"executed": False},
        )
        bot.add_strategy(strategy=strategy)
        bot.add_coroutine(coroutine=async_mark, on_separate_thread=True)
        bot.executor.timeout = 3
        bot.execute()
        assert result_holder["called"] is True


# ---------------------------------------------------------------------------
# Mixed Strategy Types
# ---------------------------------------------------------------------------

class TestBotMixedStrategies:
    """Test Bot with a mix of strategies on different symbols."""

    def test_execute_three_strategies_different_symbols(self):
        """Test execute with tick, candle, and failing strategies on different symbols."""
        bot = Bot()
        s1 = TickLoggerStrategy(
            symbol=Symbol(name="BTCUSD"),
            params={"executed": False},
        )
        s2 = CandleFetchStrategy(
            symbol=Symbol(name="ETHUSD"),
            params={"executed": False},
        )
        s3 = FailingStrategy(
            symbol=Symbol(name="BTCUSD"),
            params={"executed": False},
        )
        bot.add_strategies(strategies=[s1, s2, s3])
        bot.executor.timeout = 5
        bot.execute()
        # All strategies should have executed
        assert s1.parameters["executed"] is True
        assert s2.parameters["executed"] is True
        assert s3.parameters["executed"] is True
        # Verify specific strategy results
        assert "last_bid" in s1.parameters
        assert s2.parameters["candle_count"] == 5
        # Failing strategy should have stopped
        assert s3.running is False

    def test_same_strategy_on_multiple_symbols(self):
        """Test add_strategy_all runs the same strategy type on multiple symbols."""
        bot = Bot()
        symbols = [Symbol(name="BTCUSD"), Symbol(name="ETHUSD")]
        bot.add_strategy_all(
            strategy=TickLoggerStrategy,
            symbols=symbols,
            params={"executed": False},
        )
        bot.executor.timeout = 5
        bot.execute()
        for s in bot.strategies:
            assert s.parameters["executed"] is True
            assert "last_bid" in s.parameters
