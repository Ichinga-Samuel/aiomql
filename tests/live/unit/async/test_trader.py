"""Comprehensive tests for the Trader module.

Tests cover:
- Trader initialization with default and custom values
- set_trade_stop_levels_pips method
- set_trade_stop_levels_points method
- create_order_with_stops async method
- create_order_with_sl async method
- create_order_with_points async method
- create_order_no_stops async method
- check_order async method
- send_order async method
- record_trade async method
- Integration tests with various order types
- Edge cases and boundary conditions
"""

from math import floor
import pytest

from aiomql.lib.ram import RAM
from aiomql.lib.trader import Trader
from aiomql.contrib.traders import SimpleTrader
from aiomql.contrib.symbols import ForexSymbol
from aiomql.lib.symbol import Symbol
from aiomql.core.constants import OrderType
from aiomql.lib.account import Account
from aiomql.lib.order import Order
from aiomql.core.config import Config
from aiomql.core.models import OrderSendResult, OrderCheckResult


class TestTraderInitialization:
    """Test Trader class initialization."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.symbol = ForexSymbol(name="BTCUSD")
        cls.ram = RAM(fixed_amount=10)

    @pytest.fixture(scope="class", autouse=True)
    async def initialize(self):
        """Initialize symbol before tests."""
        await self.symbol.initialize()

    def test_init_with_symbol_only(self):
        """Test Trader can be initialized with just a symbol."""
        trader = SimpleTrader(symbol=self.symbol)
        assert trader.symbol == self.symbol
        assert isinstance(trader.ram, RAM)
        assert isinstance(trader.order, Order)

    def test_init_with_symbol_and_ram(self):
        """Test Trader initialized with symbol and custom RAM."""
        trader = SimpleTrader(symbol=self.symbol, ram=self.ram)
        assert trader.symbol == self.symbol
        assert trader.ram == self.ram

    def test_init_creates_order_with_symbol_name(self):
        """Test Trader creates order with correct symbol name."""
        trader = SimpleTrader(symbol=self.symbol)
        assert trader.order.symbol == self.symbol.name

    def test_init_has_config_attribute(self):
        """Test Trader has config attribute."""
        trader = SimpleTrader(symbol=self.symbol)
        assert hasattr(trader, 'config')
        assert isinstance(trader.config, Config)

    def test_init_has_parameters_attribute(self):
        """Test Trader has empty parameters dict."""
        trader = SimpleTrader(symbol=self.symbol)
        assert hasattr(trader, 'parameters')
        assert isinstance(trader.parameters, dict)
        assert trader.parameters == {}

    def test_init_with_default_ram_values(self):
        """Test Trader uses default RAM if not provided."""
        trader = SimpleTrader(symbol=self.symbol)
        assert trader.ram.risk_to_reward == 2
        assert trader.ram.risk == 1


class TestSetTradeStopLevelsPips:
    """Test set_trade_stop_levels_pips method."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.symbol = ForexSymbol(name="EURUSD")
        cls.ram = RAM(fixed_amount=10, risk_to_reward=2)
        cls.trader = SimpleTrader(symbol=cls.symbol, ram=cls.ram)

    @pytest.fixture(scope="class", autouse=True)
    async def initialize(self):
        """Initialize symbol."""
        await self.symbol.initialize()

    async def test_set_stop_levels_pips_buy_order(self):
        """Test setting stop levels for buy order using pips."""
        tick = await self.symbol.info_tick()
        self.trader.order.price = tick.ask
        self.trader.order.type = OrderType.BUY
        pips = 50

        self.trader.set_trade_stop_levels_pips(pips=pips)

        expected_sl = round(tick.ask - (pips * self.symbol.pip), self.symbol.digits)
        expected_tp = round(tick.ask + (pips * self.ram.risk_to_reward * self.symbol.pip), self.symbol.digits)
        assert self.trader.order.sl == expected_sl
        assert self.trader.order.tp == expected_tp

    async def test_set_stop_levels_pips_sell_order(self):
        """Test setting stop levels for sell order using pips."""
        tick = await self.symbol.info_tick()
        self.trader.order.price = tick.bid
        self.trader.order.type = OrderType.SELL
        pips = 50

        self.trader.set_trade_stop_levels_pips(pips=pips)

        expected_sl = round(tick.bid + (pips * self.symbol.pip), self.symbol.digits)
        expected_tp = round(tick.bid - (pips * self.ram.risk_to_reward * self.symbol.pip), self.symbol.digits)
        assert self.trader.order.sl == expected_sl
        assert self.trader.order.tp == expected_tp

    async def test_set_stop_levels_pips_custom_risk_to_reward(self):
        """Test setting stop levels with custom risk to reward ratio."""
        tick = await self.symbol.info_tick()
        self.trader.order.price = tick.ask
        self.trader.order.type = OrderType.BUY
        pips = 30
        custom_rr = 3

        self.trader.set_trade_stop_levels_pips(pips=pips, risk_to_reward=custom_rr)

        expected_sl = round(tick.ask - (pips * self.symbol.pip), self.symbol.digits)
        expected_tp = round(tick.ask + (pips * custom_rr * self.symbol.pip), self.symbol.digits)
        assert self.trader.order.sl == expected_sl
        assert self.trader.order.tp == expected_tp


class TestSetTradeStopLevelsPoints:
    """Test set_trade_stop_levels_points method."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.symbol = ForexSymbol(name="EURUSD")
        cls.ram = RAM(fixed_amount=10, risk_to_reward=2)
        cls.trader = SimpleTrader(symbol=cls.symbol, ram=cls.ram)

    @pytest.fixture(scope="class", autouse=True)
    async def initialize(self):
        """Initialize symbol."""
        await self.symbol.initialize()

    async def test_set_stop_levels_points_buy_order(self):
        """Test setting stop levels for buy order using points."""
        tick = await self.symbol.info_tick()
        self.trader.order.price = tick.ask
        self.trader.order.type = OrderType.BUY
        points = 500

        self.trader.set_trade_stop_levels_points(points=points)

        expected_sl = round(tick.ask - (points * self.symbol.point), self.symbol.digits)
        expected_tp = round(tick.ask + (points * self.ram.risk_to_reward * self.symbol.point), self.symbol.digits)
        assert self.trader.order.sl == expected_sl
        assert self.trader.order.tp == expected_tp

    async def test_set_stop_levels_points_custom_risk_to_reward(self):
        """Test setting stop levels with custom risk to reward."""
        tick = await self.symbol.info_tick()
        self.trader.order.price = tick.ask
        self.trader.order.type = OrderType.BUY
        points = 500
        custom_rr = 4

        self.trader.set_trade_stop_levels_points(points=points, risk_to_reward=custom_rr)

        expected_sl = round(tick.ask - (points * self.symbol.point), self.symbol.digits)
        expected_tp = round(tick.ask + (points * custom_rr * self.symbol.point), self.symbol.digits)
        assert self.trader.order.sl == expected_sl
        assert self.trader.order.tp == expected_tp


class TestCreateOrderNoStops:
    """Test create_order_no_stops async method."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.symbol = ForexSymbol(name="BTCUSD")
        cls.ram = RAM(fixed_amount=10)
        cls.trader = SimpleTrader(symbol=cls.symbol, ram=cls.ram)

    @pytest.fixture(scope="class", autouse=True)
    async def initialize(self):
        """Initialize symbol."""
        await self.symbol.initialize()

    async def test_create_order_no_stops_buy(self):
        """Test creating buy order without stops."""
        await self.trader.create_order_no_stops(order_type=OrderType.BUY)

        assert self.trader.order.type == OrderType.BUY
        assert self.trader.order.volume == self.symbol.volume_min
        assert self.trader.order.price is not None

    async def test_create_order_no_stops_sell(self):
        """Test creating sell order without stops."""
        await self.trader.create_order_no_stops(order_type=OrderType.SELL)

        assert self.trader.order.type == OrderType.SELL
        assert self.trader.order.volume == self.symbol.volume_min
        assert self.trader.order.price is not None

    async def test_create_order_no_stops_with_custom_volume(self):
        """Test creating order with custom volume."""
        custom_volume = self.symbol.volume_min * 2
        await self.trader.create_order_no_stops(order_type=OrderType.BUY, volume=custom_volume)

        assert self.trader.order.volume == custom_volume

    async def test_create_order_no_stops_uses_correct_price(self):
        """Test order uses ask for buy and bid for sell."""
        tick = await self.symbol.info_tick()

        await self.trader.create_order_no_stops(order_type=OrderType.BUY)
        # Price should be close to ask (may differ slightly due to timing)
        assert abs(self.trader.order.price - tick.ask) < tick.ask * 0.01

    async def test_create_order_no_stops_send_success(self):
        """Test sending order without stops succeeds."""
        await self.trader.create_order_no_stops(order_type=OrderType.BUY)
        result = await self.trader.order.send()

        assert result is not None
        assert result.retcode == 10009


class TestCreateOrderWithSl:
    """Test create_order_with_sl async method."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.symbol = ForexSymbol(name="BTCUSD")
        cls.ram = RAM(fixed_amount=10, risk_to_reward=2)
        cls.trader = SimpleTrader(symbol=cls.symbol, ram=cls.ram)
        cls.account = Account()

    @pytest.fixture(scope="class", autouse=True)
    async def initialize(self):
        """Initialize symbol and account."""
        await self.symbol.initialize()
        await self.account.refresh()

    async def test_create_order_with_sl_sell(self):
        """Test creating sell order with stop loss."""
        dsl = (self.symbol.trade_stops_level * 2 + self.symbol.spread) * self.symbol.point
        tick = await self.symbol.info_tick()
        sl = tick.bid + dsl

        await self.trader.create_order_with_sl(order_type=OrderType.SELL, sl=sl)

        assert self.trader.order.type == OrderType.SELL
        assert self.trader.order.sl == sl
        assert self.trader.order.tp is not None
        assert self.trader.order.volume > 0

    async def test_create_order_with_sl_buy(self):
        """Test creating buy order with stop loss."""
        dsl = (self.symbol.trade_stops_level * 2 + self.symbol.spread) * self.symbol.point
        tick = await self.symbol.info_tick()
        sl = tick.ask - dsl

        await self.trader.create_order_with_sl(order_type=OrderType.BUY, sl=sl)

        assert self.trader.order.type == OrderType.BUY
        assert self.trader.order.sl == sl
        assert self.trader.order.tp is not None

    async def test_create_order_with_sl_respects_risk_to_reward(self):
        """Test TP is set according to risk to reward ratio."""
        dsl = (self.symbol.trade_stops_level * 2 + self.symbol.spread) * self.symbol.point
        tick = await self.symbol.info_tick()
        sl = tick.bid + dsl

        await self.trader.create_order_with_sl(order_type=OrderType.SELL, sl=sl)

        # TP should be approximately at dsl * risk_to_reward distance from price
        expected_dtp = dsl * self.ram.risk_to_reward
        actual_dtp = abs(self.trader.order.price - self.trader.order.tp)
        assert abs(actual_dtp - expected_dtp) < self.symbol.point * 10

    async def test_create_order_with_sl_custom_amount_to_risk(self):
        """Test creating order with custom amount to risk."""
        dsl = (self.symbol.trade_stops_level * 2 + self.symbol.spread) * self.symbol.point
        tick = await self.symbol.info_tick()
        sl = tick.bid + dsl
        custom_amount = 20

        await self.trader.create_order_with_sl(order_type=OrderType.SELL, sl=sl, amount_to_risk=custom_amount)

        assert self.trader.order.volume > 0

    async def test_create_order_with_sl_send_success(self):
        """Test order with SL can be sent successfully."""
        dsl = (self.symbol.trade_stops_level * 2 + self.symbol.spread) * self.symbol.point
        tick = await self.symbol.info_tick()
        sl = tick.bid + dsl

        await self.trader.create_order_with_sl(order_type=OrderType.SELL, sl=sl)
        result = await self.trader.order.send()

        assert result is not None
        assert result.retcode == 10009

    async def test_create_order_with_sl_profit_loss_ratio(self):
        """Test profit and loss are in correct ratio."""
        dsl = (self.symbol.trade_stops_level * 2 + self.symbol.spread) * self.symbol.point
        tick = await self.symbol.info_tick()
        sl = tick.bid + dsl

        await self.trader.create_order_with_sl(order_type=OrderType.SELL, sl=sl)
        await self.trader.order.send()

        profit = floor(await self.trader.order.calc_profit())
        loss = -floor(abs(await self.trader.order.calc_loss()))

        assert profit == -loss * self.ram.risk_to_reward
        assert abs(profit - self.ram.fixed_amount * self.ram.risk_to_reward) <= 2.5
        assert abs(abs(loss) - abs(-self.ram.fixed_amount)) <= 2


class TestCreateOrderWithStops:
    """Test create_order_with_stops async method."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.symbol = ForexSymbol(name="BTCUSD")
        cls.ram = RAM(fixed_amount=10, risk_to_reward=2)
        cls.trader = SimpleTrader(symbol=cls.symbol, ram=cls.ram)
        cls.account = Account()

    @pytest.fixture(scope="class", autouse=True)
    async def initialize(self):
        """Initialize symbol and account."""
        await self.symbol.initialize()
        await self.account.refresh()

    async def test_create_order_with_stops_buy(self):
        """Test creating buy order with SL and TP."""
        dsl = (self.symbol.trade_stops_level * 2 + self.symbol.spread) * self.symbol.point
        dtp = dsl * self.ram.risk_to_reward
        tick = await self.symbol.info_tick()
        sl = tick.ask - dsl
        tp = tick.ask + dtp

        await self.trader.create_order_with_stops(order_type=OrderType.BUY, sl=sl, tp=tp)

        assert self.trader.order.type == OrderType.BUY
        assert self.trader.order.sl == sl
        assert self.trader.order.tp == tp
        assert self.trader.order.volume > 0

    async def test_create_order_with_stops_sell(self):
        """Test creating sell order with SL and TP."""
        dsl = (self.symbol.trade_stops_level * 2 + self.symbol.spread) * self.symbol.point
        dtp = dsl * self.ram.risk_to_reward
        tick = await self.symbol.info_tick()
        sl = tick.bid + dsl
        tp = tick.bid - dtp

        await self.trader.create_order_with_stops(order_type=OrderType.SELL, sl=sl, tp=tp)

        assert self.trader.order.type == OrderType.SELL
        assert self.trader.order.sl == sl
        assert self.trader.order.tp == tp

    async def test_create_order_with_stops_send_success(self):
        """Test order with stops can be sent successfully."""
        dsl = (self.symbol.trade_stops_level * 2 + self.symbol.spread) * self.symbol.point
        dtp = dsl * self.ram.risk_to_reward
        tick = await self.symbol.info_tick()
        sl = tick.ask - dsl
        tp = tick.ask + dtp

        await self.trader.create_order_with_stops(order_type=OrderType.BUY, sl=sl, tp=tp)
        result = await self.trader.order.send()

        assert result is not None
        assert result.retcode == 10009

    async def test_create_order_with_stops_profit_loss_calculation(self):
        """Test profit/loss calculations are correct."""
        dsl = (self.symbol.trade_stops_level * 2 + self.symbol.spread) * self.symbol.point
        dtp = dsl * self.ram.risk_to_reward
        tick = await self.symbol.info_tick()
        sl = tick.ask - dsl
        tp = tick.ask + dtp

        await self.trader.create_order_with_stops(order_type=OrderType.BUY, sl=sl, tp=tp)
        result = await self.trader.order.send()

        assert result is not None
        assert result.retcode == 10009

        profit = round(await self.trader.order.calc_profit(), self.account.currency_digits)
        loss = -round(abs(await self.trader.order.calc_loss()), self.account.currency_digits)

        assert abs(profit) - abs(-loss * self.ram.risk_to_reward) <= 2.5
        assert abs(profit - (self.ram.fixed_amount * self.ram.risk_to_reward)) <= 2.5
        assert abs(abs(loss) - self.ram.fixed_amount) <= 2.5

    async def test_create_order_with_stops_custom_amount(self):
        """Test creating order with custom amount to risk."""
        dsl = (self.symbol.trade_stops_level * 2 + self.symbol.spread) * self.symbol.point
        dtp = dsl * 2
        tick = await self.symbol.info_tick()
        sl = tick.ask - dsl
        tp = tick.ask + dtp
        custom_amount = 25

        await self.trader.create_order_with_stops(
            order_type=OrderType.BUY, sl=sl, tp=tp, amount_to_risk=custom_amount
        )

        assert self.trader.order.volume > 0


class TestCreateOrderWithPoints:
    """Test create_order_with_points async method."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.symbol = ForexSymbol(name="BTCUSD")
        cls.ram = RAM(fixed_amount=10, risk_to_reward=2)
        cls.trader = SimpleTrader(symbol=cls.symbol, ram=cls.ram)
        cls.account = Account()

    @pytest.fixture(scope="class", autouse=True)
    async def initialize(self):
        """Initialize symbol."""
        await self.symbol.initialize()
        await self.account.refresh()

    async def test_create_order_with_points_buy(self):
        """Test creating buy order with points."""
        points = self.symbol.trade_stops_level * 2 + self.symbol.spread

        await self.trader.create_order_with_points(order_type=OrderType.BUY, points=points)

        assert self.trader.order.type == OrderType.BUY
        assert self.trader.order.volume > 0
        assert self.trader.order.sl is not None
        assert self.trader.order.tp is not None

    async def test_create_order_with_points_sell(self):
        """Test creating sell order with points."""
        points = self.symbol.trade_stops_level * 2 + self.symbol.spread

        await self.trader.create_order_with_points(order_type=OrderType.SELL, points=points)

        assert self.trader.order.type == OrderType.SELL
        assert self.trader.order.volume > 0

    async def test_create_order_with_points_send_success(self):
        """Test order with points can be sent successfully."""
        points = self.symbol.trade_stops_level * 2 + self.symbol.spread

        await self.trader.create_order_with_points(order_type=OrderType.BUY, points=points)
        result = await self.trader.order.send()

        assert result is not None
        assert result.retcode == 10009

    async def test_create_order_with_points_profit_loss_ratio(self):
        """Test profit and loss are in correct ratio."""
        points = self.symbol.trade_stops_level * 2 + self.symbol.spread

        await self.trader.create_order_with_points(order_type=OrderType.BUY, points=points)
        res = await self.trader.order.send()
        profit = floor(await self.trader.order.mt5.order_calc_profit(res.request.type, res.request.symbol, res.request.volume,
         res.request.price, res.request.tp))
        loss = -floor(abs(await self.trader.order.mt5.order_calc_profit(res.request.type, res.request.symbol, res.request.volume,
         res.request.price, res.request.sl)))
        
        assert abs(profit - self.ram.fixed_amount * self.ram.risk_to_reward) <= 2.5
        assert abs(abs(loss) - abs(-self.ram.fixed_amount)) <= 2

    async def test_create_order_with_points_custom_risk_to_reward(self):
        """Test order with custom risk to reward."""
        points = self.symbol.trade_stops_level * 2 + self.symbol.spread
        custom_rr = 3

        await self.trader.create_order_with_points(
            order_type=OrderType.BUY, points=points, risk_to_reward=custom_rr
        )

        # TP should be at points * custom_rr distance from price
        expected_tp_distance = points * custom_rr * self.symbol.point
        actual_tp_distance = abs(self.trader.order.tp - self.trader.order.price)
        assert abs(actual_tp_distance - expected_tp_distance) < self.symbol.point * 10


class TestCheckOrder:
    """Test check_order async method."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.symbol = ForexSymbol(name="BTCUSD")
        cls.ram = RAM(fixed_amount=10)
        cls.trader = SimpleTrader(symbol=cls.symbol, ram=cls.ram)

    @pytest.fixture(scope="class", autouse=True)
    async def initialize(self):
        """Initialize symbol."""
        await self.symbol.initialize()

    async def test_check_order_returns_order_check_result(self):
        """Test check_order returns OrderCheckResult."""
        await self.trader.create_order_no_stops(order_type=OrderType.BUY)
        result = await self.trader.check_order()

        assert result is None or isinstance(result, OrderCheckResult)

    async def test_check_order_success(self):
        """Test check_order succeeds for valid order."""
        await self.trader.create_order_no_stops(order_type=OrderType.BUY)
        result = await self.trader.check_order()

        assert result is not None
        assert result.retcode == 0

    async def test_check_order_has_margin_info(self):
        """Test check result contains margin information."""
        await self.trader.create_order_no_stops(order_type=OrderType.BUY)
        result = await self.trader.check_order()

        assert result is not None
        assert hasattr(result, 'margin')

    async def test_check_order_sell(self):
        """Test check_order works for sell orders."""
        await self.trader.create_order_no_stops(order_type=OrderType.SELL)
        result = await self.trader.check_order()

        assert result is not None
        assert result.retcode == 0


class TestSendOrder:
    """Test send_order async method."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.symbol = ForexSymbol(name="BTCUSD")
        cls.ram = RAM(fixed_amount=10)
        cls.trader = SimpleTrader(symbol=cls.symbol, ram=cls.ram)

    @pytest.fixture(scope="class", autouse=True)
    async def initialize(self):
        """Initialize symbol."""
        await self.symbol.initialize()

    async def test_send_order_returns_order_send_result(self):
        """Test send_order returns OrderSendResult."""
        await self.trader.create_order_no_stops(order_type=OrderType.BUY)
        result = await self.trader.send_order()

        assert result is None or isinstance(result, OrderSendResult)

    async def test_send_order_success(self):
        """Test send_order succeeds for valid order."""
        await self.trader.create_order_no_stops(order_type=OrderType.BUY)
        result = await self.trader.send_order()

        assert result is not None
        assert result.retcode == 10009

    async def test_send_order_has_deal_ticket(self):
        """Test send result contains deal ticket."""
        await self.trader.create_order_no_stops(order_type=OrderType.BUY)
        result = await self.trader.send_order()

        assert result is not None
        assert hasattr(result, 'deal')
        assert result.deal > 0

    async def test_send_order_has_order_ticket(self):
        """Test send result contains order ticket."""
        await self.trader.create_order_no_stops(order_type=OrderType.BUY)
        result = await self.trader.send_order()

        assert result is not None
        assert hasattr(result, 'order')
        assert result.order > 0


class TestRecordTrade:
    """Test record_trade async method."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.symbol = ForexSymbol(name="BTCUSD")
        cls.ram = RAM(fixed_amount=10)
        cls.trader = SimpleTrader(symbol=cls.symbol, ram=cls.ram)

    @pytest.fixture(scope="class", autouse=True)
    async def initialize(self):
        """Initialize symbol."""
        await self.symbol.initialize()

    async def test_record_trade_with_successful_order(self):
        """Test recording a successful trade."""
        await self.trader.create_order_no_stops(order_type=OrderType.BUY)
        result = await self.trader.send_order()

        # Should not raise an error
        await self.trader.record_trade(result=result, parameters={"test": "value"}, name="TestStrategy", use_task_queue=False)

    async def test_record_trade_with_parameters(self):
        """Test recording trade with custom parameters."""
        await self.trader.create_order_no_stops(order_type=OrderType.BUY)
        result = await self.trader.send_order()

        params = {"strategy": "test", "risk": 1, "timeframe": "H1"}
        await self.trader.record_trade(result=result, parameters=params, name="MyStrategy", use_task_queue=False)

    async def test_record_trade_without_parameters(self):
        """Test recording trade without parameters."""
        await self.trader.create_order_no_stops(order_type=OrderType.BUY)
        result = await self.trader.send_order()

        # Should not raise an error
        await self.trader.record_trade(result=result, name="SimpleStrategy", use_task_queue=False)


class TestTraderWithDifferentSymbols:
    """Test Trader with different symbols."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.btc_usd = ForexSymbol(name="BTCUSD")
        cls.eur_jpy = ForexSymbol(name="EURJPY")
        cls.ram = RAM(fixed_amount=10)

    @pytest.fixture(scope="class", autouse=True)
    async def initialize(self):
        """Initialize symbols."""
        await self.btc_usd.initialize()
        await self.eur_jpy.initialize()

    async def test_trader_btc_usd(self):
        """Test trader with BTCUSD symbol."""
        trader = SimpleTrader(symbol=self.btc_usd, ram=self.ram)
        await trader.create_order_no_stops(order_type=OrderType.BUY)
        result = await trader.send_order()

        assert result is not None
        assert result.retcode == 10009

    async def test_trader_eur_jpy(self):
        """Test trader with EURJPY symbol."""
        trader = SimpleTrader(symbol=self.eur_jpy, ram=self.ram)
        await trader.create_order_no_stops(order_type=OrderType.SELL)
        result = await trader.send_order()

        assert result is not None
        assert result.retcode == 10009


class TestTraderIntegration:
    """Integration tests for Trader."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.symbol = ForexSymbol(name="BTCUSD")
        cls.ram = RAM(fixed_amount=10, risk_to_reward=2)
        cls.trader = SimpleTrader(symbol=cls.symbol, ram=cls.ram)
        cls.account = Account()

    @pytest.fixture(scope="class", autouse=True)
    async def initialize(self):
        """Initialize symbol and account."""
        await self.symbol.initialize()
        await self.account.refresh()

    async def test_full_trade_flow_buy(self):
        """Test complete trade flow for buy order."""
        # Create order
        points = self.symbol.trade_stops_level * 2 + self.symbol.spread
        await self.trader.create_order_with_points(order_type=OrderType.BUY, points=points)

        # Check order
        check_result = await self.trader.check_order()
        assert check_result is not None
        assert check_result.retcode == 0

        # Send order
        send_result = await self.trader.send_order()
        assert send_result is not None
        assert send_result.retcode == 10009

        # Record trade
        await self.trader.record_trade(result=send_result, parameters={"test": True}, name="IntegrationTest", use_task_queue=False)

    async def test_full_trade_flow_sell(self):
        """Test complete trade flow for sell order."""
        # Create order
        dsl = (self.symbol.trade_stops_level * 2 + self.symbol.spread) * self.symbol.point
        tick = await self.symbol.info_tick()
        sl = tick.bid + dsl

        await self.trader.create_order_with_sl(order_type=OrderType.SELL, sl=sl)

        # Check order
        check_result = await self.trader.check_order()
        assert check_result is not None
        assert check_result.retcode == 0

        # Send order
        send_result = await self.trader.send_order()
        assert send_result is not None
        assert send_result.retcode == 10009

    async def test_multiple_orders_same_trader(self):
        """Test creating multiple orders with same trader."""
        # First order
        await self.trader.create_order_no_stops(order_type=OrderType.BUY)
        result1 = await self.trader.send_order()
        assert result1 is not None
        assert result1.retcode == 10009

        # Second order (different type)
        await self.trader.create_order_no_stops(order_type=OrderType.SELL)
        result2 = await self.trader.send_order()
        assert result2 is not None
        assert result2.retcode == 10009


class TestTraderEdgeCases:
    """Test edge cases and boundary conditions."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.symbol = ForexSymbol(name="BTCUSD")

    @pytest.fixture(scope="class", autouse=True)
    async def initialize(self):
        """Initialize symbol."""
        await self.symbol.initialize()

    def test_trader_with_zero_fixed_amount(self):
        """Test trader with zero fixed amount RAM."""
        ram = RAM(fixed_amount=0)
        trader = SimpleTrader(symbol=self.symbol, ram=ram)
        assert trader.ram.fixed_amount == 0

    def test_trader_with_high_risk_to_reward(self):
        """Test trader with high risk to reward ratio."""
        ram = RAM(fixed_amount=10, risk_to_reward=10)
        trader = SimpleTrader(symbol=self.symbol, ram=ram)
        assert trader.ram.risk_to_reward == 10

    def test_trader_with_low_risk_to_reward(self):
        """Test trader with low risk to reward ratio."""
        ram = RAM(fixed_amount=10, risk_to_reward=0.5)
        trader = SimpleTrader(symbol=self.symbol, ram=ram)
        assert trader.ram.risk_to_reward == 0.5

    async def test_trader_order_modification_after_creation(self):
        """Test modifying order attributes after creation."""
        ram = RAM(fixed_amount=10)
        trader = SimpleTrader(symbol=self.symbol, ram=ram)
        await trader.create_order_no_stops(order_type=OrderType.BUY)

        original_volume = trader.order.volume
        trader.order.volume = original_volume * 2
        assert trader.order.volume == original_volume * 2

    def test_trader_parameters_modification(self):
        """Test modifying trader parameters."""
        ram = RAM(fixed_amount=10)
        trader = SimpleTrader(symbol=self.symbol, ram=ram)

        trader.parameters["custom_param"] = "value"
        trader.parameters["risk"] = 5

        assert trader.parameters["custom_param"] == "value"
        assert trader.parameters["risk"] == 5

    async def test_trader_with_minimum_volume(self):
        """Test creating order with minimum volume."""
        ram = RAM(fixed_amount=1)  # Very small amount
        trader = SimpleTrader(symbol=self.symbol, ram=ram)
        await trader.create_order_no_stops(order_type=OrderType.BUY)

        assert trader.order.volume >= self.symbol.volume_min


class TestTraderRAMIntegration:
    """Test Trader integration with RAM."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.symbol = ForexSymbol(name="BTCUSD")

    @pytest.fixture(scope="class", autouse=True)
    async def initialize(self):
        """Initialize symbol."""
        await self.symbol.initialize()

    async def test_trader_uses_ram_get_amount(self):
        """Test trader uses RAM get_amount for volume calculation."""
        ram = RAM(fixed_amount=20)
        trader = SimpleTrader(symbol=self.symbol, ram=ram)

        dsl = (self.symbol.trade_stops_level * 2 + self.symbol.spread) * self.symbol.point
        tick = await trader.symbol.info_tick()
        sl = tick.ask - dsl

        await trader.create_order_with_sl(order_type=OrderType.BUY, sl=sl)

        # Volume should be calculated based on RAM fixed_amount (20)
        assert trader.order.volume > 0

    async def test_trader_uses_ram_risk_to_reward(self):
        """Test trader uses RAM risk_to_reward for TP calculation."""
        ram = RAM(fixed_amount=10, risk_to_reward=3)
        trader = SimpleTrader(symbol=self.symbol, ram=ram)

        dsl = (self.symbol.trade_stops_level * 2 + self.symbol.spread) * self.symbol.point
        tick = await trader.symbol.info_tick()
        sl = tick.ask - dsl

        await trader.create_order_with_sl(order_type=OrderType.BUY, sl=sl)

        # TP distance should be 3x the SL distance
        sl_distance = abs(trader.order.price - trader.order.sl)
        tp_distance = abs(trader.order.tp - trader.order.price)

        assert abs(tp_distance - (sl_distance * 3)) < self.symbol.point * 10

    def test_trader_modifying_ram_after_init(self):
        """Test modifying RAM after trader initialization."""
        ram = RAM(fixed_amount=10)
        trader = SimpleTrader(symbol=self.symbol, ram=ram)

        trader.ram.modify_ram(fixed_amount=25, risk_to_reward=4)

        assert trader.ram.fixed_amount == 25
        assert trader.ram.risk_to_reward == 4
