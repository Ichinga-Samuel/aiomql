"""Comprehensive tests for the synchronous Trader module.

Tests cover:
- Trader initialization (__init__)
- set_trade_stop_levels_pips (long/short orders)
- set_trade_stop_levels_points (long/short orders)
- create_order_with_stops
- create_order_with_sl
- create_order_with_points
- create_order_no_stops
- check_order
- send_order
- record_trade
- place_trade (abstract method enforcement)
"""

from unittest.mock import MagicMock, patch
import pytest

from aiomql.lib.sync.trader import Trader
from aiomql.lib.sync.order import Order
from aiomql.lib.ram import RAM
from aiomql.lib.sync.symbol import Symbol
from aiomql.core.models import OrderType, OrderSendResult, OrderCheckResult
from aiomql.core.config import Config
from aiomql.core.task_queue import QueueItem


# --- Concrete subclass for testing abstract Trader ---

class ConcreteTrader(Trader):
    """Non-abstract subclass of Trader for testing purposes."""

    def place_trade(self, *args, **kwargs):
        pass


# --- Fixtures ---

@pytest.fixture
def mock_symbol():
    """Create a mock Symbol with standard forex attributes."""
    symbol = MagicMock(spec=Symbol)
    symbol.name = "EURUSD"
    symbol.pip = 0.0001
    symbol.point = 0.00001
    symbol.digits = 5
    symbol.volume_min = 0.01
    symbol.compute_volume_sl = MagicMock(return_value=0.1)
    symbol.compute_volume_points = MagicMock(return_value=0.1)
    symbol.amount_in_quote_currency = MagicMock(return_value=100.0)
    symbol.info_tick = MagicMock()
    return symbol


@pytest.fixture
def mock_ram():
    """Create a mock RAM instance."""
    ram = MagicMock(spec=RAM)
    ram.risk_to_reward = 2.0
    ram.get_amount = MagicMock(return_value=100.0)
    return ram


@pytest.fixture
def mock_tick():
    """Create a mock price tick."""
    tick = MagicMock()
    tick.ask = 1.10000
    tick.bid = 1.09990
    return tick


@pytest.fixture
def trader(mock_symbol, mock_ram, mock_tick):
    """Create a ConcreteTrader for testing."""
    mock_symbol.info_tick.return_value = mock_tick
    t = ConcreteTrader(symbol=mock_symbol, ram=mock_ram)
    return t


# --- Tests ---

class TestTraderInit:
    """Test Trader initialization."""

    def test_init_sets_symbol(self, mock_symbol, mock_ram):
        """Test __init__ sets symbol."""
        t = ConcreteTrader(symbol=mock_symbol, ram=mock_ram)
        assert t.symbol is mock_symbol

    def test_init_sets_ram(self, mock_symbol, mock_ram):
        """Test __init__ sets provided RAM."""
        t = ConcreteTrader(symbol=mock_symbol, ram=mock_ram)
        assert t.ram is mock_ram

    def test_init_creates_default_ram(self, mock_symbol):
        """Test __init__ creates default RAM when none provided."""
        t = ConcreteTrader(symbol=mock_symbol)
        assert isinstance(t.ram, RAM)

    def test_init_creates_order(self, mock_symbol, mock_ram):
        """Test __init__ creates Order with symbol name."""
        t = ConcreteTrader(symbol=mock_symbol, ram=mock_ram)
        assert isinstance(t.order, Order)
        assert t.order.symbol == "EURUSD"

    def test_init_creates_config(self, mock_symbol, mock_ram):
        """Test __init__ creates Config instance."""
        t = ConcreteTrader(symbol=mock_symbol, ram=mock_ram)
        assert isinstance(t.config, Config)

    def test_init_creates_empty_parameters(self, mock_symbol, mock_ram):
        """Test __init__ creates empty parameters dict."""
        t = ConcreteTrader(symbol=mock_symbol, ram=mock_ram)
        assert t.parameters == {}


class TestSetTradeStopLevelsPips:
    """Test set_trade_stop_levels_pips method."""

    def test_long_order_sl_below_price(self, trader):
        """Test long order sets SL below price."""
        trader.order.price = 1.10000
        trader.order.type = MagicMock()
        trader.order.type.is_long = True
        trader.order.type.is_short = False

        trader.set_trade_stop_levels_pips(pips=50)

        assert trader.order.sl < trader.order.price

    def test_long_order_tp_above_price(self, trader):
        """Test long order sets TP above price."""
        trader.order.price = 1.10000
        trader.order.type = MagicMock()
        trader.order.type.is_long = True
        trader.order.type.is_short = False

        trader.set_trade_stop_levels_pips(pips=50)

        assert trader.order.tp > trader.order.price

    def test_short_order_sl_above_price(self, trader):
        """Test short order sets SL above price."""
        trader.order.price = 1.10000
        trader.order.type = MagicMock()
        trader.order.type.is_long = False
        trader.order.type.is_short = True

        trader.set_trade_stop_levels_pips(pips=50)

        assert trader.order.sl > trader.order.price

    def test_short_order_tp_below_price(self, trader):
        """Test short order sets TP below price."""
        trader.order.price = 1.10000
        trader.order.type = MagicMock()
        trader.order.type.is_long = False
        trader.order.type.is_short = True

        trader.set_trade_stop_levels_pips(pips=50)

        assert trader.order.tp < trader.order.price

    def test_custom_risk_to_reward(self, trader):
        """Test custom risk_to_reward overrides RAM default."""
        trader.order.price = 1.10000
        trader.order.type = MagicMock()
        trader.order.type.is_long = True
        trader.order.type.is_short = False

        trader.set_trade_stop_levels_pips(pips=50, risk_to_reward=3.0)

        sl_distance = abs(trader.order.price - trader.order.sl)
        tp_distance = abs(trader.order.tp - trader.order.price)
        assert round(tp_distance / sl_distance, 1) == 3.0

    def test_uses_ram_risk_to_reward_by_default(self, trader):
        """Test uses RAM risk_to_reward when not specified."""
        trader.order.price = 1.10000
        trader.order.type = MagicMock()
        trader.order.type.is_long = True
        trader.order.type.is_short = False
        trader.ram.risk_to_reward = 2.0

        trader.set_trade_stop_levels_pips(pips=50)

        sl_distance = abs(trader.order.price - trader.order.sl)
        tp_distance = abs(trader.order.tp - trader.order.price)
        assert round(tp_distance / sl_distance, 1) == 2.0

    def test_rounds_to_symbol_digits(self, trader):
        """Test SL and TP are rounded to symbol.digits."""
        trader.order.price = 1.10000
        trader.order.type = MagicMock()
        trader.order.type.is_long = True
        trader.order.type.is_short = False

        trader.set_trade_stop_levels_pips(pips=50)

        sl_str = f"{trader.order.sl:.10f}".rstrip("0")
        tp_str = f"{trader.order.tp:.10f}".rstrip("0")
        sl_decimals = len(sl_str.split(".")[1]) if "." in sl_str else 0
        tp_decimals = len(tp_str.split(".")[1]) if "." in tp_str else 0
        assert sl_decimals <= 5
        assert tp_decimals <= 5


class TestSetTradeStopLevelsPoints:
    """Test set_trade_stop_levels_points method."""

    def test_long_order_sl_below_price(self, trader):
        """Test long order sets SL below price."""
        trader.order.price = 1.10000
        trader.order.type = MagicMock()
        trader.order.type.is_long = True
        trader.order.type.is_short = False

        trader.set_trade_stop_levels_points(points=500)

        assert trader.order.sl < trader.order.price

    def test_long_order_tp_above_price(self, trader):
        """Test long order sets TP above price."""
        trader.order.price = 1.10000
        trader.order.type = MagicMock()
        trader.order.type.is_long = True
        trader.order.type.is_short = False

        trader.set_trade_stop_levels_points(points=500)

        assert trader.order.tp > trader.order.price

    def test_custom_risk_to_reward(self, trader):
        """Test custom risk_to_reward for points."""
        trader.order.price = 1.10000
        trader.order.type = MagicMock()
        trader.order.type.is_long = True
        trader.order.type.is_short = False

        trader.set_trade_stop_levels_points(points=500, risk_to_reward=4.0)

        sl_distance = abs(trader.order.price - trader.order.sl)
        tp_distance = abs(trader.order.tp - trader.order.price)
        assert round(tp_distance / sl_distance, 1) == 4.0


class TestCreateOrderWithStops:
    """Test create_order_with_stops method."""

    def test_sets_order_attributes(self, trader, mock_tick):
        """Test sets sl, tp, volume, price, and type on order."""
        order_type = MagicMock()
        order_type.is_long = True

        trader.order.set_attributes = MagicMock()

        trader.create_order_with_stops(
            order_type=order_type, sl=1.09500, tp=1.11000
        )

        trader.order.set_attributes.assert_called_once()
        call_kwargs = trader.order.set_attributes.call_args[1]
        assert call_kwargs["sl"] == 1.09500
        assert call_kwargs["tp"] == 1.11000
        assert call_kwargs["type"] is order_type

    def test_uses_ask_for_long(self, trader, mock_tick):
        """Test uses ask price for long orders."""
        order_type = MagicMock()
        order_type.is_long = True

        trader.order.set_attributes = MagicMock()

        trader.create_order_with_stops(
            order_type=order_type, sl=1.09500, tp=1.11000
        )

        call_kwargs = trader.order.set_attributes.call_args[1]
        assert call_kwargs["price"] == mock_tick.ask

    def test_uses_bid_for_short(self, trader, mock_tick):
        """Test uses bid price for short orders."""
        order_type = MagicMock()
        order_type.is_long = False

        trader.order.set_attributes = MagicMock()

        trader.create_order_with_stops(
            order_type=order_type, sl=1.10500, tp=1.09000
        )

        call_kwargs = trader.order.set_attributes.call_args[1]
        assert call_kwargs["price"] == mock_tick.bid

    def test_calculates_volume(self, trader):
        """Test computes volume using symbol.compute_volume_sl."""
        order_type = MagicMock()
        order_type.is_long = True

        trader.order.set_attributes = MagicMock()

        trader.create_order_with_stops(
            order_type=order_type, sl=1.09500, tp=1.11000
        )

        trader.symbol.compute_volume_sl.assert_called_once()

    def test_custom_amount_to_risk(self, trader):
        """Test custom amount_to_risk overrides RAM.get_amount."""
        order_type = MagicMock()
        order_type.is_long = True

        trader.order.set_attributes = MagicMock()

        trader.create_order_with_stops(
            order_type=order_type, sl=1.09500, tp=1.11000, amount_to_risk=500.0
        )

        trader.ram.get_amount.assert_not_called()

    def test_default_amount_from_ram(self, trader):
        """Test uses RAM.get_amount when amount_to_risk not specified."""
        order_type = MagicMock()
        order_type.is_long = True

        trader.order.set_attributes = MagicMock()

        trader.create_order_with_stops(
            order_type=order_type, sl=1.09500, tp=1.11000
        )

        trader.ram.get_amount.assert_called_once()

    def test_converts_amount_to_quote_currency(self, trader):
        """Test converts amount using symbol.amount_in_quote_currency."""
        order_type = MagicMock()
        order_type.is_long = True

        trader.order.set_attributes = MagicMock()

        trader.create_order_with_stops(
            order_type=order_type, sl=1.09500, tp=1.11000
        )

        trader.symbol.amount_in_quote_currency.assert_called_once()


class TestCreateOrderWithSl:
    """Test create_order_with_sl method."""

    def test_calculates_tp_from_sl(self, trader, mock_tick):
        """Test calculates TP based on SL distance and risk_to_reward."""
        order_type = OrderType.BUY

        trader.order.set_attributes = MagicMock()

        trader.create_order_with_sl(
            order_type=order_type, sl=1.09500
        )

        call_kwargs = trader.order.set_attributes.call_args[1]
        assert call_kwargs["tp"] > call_kwargs["price"]

    def test_buy_uses_ask_price(self, trader, mock_tick):
        """Test BUY order uses ask price."""
        trader.order.set_attributes = MagicMock()

        trader.create_order_with_sl(
            order_type=OrderType.BUY, sl=1.09500
        )

        call_kwargs = trader.order.set_attributes.call_args[1]
        assert call_kwargs["price"] == mock_tick.ask

    def test_sell_uses_bid_price(self, trader, mock_tick):
        """Test SELL order uses bid price."""
        trader.order.set_attributes = MagicMock()

        trader.create_order_with_sl(
            order_type=OrderType.SELL, sl=1.10500
        )

        call_kwargs = trader.order.set_attributes.call_args[1]
        assert call_kwargs["price"] == mock_tick.bid

    def test_custom_risk_to_reward(self, trader, mock_tick):
        """Test custom risk_to_reward affects TP calculation."""
        trader.order.set_attributes = MagicMock()

        trader.create_order_with_sl(
            order_type=OrderType.BUY, sl=1.09500, risk_to_reward=3.0
        )

        call_kwargs = trader.order.set_attributes.call_args[1]
        price = call_kwargs["price"]
        sl_dist = abs(price - 1.09500)
        tp_dist = abs(call_kwargs["tp"] - price)
        assert round(tp_dist / sl_dist, 1) == 3.0

    def test_sell_tp_below_price(self, trader, mock_tick):
        """Test SELL order sets TP below price."""
        trader.order.set_attributes = MagicMock()

        trader.create_order_with_sl(
            order_type=OrderType.SELL, sl=1.10500
        )

        call_kwargs = trader.order.set_attributes.call_args[1]
        assert call_kwargs["tp"] < call_kwargs["price"]

    def test_custom_amount_to_risk(self, trader):
        """Test custom amount_to_risk skips RAM.get_amount."""
        trader.order.set_attributes = MagicMock()

        trader.create_order_with_sl(
            order_type=OrderType.BUY, sl=1.09500, amount_to_risk=200.0
        )

        trader.ram.get_amount.assert_not_called()


class TestCreateOrderWithPoints:
    """Test create_order_with_points method."""

    def test_sets_order_type(self, trader):
        """Test sets order type on order."""
        trader.create_order_with_points(
            order_type=OrderType.BUY, points=500
        )

        assert trader.order.type == OrderType.BUY

    def test_sets_price_from_tick(self, trader, mock_tick):
        """Test sets price from tick."""
        trader.create_order_with_points(
            order_type=OrderType.BUY, points=500
        )

        assert trader.order.price == mock_tick.ask

    def test_sell_uses_bid(self, trader, mock_tick):
        """Test SELL uses bid price."""
        trader.create_order_with_points(
            order_type=OrderType.SELL, points=500
        )

        assert trader.order.price == mock_tick.bid

    def test_computes_volume_with_points(self, trader):
        """Test uses symbol.compute_volume_points."""
        trader.create_order_with_points(
            order_type=OrderType.BUY, points=500
        )

        trader.symbol.compute_volume_points.assert_called_once()

    def test_sets_stop_levels(self, trader):
        """Test calls set_trade_stop_levels_points."""
        with patch.object(trader, 'set_trade_stop_levels_points') as mock_set_stops:
            trader.create_order_with_points(
                order_type=OrderType.BUY, points=500
            )

            mock_set_stops.assert_called_once_with(points=500, risk_to_reward=None)

    def test_custom_risk_to_reward(self, trader):
        """Test passes custom risk_to_reward to set_trade_stop_levels_points."""
        with patch.object(trader, 'set_trade_stop_levels_points') as mock_set_stops:
            trader.create_order_with_points(
                order_type=OrderType.BUY, points=500, risk_to_reward=3.0
            )

            mock_set_stops.assert_called_once_with(points=500, risk_to_reward=3.0)


class TestCreateOrderNoStops:
    """Test create_order_no_stops method."""

    def test_sets_order_type(self, trader):
        """Test sets order type."""
        trader.create_order_no_stops(order_type=OrderType.BUY)

        assert trader.order.type == OrderType.BUY

    def test_uses_min_volume_default(self, trader):
        """Test uses symbol.volume_min when volume not specified."""
        trader.symbol.volume_min = 0.01

        trader.create_order_no_stops(order_type=OrderType.BUY)

        assert trader.order.volume == 0.01

    def test_custom_volume(self, trader):
        """Test uses custom volume when provided."""
        trader.create_order_no_stops(order_type=OrderType.BUY, volume=1.5)

        assert trader.order.volume == 1.5

    def test_buy_uses_ask_price(self, trader, mock_tick):
        """Test BUY uses ask price."""
        trader.create_order_no_stops(order_type=OrderType.BUY)

        assert trader.order.price == mock_tick.ask

    def test_sell_uses_bid_price(self, trader, mock_tick):
        """Test SELL uses bid price."""
        trader.create_order_no_stops(order_type=OrderType.SELL)

        assert trader.order.price == mock_tick.bid


class TestCheckOrder:
    """Test check_order method."""

    def test_check_order_success(self, trader):
        """Test check_order returns OrderCheckResult on success."""
        mock_result = MagicMock(spec=OrderCheckResult)
        mock_result.retcode = 0
        trader.order.check = MagicMock(return_value=mock_result)

        result = trader.check_order()

        assert result is mock_result

    def test_check_order_none_result(self, trader):
        """Test check_order handles None result."""
        trader.order.check = MagicMock(return_value=None)
        trader.order.mt5 = MagicMock()
        trader.order.mt5.error = "Connection failed"

        result = trader.check_order()

        assert result is None

    def test_check_order_nonzero_retcode(self, trader):
        """Test check_order logs warning for non-zero retcode."""
        mock_result = MagicMock(spec=OrderCheckResult)
        mock_result.retcode = 10015
        mock_result.comment = "Invalid price"
        trader.order.check = MagicMock(return_value=mock_result)

        result = trader.check_order()

        assert result is mock_result
        assert result.retcode != 0

    def test_check_order_calls_order_check(self, trader):
        """Test check_order delegates to order.check."""
        mock_result = MagicMock(spec=OrderCheckResult)
        mock_result.retcode = 0
        trader.order.check = MagicMock(return_value=mock_result)

        trader.check_order()

        trader.order.check.assert_called_once()


class TestSendOrder:
    """Test send_order method."""

    def test_send_order_success(self, trader):
        """Test send_order returns result on success (retcode 10009)."""
        mock_result = MagicMock(spec=OrderSendResult)
        mock_result.retcode = 10009
        trader.order.send = MagicMock(return_value=mock_result)

        result = trader.send_order()

        assert result is mock_result
        assert result.retcode == 10009

    def test_send_order_none_result(self, trader):
        """Test send_order handles None result."""
        trader.order.send = MagicMock(return_value=None)
        trader.order.mt5 = MagicMock()
        trader.order.mt5.error = "No connection"

        result = trader.send_order()

        assert result is None

    def test_send_order_failure_retcode(self, trader):
        """Test send_order returns result for non-10009 retcode."""
        mock_result = MagicMock(spec=OrderSendResult)
        mock_result.retcode = 10006
        mock_result.comment = "Requote"
        trader.order.send = MagicMock(return_value=mock_result)

        result = trader.send_order()

        assert result is mock_result
        assert result.retcode == 10006

    def test_send_order_calls_order_send(self, trader):
        """Test send_order delegates to order.send."""
        mock_result = MagicMock(spec=OrderSendResult)
        mock_result.retcode = 10009
        trader.order.send = MagicMock(return_value=mock_result)

        trader.send_order()

        trader.order.send.assert_called_once()


class TestRecordTrade:
    """Test record_trade method."""

    @pytest.fixture
    def successful_result(self):
        """Create a successful OrderSendResult."""
        result = MagicMock(spec=OrderSendResult)
        result.retcode = 10009
        result.order = 12345
        result.request = MagicMock()
        return result

    def test_record_trade_skips_when_disabled(self, trader, successful_result):
        """Test record_trade does nothing when record_trades is False."""
        trader.config.record_trades = False

        trader.record_trade(result=successful_result)

    def test_record_trade_skips_failed_orders(self, trader):
        """Test record_trade skips when retcode is not 10009."""
        trader.config.record_trades = True
        result = MagicMock(spec=OrderSendResult)
        result.retcode = 10006

        trader.record_trade(result=result)

    def test_record_trade_uses_task_queue(self, trader, successful_result):
        """Test record_trade adds to task queue by default."""
        trader.config.record_trades = True
        trader.config.task_queue = MagicMock()
        trader.config.task_queue.add = MagicMock()

        mock_order = MagicMock()
        mock_order.sl = 1.09500
        mock_order.tp = 1.11000
        mock_order.time_setup_msc = 1705312800000
        trader.order.get_history_order_by_ticket = MagicMock(return_value=mock_order)
        trader.order.calc_profit = MagicMock(return_value=50.0)

        with patch('aiomql.lib.sync.trader.Result') as MockResult:
            mock_res = MagicMock()
            mock_res.save_sync = MagicMock()
            MockResult.return_value = mock_res

            trader.record_trade(result=successful_result, parameters={"key": "value"})

            trader.config.task_queue.add.assert_called_once()

    def test_record_trade_direct_save(self, trader, successful_result):
        """Test record_trade saves directly when use_task_queue=False."""
        trader.config.record_trades = True

        mock_order = MagicMock()
        mock_order.sl = 1.09500
        mock_order.tp = 1.11000
        mock_order.time_setup_msc = 1705312800000
        trader.order.get_history_order_by_ticket = MagicMock(return_value=mock_order)
        trader.order.calc_profit = MagicMock(return_value=50.0)

        with patch('aiomql.lib.sync.trader.Result') as MockResult:
            mock_res = MagicMock()
            mock_res.save_sync = MagicMock()
            MockResult.return_value = mock_res

            trader.record_trade(
                result=successful_result,
                use_task_queue=False
            )

            mock_res.save_sync.assert_called_once()

    def test_record_trade_with_parameters(self, trader, successful_result):
        """Test record_trade passes parameters to Result."""
        trader.config.record_trades = True
        trader.config.task_queue = MagicMock()
        trader.config.task_queue.add = MagicMock()

        mock_order = MagicMock()
        mock_order.sl = 1.09500
        mock_order.tp = 1.11000
        mock_order.time_setup_msc = 1705312800000
        trader.order.get_history_order_by_ticket = MagicMock(return_value=mock_order)
        trader.order.calc_profit = MagicMock(return_value=50.0)

        params = {"strategy": "scalping", "timeframe": "M5"}

        with patch('aiomql.lib.sync.trader.Result') as MockResult:
            mock_res = MagicMock()
            mock_res.save_sync = MagicMock()
            MockResult.return_value = mock_res

            trader.record_trade(
                result=successful_result, parameters=params, name="TestStrategy"
            )

            call_kwargs = MockResult.call_args[1]
            assert call_kwargs["parameters"] == params
            assert call_kwargs["name"] == "TestStrategy"

    def test_record_trade_with_expected_profit(self, trader, successful_result):
        """Test record_trade uses provided expected_profit."""
        trader.config.record_trades = True
        trader.config.task_queue = MagicMock()
        trader.config.task_queue.add = MagicMock()

        mock_order = MagicMock()
        mock_order.sl = 1.09500
        mock_order.tp = 1.11000
        mock_order.time_setup_msc = 1705312800000
        trader.order.get_history_order_by_ticket = MagicMock(return_value=mock_order)

        with patch('aiomql.lib.sync.trader.Result') as MockResult:
            mock_res = MagicMock()
            mock_res.save_sync = MagicMock()
            MockResult.return_value = mock_res

            trader.record_trade(
                result=successful_result, expected_profit=75.0
            )

            call_kwargs = MockResult.call_args[1]
            assert call_kwargs["expected_profit"] == 75.0

    def test_record_trade_non_dict_parameters(self, trader, successful_result):
        """Test record_trade handles non-dict parameters."""
        trader.config.record_trades = True
        trader.config.task_queue = MagicMock()
        trader.config.task_queue.add = MagicMock()

        mock_order = MagicMock()
        mock_order.sl = 1.09500
        mock_order.tp = 1.11000
        mock_order.time_setup_msc = 1705312800000
        trader.order.get_history_order_by_ticket = MagicMock(return_value=mock_order)
        trader.order.calc_profit = MagicMock(return_value=10.0)

        with patch('aiomql.lib.sync.trader.Result') as MockResult:
            mock_res = MagicMock()
            mock_res.save_sync = MagicMock()
            MockResult.return_value = mock_res

            trader.record_trade(
                result=successful_result, parameters="not_a_dict"
            )

            call_kwargs = MockResult.call_args[1]
            assert call_kwargs["parameters"] == {}

    def test_record_trade_updates_sl_tp_from_history(self, trader, successful_result):
        """Test record_trade sets sl and tp on result.request from history order."""
        trader.config.record_trades = True
        trader.config.task_queue = MagicMock()
        trader.config.task_queue.add = MagicMock()

        mock_order = MagicMock()
        mock_order.sl = 1.08000
        mock_order.tp = 1.12000
        mock_order.time_setup_msc = 1705312800000
        trader.order.get_history_order_by_ticket = MagicMock(return_value=mock_order)
        trader.order.calc_profit = MagicMock(return_value=10.0)

        with patch('aiomql.lib.sync.trader.Result') as MockResult:
            mock_res = MagicMock()
            mock_res.save_sync = MagicMock()
            MockResult.return_value = mock_res

            trader.record_trade(result=successful_result)

            assert successful_result.request.sl == 1.08000
            assert successful_result.request.tp == 1.12000


class TestPlaceTrade:
    """Test abstract place_trade method."""

    def test_cannot_instantiate_trader_directly(self, mock_symbol, mock_ram):
        """Test Trader cannot be instantiated due to abstract method."""
        with pytest.raises(TypeError):
            Trader(symbol=mock_symbol, ram=mock_ram)

    def test_subclass_must_implement_place_trade(self):
        """Test subclass without place_trade raises TypeError."""
        with pytest.raises(TypeError):
            class IncompleteTrader(Trader):
                pass

            IncompleteTrader(symbol=MagicMock())

    def test_concrete_place_trade_callable(self, trader):
        """Test ConcreteTrader.place_trade is callable."""
        trader.place_trade()


class TestIntegration:
    """Integration tests for sync Trader."""

    def test_create_and_check_order(self, trader, mock_tick):
        """Test creating order then checking it."""
        order_type = MagicMock()
        order_type.is_long = True

        trader.order.set_attributes = MagicMock()

        trader.create_order_with_stops(
            order_type=order_type, sl=1.09500, tp=1.11000
        )

        mock_check_result = MagicMock(spec=OrderCheckResult)
        mock_check_result.retcode = 0
        trader.order.check = MagicMock(return_value=mock_check_result)

        check = trader.check_order()
        assert check.retcode == 0

    def test_create_and_send_order(self, trader, mock_tick):
        """Test creating order then sending it."""
        order_type = MagicMock()
        order_type.is_long = True

        trader.order.set_attributes = MagicMock()

        trader.create_order_with_stops(
            order_type=order_type, sl=1.09500, tp=1.11000
        )

        mock_send_result = MagicMock(spec=OrderSendResult)
        mock_send_result.retcode = 10009
        trader.order.send = MagicMock(return_value=mock_send_result)

        result = trader.send_order()
        assert result.retcode == 10009

    def test_full_trade_lifecycle(self, trader, mock_tick):
        """Test full lifecycle: create, check, send, record."""
        order_type = MagicMock()
        order_type.is_long = True

        trader.order.set_attributes = MagicMock()

        # Create
        trader.create_order_with_stops(
            order_type=order_type, sl=1.09500, tp=1.11000
        )

        # Check
        mock_check = MagicMock(spec=OrderCheckResult)
        mock_check.retcode = 0
        trader.order.check = MagicMock(return_value=mock_check)
        check = trader.check_order()
        assert check.retcode == 0

        # Send
        mock_result = MagicMock(spec=OrderSendResult)
        mock_result.retcode = 10009
        mock_result.order = 99999
        mock_result.request = MagicMock()
        trader.order.send = MagicMock(return_value=mock_result)
        result = trader.send_order()
        assert result.retcode == 10009

        # Record
        trader.config.record_trades = True
        trader.config.task_queue = MagicMock()
        trader.config.task_queue.add = MagicMock()

        mock_history_order = MagicMock()
        mock_history_order.sl = 1.09500
        mock_history_order.tp = 1.11000
        mock_history_order.time_setup_msc = 1705312800000
        trader.order.get_history_order_by_ticket = MagicMock(return_value=mock_history_order)
        trader.order.calc_profit = MagicMock(return_value=50.0)

        with patch('aiomql.lib.sync.trader.Result') as MockResult:
            mock_res = MagicMock()
            mock_res.save_sync = MagicMock()
            MockResult.return_value = mock_res

            trader.record_trade(result=result, name="TestStrategy")

            trader.config.task_queue.add.assert_called_once()
