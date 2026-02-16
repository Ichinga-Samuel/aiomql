"""Configuration module for the aiomql trading library.

This module provides the Config class for managing all configuration settings
for the aiomql package. Settings can be loaded from a JSON configuration file
or set programmatically.

By default, the config class looks for a file named aiomql.json. This can be
changed by setting the filename attribute to the desired file name. The root
directory of the project can be set by passing the root argument to the
load_config method or during object instantiation. If not provided it is
assumed to be the current working directory. All directories and files are
assumed to be relative to the root directory.

Example:
    Basic usage::

        from aiomql import Config

        # Load config from default aiomql.json file
        config = Config()

        # Or specify a custom config file
        config = Config(config_file="/path/to/config.json")

        # Access configuration values
        print(config.login)
        print(config.server)
"""

import os
import json
from pathlib import Path
from typing import Literal, TypeVar, Self
from logging import getLogger
from threading import Lock
from functools import cached_property

from .task_queue import TaskQueue
from .state import  State
from .store import Store

logger = getLogger(__name__)
Bot = TypeVar("Bot")
BackTestEngine = TypeVar("BackTestEngine")
BackTestController = TypeVar("BackTestController")


class Config:
    """A singleton class for handling configuration settings for the aiomql package.

    This class manages all configuration settings for the aiomql trading library.
    It implements the singleton pattern to ensure consistent configuration across
    the application. Settings can be loaded from a JSON config file or set
    programmatically.

    Attributes:
        login (int): The MetaTrader account login number.
        password (str): The MetaTrader account password.
        server (str): The MetaTrader account server name.
        path (str | Path): The path to the MetaTrader terminal executable.
        timeout (int): The timeout for terminal connection in milliseconds.
            Defaults to 60000.
        config_file (str | Path): The absolute path to the configuration file.
        filename (str): The name of the config file to search for.
            Defaults to 'aiomql.json'.
        root (Path): The root directory of the project. All relative paths
            are resolved from this directory.
        trade_record_mode (Literal["csv", "json", "sql"]): The format for
            recording trades. Defaults to 'sql'.
        record_trades (bool): Whether to record trades. Defaults to True.
        records_dir (Path): The directory to store trade records.
        records_dir_name (str): The name of the trade records directory.
            Defaults to 'trade_records'.
        backtest_dir (Path): The directory to store backtest results.
        backtest_dir_name (str): The name of the backtest directory.
            Defaults to 'backtesting'.
        plots_dir (Path): The directory to store plot files.
        plots_dir_name (str): The name of the plots directory.
            Defaults to 'plots'.
        db_dir_name (str): The name of the database directory.
            Defaults to 'db'.
        db_name (str | Path): The name or path of the SQLite database file.
        state (State): A singleton key-value store for persistent state data.
        store (Store): A key-value database store for general data persistence.
        task_queue (TaskQueue): The TaskQueue object for handling background tasks.
        bot (Bot): The bot instance associated with this configuration.
        backtest_controller (BackTestController): The backtest controller instance.
        mode (Literal["backtest", "live"]): The trading mode. Defaults to 'live'.
        use_terminal_for_backtesting (bool): Whether to use the terminal for
            backtesting. Defaults to True.
        shutdown (bool): A signal to gracefully shut down the bot.
            Defaults to False.
        force_shutdown (bool): A signal to forcefully shut down the bot.
            Defaults to False.
        stop_trading (bool): A signal to stop opening new trades.
            Defaults to False.
        db_commit_interval (float): The interval in seconds for database commits.
            Defaults to 30.
        auto_commit (bool): Whether to auto-commit database changes.
            Defaults to False.
        flush_state (bool): Whether to flush state data on initialization.
            Defaults to False.
        lock (Lock): A threading lock for thread-safe operations.
    """

    login: int
    trade_record_mode: Literal["csv", "json", "sql"]
    password: str
    config_file: str | Path
    server: str
    path: str | Path
    timeout: int
    filename: str
    _state: State
    _store: Store
    root: Path
    record_trades: bool
    records_dir: Path
    plots_dir: Path
    backtest_dir: Path
    records_dir_name: str
    plots_dir_name: str
    backtest_dir_name: str
    db_dir_name: str  
    db_name: str | Path
    task_queue: TaskQueue
    _backtest_engine: BackTestEngine
    bot: Bot
    backtest_controller: BackTestController
    _instance: Self
    mode: Literal["backtest", "live"]
    use_terminal_for_backtesting: bool
    shutdown: bool
    force_shutdown: bool
    db_commit_interval: float
    auto_commit: bool
    flush_state: bool
    stop_trading: bool
    lock: Lock
    auto_commit_state: bool
    _defaults = {
        "timeout": 60000,
        "record_trades": True,
        "records_dir_name": "trade_records",
        "backtest_dir_name": "backtesting",
        "db_dir_name": "db",
        "config_file": None,
        "trade_record_mode": "sql",
        "mode": "live",
        "filename": "aiomql.json",
        "use_terminal_for_backtesting": True,
        "db_name": "",
        "path": "",
        "login": None,
        "password": "",
        "server": "",
        "shutdown": False,
        "force_shutdown": False,
        "root": None,
        "plots_dir_name": "plots",
        "db_commit_interval": 30,
        "auto_commit": False,
        "flush_state": False,
        "stop_trading": False,
        "auto_commit_state": True
    }

    def __new__(cls, *args, **kwargs):
        with (lock := Lock()) as _:
            if not hasattr(cls, "_instance"):
                cls._lock = lock
                cls._instance = super().__new__(cls)
                cls._instance.task_queue = TaskQueue(mode='infinite')
                cls._instance.set_attributes(**cls._defaults)
                cls._instance._backtest_engine = None
                cls._instance.bot = None
                cls._instance.backtest_controller = None
        return cls._instance

    def __init__(self, **kwargs):
        """Initializes the Config object.

        The root directory can be set here or in the load_config method.
        If the config has already been initialized and no root or config_file
        is provided, only the additional kwargs will be set as attributes.

        Args:
            **kwargs: Configuration attributes to set. Common options include:
                - root (str | Path): The root directory of the project.
                - config_file (str | Path): Path to the configuration file.
                - login (int): MetaTrader account login number.
                - password (str): MetaTrader account password.
                - server (str): MetaTrader server name.
        """
        root = kwargs.pop("root", None)
        config_file = kwargs.pop("config_file", None)
        if self.root is None or root is not None or config_file is not None:
            self.load_config(root=root, config_file=config_file, **kwargs)
        else:
            self.set_attributes(**kwargs)

    def __setattr__(self, name, value):
        """Set all instance attributes class as class attributes."""
        super().__setattr__(name, value)
        setattr(self.__class__, name, value)

    @property
    def backtest_engine(self):
        """Returns the backtest engine object"""
        return self._backtest_engine

    @backtest_engine.setter
    def backtest_engine(self, value: BackTestEngine):
        """Set the backtest engine object"""
        self._backtest_engine = value

    def set_attributes(self, **kwargs):
        """Set keyword arguments as object attributes. The root folder attribute can't be set here.

        Args:
            **kwargs: Object attributes and values as keyword arguments
        """
        if kwargs.get("root", None) is not None:
            kwargs.pop("root", None)
            logger.debug("Tried setting root from set_attributes. Use load_config to change project root")
        if kwargs.get("config_file", None) is not None:
            kwargs.pop("config_file", None)
            logger.debug("Tried setting config_file from set_attributes. Use load_config to change project root")
        [setattr(self, key, value) for key, value in kwargs.items()]

    def find_config_file(self):
        """Searches for the configuration file in the project directory tree.

        Starts from the current working directory and searches up through
        parent directories until the root directory is reached.

        Returns:
            Path | None: The path to the config file if found, None otherwise.
        """
        try:
            current = Path.cwd()
            current = os.path.commonpath([current, self.root])
            current = Path(current).resolve()
            config_file = current / self.filename
            if config_file.exists():
                return config_file
            if current == self.root:
                return None
            for dirname in current.parents:
                config_file = dirname / self.filename
                if config_file.exists():
                    return config_file
                if self.root == dirname:
                    break
            return None
        except Exception as err:
            logger.debug(f"Error finding config file: {err}")
            return None

    def set_root(self, root: str | Path = None):
        """Sets the root directory for the project.

        If a root path is provided, it is resolved and created if it doesn't
        exist. If no root is provided, the current working directory is used.

        Args:
            root: The path to set as the project root directory.
                Defaults to None (uses current working directory).
        """
        try:
            if root is not None:
                root = Path(root).resolve()
                root.mkdir(parents=True, exist_ok=True) if not root.exists() else ...
                self.root = root

            elif self.root is None:
                self.root = Path.cwd()

            elif not isinstance(self.root, Path):
                self.root = Path(self.root).resolve()
        except Exception as err:
            logger.warning("Error finding root path: %s. The current working directory will be used.", err)
            self.root = Path.cwd()

    def load_config(self, *, config_file: str | Path = None, filename: str = None, root: str | Path = None, **kwargs) -> Self:
        """Loads configuration settings from a file and initializes the config object.

        This method sets up the project root, locates and loads the config file,
        initializes the database connections, and sets all configuration attributes.

        Args:
            config_file: The absolute path to the config file. If provided and
                exists, this file is used directly.
            filename: The name of the file to search for if config_file is not
                specified or doesn't exist. Defaults to 'aiomql.json'.
            root: The root directory of the project. All relative paths are
                resolved from this directory.
            **kwargs: Additional configuration attributes to set. These override
                values loaded from the config file.

        Returns:
            Self: The Config instance for method chaining.
        """
        self.set_root(root=root)

        if config_file is not None:
            config_file = Path(config_file).resolve()
            if not config_file.exists():
                self.filename = filename or self.filename
                self.config_file = self.find_config_file()
            else:
                self.filename = config_file.name
                self.config_file = config_file
        else:
            self.filename = filename or self.filename
            self.config_file = self.find_config_file()

        if self.config_file is None:
            logger.debug("No Config File Found")
            file_config = {}
        else:
            file_config = {}
            with open(self.config_file, mode="r") as fh:
                file_config = json.load(fh)

        data = file_config | kwargs
        self.set_attributes(**data)
        db_name = self.db_name or (f"db_{self.login}.sqlite3" if self.login else "db.sqlite3") 
        if not Path(db_name).exists():
            db_name = self.root / self.db_dir_name / db_name
            db_name.parent.mkdir(parents=True, exist_ok=True)
            self.db_name = str(db_name)
        os.environ["DB_NAME"] = self.db_name
        self.init_state()
        self.init_store()
        try:
            if self.path:
                self.path = self.root / self.path if not Path(self.path).resolve().exists() else self.path
        except Exception as err:
            logger.debug(f"Error setting path: {err}")
            self.path = ""
        return self

    @property
    def state(self):
        """Returns the State instance for persistent key-value storage.

        Lazily initializes the state if it hasn't been created yet.

        Returns:
            State: The singleton State instance.
        """
        if not hasattr(self, "_state"):
            self.init_state()
        return self._state

    @state.setter
    def state(self, value: State):
        """Sets the State instance.

        Args:
            value: The State instance to set.
        """
        self._state = value

    @property
    def store(self):
        """Returns the Store instance for persistent key-value storage.

        Lazily initializes the store if it hasn't been created yet.

        Returns:
            Store: The Store instance.
        """
        if not hasattr(self, "_store"):
            self.init_store()
        return self._store

    @store.setter
    def store(self, value: Store):
        """Sets the Store instance.

        Args:
            value: The Store instance to set.
        """
        self._store = value

    def init_state(self):
        """Initializes the State instance with the configured database."""
        self.state = State(db_name=self.db_name, flush=self.flush_state, autocommit=self.auto_commit_state)

    def init_store(self):
        """Initializes the Store instance with the configured database."""
        self.store = Store(db_name=self.db_name, flush=self.flush_state, autocommit=self.auto_commit_state)

    @cached_property
    def records_dir(self):
        """Returns the directory path for storing trade records.

        Creates the directory if it doesn't exist.

        Returns:
            Path: The path to the trade records directory.
        """
        rec_dir = self.root / self.records_dir_name
        rec_dir.mkdir(parents=True, exist_ok=True) if rec_dir.exists() is False else ...
        return rec_dir

    @cached_property
    def backtest_dir(self) -> Path:
        """Returns the directory path for storing backtest results.

        Creates the directory if it doesn't exist.

        Returns:
            Path: The path to the backtest results directory.
        """
        b_dir = self.root / self.backtest_dir_name
        b_dir.mkdir(parents=True, exist_ok=True) if b_dir.exists() is False else ...
        return b_dir

    @cached_property
    def plots_dir(self):
        """Returns the directory path for storing plot files.

        Creates the directory if it doesn't exist.

        Returns:
            Path: The path to the plots directory.
        """
        p_dir = self.root / self.plots_dir_name
        p_dir.mkdir(parents=True, exist_ok=True) if p_dir.exists() is False else ...
        return p_dir

    @property
    def account_info(self) -> dict[str, int | str]:
        """Returns Account login details as found in the config object if available

        Returns:
            dict[str, int | str]: A dictionary of login details
        """
        return {"login": self.login, "password": self.password, "server": self.server}
