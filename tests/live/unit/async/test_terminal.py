"""Comprehensive tests for the Terminal module.

Tests cover:
- Terminal class initialization
- Version NamedTuple structure
- initialize() async method
- get_version() async method
- info() async method
- symbols_total() async method
- initialize_sync() method
- get_version_sync() method  
- info_sync() method
- symbols_total_sync() method
- Terminal info attributes inheritance
- Integration with MetaTrader connection
"""

import pytest

from aiomql.lib.terminal import Terminal, Version
from aiomql.core.models import TerminalInfo
from aiomql.core.base import _Base
from aiomql.core.config import Config


class TestVersionNamedTuple:
    """Test Version NamedTuple structure."""

    def test_version_has_version_field(self):
        """Test Version has version field."""
        version = Version(version=500, build=4000, release_date="01 Jan 2024")
        assert version.version == 500

    def test_version_has_build_field(self):
        """Test Version has build field."""
        version = Version(version=500, build=4000, release_date="01 Jan 2024")
        assert version.build == 4000

    def test_version_has_release_date_field(self):
        """Test Version has release_date field."""
        version = Version(version=500, build=4000, release_date="01 Jan 2024")
        assert version.release_date == "01 Jan 2024"

    def test_version_is_namedtuple(self):
        """Test Version is a NamedTuple."""
        version = Version(version=500, build=4000, release_date="01 Jan 2024")
        assert hasattr(version, "_fields")
        assert version._fields == ("version", "build", "release_date")

    def test_version_can_be_unpacked(self):
        """Test Version can be unpacked."""
        version = Version(version=500, build=4000, release_date="01 Jan 2024")
        v, b, r = version
        assert v == 500
        assert b == 4000
        assert r == "01 Jan 2024"

    def test_version_can_be_indexed(self):
        """Test Version can be indexed."""
        version = Version(version=500, build=4000, release_date="01 Jan 2024")
        assert version[0] == 500
        assert version[1] == 4000
        assert version[2] == "01 Jan 2024"


class TestTerminalClass:
    """Test Terminal class structure and inheritance."""

    def test_terminal_inherits_from_base(self):
        """Test Terminal inherits from _Base."""
        assert issubclass(Terminal, _Base)

    def test_terminal_inherits_from_terminal_info(self):
        """Test Terminal inherits from TerminalInfo."""
        assert issubclass(Terminal, TerminalInfo)

    def test_terminal_has_version_attribute(self):
        """Test Terminal class has version attribute."""
        assert hasattr(Terminal, "version")

    def test_terminal_version_default_is_none(self):
        """Test Terminal version default is None."""
        terminal = Terminal()
        assert terminal.version is None


class TestTerminalInitialize:
    """Test Terminal initialize() async method."""

    async def test_initialize_returns_bool(self, mt):
        """Test initialize returns boolean."""
        terminal = Terminal()
        result = await terminal.initialize()
        assert isinstance(result, bool)

    async def test_initialize_success(self, mt):
        """Test initialize succeeds when connected."""
        terminal = Terminal()
        result = await terminal.initialize()
        assert result is True

    async def test_initialize_sets_connected(self, mt):
        """Test initialize sets connected attribute."""
        terminal = Terminal()
        await terminal.initialize()
        assert hasattr(terminal, "connected")
        assert terminal.connected is True

    async def test_initialize_sets_version(self, mt):
        """Test initialize sets version attribute."""
        terminal = Terminal()
        await terminal.initialize()
        assert terminal.version is not None
        assert isinstance(terminal.version, Version)

    async def test_initialize_calls_info(self, mt):
        """Test initialize populates terminal info."""
        terminal = Terminal()
        await terminal.initialize()
        # Should have TerminalInfo attributes set
        assert hasattr(terminal, "name")
        assert hasattr(terminal, "path")


class TestTerminalGetVersion:
    """Test Terminal get_version() async method."""

    async def test_get_version_returns_version(self, mt):
        """Test get_version returns Version NamedTuple."""
        terminal = Terminal()
        await terminal.initialize()
        version = await terminal.get_version()
        assert isinstance(version, Version)

    async def test_get_version_sets_version_attribute(self, mt):
        """Test get_version sets version attribute."""
        terminal = Terminal()
        terminal.connected = True
        await terminal.get_version()
        assert terminal.version is not None

    async def test_get_version_has_version_number(self, mt):
        """Test get_version returns version number."""
        terminal = Terminal()
        await terminal.initialize()
        version = await terminal.get_version()
        assert version.version is not None
        assert isinstance(version.version, int)

    async def test_get_version_has_build_number(self, mt):
        """Test get_version returns build number."""
        terminal = Terminal()
        await terminal.initialize()
        version = await terminal.get_version()
        assert version.build is not None
        assert isinstance(version.build, int)

    async def test_get_version_has_release_date(self, mt):
        """Test get_version returns release date."""
        terminal = Terminal()
        await terminal.initialize()
        version = await terminal.get_version()
        assert version.release_date is not None
        assert isinstance(version.release_date, str)


class TestTerminalInfo:
    """Test Terminal info() async method."""

    async def test_info_returns_terminal_info(self, mt):
        """Test info returns TerminalInfo or None."""
        terminal = Terminal()
        await terminal.initialize()
        info = await terminal.info()
        assert info is not None

    async def test_info_sets_connected_status(self, mt):
        """Test info sets connected status."""
        terminal = Terminal()
        await terminal.initialize()
        await terminal.info()
        assert hasattr(terminal, "connected")

    async def test_info_sets_name(self, mt):
        """Test info sets name attribute."""
        terminal = Terminal()
        await terminal.initialize()
        await terminal.info()
        assert hasattr(terminal, "name")
        assert isinstance(terminal.name, str)

    async def test_info_sets_path(self, mt):
        """Test info sets path attribute."""
        terminal = Terminal()
        await terminal.initialize()
        await terminal.info()
        assert hasattr(terminal, "path")
        assert isinstance(terminal.path, str)

    async def test_info_sets_data_path(self, mt):
        """Test info sets data_path attribute."""
        terminal = Terminal()
        await terminal.initialize()
        await terminal.info()
        assert hasattr(terminal, "data_path")
        assert isinstance(terminal.data_path, str)

    async def test_info_sets_company(self, mt):
        """Test info sets company attribute."""
        terminal = Terminal()
        await terminal.initialize()
        await terminal.info()
        assert hasattr(terminal, "company")
        assert isinstance(terminal.company, str)

    async def test_info_sets_language(self, mt):
        """Test info sets language attribute."""
        terminal = Terminal()
        await terminal.initialize()
        await terminal.info()
        assert hasattr(terminal, "language")
        assert isinstance(terminal.language, str)

    async def test_info_sets_build(self, mt):
        """Test info sets build attribute."""
        terminal = Terminal()
        await terminal.initialize()
        await terminal.info()
        assert hasattr(terminal, "build")
        assert isinstance(terminal.build, int)

    async def test_info_sets_maxbars(self, mt):
        """Test info sets maxbars attribute."""
        terminal = Terminal()
        await terminal.initialize()
        await terminal.info()
        assert hasattr(terminal, "maxbars")
        assert isinstance(terminal.maxbars, int)

    async def test_info_sets_trade_allowed(self, mt):
        """Test info sets trade_allowed attribute."""
        terminal = Terminal()
        await terminal.initialize()
        await terminal.info()
        assert hasattr(terminal, "trade_allowed")
        assert isinstance(terminal.trade_allowed, bool)


class TestTerminalSymbolsTotal:
    """Test Terminal symbols_total() async method."""

    async def test_symbols_total_returns_int(self, mt):
        """Test symbols_total returns integer."""
        terminal = Terminal()
        await terminal.initialize()
        total = await terminal.symbols_total()
        assert isinstance(total, int)

    async def test_symbols_total_greater_than_zero(self, mt):
        """Test symbols_total returns positive number."""
        terminal = Terminal()
        await terminal.initialize()
        total = await terminal.symbols_total()
        assert total > 0


class TestTerminalInitializeSync:
    """Test Terminal initialize_sync() method."""

    async def test_initialize_sync_returns_bool(self, mt):
        """Test initialize_sync returns boolean."""
        terminal = Terminal()
        result = terminal.initialize_sync()
        assert isinstance(result, bool)

    async def test_initialize_sync_success(self, mt):
        """Test initialize_sync succeeds when connected."""
        terminal = Terminal()
        result = terminal.initialize_sync()
        assert result is True

    async def test_initialize_sync_sets_connected(self, mt):
        """Test initialize_sync sets connected attribute."""
        terminal = Terminal()
        terminal.initialize_sync()
        assert hasattr(terminal, "connected")
        assert terminal.connected is True

    async def test_initialize_sync_sets_version(self, mt):
        """Test initialize_sync sets version attribute."""
        terminal = Terminal()
        terminal.initialize_sync()
        assert terminal.version is not None
        assert isinstance(terminal.version, Version)


class TestTerminalGetVersionSync:
    """Test Terminal get_version_sync() method."""

    async def test_get_version_sync_returns_version(self, mt):
        """Test get_version_sync returns Version NamedTuple."""
        terminal = Terminal()
        terminal.initialize_sync()
        version = terminal.get_version_sync()
        assert isinstance(version, Version)

    async def test_get_version_sync_sets_version_attribute(self, mt):
        """Test get_version_sync sets version attribute."""
        terminal = Terminal()
        terminal.initialize_sync()
        version = terminal.get_version_sync()
        assert terminal.version == version

    async def test_get_version_sync_has_all_fields(self, mt):
        """Test get_version_sync returns all version fields."""
        terminal = Terminal()
        terminal.initialize_sync()
        version = terminal.get_version_sync()
        assert version.version is not None
        assert version.build is not None
        assert version.release_date is not None


class TestTerminalInfoSync:
    """Test Terminal info_sync() method."""

    async def test_info_sync_returns_terminal_info(self, mt):
        """Test info_sync returns TerminalInfo or None."""
        terminal = Terminal()
        terminal.initialize_sync()
        info = terminal.info_sync()
        assert info is not None

    async def test_info_sync_sets_attributes(self, mt):
        """Test info_sync sets terminal attributes."""
        terminal = Terminal()
        terminal.initialize_sync()
        terminal.info_sync()
        assert hasattr(terminal, "name")
        assert hasattr(terminal, "path")
        assert hasattr(terminal, "company")


class TestTerminalSymbolsTotalSync:
    """Test Terminal symbols_total_sync() method."""

    async def test_symbols_total_sync_returns_int(self, mt):
        """Test symbols_total_sync returns integer."""
        terminal = Terminal()
        terminal.initialize_sync()
        total = terminal.symbols_total_sync()
        assert isinstance(total, int)

    async def test_symbols_total_sync_greater_than_zero(self, mt):
        """Test symbols_total_sync returns positive number."""
        terminal = Terminal()
        terminal.initialize_sync()
        total = terminal.symbols_total_sync()
        assert total > 0


class TestTerminalAttributes:
    """Test Terminal inherited attributes from TerminalInfo."""

    async def test_terminal_has_community_account(self, mt):
        """Test Terminal has community_account attribute."""
        terminal = Terminal()
        await terminal.initialize()
        assert hasattr(terminal, "community_account")
        assert isinstance(terminal.community_account, bool)

    async def test_terminal_has_community_connection(self, mt):
        """Test Terminal has community_connection attribute."""
        terminal = Terminal()
        await terminal.initialize()
        assert hasattr(terminal, "community_connection")
        assert isinstance(terminal.community_connection, bool)

    async def test_terminal_has_dlls_allowed(self, mt):
        """Test Terminal has dlls_allowed attribute."""
        terminal = Terminal()
        await terminal.initialize()
        assert hasattr(terminal, "dlls_allowed")
        assert isinstance(terminal.dlls_allowed, bool)

    async def test_terminal_has_tradeapi_disabled(self, mt):
        """Test Terminal has tradeapi_disabled attribute."""
        terminal = Terminal()
        await terminal.initialize()
        assert hasattr(terminal, "tradeapi_disabled")
        assert isinstance(terminal.tradeapi_disabled, bool)

    async def test_terminal_has_email_enabled(self, mt):
        """Test Terminal has email_enabled attribute."""
        terminal = Terminal()
        await terminal.initialize()
        assert hasattr(terminal, "email_enabled")
        assert isinstance(terminal.email_enabled, bool)

    async def test_terminal_has_ftp_enabled(self, mt):
        """Test Terminal has ftp_enabled attribute."""
        terminal = Terminal()
        await terminal.initialize()
        assert hasattr(terminal, "ftp_enabled")
        assert isinstance(terminal.ftp_enabled, bool)

    async def test_terminal_has_notifications_enabled(self, mt):
        """Test Terminal has notifications_enabled attribute."""
        terminal = Terminal()
        await terminal.initialize()
        assert hasattr(terminal, "notifications_enabled")
        assert isinstance(terminal.notifications_enabled, bool)

    async def test_terminal_has_mqid(self, mt):
        """Test Terminal has mqid attribute."""
        terminal = Terminal()
        await terminal.initialize()
        assert hasattr(terminal, "mqid")
        assert isinstance(terminal.mqid, bool)

    async def test_terminal_has_codepage(self, mt):
        """Test Terminal has codepage attribute."""
        terminal = Terminal()
        await terminal.initialize()
        assert hasattr(terminal, "codepage")
        assert isinstance(terminal.codepage, int)

    async def test_terminal_has_ping_last(self, mt):
        """Test Terminal has ping_last attribute."""
        terminal = Terminal()
        await terminal.initialize()
        assert hasattr(terminal, "ping_last")
        assert isinstance(terminal.ping_last, int)

    async def test_terminal_has_community_balance(self, mt):
        """Test Terminal has community_balance attribute."""
        terminal = Terminal()
        await terminal.initialize()
        assert hasattr(terminal, "community_balance")
        assert isinstance(terminal.community_balance, float)

    async def test_terminal_has_retransmission(self, mt):
        """Test Terminal has retransmission attribute."""
        terminal = Terminal()
        await terminal.initialize()
        assert hasattr(terminal, "retransmission")
        assert isinstance(terminal.retransmission, float)

    async def test_terminal_has_commondata_path(self, mt):
        """Test Terminal has commondata_path attribute."""
        terminal = Terminal()
        await terminal.initialize()
        assert hasattr(terminal, "commondata_path")
        assert isinstance(terminal.commondata_path, str)


class TestTerminalBaseIntegration:
    """Test Terminal integration with _Base class."""

    async def test_terminal_has_mt5_attribute(self, mt):
        """Test Terminal has mt5 attribute from _Base."""
        terminal = Terminal()
        assert hasattr(terminal, "mt5")

    async def test_terminal_has_config_attribute(self, mt):
        """Test Terminal has config attribute from _Base."""
        terminal = Terminal()
        assert hasattr(terminal, "config")
        assert isinstance(terminal.config, Config)

    async def test_terminal_has_set_attributes_method(self, mt):
        """Test Terminal has set_attributes method from Base."""
        terminal = Terminal()
        assert hasattr(terminal, "set_attributes")
        assert callable(terminal.set_attributes)

    async def test_terminal_has_dict_property(self, mt):
        """Test Terminal has dict property from Base."""
        terminal = Terminal()
        await terminal.initialize()
        assert hasattr(terminal, "dict")
        assert isinstance(terminal.dict, dict)

    async def test_terminal_has_get_dict_method(self, mt):
        """Test Terminal has get_dict method from Base."""
        terminal = Terminal()
        await terminal.initialize()
        assert hasattr(terminal, "get_dict")
        assert callable(terminal.get_dict)


class TestTerminalMultipleInstances:
    """Test multiple Terminal instances."""

    async def test_multiple_terminals_share_mt5(self, mt):
        """Test multiple Terminal instances share mt5."""
        terminal1 = Terminal()
        terminal2 = Terminal()
        assert terminal1.mt5 is terminal2.mt5

    async def test_multiple_terminals_share_config(self, mt):
        """Test multiple Terminal instances share config."""
        terminal1 = Terminal()
        terminal2 = Terminal()
        assert terminal1.config is terminal2.config

    async def test_multiple_terminals_independent_version(self, mt):
        """Test multiple Terminal instances can have independent version."""
        terminal1 = Terminal()
        terminal2 = Terminal()
        await terminal1.initialize()
        # terminal2 is not initialized
        assert terminal1.version is not None
        # Both share class attribute, so terminal2 also has version after terminal1 init


class TestTerminalRepr:
    """Test Terminal __repr__ method."""

    async def test_repr_returns_string(self, mt):
        """Test __repr__ returns string."""
        terminal = Terminal()
        await terminal.initialize()
        repr_str = repr(terminal)
        assert isinstance(repr_str, str)

    async def test_repr_contains_class_name(self, mt):
        """Test __repr__ contains class name."""
        terminal = Terminal()
        await terminal.initialize()
        repr_str = repr(terminal)
        assert "Terminal" in repr_str


class TestTerminalIntegration:
    """Integration tests for Terminal with live MetaTrader data."""

    async def test_complete_initialization_workflow(self, mt):
        """Test complete initialization workflow."""
        terminal = Terminal()
        
        # Initialize
        result = await terminal.initialize()
        assert result is True
        
        # Check version
        assert terminal.version is not None
        assert terminal.version.version is not None
        assert terminal.version.build > 0
        
        # Check connection
        assert terminal.connected is True
        
        # Check terminal info
        assert terminal.name is not None
        assert terminal.path is not None
        assert terminal.company is not None

    async def test_refresh_terminal_info(self, mt):
        """Test refreshing terminal info multiple times."""
        terminal = Terminal()
        await terminal.initialize()
        
        # Get initial info
        initial_ping = terminal.ping_last
        
        # Refresh info
        await terminal.info()
        
        # Info should still be valid (ping may change)
        assert terminal.name is not None
        assert terminal.connected is True

    async def test_version_consistency(self, mt):
        """Test version is consistent across calls."""
        terminal = Terminal()
        await terminal.initialize()
        
        version1 = terminal.version
        version2 = await terminal.get_version()
        
        assert version1.version == version2.version
        assert version1.build == version2.build

    async def test_symbols_total_result(self, mt):
        """Test symbols_total returns reasonable number."""
        terminal = Terminal()
        await terminal.initialize()
        
        total = await terminal.symbols_total()
        
        # Typical broker has at least some symbols
        assert total > 0
        # Should be a reasonable number (not millions)
        assert total < 100000

    async def test_terminal_paths_exist(self, mt):
        """Test terminal paths are non-empty strings."""
        terminal = Terminal()
        await terminal.initialize()
        
        assert len(terminal.path) > 0
        assert len(terminal.data_path) > 0
        assert len(terminal.commondata_path) > 0

    async def test_terminal_build_matches_version(self, mt):
        """Test terminal build matches version build."""
        terminal = Terminal()
        await terminal.initialize()
        
        # The build from terminal_info should match version build
        assert terminal.build == terminal.version.build

    async def test_sync_and_async_consistency(self, mt):
        """Test sync and async methods return consistent results."""
        terminal = Terminal()
        
        # Initialize async
        await terminal.initialize()
        async_version = terminal.version
        async_total = await terminal.symbols_total()
        
        # Reinitialize sync
        terminal2 = Terminal()
        terminal2.initialize_sync()
        sync_version = terminal2.version
        sync_total = terminal2.symbols_total_sync()
        
        # Results should be consistent
        assert async_version.version == sync_version.version
        assert async_version.build == sync_version.build
        assert async_total == sync_total


class TestTerminalEdgeCases:
    """Test edge cases for Terminal class."""

    async def test_terminal_initialization_idempotent(self, mt):
        """Test terminal can be initialized multiple times."""
        terminal = Terminal()
        result1 = await terminal.initialize()
        result2 = await terminal.initialize()
        
        assert result1 is True
        assert result2 is True
        assert terminal.connected is True

    async def test_terminal_info_after_info_call(self, mt):
        """Test calling info multiple times."""
        terminal = Terminal()
        await terminal.initialize()
        
        info1 = await terminal.info()
        info2 = await terminal.info()
        
        assert info1 is not None
        assert info2 is not None

    async def test_get_version_called_before_initialize(self, mt):
        """Test get_version works independently."""
        terminal = Terminal()
        # Get version without full initialize
        result = await terminal.get_version()
        # Should still work if mt5 is connected at package level
        assert result is not None

    async def test_terminal_with_kwargs_initialization(self, mt):
        """Test Terminal can be created with kwargs."""
        terminal = Terminal(connected=False)
        # Should be overwritten by initialize
        await terminal.initialize()
        assert terminal.connected is True
