"""Comprehensive tests for the Account class.

This module contains tests for the Account class, which is a singleton class
for managing trading account connections to MetaTrader 5.
"""

import pytest
from aiomql.lib.account import Account
from aiomql.core.models import AccountInfo
from aiomql.core.constants import AccountTradeMode, AccountMarginMode, AccountStopOutMode


class TestAccountBasic:
    """Tests for basic Account functionality."""

    @classmethod
    def setup_class(cls):
        cls.account = Account()

    @pytest.fixture(scope="class", autouse=True)
    async def refresh(self):
        """Refresh account data before running tests."""
        await self.account.refresh()

    async def test_connected(self):
        """Test that account is connected after refresh."""
        assert self.account.connected is True

    async def test_account_is_singleton(self):
        """Test that Account follows singleton pattern."""
        account1 = Account()
        account2 = Account()
        assert account1 is account2
        assert id(account1) == id(account2)

    async def test_account_inherits_from_account_info(self):
        """Test that Account inherits from AccountInfo."""
        assert isinstance(self.account, AccountInfo)


class TestAccountInfo:
    """Tests for AccountInfo attributes on Account."""

    @classmethod
    def setup_class(cls):
        cls.account = Account()

    @pytest.fixture(scope="class", autouse=True)
    async def refresh(self):
        """Refresh account data before running tests."""
        await self.account.refresh()

    async def test_login(self):
        """Test that login is a valid positive integer."""
        assert isinstance(self.account.login, int)
        assert self.account.login > 0

    async def test_server(self):
        """Test that server is a non-empty string."""
        assert isinstance(self.account.server, str)
        assert len(self.account.server) > 0

    async def test_balance(self):
        """Test that balance is a valid float."""
        assert isinstance(self.account.balance, (int, float))
        assert self.account.balance >= 0

    async def test_equity(self):
        """Test that equity is a valid float."""
        assert isinstance(self.account.equity, (int, float))
        # Equity can be less than balance if there are losing positions

    async def test_margin(self):
        """Test that margin is a valid float."""
        assert isinstance(self.account.margin, (int, float))
        assert self.account.margin >= 0

    async def test_margin_free(self):
        """Test that margin_free is a valid float."""
        assert isinstance(self.account.margin_free, (int, float))

    async def test_leverage(self):
        """Test that leverage is a valid positive value."""
        assert isinstance(self.account.leverage, (int, float))
        assert self.account.leverage > 0

    async def test_profit(self):
        """Test that profit is a valid float (can be negative)."""
        assert isinstance(self.account.profit, (int, float))

    async def test_currency(self):
        """Test that currency is a valid string."""
        assert isinstance(self.account.currency, str)
        assert len(self.account.currency) > 0

    async def test_currency_digits(self):
        """Test that currency_digits is a valid integer."""
        assert isinstance(self.account.currency_digits, int)
        assert self.account.currency_digits >= 0

    async def test_credit(self):
        """Test that credit is a valid float."""
        assert isinstance(self.account.credit, (int, float))
        assert self.account.credit >= 0

    async def test_name(self):
        """Test that name is a valid string."""
        assert isinstance(self.account.name, str)

    async def test_company(self):
        """Test that company (broker) is a valid string."""
        assert isinstance(self.account.company, str)

    async def test_limit_orders(self):
        """Test that limit_orders is a valid value."""
        assert isinstance(self.account.limit_orders, (int, float))
        assert self.account.limit_orders >= 0


class TestAccountEnums:
    """Tests for Account enum attributes."""

    @classmethod
    def setup_class(cls):
        cls.account = Account()

    @pytest.fixture(scope="class", autouse=True)
    async def refresh(self):
        """Refresh account data before running tests."""
        await self.account.refresh()

    async def test_trade_mode(self):
        """Test that trade_mode is a valid AccountTradeMode."""
        assert isinstance(self.account.trade_mode, (AccountTradeMode, int))

    async def test_margin_mode(self):
        """Test that margin_mode is a valid AccountMarginMode."""
        assert isinstance(self.account.margin_mode, (AccountMarginMode, int))

    async def test_margin_so_mode(self):
        """Test that margin_so_mode is a valid AccountStopOutMode."""
        assert isinstance(self.account.margin_so_mode, (AccountStopOutMode, int))


class TestAccountMargin:
    """Tests for Account margin-related attributes."""

    @classmethod
    def setup_class(cls):
        cls.account = Account()

    @pytest.fixture(scope="class", autouse=True)
    async def refresh(self):
        """Refresh account data before running tests."""
        await self.account.refresh()

    async def test_margin_level(self):
        """Test that margin_level is a valid float."""
        assert isinstance(self.account.margin_level, (int, float))
        # margin_level can be 0 if there are no open positions

    async def test_margin_so_call(self):
        """Test that margin_so_call (margin call level) is a valid value."""
        assert isinstance(self.account.margin_so_call, (int, float))

    async def test_margin_so_so(self):
        """Test that margin_so_so (stop out level) is a valid value."""
        assert isinstance(self.account.margin_so_so, (int, float))

    async def test_margin_initial(self):
        """Test that margin_initial is a valid float."""
        assert isinstance(self.account.margin_initial, (int, float))
        assert self.account.margin_initial >= 0

    async def test_margin_maintenance(self):
        """Test that margin_maintenance is a valid float."""
        assert isinstance(self.account.margin_maintenance, (int, float))
        assert self.account.margin_maintenance >= 0

    async def test_margin_call_less_than_stop_out(self):
        """Test that margin call level is above stop out level."""
        # A margin call should happen before a stop out
        assert self.account.margin_so_call >= self.account.margin_so_so


class TestAccountTrading:
    """Tests for Account trading-related attributes."""

    @classmethod
    def setup_class(cls):
        cls.account = Account()

    @pytest.fixture(scope="class", autouse=True)
    async def refresh(self):
        """Refresh account data before running tests."""
        await self.account.refresh()

    async def test_trade_allowed(self):
        """Test that trade_allowed is a boolean."""
        assert isinstance(self.account.trade_allowed, bool)

    async def test_trade_expert(self):
        """Test that trade_expert is a boolean."""
        assert isinstance(self.account.trade_expert, bool)

    async def test_fifo_close(self):
        """Test that fifo_close is a boolean."""
        assert isinstance(self.account.fifo_close, bool)


class TestAccountAssets:
    """Tests for Account asset-related attributes."""

    @classmethod
    def setup_class(cls):
        cls.account = Account()

    @pytest.fixture(scope="class", autouse=True)
    async def refresh(self):
        """Refresh account data before running tests."""
        await self.account.refresh()

    async def test_assets(self):
        """Test that assets is a valid float."""
        assert isinstance(self.account.assets, (int, float))
        assert self.account.assets >= 0

    async def test_liabilities(self):
        """Test that liabilities is a valid float."""
        assert isinstance(self.account.liabilities, (int, float))
        assert self.account.liabilities >= 0

    async def test_commission_blocked(self):
        """Test that commission_blocked is a valid float."""
        assert isinstance(self.account.commission_blocked, (int, float))
        assert self.account.commission_blocked >= 0


class TestAccountConsistency:
    """Tests for Account data consistency."""

    @classmethod
    def setup_class(cls):
        cls.account = Account()

    @pytest.fixture(scope="class", autouse=True)
    async def refresh(self):
        """Refresh account data before running tests."""
        await self.account.refresh()

    async def test_mt5_account_info_matches(self):
        """Test that Account attributes match mt5.account_info() data."""
        acc_info = await self.account.mt5.account_info()
        assert acc_info.login == self.account.login
        assert acc_info.server == self.account.server
        assert acc_info.currency == self.account.currency

    async def test_equity_balance_profit_relationship(self):
        """Test the relationship between equity, balance and profit.

        Equity ≈ Balance + Credit + Profit - Commission
        This is an approximation as swap and other factors may affect it.
        """
        # The basic relationship, allowing for some tolerance
        # due to swap, fees, and floating point precision
        expected_equity_approx = (
            self.account.balance + self.account.credit + self.account.profit
        )
        tolerance = abs(self.account.equity) * 0.01 + 1  # 1% + 1 unit tolerance
        assert abs(self.account.equity - expected_equity_approx) < tolerance

    async def test_margin_free_calculation(self):
        """Test that margin_free is approximately equity - margin."""
        expected_margin_free = self.account.equity - self.account.margin
        tolerance = abs(expected_margin_free) * 0.01 + 1  # 1% + 1 unit tolerance
        assert abs(self.account.margin_free - expected_margin_free) < tolerance


class TestAccountRefresh:
    """Tests for Account refresh functionality."""

    @classmethod
    def setup_class(cls):
        cls.account = Account()

    @pytest.fixture(scope="class", autouse=True)
    async def initial_refresh(self):
        """Initial refresh before running tests."""
        await self.account.refresh()

    async def test_refresh_updates_connection_status(self):
        """Test that refresh sets connected to True."""
        await self.account.refresh()
        assert self.account.connected is True

    async def test_refresh_updates_balance(self):
        """Test that refresh updates the balance attribute."""
        initial_balance = self.account.balance
        await self.account.refresh()
        # Balance should still be a valid value after refresh
        assert isinstance(self.account.balance, (int, float))
        assert self.account.balance >= 0

    async def test_multiple_refreshes(self):
        """Test that multiple refreshes work correctly."""
        for _ in range(3):
            await self.account.refresh()
            assert self.account.connected is True
            assert self.account.login > 0


class TestAccountMethods:
    """Tests for Account methods."""

    @classmethod
    def setup_class(cls):
        cls.account = Account()

    @pytest.fixture(scope="class", autouse=True)
    async def refresh(self):
        """Refresh account data before running tests."""
        await self.account.refresh()

    async def test_dict_method(self):
        """Test the dict method returns account data as dictionary."""
        account_dict = self.account.dict
        assert isinstance(account_dict, dict)
        assert "login" in account_dict or "balance" in account_dict

    async def test_annotations_method(self):
        """Test the annotations method returns class annotations."""
        annotations = self.account.annotations
        assert isinstance(annotations, dict)
        assert "login" in annotations
        assert "balance" in annotations
        assert "connected" in annotations

    async def test_get_dict_method(self):
        """Test the get_dict method with filtering."""
        # Test with include
        included = self.account.get_dict(include={"login", "balance"})
        assert "login" in included
        assert "balance" in included

        # Test with exclude
        excluded = self.account.get_dict(exclude={"login"})
        assert "login" not in excluded


class TestAccountSingleton:
    """Tests for Account singleton behavior."""

    async def test_singleton_preserves_state(self):
        """Test that singleton instances share state."""
        account1 = Account()
        await account1.refresh()
        login1 = account1.login

        account2 = Account()
        assert account2.login == login1
        assert account2.connected == account1.connected

    async def test_singleton_across_instances(self):
        """Test singleton pattern ensures all instances are the same."""
        accounts = [Account() for _ in range(5)]

        # All should be the same instance
        for account in accounts[1:]:
            assert account is accounts[0]

        # All should have same data
        await accounts[0].refresh()
        for account in accounts[1:]:
            assert account.login == accounts[0].login
            assert account.server == accounts[0].server
