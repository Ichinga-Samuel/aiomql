import os
from pathlib import Path
from typing import Literal, TypeVar, Self
import json
from logging import getLogger

from .task_queue import TaskQueue

logger = getLogger(__name__)
Bot = TypeVar("Bot")
BackTestEngine = TypeVar("BackTestEngine")
BackTestController = TypeVar("BackTestController")


class Config:
    login: int
    trade_record_mode: Literal["csv", "json"]
    password: str
    config_file: str | Path
    server: str
    path: str | Path
    timeout: int
    filename: str
    state: dict
    root: Path
    record_trades: bool
    records_dir: Path
    plots_dir: Path
    backtest_dir: Path
    records_dir_name: str
    plots_dir_name: str
    backtest_dir_name: str  #Todo: add to docs
    task_queue: TaskQueue
    _backtest_engine: BackTestEngine
    bot: Bot
    backtest_controller: BackTestController
    _instance: Self
    mode: Literal["backtest", "live"]
    use_terminal_for_backtesting: bool
    shutdown: bool
    force_shutdown: bool
    _defaults = {
        "timeout": 60000,
        "record_trades": True,
        "records_dir_name": "trade_records",
        "backtest_dir_name": "backtesting",
        "config_file": None,
        "trade_record_mode": "csv",
        "mode": "live",
        "filename": "aiomql.json",
        "use_terminal_for_backtesting": True,
        "path": "",
        "login": 0,
        "password": "",
        "server": "",
        "shutdown": False,
        "force_shutdown": False,
        "root": None,
        "plots_dir_name": "plots"
    }

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance.state = {}
            cls._instance.task_queue = TaskQueue(mode='infinite', workers=10)
            cls._instance.set_attributes(**cls._defaults)
            cls._instance._backtest_engine = None
            cls._instance.bot = None
            cls._instance.backtest_controller = None
        return cls._instance

    def __init__(self, **kwargs):
        """Initialize the Config object. The root directory can be set here or in the load_config method."""

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
        """Load configuration settings from a file and reset the config object.

        Args:
            config_file (str | Path): The absolute path to the config file.
            filename (str): The name of the file to load if file path is not specified. If not provided aiomql.json is used
            root (str): The root directory of the project.
            **kwargs: Additional keyword arguments to be set on the config object.
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
            fh = open(self.config_file, mode="r")
            file_config = json.load(fh)
            fh.close()

        data = file_config | kwargs
        self.set_attributes(**data)

        try:
            if self.path:
                self.path = self.root / self.path if not Path(self.path).resolve().exists() else self.path
        except Exception as err:
            logger.debug(f"Error setting path: {err}")
            self.path = ""
        return self

    @property
    def records_dir(self):
        rec_dir = self.root / self.records_dir_name or 'trade_records'
        rec_dir.mkdir(parents=True, exist_ok=True) if rec_dir.exists() is False else ...
        return rec_dir

    @property
    def backtest_dir(self) -> Path:
        b_dir = self.root / self.backtest_dir_name or 'backtesting'
        b_dir.mkdir(parents=True, exist_ok=True) if b_dir.exists() is False else ...
        return b_dir

    @property
    def plots_dir(self):
        p_dir = self.root / self.plots_dir_name or "plots"
        p_dir.mkdir(parents=True, exist_ok=True) if p_dir.exists() is False else ...
        return p_dir

    def account_info(self) -> dict[str, int | str]:
        """Returns Account login details as found in the config object if available

        Returns:
            dict[str, int | str]: A dictionary of login details
        """
        return {"login": self.login, "password": self.password, "server": self.server}


Config.__doc__ = """A class for handling configuration settings for the aiomql package.
    Attributes:
        login (int): The account login number
        trade_record_mode (Literal["csv", "json"]): The mode for recording trades
        password (str): The account password
        server (str): The account server
        path (str | Path): The path to the terminal
        timeout (int): The timeout argument for the terminal
        filename (str): The filename of the config file
        config_file (Path): The config file path
        state (dict): The
        root (Path): The root directory of the project
        record_trades (bool): To record trades or not. Default is True
        records_dir (Path): The directory to store trade records, relative to the root directory
        backtest_dir (Path): The directory to store backtest results, relative to the root directory
        task_queue (TaskQueue): The TaskQueue object for handling background tasks
        _backtest_engine (BackTestEngine): The backtest engine object
        bot (Bot): The bot object
        _instance (Self): The instance of the Config class
        mode (Literal["backtest", "live"]): The trading mode, either backtest or live, default is live
        use_terminal_for_backtesting (bool): Use the terminal for backtesting, default is True
        shutdown (bool): A signal to shut down the terminal, default is False
        force_shutdown (bool): A signal to force shut down the terminal, default is False

    Notes:
        By default, the config class looks for a file named aiomql.json. This can be changed by setting the filename
        attribute to the desired file name. The root directory of the project can be set by passing the root argument
        to the load_config method or during object instantiation. If not provided it is assumed to be the current working
        directory. All directories and files are assumed to be relative to the root directory except when an absolute path
        is provided, this includes the config file, the records_dir and the backtest_dir attributes.
        The root directory is used to locate the config file and to set the records_dir and backtest_dir attributes.
    """
