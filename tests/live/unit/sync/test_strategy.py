"""Comprehensive tests for the sync Strategy module.

Tests cover (excluding backtest-related methods):
- Strategy initialization and attributes
- Strategy __repr__ method
- Strategy __getattr__ and __setattr__ for parameter access
- Strategy __enter__ and __exit__ context manager
- Strategy initialize method
- Strategy live_sleep static method
- Strategy sleep method in live mode
- Strategy delay method in live mode
- Strategy live_strategy method
- Strategy trade method (abstract)
- Integration tests
"""

import time
from datetime import time as dtime
from unittest.mock import MagicMock, patch
import pytest

from aiomql.lib.sync.strategy import Strategy
from aiomql.lib.sync.sessions import Session, Sessions
from aiomql.lib.sync.symbol import Symbol
from aiomql.core.config import Config
from aiomql.core.meta_trader import MetaTrader
from aiomql.core.exceptions import StopTrading


class ConcreteStrategy(Strategy):
    """Concrete implementation of Strategy for testing."""

    name = "TestStrategy"

    def trade(self):
        """Implement abstract trade method."""
        pass


class CountingStrategy(Strategy):
    """Strategy that counts trade calls for testing."""

    def __init__(self, *args, max_trades: int = 3, **kwargs):
        super().__init__(*args, **kwargs)
        self.trade_count = 0
        self.max_trades = max_trades

    def trade(self):
        self.trade_count += 1
        if self.trade_count >= self.max_trades:
            self.running = False


class ErrorStrategy(Strategy):
    """Strategy that raises an error in trade."""

    def trade(self):
        raise Exception("Test error in trade")


class StopTradingStrategy(Strategy):
    """Strategy that raises StopTrading exception."""

    def trade(self):
        raise StopTrading("Stop trading requested")


class TestStrategyInitialization:
    """Test Strategy class initialization."""

    @pytest.fixture
    def mock_symbol(self):
        """Create a mock Symbol for testing."""
        symbol = MagicMock(spec=Symbol)
        symbol.name = "EURUSD"
        return symbol

    @patch.object(Config, '__new__')
    def test_init_with_symbol_only(self, mock_config, mock_symbol):
        """Test Strategy init with only symbol."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)

        assert strategy.symbol == mock_symbol
        assert strategy.name == "ConcreteStrategy"  # Class name used
        assert strategy.running is True
        assert "symbol" in strategy.parameters
        assert strategy.parameters["symbol"] == "EURUSD"
        assert "name" in strategy.parameters

    @patch.object(Config, '__new__')
    def test_init_with_custom_name(self, mock_config, mock_symbol):
        """Test Strategy init with custom name."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol, name="MyCustomStrategy")

        assert strategy.name == "MyCustomStrategy"
        assert strategy.parameters["name"] == "MyCustomStrategy"

    @patch.object(Config, '__new__')
    def test_init_with_params(self, mock_config, mock_symbol):
        """Test Strategy init with custom parameters."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        params = {"risk_percent": 0.02, "take_profit_pips": 50}
        strategy = ConcreteStrategy(symbol=mock_symbol, params=params)

        assert strategy.parameters["risk_percent"] == 0.02
        assert strategy.parameters["take_profit_pips"] == 50

    @patch.object(Config, '__new__')
    def test_init_with_sessions(self, mock_config, mock_symbol):
        """Test Strategy init with custom sessions."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        sessions = Sessions(sessions=[Session(start=8, end=16)])
        strategy = ConcreteStrategy(symbol=mock_symbol, sessions=sessions)

        assert strategy.sessions == sessions

    @patch.object(Config, '__new__')
    def test_init_default_sessions(self, mock_config, mock_symbol):
        """Test Strategy init creates default sessions."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)

        assert strategy.sessions is not None
        assert isinstance(strategy.sessions, Sessions)

    @patch.object(Config, '__new__')
    def test_init_creates_config(self, mock_config, mock_symbol):
        """Test Strategy init creates config."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)

        assert strategy.config is not None

    @patch.object(Config, '__new__')
    def test_init_creates_meta_trader_in_live_mode(self, mock_config, mock_symbol):
        """Test Strategy init creates MetaTrader in live mode."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)

        assert isinstance(strategy.mt5, MetaTrader)

    @patch.object(Config, '__new__')
    def test_init_class_parameters_merged(self, mock_config, mock_symbol):
        """Test class-level parameters are merged with instance params."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        class StrategyWithDefaults(Strategy):
            parameters = {"default_sl": 50, "default_tp": 100}

            def trade(self):
                pass

        strategy = StrategyWithDefaults(
            symbol=mock_symbol, params={"custom_param": "value"}
        )

        assert strategy.parameters["default_sl"] == 50
        assert strategy.parameters["default_tp"] == 100
        assert strategy.parameters["custom_param"] == "value"


class TestStrategyRepr:
    """Test Strategy __repr__ method."""

    @pytest.fixture
    def mock_symbol(self):
        """Create a mock Symbol for testing."""
        symbol = MagicMock(spec=Symbol)
        symbol.name = "EURUSD"
        symbol.__repr__ = MagicMock(return_value="Symbol(EURUSD)")
        return symbol

    @patch.object(Config, '__new__')
    def test_repr(self, mock_config, mock_symbol):
        """Test __repr__ returns formatted string."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)
        result = repr(strategy)

        assert "ConcreteStrategy" in result
        assert "Symbol(EURUSD)" in result

    @patch.object(Config, '__new__')
    def test_repr_with_custom_name(self, mock_config, mock_symbol):
        """Test __repr__ with custom strategy name."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol, name="MyStrategy")
        result = repr(strategy)

        assert "MyStrategy" in result


class TestStrategyGetSetAttr:
    """Test Strategy __getattr__ and __setattr__ methods."""

    @pytest.fixture
    def mock_symbol(self):
        """Create a mock Symbol for testing."""
        symbol = MagicMock(spec=Symbol)
        symbol.name = "EURUSD"
        return symbol

    @patch.object(Config, '__new__')
    def test_getattr_returns_parameter(self, mock_config, mock_symbol):
        """Test __getattr__ returns parameter value."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(
            symbol=mock_symbol, params={"risk_percent": 0.02}
        )

        assert strategy.risk_percent == 0.02

    @patch.object(Config, '__new__')
    def test_getattr_raises_for_missing(self, mock_config, mock_symbol):
        """Test __getattr__ raises AttributeError for missing attribute."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)

        with pytest.raises(AttributeError) as exc_info:
            _ = strategy.nonexistent_attribute

        assert "nonexistent_attribute" in str(exc_info.value)

    @patch.object(Config, '__new__')
    def test_setattr_updates_parameter(self, mock_config, mock_symbol):
        """Test __setattr__ updates parameter value."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(
            symbol=mock_symbol, params={"risk_percent": 0.02}
        )
        strategy.risk_percent = 0.05

        assert strategy.parameters["risk_percent"] == 0.05

    @patch.object(Config, '__new__')
    def test_setattr_regular_attribute(self, mock_config, mock_symbol):
        """Test __setattr__ works for regular attributes."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)
        strategy.running = False

        assert strategy.running is False


class TestStrategyContextManager:
    """Test Strategy sync context manager."""

    @pytest.fixture
    def mock_symbol(self):
        """Create a mock Symbol for testing."""
        symbol = MagicMock(spec=Symbol)
        symbol.name = "EURUSD"
        return symbol

    @patch.object(Config, '__new__')
    def test_enter_checks_session(self, mock_config, mock_symbol):
        """Test __enter__ calls sessions.check."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)
        strategy.sessions = MagicMock()
        strategy.sessions.check = MagicMock()
        strategy.sessions.current_session = MagicMock()

        strategy.__enter__()

        strategy.sessions.check.assert_called_once()

    @patch.object(Config, '__new__')
    def test_enter_sets_running_true(self, mock_config, mock_symbol):
        """Test __enter__ sets running to True."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)
        strategy.running = False
        strategy.sessions = MagicMock()
        strategy.sessions.check = MagicMock()
        strategy.sessions.current_session = MagicMock()

        strategy.__enter__()

        assert strategy.running is True

    @patch.object(Config, '__new__')
    def test_enter_sets_current_session(self, mock_config, mock_symbol):
        """Test __enter__ sets current_session."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)
        mock_session = MagicMock()
        strategy.sessions = MagicMock()
        strategy.sessions.check = MagicMock()
        strategy.sessions.current_session = mock_session

        strategy.__enter__()

        assert strategy.current_session == mock_session

    @patch.object(Config, '__new__')
    def test_exit_closes_session(self, mock_config, mock_symbol):
        """Test __exit__ closes current session."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)
        mock_session = MagicMock()
        mock_session.close = MagicMock()
        strategy.current_session = mock_session

        strategy.__exit__(None, None, None)

        mock_session.close.assert_called_once()

    @patch.object(Config, '__new__')
    def test_exit_sets_running_false(self, mock_config, mock_symbol):
        """Test __exit__ sets running to False."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)
        strategy.running = True
        strategy.current_session = MagicMock()
        strategy.current_session.close = MagicMock()

        strategy.__exit__(None, None, None)

        assert strategy.running is False

    @patch.object(Config, '__new__')
    def test_exit_handles_no_session(self, mock_config, mock_symbol):
        """Test __exit__ handles no current session."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)
        strategy.current_session = None

        # Should not raise
        strategy.__exit__(None, None, None)
        assert strategy.running is False

    @patch.object(Config, '__new__')
    def test_exit_handles_exception(self, mock_config, mock_symbol):
        """Test __exit__ handles exception in close."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)
        mock_session = MagicMock()
        mock_session.close = MagicMock(side_effect=Exception("Close error"))
        strategy.current_session = mock_session

        # Should not raise, just log
        strategy.__exit__(None, None, None)


class TestStrategyInitialize:
    """Test Strategy initialize method."""

    @pytest.fixture
    def mock_symbol(self):
        """Create a mock Symbol for testing."""
        symbol = MagicMock(spec=Symbol)
        symbol.name = "EURUSD"
        symbol.initialize_sync = MagicMock(return_value=True)
        return symbol

    @patch.object(Config, '__new__')
    def test_initialize_calls_symbol_initialize_sync(self, mock_config, mock_symbol):
        """Test initialize calls symbol.initialize_sync."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)
        result = strategy.initialize()

        mock_symbol.initialize_sync.assert_called_once()
        assert result is True

    @patch.object(Config, '__new__')
    def test_initialize_returns_symbol_result(self, mock_config, mock_symbol):
        """Test initialize returns symbol.initialize_sync result."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        mock_symbol.initialize_sync = MagicMock(return_value=False)
        strategy = ConcreteStrategy(symbol=mock_symbol)
        result = strategy.initialize()

        assert result is False


class TestStrategyLiveSleep:
    """Test Strategy live_sleep static method."""

    def test_live_sleep_sleeps_remaining_time(self):
        """Test live_sleep calculates correct sleep time."""
        with patch('time.sleep') as mock_sleep:
            Strategy.live_sleep(secs=60)
            
            # Should have been called once
            mock_sleep.assert_called_once()
            # Sleep time should be between 0.1 and 60.1
            call_args = mock_sleep.call_args[0][0]
            assert 0.1 <= call_args <= 60.1

    def test_live_sleep_short_duration(self):
        """Test live_sleep with short duration."""
        with patch('time.sleep') as mock_sleep:
            Strategy.live_sleep(secs=1)
            
            mock_sleep.assert_called_once()
            call_args = mock_sleep.call_args[0][0]
            assert call_args >= 0.1


class TestStrategySleep:
    """Test Strategy sleep method."""

    @pytest.fixture
    def mock_symbol(self):
        """Create a mock Symbol for testing."""
        symbol = MagicMock(spec=Symbol)
        symbol.name = "EURUSD"
        return symbol

    @patch.object(Config, '__new__')
    def test_sleep_live_mode(self, mock_config, mock_symbol):
        """Test sleep calls live_sleep in live mode."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)

        with patch.object(Strategy, 'live_sleep') as mock_live_sleep:
            strategy.sleep(secs=60)
            mock_live_sleep.assert_called_once_with(secs=60)


class TestStrategyDelay:
    """Test Strategy delay method."""

    @pytest.fixture
    def mock_symbol(self):
        """Create a mock Symbol for testing."""
        symbol = MagicMock(spec=Symbol)
        symbol.name = "EURUSD"
        return symbol

    @patch.object(Config, '__new__')
    def test_delay_live_mode(self, mock_config, mock_symbol):
        """Test delay calls time.sleep in live mode."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)

        with patch('time.sleep') as mock_sleep:
            strategy.delay(secs=5)
            mock_sleep.assert_called_once_with(5)


class TestStrategyRunStrategy:
    """Test Strategy run_strategy method."""

    @pytest.fixture
    def mock_symbol(self):
        """Create a mock Symbol for testing."""
        symbol = MagicMock(spec=Symbol)
        symbol.name = "EURUSD"
        return symbol

    @patch.object(Config, '__new__')
    def test_run_strategy_live_mode(self, mock_config, mock_symbol):
        """Test run_strategy calls live_strategy in live mode."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)
        strategy.live_strategy = MagicMock()

        strategy.run_strategy()

        strategy.live_strategy.assert_called_once()


class TestStrategyLiveStrategy:
    """Test Strategy live_strategy method."""

    @pytest.fixture
    def mock_symbol(self):
        """Create a mock Symbol for testing."""
        symbol = MagicMock(spec=Symbol)
        symbol.name = "EURUSD"
        return symbol

    @patch.object(Config, '__new__')
    def test_live_strategy_runs_trade_loop(self, mock_config, mock_symbol):
        """Test live_strategy runs trade in a loop."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = CountingStrategy(symbol=mock_symbol, max_trades=3)
        strategy.sessions = MagicMock()
        strategy.sessions.check = MagicMock()
        strategy.sessions.current_session = MagicMock()
        strategy.sessions.current_session.close = MagicMock()

        strategy.live_strategy()

        assert strategy.trade_count == 3
        assert strategy.running is False

    @patch.object(Config, '__new__')
    def test_live_strategy_handles_stop_trading(self, mock_config, mock_symbol):
        """Test live_strategy handles StopTrading exception."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = StopTradingStrategy(symbol=mock_symbol)
        strategy.sessions = MagicMock()
        strategy.sessions.check = MagicMock()
        strategy.sessions.current_session = MagicMock()
        strategy.sessions.current_session.close = MagicMock()

        strategy.live_strategy()

        assert strategy.running is False

    @patch.object(Config, '__new__')
    def test_live_strategy_handles_general_exception(self, mock_config, mock_symbol):
        """Test live_strategy handles and logs general exceptions."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ErrorStrategy(symbol=mock_symbol)
        strategy.sessions = MagicMock()
        strategy.sessions.check = MagicMock()
        strategy.sessions.current_session = MagicMock()
        strategy.sessions.current_session.close = MagicMock()

        strategy.live_strategy()

        assert strategy.running is False


class TestStrategyTrade:
    """Test Strategy trade abstract method."""

    @pytest.fixture
    def mock_symbol(self):
        """Create a mock Symbol for testing."""
        symbol = MagicMock(spec=Symbol)
        symbol.name = "EURUSD"
        return symbol

    @patch.object(Config, '__new__')
    def test_trade_not_implemented(self, mock_config, mock_symbol):
        """Test trade raises NotImplementedError in base class."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        # Need to bypass ABC
        strategy = Strategy.__new__(Strategy)
        strategy.parameters = {}
        strategy.symbol = mock_symbol
        strategy.name = "TestStrategy"
        strategy.running = True
        strategy.config = config
        strategy.mt5 = MagicMock()

        with pytest.raises(NotImplementedError) as exc_info:
            strategy.trade()

        assert "Implement this method" in str(exc_info.value)


class TestStrategyTest:
    """Test Strategy test method."""

    @pytest.fixture
    def mock_symbol(self):
        """Create a mock Symbol for testing."""
        symbol = MagicMock(spec=Symbol)
        symbol.name = "EURUSD"
        return symbol

    @patch.object(Config, '__new__')
    def test_test_calls_trade(self, mock_config, mock_symbol):
        """Test test method calls trade."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)
        strategy.trade = MagicMock()

        strategy.test()

        strategy.trade.assert_called_once()


class TestIntegration:
    """Integration tests for Strategy."""

    @pytest.fixture
    def mock_symbol(self):
        """Create a mock Symbol for testing."""
        symbol = MagicMock(spec=Symbol)
        symbol.name = "EURUSD"
        symbol.initialize_sync = MagicMock(return_value=True)
        return symbol

    @patch.object(Config, '__new__')
    def test_strategy_with_complete_setup(self, mock_config, mock_symbol):
        """Test strategy with complete configuration."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        sessions = Sessions(
            sessions=[
                Session(start=8, end=12, name="Morning"),
                Session(start=13, end=17, name="Afternoon"),
            ]
        )
        params = {
            "risk_percent": 0.02,
            "max_trades": 5,
            "stop_loss_pips": 30,
            "take_profit_pips": 60,
        }

        strategy = ConcreteStrategy(
            symbol=mock_symbol,
            params=params,
            sessions=sessions,
            name="CompleteStrategy",
        )

        assert strategy.name == "CompleteStrategy"
        assert strategy.symbol == mock_symbol
        assert strategy.risk_percent == 0.02
        assert strategy.max_trades == 5
        assert len(strategy.sessions.sessions) == 2

    @patch.object(Config, '__new__')
    def test_strategy_full_lifecycle(self, mock_config, mock_symbol):
        """Test strategy through full lifecycle."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = CountingStrategy(symbol=mock_symbol, max_trades=2)
        strategy.sessions = MagicMock()
        strategy.sessions.check = MagicMock()
        mock_session = MagicMock()
        mock_session.close = MagicMock()
        strategy.sessions.current_session = mock_session

        # Enter context
        strategy.__enter__()
        assert strategy.running is True

        # Run trades
        while strategy.running:
            strategy.trade()

        # Exit context
        strategy.__exit__(None, None, None)
        assert strategy.running is False
        assert strategy.trade_count == 2

    @patch.object(Config, '__new__')
    def test_parameter_inheritance(self, mock_config, mock_symbol):
        """Test parameter inheritance from class to instance."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        class BaseStrategy(Strategy):
            parameters = {"base_param": "base_value"}

            def trade(self):
                pass

        class DerivedStrategy(BaseStrategy):
            parameters = {**BaseStrategy.parameters, "derived_param": "derived_value"}

        strategy = DerivedStrategy(
            symbol=mock_symbol, params={"instance_param": "instance_value"}
        )

        assert strategy.parameters["base_param"] == "base_value"
        assert strategy.parameters["derived_param"] == "derived_value"
        assert strategy.parameters["instance_param"] == "instance_value"

    @patch.object(Config, '__new__')
    def test_context_manager_with_statement(self, mock_config, mock_symbol):
        """Test strategy works with 'with' statement."""
        config = MagicMock()
        config.mode = "live"
        mock_config.return_value = config

        strategy = ConcreteStrategy(symbol=mock_symbol)
        strategy.sessions = MagicMock()
        strategy.sessions.check = MagicMock()
        mock_session = MagicMock()
        mock_session.close = MagicMock()
        strategy.sessions.current_session = mock_session

        with strategy as _:
            assert strategy.running is True
            assert strategy.current_session == mock_session

        assert strategy.running is False
        mock_session.close.assert_called_once()
