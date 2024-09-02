import os
from pathlib import Path
from typing import Iterator, Literal, TypeVar
import json
from logging import getLogger

from .task_queue import TaskQueue

logger = getLogger(__name__)
Bot = TypeVar("Bot")


class Config:
    """A class for handling configuration settings for the aiomql package.

    Attributes:
        record_trades (bool): Whether to keep record of trades or not.
        trade_record_mode: How to save trade, json or csv. Defaults to json
        filename (str): Name of the config file
        records_dir (str): Path to the directory where trade records are saved
        login (int): Trading account number
        password (str): Trading account password
        server (str): Broker server
        path (str): Path to terminal file
        timeout (int): Timeout for terminal connection
        state (dict): A global state dictionary for storing data across the framework
        root (str): Root directory of the project

    Notes:
        By default, the config class looks for a file named aiomql.json.
        You can change this by passing the filename and/or the config_dir keyword argument(s) to the constructor
        or the load_config method.
        By passing reload=True to the load_config method, you can reload and search again for the config file.
    """
    login: int
    trade_record_mode: Literal['csv', 'json']
    password: str
    server: str
    path: str | Path
    timeout: int
    filename: str
    state: dict
    root: Path
    record_trades: bool
    records_dir: Path
    records_dir_name: str
    test_data_dir: Path
    test_data_dir_name: str
    task_queue: TaskQueue
    bot: Bot
    _instance: 'Config'
    mode: Literal['backtest', 'live']
    use_terminal_for_backtesting: bool
    _defaults = {"timeout": 60000, "record_trades": True, "trade_record_mode": "csv", "mode": "live",
                'filename': "aiomql.json", "records_dir_name": "trade_records", "test_data_dir_name": "test_data",
                "use_terminal_for_backtesting": True, 'path': '', 'login': 0, 'password': '', 'server': ''}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance.state = {}
            cls._instance.task_queue = TaskQueue()
            cls._instance.set_attributes(**cls._defaults)
            cls._instance.load_config(**kwargs)
        return cls._instance

    def __init__(self, **kwargs):
        self.set_attributes(**kwargs)

    def set_attributes(self, **kwargs):
        """Set keyword arguments as object attributes

        Keyword Args:
            **kwargs: Object attributes and values as keyword arguments
        """
        [setattr(self, key, value) for key, value in kwargs.items()]

    @staticmethod
    def walk_to_root(path: str | Path) -> Iterator[str]:
        if not os.path.exists(path):
            raise IOError("Starting path not found")

        if os.path.isfile(path):
            path = os.path.dirname(path)

        last_dir = None
        current_dir = os.path.abspath(path)
        while last_dir != current_dir:
            yield current_dir
            parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
            last_dir, current_dir = current_dir, parent_dir

    def find_config_file(self):
        try:
            for dirname in self.walk_to_root(self.root):
                check_path = os.path.join(dirname, self.filename)
                if os.path.isfile(check_path):
                    return check_path
            return None
        except Exception as _:
            return

    def load_config(self, *, file: str | Path = None, filename: str = None, root: str | Path = None, **kwargs):
        """Load configuration settings from a file.

        Keyword Args:
            file (str | Path): The absolute path to the config file.
            filename (str): The name of the file to load if file path is not specified. If not provided aiomql.json is used
            root (str): The root directory of the project.
            kwargs: Additional keyword arguments to set as object attributes.
        """
        if root is not None:
            root = Path(root).resolve()
            root.mkdir(parents=True, exist_ok=True) if not root.exists() else ...
            self.root = root
        else:
            self.root = self.root if hasattr(self, 'root') else Path.cwd()

        if file is not None:
            file = Path(file).resolve()
            if not file.exists():
                self.filename = filename or self.filename
                file = self.find_config_file()
            else:
                self.filename = file.name
        else:
            self.filename = filename or self.filename
            file = self.find_config_file()

        if file is None:
            logger.warning("No Config File Found")
            file_config = {}
        else:
            fh = open(file, mode="r")
            file_config = json.load(fh)
            fh.close()

        data = file_config | kwargs
        self.set_attributes(**data)

        if self.record_trades and not hasattr(self, "records_dir"):
            self.records_dir = self.root / self.records_dir_name
            self.records_dir.mkdir(parents=True, exist_ok=True)

        if self.mode == "backtest" and not hasattr(self, "test_data_dir"):
            self.test_data_dir = self.root / self.test_data_dir_name
            self.test_data_dir.mkdir(parents=True, exist_ok=True)

    def account_info(self) -> dict[str, int | str]:
        """Returns Account login details as found in the config object if available

        Returns:
            dict: A dictionary of login details
        """
        return {'login': self.login, 'password': self.password, 'server': self.server}
