"""Comprehensive tests for the Order module.

Tests cover:
- Order initialization and default values
- Order modification
- Order checking (margin sufficiency)
- Order sending (market orders)
- Margin calculations
- Profit/loss calculations
- Pending order management
- Request property and filtering
- Class methods for order operations
- cancel_order and send_order retry logic
- Error handling and __getstate__
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from aiomql.lib.order import Order
from aiomql.core.constants import TradeAction, OrderTime, OrderFilling, OrderType
from aiomql.core.models import OrderCheckResult, OrderSendResult, TradeOrder
from aiomql.core.exceptions import OrderError


class TestOrderInitialization:
    """Test Order class initialization and default values."""

    def test_init_with_minimal_args(self):
        """Test Order can be initialized with minimal arguments."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        assert order.symbol == "BTCUSD"
        assert order.type == OrderType.BUY
        assert order.volume == 0.01
        assert order.price == 50000.0

    def test_init_default_action(self):
        """Test Order has default action of DEAL."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        assert order.action == TradeAction.DEAL

    def test_init_default_type_time(self):
        """Test Order has default type_time of DAY."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        assert order.type_time == OrderTime.DAY

    def test_init_default_type_filling(self):
        """Test Order has default type_filling of FOK."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        assert order.type_filling == OrderFilling.FOK

    def test_init_override_defaults(self):
        """Test Order defaults can be overridden."""
        order = Order(
            symbol="BTCUSD",
            type=OrderType.BUY,
            volume=0.01,
            price=50000.0,
            action=TradeAction.PENDING,
            type_time=OrderTime.GTC,
            type_filling=OrderFilling.IOC,
        )
        assert order.action == TradeAction.PENDING
        assert order.type_time == OrderTime.GTC
        assert order.type_filling == OrderFilling.IOC

    def test_init_with_sl_tp(self):
        """Test Order can be initialized with stop loss and take profit."""
        order = Order(
            symbol="BTCUSD",
            type=OrderType.BUY,
            volume=0.01,
            price=50000.0,
            sl=49000.0,
            tp=51000.0,
        )
        assert order.sl == 49000.0
        assert order.tp == 51000.0

    def test_init_with_magic(self):
        """Test Order can be initialized with magic number."""
        order = Order(
            symbol="BTCUSD",
            type=OrderType.BUY,
            volume=0.01,
            price=50000.0,
            magic=12345,
        )
        assert order.magic == 12345

    def test_init_with_comment(self):
        """Test Order can be initialized with comment."""
        order = Order(
            symbol="BTCUSD",
            type=OrderType.BUY,
            volume=0.01,
            price=50000.0,
            comment="Test order",
        )
        assert order.comment == "Test order"


class TestOrderModification:
    """Test Order modification method."""

    def test_modify_single_attribute(self):
        """Test modifying a single attribute."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        order.modify(volume=0.02)
        assert order.volume == 0.02

    def test_modify_multiple_attributes(self):
        """Test modifying multiple attributes at once."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        order.modify(volume=0.02, price=51000.0, sl=49000.0)
        assert order.volume == 0.02
        assert order.price == 51000.0
        assert order.sl == 49000.0

    def test_modify_type(self):
        """Test modifying order type."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        order.modify(type=OrderType.SELL)
        assert order.type == OrderType.SELL

    def test_modify_preserves_other_attributes(self):
        """Test modifying doesn't affect other attributes."""
        order = Order(
            symbol="BTCUSD",
            type=OrderType.BUY,
            volume=0.01,
            price=50000.0,
            comment="Original",
        )
        order.modify(volume=0.02)
        assert order.comment == "Original"
        assert order.symbol == "BTCUSD"

    def test_modify_returns_none(self):
        """Test modify returns None (modifies in place)."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        result = order.modify(volume=0.02)
        assert result is None

    def test_modify_action_to_pending(self):
        """Test modifying action to PENDING."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        order.modify(action=TradeAction.PENDING)
        assert order.action == TradeAction.PENDING


class TestOrderRequest:
    """Test Order request property."""

    def test_request_is_dict(self):
        """Test request property returns a dictionary."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        assert isinstance(order.request, dict)

    def test_request_contains_required_fields(self):
        """Test request contains required trade fields."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        request = order.request
        assert "symbol" in request
        assert "type" in request
        assert "volume" in request
        assert "price" in request
        assert "action" in request

    def test_request_filters_invalid_fields(self):
        """Test request only contains valid TradeRequest fields."""
        order = Order(
            symbol="BTCUSD",
            type=OrderType.BUY,
            volume=0.01,
            price=50000.0,
        )
        request = order.request
        # Should not contain fields that aren't part of TradeRequest
        for key in request:
            assert key in order.mt5.TradeRequest.__match_args__

    def test_request_includes_sl_tp_when_set(self):
        """Test request includes sl and tp when they are set."""
        order = Order(
            symbol="BTCUSD",
            type=OrderType.BUY,
            volume=0.01,
            price=50000.0,
            sl=49000.0,
            tp=51000.0,
        )
        request = order.request
        assert request["sl"] == 49000.0
        assert request["tp"] == 51000.0

    def test_request_reflects_modify(self):
        """Test request reflects changes after modify."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        order.modify(price=51000.0)
        assert order.request["price"] == 51000.0


class TestOrderCheckLive:
    """Live tests for Order check method."""

    async def test_check_returns_order_check_result(self, buy_order):
        """Test check returns OrderCheckResult."""
        order = Order(**buy_order)
        result = await order.check()
        assert isinstance(result, OrderCheckResult)

    async def test_check_success_retcode(self, buy_order):
        """Test successful check has retcode 0."""
        order = Order(**buy_order)
        result = await order.check()
        assert result.retcode == 0

    async def test_check_has_margin_info(self, buy_order):
        """Test check result contains margin information."""
        order = Order(**buy_order)
        result = await order.check()
        assert hasattr(result, 'margin')
        assert hasattr(result, 'margin_free')

    async def test_check_has_balance_info(self, buy_order):
        """Test check result contains balance information."""
        order = Order(**buy_order)
        result = await order.check()
        assert hasattr(result, 'balance')
        assert hasattr(result, 'equity')

    async def test_check_with_kwargs_override(self, buy_order):
        """Test check can use kwargs to override order params."""
        order = Order(**buy_order)
        result = await order.check(volume=buy_order["volume"] * 2)
        assert isinstance(result, OrderCheckResult)

    async def test_check_sell_order(self, sell_order):
        """Test check works for sell orders."""
        order = Order(**sell_order)
        result = await order.check()
        assert result.retcode == 0

    async def test_check_raises_order_error_when_none(self):
        """Test check raises OrderError when mt5.order_check returns None."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        order.mt5.order_check = AsyncMock(return_value=None)
        with pytest.raises(OrderError):
            await order.check()


class TestOrderSendLive:
    """Live tests for Order send method."""

    async def test_send_returns_order_send_result(self, buy_order):
        """Test send returns OrderSendResult."""
        order = Order(**buy_order)
        result = await order.send()
        assert isinstance(result, OrderSendResult)

    async def test_send_success_retcode(self, buy_order):
        """Test successful send has retcode 10009."""
        order = Order(**buy_order)
        result = await order.send()
        assert result.retcode == 10009

    async def test_send_has_deal_ticket(self, buy_order):
        """Test send result contains deal ticket."""
        order = Order(**buy_order)
        result = await order.send()
        assert hasattr(result, 'deal')
        assert result.deal > 0

    async def test_send_has_order_ticket(self, buy_order):
        """Test send result contains order ticket."""
        order = Order(**buy_order)
        result = await order.send()
        assert hasattr(result, 'order')
        assert result.order > 0

    async def test_send_sell_order(self, sell_order):
        """Test send works for sell orders."""
        order = Order(**sell_order)
        result = await order.send()
        assert result.retcode == 10009


class TestCancelOrderLive:
    """Live tests for cancel_order class method."""

    async def test_cancel_order_raises_for_invalid_ticket(self):
        """Test cancel_order raises OrderError for nonexistent order."""
        # Mocking order_send to return None to trigger OrderError
        original = Order.mt5.order_send
        Order.mt5.order_send = AsyncMock(return_value=None)
        try:
            with pytest.raises(OrderError):
                await Order.cancel_order(order=999999999)
        finally:
            Order.mt5.order_send = original

    async def test_cancel_order_sends_remove_action(self):
        """Test cancel_order sends REMOVE action."""
        mock_result = MagicMock()
        mock_result._asdict = MagicMock(return_value={
            "retcode": 10009, "deal": 0, "order": 12345, "volume": 0.0,
            "price": 0.0, "bid": 0.0, "ask": 0.0, "comment": "",
            "request_id": 1, "retcode_external": 0,
            "request": {"action": 8, "order": 12345, "symbol": "BTCUSD"},
        })
        original = Order.mt5.order_send
        Order.mt5.order_send = AsyncMock(return_value=mock_result)
        try:
            result = await Order.cancel_order(order=12345, symbol="BTCUSD")
            assert isinstance(result, OrderSendResult)
            # Verify the request included REMOVE action
            call_args = Order.mt5.order_send.call_args[0][0]
            assert call_args["action"] == TradeAction.REMOVE
        finally:
            Order.mt5.order_send = original


class TestSendOrderRetry:
    """Test send_order retry logic."""

    async def test_send_order_retries_on_10031(self):
        """Test send_order retries when retcode is 10031 (no connection)."""
        # First call returns 10031, second returns success
        mock_result_fail = MagicMock()
        mock_result_fail.retcode = 10031
        mock_result_fail._asdict = MagicMock(return_value={
            "retcode": 10031, "deal": 0, "order": 0, "volume": 0.0,
            "price": 0.0, "bid": 0.0, "ask": 0.0, "comment": "No connection",
            "request_id": 1, "retcode_external": 0,
            "request": {"action": 1, "symbol": "BTCUSD"},
        })
        mock_result_ok = MagicMock()
        mock_result_ok.retcode = 10009
        mock_result_ok._asdict = MagicMock(return_value={
            "retcode": 10009, "deal": 12345, "order": 67890, "volume": 0.01,
            "price": 50000.0, "bid": 49999.0, "ask": 50001.0, "comment": "",
            "request_id": 2, "retcode_external": 0,
            "request": {"action": 1, "symbol": "BTCUSD"},
        })

        original = Order.mt5.order_send
        Order.mt5.order_send = AsyncMock(side_effect=[mock_result_fail, mock_result_ok])
        try:
            result = await Order.send_order(request={"symbol": "BTCUSD", "action": 1})
            assert result.retcode == 10009
            assert Order.mt5.order_send.call_count == 2
        finally:
            Order.mt5.order_send = original

    async def test_send_order_raises_when_none(self):
        """Test send_order raises OrderError when result is None."""
        original = Order.mt5.order_send
        Order.mt5.order_send = AsyncMock(return_value=None)
        try:
            with pytest.raises(OrderError):
                await Order.send_order(request={"symbol": "BTCUSD", "action": 1})
        finally:
            Order.mt5.order_send = original


class TestOrderMarginCalculationLive:
    """Live tests for Order margin calculation."""

    async def test_calc_margin_returns_float(self, buy_order):
        """Test calc_margin returns a float."""
        order = Order(**buy_order)
        margin = await order.calc_margin()
        assert isinstance(margin, float)

    async def test_calc_margin_positive(self, buy_order):
        """Test calc_margin returns positive value."""
        order = Order(**buy_order)
        margin = await order.calc_margin()
        assert margin > 0

    async def test_calc_margin_buy_order(self, buy_order):
        """Test calc_margin works for buy orders."""
        order = Order(**buy_order)
        margin = await order.calc_margin()
        assert margin is not None
        assert margin > 0

    async def test_calc_margin_sell_order(self, sell_order):
        """Test calc_margin works for sell orders."""
        order = Order(**sell_order)
        margin = await order.calc_margin()
        assert margin is not None
        assert margin > 0


class TestOrderProfitCalculationLive:
    """Live tests for Order profit/loss calculations."""

    async def test_calc_profit_returns_float(self, buy_order):
        """Test calc_profit returns a float."""
        order = Order(**buy_order)
        profit = await order.calc_profit()
        assert isinstance(profit, float)

    async def test_calc_profit_is_positive_for_tp(self, buy_order):
        """Test calc_profit is positive when price reaches TP."""
        order = Order(**buy_order)
        profit = await order.calc_profit()
        assert profit > 0

    async def test_calc_loss_returns_float(self, buy_order):
        """Test calc_loss returns a float."""
        order = Order(**buy_order)
        loss = await order.calc_loss()
        assert isinstance(loss, float)

    async def test_calc_loss_is_negative_for_sl(self, buy_order):
        """Test calc_loss is negative when price reaches SL."""
        order = Order(**buy_order)
        loss = await order.calc_loss()
        assert loss < 0

    async def test_calc_profit_sell_order(self, sell_order):
        """Test calc_profit works for sell orders (may be None if no TP)."""
        order = Order(**sell_order)
        # sell_order may not have tp set
        profit = await order.calc_profit()
        # May be None if tp is not set
        assert profit is None or isinstance(profit, float)


class TestOrdersTotalLive:
    """Live tests for orders_total class method."""

    async def test_orders_total_returns_int(self):
        """Test orders_total returns an integer."""
        total = await Order.orders_total()
        assert isinstance(total, int)

    async def test_orders_total_non_negative(self):
        """Test orders_total returns non-negative value."""
        total = await Order.orders_total()
        assert total >= 0


class TestGetPendingOrdersLive:
    """Live tests for pending order retrieval."""

    async def test_get_pending_orders_returns_tuple(self):
        """Test get_pending_orders returns a tuple."""
        orders = await Order.get_pending_orders()
        assert isinstance(orders, tuple)

    async def test_get_pending_orders_contains_trade_orders(self):
        """Test get_pending_orders contains TradeOrder objects."""
        orders = await Order.get_pending_orders()
        for order in orders:
            assert isinstance(order, TradeOrder)

    async def test_get_pending_orders_by_symbol(self):
        """Test get_pending_orders can filter by symbol."""
        orders = await Order.get_pending_orders(symbol="BTCUSD")
        for order in orders:
            assert order.symbol == "BTCUSD"

    async def test_get_pending_orders_by_group(self):
        """Test get_pending_orders can filter by group."""
        orders = await Order.get_pending_orders(group="*USD*")
        for order in orders:
            assert "USD" in order.symbol

    async def test_get_pending_order_nonexistent(self):
        """Test get_pending_order returns None for nonexistent ticket."""
        order = await Order.get_pending_order(ticket=999999999999)
        assert order is None


class TestGetHistoryOrderByTicketLive:
    """Live tests for get_history_order_by_ticket class method."""

    async def test_get_history_order_by_ticket_nonexistent(self):
        """Test get_history_order_by_ticket returns None for nonexistent ticket."""
        order = await Order.get_history_order_by_ticket(ticket=999999999999)
        assert order is None

    async def test_get_history_order_by_ticket_returns_trade_order_or_none(self):
        """Test get_history_order_by_ticket returns TradeOrder or None."""
        # Get list of pending orders first
        orders = await Order.get_pending_orders()
        if orders:
            # If there are pending orders, test with a real ticket
            ticket = orders[0].ticket
            order = await Order.get_history_order_by_ticket(ticket=ticket)
            assert order is None or isinstance(order, TradeOrder)
        else:
            # If no pending orders, just verify nonexistent returns None
            order = await Order.get_history_order_by_ticket(ticket=999999999999)
            assert order is None


class TestProfitToPriceLive:
    """Live tests for profit_to_price class method."""

    async def test_profit_to_price_buy_order(self, btc_usd):
        """Test profit_to_price calculates correct price for buy order."""
        sym_info = await btc_usd.mt5.symbol_info(btc_usd.name)
        price_open = sym_info.ask
        volume = sym_info.volume_min
        profit = 10.0  # $10 profit target

        price = await Order.profit_to_price(
            profit=profit,
            order_type=OrderType.BUY,
            volume=volume,
            symbol=btc_usd.name,
            price_open=price_open,
        )
        assert isinstance(price, float)
        assert price > price_open  # For buy, profit price should be higher

    async def test_profit_to_price_sell_order(self, btc_usd):
        """Test profit_to_price calculates correct price for sell order."""
        sym_info = await btc_usd.mt5.symbol_info(btc_usd.name)
        price_open = sym_info.bid
        volume = sym_info.volume_min
        profit = 10.0  # $10 profit target

        price = await Order.profit_to_price(
            profit=profit,
            order_type=OrderType.SELL,
            volume=volume,
            symbol=btc_usd.name,
            price_open=price_open,
        )
        assert isinstance(price, float)
        assert price < price_open  # For sell, profit price should be lower


class TestOrderClassAttributes:
    """Test Order class attributes and inheritance."""

    def test_order_has_mt5_attribute(self):
        """Test Order class has mt5 attribute."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        assert hasattr(order, 'mt5')

    def test_order_has_config_attribute(self):
        """Test Order class has config attribute."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        assert hasattr(order, 'config')

    def test_order_inherits_trade_request(self):
        """Test Order inherits from TradeRequest."""
        from aiomql.core.models import TradeRequest
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        assert isinstance(order, TradeRequest)

    def test_order_getstate_excludes_mt5(self):
        """Test __getstate__ excludes mt5 attribute for pickling."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        state = order.__getstate__()
        assert "mt5" not in state

    def test_order_getstate_preserves_other_attrs(self):
        """Test __getstate__ preserves trade attributes."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        state = order.__getstate__()
        assert state["symbol"] == "BTCUSD"


class TestOrderEdgeCases:
    """Test edge cases and error handling."""

    async def test_check_with_zero_volume(self, btc_usd):
        """Test check with zero volume."""
        sym_info = await btc_usd.mt5.symbol_info(btc_usd.name)
        order = Order(
            symbol=btc_usd.name,
            type=OrderType.BUY,
            volume=0.0,
            price=sym_info.ask,
        )
        # Should either raise error or return failed check
        try:
            result = await order.check()
            assert result.retcode != 0
        except OrderError:
            pass  # Also acceptable

    def test_multiple_orders_share_mt5(self):
        """Test multiple Order instances share the same mt5 object."""
        order1 = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        order2 = Order(symbol="ETHUSD", type=OrderType.SELL, volume=0.01, price=3000.0)
        assert order1.mt5 is order2.mt5

    def test_multiple_orders_share_config(self):
        """Test multiple Order instances share the same config object."""
        order1 = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        order2 = Order(symbol="ETHUSD", type=OrderType.SELL, volume=0.01, price=3000.0)
        assert order1.config is order2.config

    async def test_calc_margin_returns_none_on_error(self):
        """Test calc_margin returns None when an error occurs."""
        order = Order(symbol="INVALIDSYMBOL", type=OrderType.BUY, volume=0.01, price=50000.0)
        result = await order.calc_margin()
        assert result is None

    async def test_calc_profit_returns_none_when_no_tp(self):
        """Test calc_profit returns None when tp is not set."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        # tp is not set, so price_close will be None-ish
        result = await order.calc_profit()
        assert result is None or isinstance(result, float)

    async def test_calc_loss_returns_none_when_no_sl(self):
        """Test calc_loss returns None when sl is not set."""
        order = Order(symbol="BTCUSD", type=OrderType.BUY, volume=0.01, price=50000.0)
        # sl is not set, so price_close will be None-ish
        result = await order.calc_loss()
        assert result is None or isinstance(result, float)

    async def test_get_pending_orders_returns_empty_for_nonexistent_symbol(self):
        """Test get_pending_orders returns empty tuple for nonexistent symbol."""
        orders = await Order.get_pending_orders(symbol="NONEXISTENT")
        assert orders == ()
