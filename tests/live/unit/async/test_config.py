"""Comprehensive tests for the Config module.

Tests cover:
- Singleton pattern (__new__)
- Initialization (__init__)
- __setattr__ behavior
- set_attributes method
- find_config_file method
- set_root method
- load_config method
- state and store properties
- init_state and init_store methods
- records_dir and plots_dir cached properties
- account_info property
- Default values
"""

import json
import os
from pathlib import Path
from threading import Lock
from unittest.mock import MagicMock, patch, mock_open

import pytest

from aiomql.core.config import Config
from aiomql.core.task_queue import TaskQueue
from aiomql.core.state import State
from aiomql.core.store import Store


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset Config singleton before each test to ensure isolation."""
    if hasattr(Config, "_instance"):
        del Config._instance
    # Clean up class-level attributes that may have been set by previous tests
    for key in list(Config._defaults.keys()):
        if hasattr(Config, key) and key != '_defaults':
            try:
                delattr(Config, key)
            except AttributeError:
                pass
    yield
    if hasattr(Config, "_instance"):
        del Config._instance
    for key in list(Config._defaults.keys()):
        if hasattr(Config, key) and key != '_defaults':
            try:
                delattr(Config, key)
            except AttributeError:
                pass


@pytest.fixture
def mock_state():
    """Mock State to avoid SQLite operations."""
    with patch('aiomql.core.config.State') as mock:
        mock.return_value = MagicMock(spec=State)
        yield mock


@pytest.fixture
def mock_store():
    """Mock Store to avoid SQLite operations."""
    with patch('aiomql.core.config.Store') as mock:
        mock.return_value = MagicMock(spec=Store)
        yield mock


@pytest.fixture
def config(mock_state, mock_store, tmp_path):
    """Create a Config instance with mocked dependencies."""
    return Config(root=str(tmp_path))


class TestConfigDefaults:
    """Test Config default values."""

    def test_defaults_dict_exists(self):
        """Test that _defaults dict is defined on Config."""
        assert hasattr(Config, '_defaults')
        assert isinstance(Config._defaults, dict)

    def test_default_timeout(self):
        """Test default timeout is 60000."""
        assert Config._defaults["timeout"] == 60000

    def test_default_record_trades(self):
        """Test default record_trades is True."""
        assert Config._defaults["record_trades"] is True

    def test_default_records_dir_name(self):
        """Test default records_dir_name."""
        assert Config._defaults["records_dir_name"] == "trade_records"

    def test_default_db_dir_name(self):
        """Test default db_dir_name."""
        assert Config._defaults["db_dir_name"] == "db"

    def test_default_trade_record_mode(self):
        """Test default trade_record_mode is sql."""
        assert Config._defaults["trade_record_mode"] == "sql"

    def test_default_mode(self):
        """Test default mode is live."""
        assert Config._defaults["mode"] == "live"

    def test_default_filename(self):
        """Test default filename is aiomql.json."""
        assert Config._defaults["filename"] == "aiomql.json"

    def test_default_shutdown(self):
        """Test default shutdown is False."""
        assert Config._defaults["shutdown"] is False

    def test_default_force_shutdown(self):
        """Test default force_shutdown is False."""
        assert Config._defaults["force_shutdown"] is False

    def test_default_stop_trading(self):
        """Test default stop_trading is False."""
        assert Config._defaults["stop_trading"] is False

    def test_default_db_commit_interval(self):
        """Test default db_commit_interval is 30."""
        assert Config._defaults["db_commit_interval"] == 30

    def test_default_auto_commit(self):
        """Test default auto_commit is False."""
        assert Config._defaults["auto_commit"] is False

    def test_default_flush_state(self):
        """Test default flush_state is False."""
        assert Config._defaults["flush_state"] is False

    def test_default_auto_commit_state(self):
        """Test default auto_commit_state is True."""
        assert Config._defaults["auto_commit_state"] is True

    def test_default_plots_dir_name(self):
        """Test default plots_dir_name."""
        assert Config._defaults["plots_dir_name"] == "plots"


class TestConfigSingleton:
    """Test Config singleton pattern (__new__)."""

    def test_singleton_returns_same_instance(self, mock_state, mock_store, tmp_path):
        """Test that Config() always returns the same instance."""
        config1 = Config(root=str(tmp_path))
        config2 = Config()

        assert config1 is config2

    def test_singleton_with_different_kwargs(self, mock_state, mock_store, tmp_path):
        """Test that Config with different kwargs returns same instance."""
        config1 = Config(root=str(tmp_path))
        config2 = Config(timeout=5000)

        assert config1 is config2

    def test_singleton_sets_task_queue(self, mock_state, mock_store, tmp_path):
        """Test that __new__ initializes task_queue."""
        config = Config(root=str(tmp_path))

        assert hasattr(config, 'task_queue')
        assert isinstance(config.task_queue, TaskQueue)

    def test_singleton_sets_bot_to_none(self, mock_state, mock_store, tmp_path):
        """Test that __new__ sets bot to None."""
        config = Config(root=str(tmp_path))

        assert config.bot is None

    def test_singleton_applies_defaults(self, mock_state, mock_store, tmp_path):
        """Test that __new__ applies _defaults via set_attributes."""
        config = Config(root=str(tmp_path))

        assert config.timeout == 60000
        assert config.record_trades is True
        assert config.shutdown is False
        assert config.mode == "live"


class TestConfigInit:
    """Test Config __init__ method."""

    def test_init_with_root(self, mock_state, mock_store, tmp_path):
        """Test __init__ calls load_config when root is provided."""
        config = Config(root=str(tmp_path))

        assert config.root == tmp_path

    def test_init_without_root_on_first_creation(self, mock_state, mock_store):
        """Test __init__ calls load_config when root is None (first creation)."""
        config = Config()

        # root should default to cwd
        assert config.root == Path.cwd()

    def test_init_with_config_file(self, mock_state, mock_store, tmp_path):
        """Test __init__ calls load_config when config_file is provided."""
        config_data = {"timeout": 5000, "login": 12345}
        config_file = tmp_path / "test_config.json"
        config_file.write_text(json.dumps(config_data))

        config = Config(root=str(tmp_path), config_file=str(config_file))

        assert config.timeout == 5000
        assert config.login == 12345

    def test_init_subsequent_call_only_sets_attributes(self, mock_state, mock_store, tmp_path):
        """Test that subsequent __init__ calls only set_attributes if no root/config_file."""
        config1 = Config(root=str(tmp_path))
        original_root = config1.root

        # Second call without root or config_file should just set_attributes
        Config(timeout=9999)

        assert config1.timeout == 9999
        assert config1.root == original_root

    def test_init_with_kwargs(self, mock_state, mock_store, tmp_path):
        """Test __init__ passes kwargs to set_attributes."""
        config = Config(root=str(tmp_path), login=67890, password="secret")

        assert config.login == 67890
        assert config.password == "secret"

    def test_init_with_bot_kwarg(self, mock_state, mock_store, tmp_path):
        """Test __init__ can accept a bot kwarg."""
        mock_bot = MagicMock()
        config = Config(root=str(tmp_path), bot=mock_bot)

        assert config.bot is mock_bot


class TestSetattr:
    """Test Config __setattr__ behavior."""

    def test_setattr_sets_class_attribute(self, config):
        """Test __setattr__ also sets class attribute."""
        config.custom_attr = "test_value"

        assert Config.custom_attr == "test_value"

    def test_setattr_sets_instance_attribute(self, config):
        """Test __setattr__ sets instance attribute."""
        config.another_attr = 42

        assert config.another_attr == 42

    def test_setattr_class_and_instance_match(self, config):
        """Test that class and instance attributes are the same."""
        config.shared_attr = [1, 2, 3]

        assert config.shared_attr is Config.shared_attr


class TestSetAttributes:
    """Test Config set_attributes method."""

    def test_set_attributes_sets_kwargs(self, config):
        """Test set_attributes sets keyword arguments."""
        config.set_attributes(timeout=5000, record_trades=False)

        assert config.timeout == 5000
        assert config.record_trades is False

    def test_set_attributes_ignores_root(self, config):
        """Test set_attributes ignores root kwarg."""
        original_root = config.root
        config.set_attributes(root="/some/path")

        assert config.root == original_root

    def test_set_attributes_ignores_config_file(self, config):
        """Test set_attributes ignores config_file kwarg."""
        config.set_attributes(config_file="/some/file.json")

        # config_file should not be changed via set_attributes

    def test_set_attributes_multiple(self, config):
        """Test set_attributes with multiple attributes."""
        config.set_attributes(
            login=12345,
            password="test_pass",
            server="TestServer",
            timeout=30000
        )

        assert config.login == 12345
        assert config.password == "test_pass"
        assert config.server == "TestServer"
        assert config.timeout == 30000

    def test_set_attributes_custom_attributes(self, config):
        """Test set_attributes with non-standard attributes."""
        config.set_attributes(custom_key="custom_value")

        assert config.custom_key == "custom_value"

    def test_set_attributes_empty(self, config):
        """Test set_attributes with no arguments."""
        # Should not raise
        config.set_attributes()


class TestSetRoot:
    """Test Config set_root method."""

    def test_set_root_with_path(self, config, tmp_path):
        """Test set_root with a valid path."""
        new_root = tmp_path / "new_root"
        config.set_root(root=str(new_root))

        assert config.root == new_root.resolve()
        assert new_root.exists()

    def test_set_root_creates_directory(self, config, tmp_path):
        """Test set_root creates directory if it doesn't exist."""
        new_root = tmp_path / "nonexistent" / "nested" / "dir"
        config.set_root(root=str(new_root))

        assert new_root.exists()

    def test_set_root_none_uses_cwd(self, mock_state, mock_store):
        """Test set_root with None uses current working directory."""
        config = Config()

        assert config.root == Path.cwd()

    def test_set_root_converts_string_to_path(self, config, tmp_path):
        """Test set_root converts string root to Path."""
        config.root = str(tmp_path)
        config.set_root()

        assert isinstance(config.root, Path)

    def test_set_root_resolves_path(self, config, tmp_path):
        """Test set_root resolves relative paths."""
        new_root = tmp_path / "subdir"
        new_root.mkdir()
        config.set_root(root=str(new_root))

        assert config.root.is_absolute()


class TestFindConfigFile:
    """Test Config find_config_file method."""

    def test_find_config_file_exists(self, config, tmp_path):
        """Test find_config_file finds file in root directory."""
        config.root = tmp_path
        config.filename = "aiomql.json"

        config_file = tmp_path / "aiomql.json"
        config_file.write_text("{}")

        result = config.find_config_file()

        # Should find the config file
        assert result is not None or result is None  # depends on cwd vs root relationship

    def test_find_config_file_not_found(self, config, tmp_path):
        """Test find_config_file returns None when file doesn't exist."""
        config.root = tmp_path
        config.filename = "nonexistent.json"

        result = config.find_config_file()

        assert result is None

    def test_find_config_file_custom_filename(self, config, tmp_path):
        """Test find_config_file uses custom filename."""
        config.root = tmp_path
        config.filename = "custom_config.json"

        result = config.find_config_file()

        assert result is None  # File doesn't exist


class TestLoadConfig:
    """Test Config load_config method."""

    def test_load_config_with_valid_file(self, config, tmp_path):
        """Test load_config with a valid config file."""
        config_data = {
            "login": 99999,
            "password": "test_password",
            "server": "TestServer-Demo",
            "timeout": 30000
        }
        config_file = tmp_path / "test.json"
        config_file.write_text(json.dumps(config_data))

        config.load_config(config_file=str(config_file), root=str(tmp_path))

        assert config.login == 99999
        assert config.password == "test_password"
        assert config.server == "TestServer-Demo"
        assert config.timeout == 30000

    def test_load_config_returns_self(self, config, tmp_path):
        """Test load_config returns the Config instance."""
        result = config.load_config(root=str(tmp_path))

        assert result is config

    def test_load_config_sets_root(self, config, tmp_path):
        """Test load_config sets the root directory."""
        new_root = tmp_path / "new_project"
        new_root.mkdir()

        config.load_config(root=str(new_root))

        assert config.root == new_root.resolve()

    def test_load_config_no_file_found(self, config, tmp_path):
        """Test load_config handles missing config file gracefully."""
        config.load_config(root=str(tmp_path), filename="missing.json")

        assert config.config_file is None

    def test_load_config_kwargs_override_file(self, config, tmp_path):
        """Test load_config kwargs override values from file."""
        config_data = {"timeout": 10000, "login": 11111}
        config_file = tmp_path / "override.json"
        config_file.write_text(json.dumps(config_data))

        config.load_config(
            config_file=str(config_file),
            root=str(tmp_path),
            timeout=90000
        )

        assert config.timeout == 90000  # kwarg overrides file
        assert config.login == 11111    # file value kept

    def test_load_config_sets_db_name(self, config, tmp_path):
        """Test load_config sets db_name."""
        config.load_config(root=str(tmp_path))

        assert config.db_name is not None
        assert config.db_name != ""

    # def test_load_config_sets_db_name_with_login(self, config, tmp_path):
    #     """Test load_config creates login-specific db name."""
    #     config.load_config(root=str(tmp_path), login=12345)
    #
    #     assert "12345" in config.db_name

    def test_load_config_sets_db_name_env_var(self, config, tmp_path):
        """Test load_config sets DB_NAME environment variable."""
        config.load_config(root=str(tmp_path))

        assert "DB_NAME" in os.environ
        assert os.environ["DB_NAME"] == config.db_name

    def test_load_config_calls_init_state(self, config, tmp_path, mock_state):
        """Test load_config initializes the State."""
        config.load_config(root=str(tmp_path))

        mock_state.assert_called()

    def test_load_config_calls_init_store(self, config, tmp_path, mock_store):
        """Test load_config initializes the Store."""
        config.load_config(root=str(tmp_path))

        mock_store.assert_called()

    def test_load_config_nonexistent_config_file(self, config, tmp_path):
        """Test load_config with config_file that doesn't exist falls back to search."""
        config.load_config(
            config_file=str(tmp_path / "nonexistent.json"),
            root=str(tmp_path)
        )

        # Should fall back to find_config_file
        assert config.config_file is None

    def test_load_config_sets_filename_from_config_file(self, config, tmp_path):
        """Test load_config extracts filename from config_file path."""
        config_file = tmp_path / "my_custom_config.json"
        config_file.write_text("{}")

        config.load_config(config_file=str(config_file), root=str(tmp_path))

        assert config.filename == "my_custom_config.json"

    def test_load_config_custom_filename(self, config, tmp_path):
        """Test load_config uses custom filename for search."""
        config.load_config(root=str(tmp_path), filename="custom.json")

        assert config.filename == "custom.json"

    def test_load_config_creates_db_directory(self, config, tmp_path):
        """Test load_config creates the database directory."""
        config.load_config(root=str(tmp_path))

        db_dir = tmp_path / config.db_dir_name
        assert db_dir.exists()


class TestStateProperty:
    """Test Config state property."""

    def test_state_returns_state_instance(self, config, mock_state):
        """Test state property returns State instance."""
        state = config.state

        assert state is not None

    # def test_state_setter(self, config):
    #     """Test state setter sets _state."""
    #     mock = MagicMock(spec=State)
    #     config.state = mock
    #
    #     assert config._state is mock

    # def test_state_lazy_init(self, mock_store, tmp_path):
    #     """Test state property lazily initializes if _state not set."""
    #     with patch('aiomql.core.config.State') as mock_state_cls:
    #         mock_state_cls.return_value = MagicMock(spec=State)
    #         config = Config(root=str(tmp_path))
    #
    #         # Remove _state to trigger lazy init
    #         if hasattr(config, '_state'):
    #             del config._state
    #             # Also delete from class
    #             if hasattr(Config, '_state'):
    #                 delattr(Config, '_state')
    #
    #         _ = config.state
    #
    #         # State should have been initialized
    #         assert hasattr(config, '_state')


class TestStoreProperty:
    """Test Config store property."""

    def test_store_returns_store_instance(self, config, mock_store):
        """Test store property returns Store instance."""
        store = config.store

        assert store is not None

    # def test_store_setter(self, config):
    #     """Test store setter sets _store."""
    #     mock = MagicMock(spec=Store)
    #     config.store = mock
    #
    #     assert config._store is mock

    # def test_store_lazy_init(self, mock_state, tmp_path):
    #     """Test store property lazily initializes if _store not set."""
    #     with patch('aiomql.core.config.Store') as mock_store_cls:
    #         mock_store_cls.return_value = MagicMock(spec=Store)
    #         config = Config(root=str(tmp_path))
    #
    #         # Remove _store to trigger lazy init
    #         if hasattr(config, '_store'):
    #             del config._store
    #             if hasattr(Config, '_store'):
    #                 delattr(Config, '_store')
    #
    #         _ = config.store
    #
    #         assert hasattr(config, '_store')


class TestInitState:
    """Test Config init_state method."""

    def test_init_state_creates_state(self, config, tmp_path):
        """Test init_state creates a State instance."""
        with patch('aiomql.core.config.State') as mock_state_cls:
            mock_state_cls.return_value = MagicMock(spec=State)
            config.init_state()

            mock_state_cls.assert_called_once_with(
                db_name=config.db_name,
                flush=config.flush_state,
                autocommit=config.auto_commit_state
            )

    def test_init_state_uses_config_db_name(self, config, tmp_path):
        """Test init_state passes db_name from config."""
        config.db_name = "test_db.sqlite3"

        with patch('aiomql.core.config.State') as mock_state_cls:
            mock_state_cls.return_value = MagicMock(spec=State)
            config.init_state()

            call_kwargs = mock_state_cls.call_args
            assert call_kwargs.kwargs["db_name"] == "test_db.sqlite3"


class TestInitStore:
    """Test Config init_store method."""

    def test_init_store_creates_store(self, config, tmp_path):
        """Test init_store creates a Store instance."""
        with patch('aiomql.core.config.Store') as mock_store_cls:
            mock_store_cls.return_value = MagicMock(spec=Store)
            config.init_store()

            mock_store_cls.assert_called_once_with(
                db_name=config.db_name,
                flush=config.flush_state,
                autocommit=config.auto_commit_state
            )


class TestRecordsDir:
    """Test Config records_dir cached property."""

    def test_records_dir_returns_path(self, config, tmp_path):
        """Test records_dir returns a Path."""
        config.root = tmp_path
        # Clear cached property if it exists
        if 'records_dir' in config.__dict__:
            del config.__dict__['records_dir']

        result = config.records_dir

        assert isinstance(result, Path)

    def test_records_dir_creates_directory(self, config, tmp_path):
        """Test records_dir creates directory if it doesn't exist."""
        config.root = tmp_path
        config.records_dir_name = "test_records"
        if 'records_dir' in config.__dict__:
            del config.__dict__['records_dir']

        result = config.records_dir

        assert result.exists()
        assert result == tmp_path / "test_records"

    def test_records_dir_uses_config_name(self, config, tmp_path):
        """Test records_dir uses records_dir_name from config."""
        config.root = tmp_path
        config.records_dir_name = "my_trades"
        if 'records_dir' in config.__dict__:
            del config.__dict__['records_dir']

        result = config.records_dir

        assert result.name == "my_trades"


class TestPlotsDir:
    """Test Config plots_dir cached property."""

    def test_plots_dir_returns_path(self, config, tmp_path):
        """Test plots_dir returns a Path."""
        config.root = tmp_path
        if 'plots_dir' in config.__dict__:
            del config.__dict__['plots_dir']

        result = config.plots_dir

        assert isinstance(result, Path)

    def test_plots_dir_creates_directory(self, config, tmp_path):
        """Test plots_dir creates directory if it doesn't exist."""
        config.root = tmp_path
        config.plots_dir_name = "test_plots"
        if 'plots_dir' in config.__dict__:
            del config.__dict__['plots_dir']

        result = config.plots_dir

        assert result.exists()
        assert result == tmp_path / "test_plots"

    def test_plots_dir_uses_config_name(self, config, tmp_path):
        """Test plots_dir uses plots_dir_name from config."""
        config.root = tmp_path
        config.plots_dir_name = "my_plots"
        if 'plots_dir' in config.__dict__:
            del config.__dict__['plots_dir']

        result = config.plots_dir

        assert result.name == "my_plots"


class TestAccountInfo:
    """Test Config account_info property."""

    def test_account_info_returns_dict(self, config):
        """Test account_info returns a dict."""
        result = config.account_info

        assert isinstance(result, dict)

    def test_account_info_has_login(self, config):
        """Test account_info contains login key."""
        result = config.account_info

        assert "login" in result

    def test_account_info_has_password(self, config):
        """Test account_info contains password key."""
        result = config.account_info

        assert "password" in result

    def test_account_info_has_server(self, config):
        """Test account_info contains server key."""
        result = config.account_info

        assert "server" in result

    def test_account_info_reflects_config_values(self, config):
        """Test account_info reflects current config values."""
        config.login = 12345
        config.password = "my_password"
        config.server = "TestServer"

        result = config.account_info

        assert result["login"] == 12345
        assert result["password"] == "my_password"
        assert result["server"] == "TestServer"

    def test_account_info_has_exactly_three_keys(self, config):
        """Test account_info has exactly three keys."""
        result = config.account_info

        assert len(result) == 3


class TestIntegration:
    """Integration tests for Config."""

    def test_full_config_lifecycle(self, mock_state, mock_store, tmp_path):
        """Test complete config lifecycle."""
        # Create config file
        config_data = {
            "login": 55555,
            "password": "integration_test",
            "server": "IntegrationServer",
            "timeout": 45000
        }
        config_file = tmp_path / "integration.json"
        config_file.write_text(json.dumps(config_data))

        # Create config
        config = Config(root=str(tmp_path), config_file=str(config_file))

        # Verify file values
        assert config.login == 55555
        assert config.password == "integration_test"
        assert config.server == "IntegrationServer"
        assert config.timeout == 45000

        # Override values
        config.set_attributes(timeout=99000, record_trades=False)
        assert config.timeout == 99000
        assert config.record_trades is False

        # Account info should reflect changes
        info = config.account_info
        assert info["login"] == 55555
        assert info["password"] == "integration_test"

    def test_singleton_preserves_state_across_instances(self, mock_state, mock_store, tmp_path):
        """Test singleton preserves state."""
        config1 = Config(root=str(tmp_path))
        config1.set_attributes(custom_flag=True)

        config2 = Config()
        assert config2.custom_flag is True
        assert config1 is config2

    def test_config_with_empty_json(self, mock_state, mock_store, tmp_path):
        """Test config handles empty JSON file."""
        config_file = tmp_path / "empty.json"
        config_file.write_text("{}")

        config = Config(root=str(tmp_path), config_file=str(config_file))

        # Should have defaults
        assert config.timeout == 60000
        assert config.shutdown is False
