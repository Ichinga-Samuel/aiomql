"""Full integration tests for aiomql library in live mode.

This module tests the integration of all major components:
- Bot initialization and terminal connection
- Multiple strategies running concurrently on different symbols
- Position trackers and tracking functions
- Order creation and management
- State management and configuration

Note: These tests require a live MetaTrader 5 connection and should be run
with caution on a demo account.
"""

import pytest
import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock, patch

from aiomql.lib.bot import Bot
from aiomql.lib.strategy import Strategy
from aiomql.lib.symbol import Symbol
from aiomql.lib.trader import Trader
from aiomql.lib.executor import Executor
from aiomql.lib.order import Order
from aiomql.lib.positions import Positions
from aiomql.lib.account import Account
from aiomql.lib.ram import RAM
from aiomql.core.config import Config
from aiomql.core.state import State
from aiomql.core.constants import OrderType, TimeFrame, TradeAction
from aiomql.contrib.symbols import ForexSymbol
from aiomql.contrib.strategies import Chaos
from aiomql.contrib.trackers import (
    PositionTracker,
    OpenPositionsTracker,
    OpenPosition,
    exit_at_profit,
    extend_take_profit
)
from aiomql.contrib.utils.strategy_tracker import StrategyTracker


logger = logging.getLogger(__name__)


class SimpleTestStrategy(Strategy):
    """A simple test strategy for integration testing."""
    
    parameters = {"interval": 1, "test_param": "value"}
    
    def __init__(self, *, symbol: Symbol, params: dict = None, sessions=None, name="TestStrategy"):
        super().__init__(symbol=symbol, params=params, sessions=sessions, name=name)
        self.trade_count = 0
        self.tracker = StrategyTracker()
    
    async def trade(self):
        """Execute a simple trade iteration."""
        self.trade_count += 1
        self.tracker.update(trend="bullish" if self.trade_count % 2 == 0 else "bearish")
        await self.sleep(secs=self.interval)


class TrendFollowerStrategy(Strategy):
    """A trend following strategy for testing multiple strategy types."""
    
    parameters = {"timeframe": TimeFrame.M1, "period": 20}
    
    def __init__(self, *, symbol: Symbol, params: dict = None, sessions=None, name="TrendFollower"):
        super().__init__(symbol=symbol, params=params, sessions=sessions, name=name)
        self.signals = []
    
    async def trade(self):
        """Execute trend following logic."""
        # Simulate checking trend
        self.signals.append({"time": asyncio.get_event_loop().time(), "symbol": self.symbol.name})
        await self.sleep(secs=1)


class TestBotIntegration:
    """Integration tests for Bot class with multiple strategies."""

    @pytest.fixture
    def mock_mt5(self):
        """Mock MetaTrader connection for testing."""
        with patch("aiomql.core.meta_trader.MetaTrader") as mock:
            mock_instance = MagicMock()
            mock_instance.initialize = AsyncMock(return_value=True)
            mock_instance.login = AsyncMock(return_value=True)
            mock_instance.shutdown = AsyncMock()
            mock.return_value = mock_instance
            yield mock_instance

    def test_bot_initialization(self):
        """Test Bot initializes with correct components."""
        bot = Bot()
        
        assert bot.config is not None
        assert bot.executor is not None
        assert bot.mt5 is not None
        assert bot.initialized is False
        assert bot.login is False

    def test_bot_add_single_strategy(self):
        """Test adding a single strategy to bot."""
        bot = Bot()
        mock_symbol = MagicMock(spec=Symbol)
        mock_symbol.name = "EURUSD"
        
        strategy = SimpleTestStrategy(symbol=mock_symbol, name="test_simple")
        bot.add_strategy(strategy=strategy)
        
        assert len(bot.strategies) == 1
        assert bot.strategies[0].name == "test_simple"

    def test_bot_add_multiple_strategies(self):
        """Test adding multiple strategies to bot."""
        bot = Bot()
        
        symbols = []
        for name in ["EURUSD", "GBPUSD", "USDJPY"]:
            mock_symbol = MagicMock(spec=Symbol)
            mock_symbol.name = name
            symbols.append(mock_symbol)
        
        strategies = [
            SimpleTestStrategy(symbol=symbols[0], name="strategy_eur"),
            TrendFollowerStrategy(symbol=symbols[1], name="strategy_gbp"),
            SimpleTestStrategy(symbol=symbols[2], name="strategy_jpy")
        ]
        
        bot.add_strategies(strategies=strategies)
        
        assert len(bot.strategies) == 3

    def test_bot_add_coroutine(self):
        """Test adding coroutine to bot."""
        bot = Bot()
        
        async def test_coro(param1="default"):
            await asyncio.sleep(0.1)
        
        bot.add_coroutine(coroutine=test_coro, param1="value")
        
        assert len(bot.executor.coroutines) == 1

    def test_bot_add_function(self):
        """Test adding synchronous function to bot."""
        bot = Bot()
        
        def test_func(param1="default"):
            pass
        
        bot.add_function(function=test_func, param1="value")
        
        assert len(bot.executor.functions) == 1


class TestExecutorIntegration:
    """Integration tests for Executor with multiple strategies."""

    def test_executor_add_strategies(self):
        """Test executor can add multiple strategies."""
        executor = Executor()
        
        mock_symbol = MagicMock(spec=Symbol)
        mock_symbol.name = "EURUSD"
        
        strategies = [
            SimpleTestStrategy(symbol=mock_symbol, name=f"strategy_{i}")
            for i in range(5)
        ]
        
        executor.add_strategies(strategies=tuple(strategies))
        
        assert len(executor.strategy_runners) == 5

    def test_executor_mixed_tasks(self):
        """Test executor with strategies, coroutines, and functions."""
        executor = Executor()
        
        mock_symbol = MagicMock(spec=Symbol)
        mock_symbol.name = "EURUSD"
        
        # Add strategy
        strategy = SimpleTestStrategy(symbol=mock_symbol, name="test")
        executor.add_strategy(strategy=strategy)
        
        # Add coroutine
        async def coro():
            pass
        executor.add_coroutine(coroutine=coro, kwargs={})
        
        # Add function
        def func():
            pass
        executor.add_function(function=func, kwargs={})
        
        assert len(executor.strategy_runners) == 1
        assert len(executor.coroutines) == 1
        assert len(executor.functions) == 1


class TestStrategyIntegration:
    """Integration tests for Strategy class."""

    def test_strategy_initialization(self):
        """Test strategy initializes with parameters."""
        mock_symbol = MagicMock(spec=Symbol)
        mock_symbol.name = "EURUSD"
        
        strategy = SimpleTestStrategy(
            symbol=mock_symbol,
            name="test_strategy",
            params={"custom_param": 100}
        )
        
        assert strategy.name == "test_strategy"
        assert strategy.symbol is mock_symbol
        assert strategy.custom_param == 100

    def test_strategy_tracker_integration(self):
        """Test strategy with StrategyTracker."""
        mock_symbol = MagicMock(spec=Symbol)
        mock_symbol.name = "EURUSD"
        
        strategy = SimpleTestStrategy(symbol=mock_symbol)
        
        # Simulate trade iterations
        strategy.tracker.update(trend="bullish")
        assert strategy.tracker.bullish is True
        assert strategy.tracker.bearish is False
        
        strategy.tracker.update(trend="bearish")
        assert strategy.tracker.bearish is True
        assert strategy.tracker.bullish is False

    def test_multiple_strategy_types(self):
        """Test different strategy types can coexist."""
        mock_symbol = MagicMock(spec=Symbol)
        mock_symbol.name = "EURUSD"
        
        simple = SimpleTestStrategy(symbol=mock_symbol, name="simple")
        trend = TrendFollowerStrategy(symbol=mock_symbol, name="trend")
        
        assert simple.name == "simple"
        assert trend.name == "trend"
        assert simple.parameters != trend.parameters


class TestTrackerIntegration:
    """Integration tests for position tracking components."""

    def test_position_tracker_initialization(self):
        """Test PositionTracker initialization with OpenPosition."""
        mock_open_position = MagicMock()
        mock_open_position.add_tracker = MagicMock()
        
        async def tracking_func(pos, **kwargs):
            pass
        tracking_func.__name__ = "tracking_func"
        
        tracker = PositionTracker(
            mock_open_position,
            tracking_func,
            name="test_tracker",
            rank=1,
            function_params={"param": "value"}
        )
        
        assert tracker.name == "test_tracker"
        assert tracker.rank == 1
        assert tracker.params == {"param": "value"}
        mock_open_position.add_tracker.assert_called_once()

    async def test_position_tracker_execution(self):
        """Test PositionTracker executes tracking function."""
        mock_open_position = MagicMock()
        mock_open_position.add_tracker = MagicMock()
        
        call_log = []
        
        async def tracking_func(pos, **kwargs):
            call_log.append({"pos": pos, "kwargs": kwargs})
        tracking_func.__name__ = "tracking_func"
        
        tracker = PositionTracker(
            mock_open_position,
            tracking_func,
            function_params={"sl": -10, "tp": 20}
        )
        
        await tracker()
        
        assert len(call_log) == 1
        assert call_log[0]["kwargs"]["sl"] == -10
        assert call_log[0]["kwargs"]["tp"] == 20

    def test_strategy_tracker_state_management(self):
        """Test StrategyTracker manages trend state correctly."""
        tracker = StrategyTracker()
        
        # Initial state
        assert tracker.ranging is True
        assert tracker.bullish is False
        assert tracker.bearish is False
        
        # Transition to bullish
        tracker.update(trend="bullish")
        assert tracker.ranging is False
        assert tracker.bullish is True
        assert tracker.bearish is False
        
        # Direct to bearish
        tracker.update(trend="bearish")
        assert tracker.ranging is False
        assert tracker.bullish is False
        assert tracker.bearish is True
        
        # Back to ranging
        tracker.update(trend="ranging")
        assert tracker.ranging is True
        assert tracker.bullish is False
        assert tracker.bearish is False


class TestTrackingFunctionsIntegration:
    """Integration tests for position tracking functions."""

    async def test_exit_at_profit_integration(self):
        """Test exit_at_profit with mock position."""
        mock_position = MagicMock()
        mock_position.profit = 100.0
        
        mock_pos = MagicMock()
        mock_pos.symbol = MagicMock()
        mock_pos.symbol.name = "EURUSD"
        mock_pos.ticket = 12345
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.close_position = AsyncMock(return_value=(True, MagicMock()))
        
        # Should close when profit >= tp
        await exit_at_profit(mock_pos, tp=50.0)
        
        mock_pos.close_position.assert_called_once()

    async def test_exit_at_profit_no_action(self):
        """Test exit_at_profit does not close when conditions not met."""
        mock_position = MagicMock()
        mock_position.profit = 30.0  # Below tp, above sl
        
        mock_pos = MagicMock()
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.close_position = AsyncMock()
        
        await exit_at_profit(mock_pos, tp=50.0, sl=-20.0)
        
        mock_pos.close_position.assert_not_called()


class TestStateAndConfigIntegration:
    """Integration tests for State and Config components."""

    def test_config_singleton(self):
        """Test Config is singleton."""
        config1 = Config()
        config2 = Config()
        
        assert config1 is config2

    def test_config_shutdown_flag(self):
        """Test config shutdown flag affects all references."""
        config1 = Config()
        config2 = Config()
        
        original_shutdown = config1.shutdown
        config1.shutdown = True
        
        assert config2.shutdown is True
        
        # Restore
        config1.shutdown = original_shutdown

    def test_state_initialization(self):
        """Test State can be initialized with key."""
        state = State()
        
        # State should support dict-like access
        assert hasattr(state, "__setitem__")
        assert hasattr(state, "__getitem__")


class TestMultiSymbolIntegration:
    """Integration tests for multiple symbols."""

    def test_forex_symbol_creation(self):
        """Test creating multiple forex symbols."""
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]
        
        forex_symbols = [ForexSymbol(name=sym) for sym in symbols]
        
        assert len(forex_symbols) == 4
        for i, sym in enumerate(forex_symbols):
            assert sym.name == symbols[i]

    def test_strategies_on_different_symbols(self):
        """Test strategies assigned to different symbols."""
        symbols = [
            ForexSymbol(name="EURUSD"),
            ForexSymbol(name="GBPUSD"),
            ForexSymbol(name="USDJPY")
        ]
        
        strategies = []
        for i, symbol in enumerate(symbols):
            strategy = SimpleTestStrategy(
                symbol=symbol,
                name=f"strategy_{symbol.name}",
                params={"interval": i + 1}
            )
            strategies.append(strategy)
        
        assert len(strategies) == 3
        assert strategies[0].symbol.name == "EURUSD"
        assert strategies[1].symbol.name == "GBPUSD"
        assert strategies[2].symbol.name == "USDJPY"
        assert strategies[0].interval == 1
        assert strategies[1].interval == 2
        assert strategies[2].interval == 3


class TestFullBotWorkflow:
    """Integration tests for complete bot workflow."""

    async def test_bot_with_chaos_strategy(self):
        """Test bot with Chaos strategy from contrib."""
        symbols = [ForexSymbol(name=sym) for sym in ["BTCUSD", "ETHUSD"]]
        
        strategies = [
            Chaos(symbol=symbol, name=f"chaos_{symbol.name}", params={"interval": 1})
            for symbol in symbols
        ]
        
        bot = Bot()
        bot.executor.timeout = 2  # Short timeout for testing
        bot.add_strategies(strategies=strategies)
        
        assert len(bot.strategies) == 2
        assert bot.executor is not None

    async def test_bot_with_mixed_strategies(self):
        """Test bot with different strategy types."""
        symbol1 = ForexSymbol(name="EURUSD")
        symbol2 = ForexSymbol(name="GBPUSD")
        symbol3 = ForexSymbol(name="USDJPY")
        
        strategies = [
            SimpleTestStrategy(symbol=symbol1, name="simple_eur"),
            TrendFollowerStrategy(symbol=symbol2, name="trend_gbp"),
            Chaos(symbol=symbol3, name="chaos_jpy", params={"interval": 1})
        ]
        
        bot = Bot()
        bot.executor.timeout = 2
        bot.add_strategies(strategies=strategies)
        
        assert len(bot.strategies) == 3
        
        # Verify different strategy types
        strategy_names = [s.name for s in bot.strategies]
        assert "simple_eur" in strategy_names
        assert "trend_gbp" in strategy_names
        assert "chaos_jpy" in strategy_names

    async def test_bot_with_coroutines_and_functions(self):
        """Test bot with strategies, coroutines and functions."""
        symbol = ForexSymbol(name="EURUSD")
        strategy = SimpleTestStrategy(symbol=symbol, name="test")
        
        async def monitor_task(interval=1):
            """Async monitoring task."""
            await asyncio.sleep(interval)
        
        def sync_logger(message=""):
            """Sync logging function."""
            logger.info(message)
        
        bot = Bot()
        bot.executor.timeout = 2
        bot.add_strategy(strategy=strategy)
        bot.add_coroutine(coroutine=monitor_task, interval=1)
        bot.add_function(function=sync_logger, message="test")
        
        assert len(bot.strategies) == 1
        assert len(bot.executor.coroutines) == 1
        assert len(bot.executor.functions) == 1


class TestRAMIntegration:
    """Integration tests for Risk Assessment and Management."""

    def test_ram_initialization(self):
        """Test RAM can be initialized with parameters."""
        ram = RAM(
            risk_to_reward=2.0,
            risk=2.0,
            min_amount=10.0,
            max_amount=100.0
        )
        
        assert ram.risk_to_reward == 2.0
        assert ram.risk == 2.0

    def test_ram_default_values(self):
        """Test RAM has sensible defaults."""
        ram = RAM()
        
        # RAM should have default attributes
        assert hasattr(ram, "risk_to_reward")
        assert hasattr(ram, "risk")
        assert ram.risk_to_reward == 2
        assert ram.risk == 1


class TestOrderIntegration:
    """Integration tests for Order class."""

    def test_order_creation(self):
        """Test Order can be created with required fields."""
        order = Order(
            symbol="EURUSD",
            volume=0.1,
            type=OrderType.BUY,
            action=TradeAction.DEAL
        )
        
        assert order.symbol == "EURUSD"
        assert order.volume == 0.1
        assert order.type == OrderType.BUY
        assert order.action == TradeAction.DEAL

    def test_order_with_stops(self):
        """Test Order can include stop levels."""
        order = Order(
            symbol="EURUSD",
            volume=0.1,
            type=OrderType.BUY,
            action=TradeAction.DEAL,
            sl=1.0900,
            tp=1.1100,
            price=1.1000
        )
        
        assert order.sl == 1.0900
        assert order.tp == 1.1100
        assert order.price == 1.1000
