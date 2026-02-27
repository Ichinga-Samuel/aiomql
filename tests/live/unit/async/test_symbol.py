"""Comprehensive tests for the Symbol class.

This module contains live tests for the Symbol class, which provides
the interface for interacting with trading instruments in MetaTrader 5.
"""

from datetime import datetime, timedelta

import pytest

from aiomql.lib.symbol import Symbol
from aiomql.lib.candle import Candles
from aiomql.lib.ticks import Tick, Ticks
from aiomql.core.models import SymbolInfo, BookInfo


class TestSymbolInit:
    """Tests for Symbol initialisation."""

    async def test_requires_name(self):
        """Test that Symbol raises AssertionError without a name."""
        with pytest.raises(AssertionError):
            Symbol()

    async def test_initialized_starts_false(self):
        """Test that a newly created Symbol is not initialized."""
        sym = Symbol(name="BTCUSD")
        assert sym.initialized is False

    async def test_has_account(self):
        """Test that a newly created Symbol has an account attribute."""
        sym = Symbol(name="BTCUSD")
        assert sym.account is not None

    async def test_name_attribute(self):
        """Test that the name attribute is set correctly."""
        sym = Symbol(name="BTCUSD")
        assert sym.name == "BTCUSD"


class TestSymbolInitialize:
    """Tests for Symbol.initialize() and Symbol.initialize_sync()."""

    @pytest.fixture(scope="class")
    async def btc(self):
        symbol = Symbol(name="BTCUSD")
        await symbol.initialize()
        return symbol

    async def test_initialize_returns_true(self, btc):
        """Test that initialize() returns True for a valid symbol."""
        assert btc.initialized is True

    async def test_initialize_sets_select(self, btc):
        """Test that initialize() sets the select attribute."""
        assert btc.select is True

    async def test_initialize_sets_tick(self, btc):
        """Test that initialize() sets the tick attribute."""
        assert btc.tick is not None
        assert isinstance(btc.tick, Tick)

    async def test_initialize_sets_symbol_properties(self, btc):
        """Test that initialize() populates SymbolInfo properties."""
        assert btc.volume_min > 0
        assert btc.volume_max > 0
        assert btc.volume_step > 0
        assert btc.point > 0

    async def test_initialize_sync(self):
        """Test that initialize_sync() works correctly."""
        sym = Symbol(name="BTCUSD")
        result = sym.initialize_sync()
        assert result is True
        assert sym.initialized is True
        assert sym.tick is not None


class TestSymbolInfo:
    """Tests for Symbol.info() and Symbol.info_tick()."""

    @pytest.fixture(scope="class")
    async def btc(self):
        symbol = Symbol(name="BTCUSD")
        await symbol.initialize()
        return symbol

    async def test_info_returns_symbol_info(self, btc):
        """Test that info() returns a SymbolInfo object."""
        result = await btc.info()
        assert result is not None
        assert isinstance(result, SymbolInfo)

    async def test_info_tick_returns_tick(self, btc):
        """Test that info_tick() returns a Tick object."""
        tick = await btc.info_tick()
        assert tick is not None
        assert isinstance(tick, Tick)

    async def test_info_tick_updates_tick_attribute(self, btc):
        """Test that info_tick() updates the symbol's tick attribute."""
        tick = await btc.info_tick()
        assert btc.tick is tick

    async def test_info_tick_with_name(self, btc):
        """Test info_tick() with an explicit symbol name."""
        tick = await btc.info_tick(name="ETHUSD")
        assert tick is not None
        assert isinstance(tick, Tick)


class TestSymbolSelect:
    """Tests for Symbol.symbol_select()."""

    @pytest.fixture(scope="class")
    async def btc(self):
        symbol = Symbol(name="BTCUSD")
        await symbol.initialize()
        return symbol

    async def test_symbol_select_enable(self, btc):
        """Test that symbol_select(enable=True) selects the symbol."""
        result = await btc.symbol_select(enable=True)
        assert result is True
        assert btc.select is True

    async def test_symbol_select_disable_and_renable(self, btc):
        """Test toggling symbol selection off and on."""
        await btc.symbol_select(enable=False)
        assert btc.select is False
        await btc.symbol_select(enable=True)
        assert btc.select is True


class TestSymbolBook:
    """Tests for Symbol market depth (book) methods."""

    @pytest.fixture(scope="class")
    async def btc(self):
        symbol = Symbol(name="BTCUSD")
        await symbol.initialize()
        return symbol

    async def test_book_add(self, btc):
        """Test that book_add() returns a boolean."""
        result = await btc.book_add()
        assert isinstance(result, bool)

    async def test_book_get(self, btc):
        """Test that book_get() returns a tuple of BookInfo."""
        await btc.book_add()
        try:
            books = await btc.book_get()
            assert isinstance(books, tuple)
            if len(books) > 0:
                assert isinstance(books[0], BookInfo)
        except ValueError:
            # Market depth may not be available for all symbols
            pass

    async def test_book_release(self, btc):
        """Test that book_release() returns a boolean."""
        result = await btc.book_release()
        assert isinstance(result, bool)


class TestSymbolVolume:
    """Tests for Symbol volume-related methods."""

    @pytest.fixture(scope="class")
    async def btc(self):
        symbol = Symbol(name="BTCUSD")
        await symbol.initialize()
        return symbol

    async def test_check_volume_below_min(self, btc):
        """Test check_volume with volume below minimum."""
        volume = btc.volume_min - btc.volume_step
        success, result_vol = btc.check_volume(volume=volume)
        assert success is False
        assert result_vol == btc.volume_min

    async def test_check_volume_valid(self, btc):
        """Test check_volume with a valid volume."""
        volume = btc.volume_min + btc.volume_step * 2
        success, result_vol = btc.check_volume(volume=volume)
        assert success is True
        assert result_vol == volume

    async def test_check_volume_above_max(self, btc):
        """Test check_volume with volume above maximum."""
        volume = btc.volume_max + btc.volume_step
        success, result_vol = btc.check_volume(volume=volume)
        assert success is False
        assert result_vol == btc.volume_max

    async def test_round_off_volume(self, btc):
        """Test round_off_volume rounds to nearest step."""
        volume = btc.volume_min + btc.volume_step * 2.5
        rounded = btc.round_off_volume(volume=volume, round_down=True)
        assert rounded == btc.volume_min + btc.volume_step * 2

    async def test_round_off_volume_up(self, btc):
        """Test round_off_volume rounding up."""
        volume = btc.volume_min + btc.volume_step * 2.5
        rounded = btc.round_off_volume(volume=volume, round_down=False)
        assert rounded == btc.volume_min + btc.volume_step * 3

    async def test_compute_volume_returns_min(self, btc):
        """Test that the base compute_volume() returns volume_min."""
        result = await btc.compute_volume()
        assert result == btc.volume_min


class TestSymbolCurrency:
    """Tests for Symbol currency conversion methods."""

    @pytest.fixture(scope="class")
    async def btc(self):
        symbol = Symbol(name="BTCUSD")
        await symbol.initialize()
        return symbol

    async def test_amount_in_quote_currency(self, btc):
        """Test amount_in_quote_currency returns a float."""
        result = await btc.amount_in_quote_currency(amount=100.0)
        assert isinstance(result, (int, float))

    async def test_convert_currency(self, btc):
        """Test convert_currency between two currencies."""
        result = await btc.convert_currency(
            amount=100.0, from_currency="USD", to_currency="EUR"
        )
        # Result may be None if the conversion pair is not available
        if result is not None:
            assert isinstance(result, float)
            assert result > 0


class TestSymbolRates:
    """Tests for Symbol copy rates and ticks methods."""

    @pytest.fixture(scope="class")
    async def btc(self):
        symbol = Symbol(name="BTCUSD")
        await symbol.initialize()
        return symbol

    async def test_copy_rates_from(self, btc):
        """Test copy_rates_from returns Candles."""
        start = datetime(year=2023, month=10, day=5)
        rates = await btc.copy_rates_from(
            timeframe=btc.mt5.TIMEFRAME_H1, date_from=start, count=10
        )
        assert isinstance(rates, Candles)
        assert len(rates) == 10

    async def test_copy_rates_from_pos(self, btc):
        """Test copy_rates_from_pos returns Candles."""
        rates = await btc.copy_rates_from_pos(
            timeframe=btc.mt5.TIMEFRAME_H1, count=10, start_position=0
        )
        assert isinstance(rates, Candles)
        assert len(rates) == 10

    async def test_copy_rates_range(self, btc):
        """Test copy_rates_range returns Candles."""
        start = datetime(year=2023, month=10, day=5)
        end = start + timedelta(hours=9)
        rates = await btc.copy_rates_range(
            timeframe=btc.mt5.TIMEFRAME_H1, date_from=start, date_to=end
        )
        assert isinstance(rates, Candles)
        assert len(rates) == 10

    async def test_copy_ticks_from(self, btc):
        """Test copy_ticks_from returns Ticks."""
        start = datetime(year=2023, month=10, day=5)
        ticks = await btc.copy_ticks_from(date_from=start, count=10)
        assert isinstance(ticks, Ticks)
        assert len(ticks) == 10

    async def test_copy_ticks_range(self, btc):
        """Test copy_ticks_range returns Ticks."""
        start = datetime(year=2023, month=10, day=5)
        end = start + timedelta(seconds=20)
        ticks = await btc.copy_ticks_range(date_from=start, date_to=end)
        assert isinstance(ticks, Ticks)
        assert len(ticks) >= 10


class TestSymbolProperties:
    """Tests for Symbol properties."""

    @pytest.fixture(scope="class")
    async def btc(self):
        symbol = Symbol(name="BTCUSD")
        await symbol.initialize()
        return symbol

    async def test_pip_property(self, btc):
        """Test that pip equals point * 10."""
        assert btc.pip == btc.point * 10


class TestSymbolAbstract:
    """Tests for Symbol abstract/overridable methods."""

    @pytest.fixture(scope="class")
    async def btc(self):
        symbol = Symbol(name="BTCUSD")
        await symbol.initialize()
        return symbol

    async def test_compute_volume_sl_raises(self, btc):
        """Test that compute_volume_sl raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            await btc.compute_volume_sl(amount=100.0, price=50000.0, sl=49500.0)

    async def test_compute_volume_points_raises(self, btc):
        """Test that compute_volume_points raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            await btc.compute_volume_points(amount=100.0, points=500.0)
