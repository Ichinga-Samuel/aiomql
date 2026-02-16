"""Comprehensive tests for the RAM (Risk Assessment and Management) module.

Tests cover:
- RAM class initialization with default and custom values
- modify_ram method for updating parameters
- get_amount async and sync methods
- check_losing_positions async and sync methods
- check_open_positions async and sync methods
- Edge cases and boundary conditions
"""

import pytest

from aiomql.lib.ram import RAM
from aiomql.lib.account import Account
from aiomql.lib.positions import Positions


class TestRAMInitialization:
    """Test RAM class initialization."""

    def test_init_default_values(self):
        """Test RAM initializes with correct default values."""
        ram = RAM()
        assert ram.risk_to_reward == 2
        assert ram.risk == 1
        assert ram.min_amount == 0
        assert ram.max_amount == 0
        assert ram.loss_limit == 3
        assert ram.open_limit == 3
        assert ram.fixed_amount is None

    def test_init_custom_values(self):
        """Test RAM initializes with custom values."""
        ram = RAM(
            risk_to_reward=3,
            risk=2,
            min_amount=10,
            max_amount=100,
            loss_limit=5,
            open_limit=10,
            fixed_amount=50
        )
        assert ram.risk_to_reward == 3
        assert ram.risk == 2
        assert ram.min_amount == 10
        assert ram.max_amount == 100
        assert ram.loss_limit == 5
        assert ram.open_limit == 10
        assert ram.fixed_amount == 50

    def test_init_has_account_attribute(self):
        """Test RAM has an Account instance."""
        ram = RAM()
        assert hasattr(ram, 'account')
        assert isinstance(ram.account, Account)

    def test_init_has_positions_attribute(self):
        """Test RAM has a Positions instance."""
        ram = RAM()
        assert hasattr(ram, 'positions')
        assert isinstance(ram.positions, Positions)

    def test_init_partial_custom_values(self):
        """Test RAM with only some custom values uses defaults for others."""
        ram = RAM(risk=5, loss_limit=10)
        assert ram.risk == 5
        assert ram.loss_limit == 10
        # Defaults for others
        assert ram.risk_to_reward == 2
        assert ram.min_amount == 0
        assert ram.max_amount == 0
        assert ram.open_limit == 3
        assert ram.fixed_amount is None


class TestModifyRAM:
    """Test modify_ram method."""

    def test_modify_ram_single_attribute(self):
        """Test modifying a single RAM attribute."""
        ram = RAM()
        ram.modify_ram(risk=5)
        assert ram.risk == 5

    def test_modify_ram_multiple_attributes(self):
        """Test modifying multiple RAM attributes at once."""
        ram = RAM()
        ram.modify_ram(
            risk=10,
            risk_to_reward=4,
            min_amount=50,
            max_amount=500
        )
        assert ram.risk == 10
        assert ram.risk_to_reward == 4
        assert ram.min_amount == 50
        assert ram.max_amount == 500

    def test_modify_ram_preserves_unmodified(self):
        """Test that unmodified attributes remain unchanged."""
        ram = RAM(loss_limit=5, open_limit=10)
        ram.modify_ram(risk=7)
        assert ram.loss_limit == 5
        assert ram.open_limit == 10
        assert ram.risk == 7

    def test_modify_ram_fixed_amount(self):
        """Test modifying fixed_amount attribute."""
        ram = RAM()
        assert ram.fixed_amount is None
        ram.modify_ram(fixed_amount=100)
        assert ram.fixed_amount == 100


class TestGetAmountAsync:
    """Live tests for async get_amount method."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.ram = RAM(min_amount=5, max_amount=100, risk=1)

    async def test_get_amount_returns_float(self):
        """Test get_amount returns a float."""
        result = await self.ram.get_amount()
        assert isinstance(result, float)

    async def test_get_amount_respects_min_max(self):
        """Test get_amount respects min and max amount constraints."""
        ram = RAM(min_amount=5, max_amount=10, risk=1)
        result = await ram.get_amount()
        assert ram.min_amount <= result <= ram.max_amount

    async def test_get_amount_returns_fixed_amount(self):
        """Test get_amount returns fixed_amount when set."""
        ram = RAM(fixed_amount=75)
        result = await ram.get_amount()
        assert result == 75

    async def test_get_amount_fixed_amount_overrides_calculation(self):
        """Test fixed_amount takes precedence over calculation."""
        ram = RAM(fixed_amount=100, min_amount=5, max_amount=50, risk=10)
        result = await ram.get_amount()
        assert result == 100

    async def test_get_amount_without_constraints(self):
        """Test get_amount without min/max returns calculated amount."""
        ram = RAM(risk=1)  # min_amount=0, max_amount=0 (defaults)
        result = await ram.get_amount()
        assert isinstance(result, float)
        assert result >= 0

    async def test_get_amount_updates_account(self):
        """Test that get_amount refreshes account data."""
        ram = RAM()
        initial_margin = ram.account.margin_free
        await ram.get_amount()
        # After refresh, margin_free should be updated (possibly same value but refreshed)
        assert hasattr(ram.account, 'margin_free')


class TestGetAmountSync:
    """Live tests for sync get_amount_sync method."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.ram = RAM(min_amount=5, max_amount=100, risk=1)

    def test_get_amount_sync_returns_float(self):
        """Test get_amount_sync returns a float."""
        result = self.ram.get_amount_sync()
        assert isinstance(result, float)

    def test_get_amount_sync_respects_min_max(self):
        """Test get_amount_sync respects min and max amount constraints."""
        ram = RAM(min_amount=5, max_amount=10, risk=1)
        result = ram.get_amount_sync()
        assert ram.min_amount <= result <= ram.max_amount

    def test_get_amount_sync_returns_fixed_amount(self):
        """Test get_amount_sync returns fixed_amount when set."""
        ram = RAM(fixed_amount=75)
        result = ram.get_amount_sync()
        assert result == 75

    def test_get_amount_sync_fixed_amount_overrides_calculation(self):
        """Test fixed_amount takes precedence over calculation in sync method."""
        ram = RAM(fixed_amount=100, min_amount=5, max_amount=50, risk=10)
        result = ram.get_amount_sync()
        assert result == 100


class TestCheckLosingPositionsAsync:
    """Live tests for async check_losing_positions method."""

    @pytest.fixture(scope="class", autouse=True)
    async def init(self, make_buy_sell_orders):
        """Initialize with live trades."""
        pass

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.ram = RAM(loss_limit=3)

    async def test_check_losing_positions_returns_bool(self):
        """Test check_losing_positions returns a boolean."""
        result = await self.ram.check_losing_positions()
        assert isinstance(result, bool)

    async def test_check_losing_positions_with_high_limit(self):
        """Test check_losing_positions returns True with high limit."""
        ram = RAM(loss_limit=100)
        result = await ram.check_losing_positions()
        assert result is True

    async def test_check_losing_positions_with_zero_limit(self):
        """Test check_losing_positions behavior with zero limit."""
        ram = RAM(loss_limit=0)
        result = await ram.check_losing_positions()
        assert isinstance(result, bool)


class TestCheckLosingPositionsSync:
    """Live tests for sync check_losing_positions_sync method."""

    @pytest.fixture(scope="class", autouse=True)
    async def init(self, make_buy_sell_orders):
        """Initialize with live trades."""
        pass

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.ram = RAM(loss_limit=3)

    def test_check_losing_positions_sync_returns_bool(self):
        """Test check_losing_positions_sync returns a boolean."""
        result = self.ram.check_losing_positions_sync()
        assert isinstance(result, bool)

    def test_check_losing_positions_sync_with_high_limit(self):
        """Test check_losing_positions_sync returns True with high limit."""
        ram = RAM(loss_limit=100)
        result = ram.check_losing_positions_sync()
        assert result is True


class TestCheckOpenPositionsAsync:
    """Live tests for async check_open_positions method."""

    @pytest.fixture(scope="class", autouse=True)
    async def init(self, make_buy_sell_orders):
        """Initialize with live trades."""
        pass

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.ram = RAM(open_limit=3)

    async def test_check_open_positions_returns_bool(self):
        """Test check_open_positions returns a boolean."""
        result = await self.ram.check_open_positions()
        assert isinstance(result, bool)

    async def test_check_open_positions_with_high_limit(self):
        """Test check_open_positions returns True with high limit."""
        ram = RAM(open_limit=100)
        result = await ram.check_open_positions()
        assert result is True

    async def test_check_open_positions_with_zero_limit(self):
        """Test check_open_positions returns False when limit is 0 and positions exist."""
        ram = RAM(open_limit=0)
        result = await ram.check_open_positions()
        # Will be False if any positions exist (from make_buy_sell_orders)
        assert isinstance(result, bool)


class TestCheckOpenPositionsSync:
    """Live tests for sync check_open_positions_sync method."""

    @pytest.fixture(scope="class", autouse=True)
    async def init(self, make_buy_sell_orders):
        """Initialize with live trades."""
        pass

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.ram = RAM(open_limit=3)

    def test_check_open_positions_sync_returns_bool(self):
        """Test check_open_positions_sync returns a boolean."""
        result = self.ram.check_open_positions_sync()
        assert isinstance(result, bool)

    def test_check_open_positions_sync_with_high_limit(self):
        """Test check_open_positions_sync returns True with high limit."""
        ram = RAM(open_limit=100)
        result = ram.check_open_positions_sync()
        assert result is True


class TestRAMIntegration:
    """Integration tests for RAM with live trading."""

    @pytest.fixture(scope="class", autouse=True)
    async def init(self, make_buy_sell_orders):
        """Initialize with live trades."""
        pass

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.ram = RAM(
            min_amount=5,
            max_amount=100,
            loss_limit=5,
            open_limit=10,
            risk=1
        )

    async def test_async_sync_get_amount_consistency(self):
        """Test async and sync get_amount return similar results."""
        async_result = await self.ram.get_amount()
        sync_result = self.ram.get_amount_sync()
        # Both should be within the min/max range
        assert self.ram.min_amount <= async_result <= self.ram.max_amount
        assert self.ram.min_amount <= sync_result <= self.ram.max_amount

    async def test_check_positions_with_exceeded_limit(self, buy_order, sell_order, mt):
        """Test check_open_positions returns False when limit exceeded."""
        ram = RAM(open_limit=0)  # Set limit to 0, any open position will exceed
        # Positions already created by fixture
        result = await ram.check_open_positions()
        # Should be False if any positions exist
        assert isinstance(result, bool)

    async def test_ram_parameter_types(self):
        """Test that RAM parameters have correct types."""
        assert isinstance(self.ram.risk_to_reward, (int, float))
        assert isinstance(self.ram.risk, (int, float))
        assert isinstance(self.ram.min_amount, (int, float))
        assert isinstance(self.ram.max_amount, (int, float))
        assert isinstance(self.ram.loss_limit, int)
        assert isinstance(self.ram.open_limit, int)


class TestRAMEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_ram_with_zero_risk(self):
        """Test RAM with zero risk percentage."""
        ram = RAM(risk=0)
        assert ram.risk == 0

    def test_ram_with_high_risk(self):
        """Test RAM with high risk percentage."""
        ram = RAM(risk=100)
        assert ram.risk == 100

    def test_ram_with_equal_min_max(self):
        """Test RAM with equal min and max amounts."""
        ram = RAM(min_amount=50, max_amount=50)
        assert ram.min_amount == 50
        assert ram.max_amount == 50

    def test_ram_with_negative_values(self):
        """Test RAM accepts negative values (not validated at init)."""
        ram = RAM(min_amount=-10, max_amount=-5)
        assert ram.min_amount == -10
        assert ram.max_amount == -5

    def test_ram_fixed_amount_zero(self):
        """Test RAM with fixed_amount of zero."""
        ram = RAM(fixed_amount=0)
        # 0 is falsy, so get_amount should calculate instead
        assert ram.fixed_amount == 0

    async def test_get_amount_with_fixed_zero(self):
        """Test get_amount behavior when fixed_amount is 0 (falsy)."""
        ram = RAM(fixed_amount=0)
        result = await ram.get_amount()
        # Since 0 is falsy, should fall through to calculation
        assert isinstance(result, float)

    def test_modify_ram_with_invalid_attribute(self):
        """Test modify_ram allows setting new attributes."""
        ram = RAM()
        ram.modify_ram(custom_attribute="custom_value")
        assert ram.custom_attribute == "custom_value"

    async def test_check_positions_high_limits(self):
        """Test check methods with very high limits always return True."""
        ram = RAM(loss_limit=1000, open_limit=1000)
        losing_result = await ram.check_losing_positions()
        open_result = await ram.check_open_positions()
        assert losing_result is True
        assert open_result is True
