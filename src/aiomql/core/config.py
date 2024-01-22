import os
from pathlib import Path
from typing import Iterator
import json
from logging import getLogger

from .task_queue import TaskQueue

logger = getLogger(__name__)


class Config:
    """A class for handling configuration settings for the aiomql package.

    Attributes:
        record_trades (bool): Whether to keep record of trades or not.
        filename (str): Name of the config file
        records_dir (str): Path to the directory where trade records are saved
        win_percentage (float): Percentage of achieved target profit in a trade to be considered a win
        login (int): Trading account number
        password (str): Trading account password
        server (str): Broker server
        path (str): Path to terminal file
        timeout (int): Timeout for terminal connection
        _initialize (bool): First time initialization flag
        state (dict): A global state dictionary for storing data across the framework
        root_dir (str): The root directory of the project
    Notes:
        By default, the config class looks for a file named aiomql.json.
        You can change this by passing the filename and/or the config_dir keyword argument(s) to the constructor
        or the load_config method.
        By passing reload=True to the load_config method, you can reload and search again for the config file.
    """

    login: int = 0
    password: str = ""
    server: str = ""
    path: str = ""
    timeout: int = 60000
    record_trades: bool = True
    filename: str = "aiomql.json"
    win_percentage: float = 0.85
    records_dir = Path.home() / "Documents" / "Aiomql" / "Trade Records"
    config_dir: str = ''
    _initialize = True
    state: dict = {}
    root_dir: Path = Path('.').absolute().resolve()
    task_queue: TaskQueue = TaskQueue()

    _instance: 'Config'

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        reload = kwargs.pop('reload', False)
        [setattr(self, key, value) for key, value in kwargs.items()]
        self.load_config(reload=reload)

    def __setattr__(self, key, value):
        if key == 'root_dir':
            value = Path(value).absolute().resolve()
        super().__setattr__(key, value)

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

    def find_config(self):
        try:
            path = self.root_dir / self.config_dir
            for dirname in self.walk_to_root(path):
                check_path = os.path.join(dirname, self.filename)
                if os.path.isfile(check_path):
                    return check_path
            return None
        except Exception as _:
            return

    def load_config(self, file: str = None, reload: bool = True, filename: str = None, config_dir: str = ''):
        """Load configuration settings from a file."""
        if not (self._initialize or reload):
            return
        self._initialize = False
        data = {}
        self.filename = filename or self.filename
        self.config_dir = config_dir or self.config_dir
        if (file := (file or self.find_config())) is None:
            logger.warning("No Config File Found")
        else:
            fh = open(file, mode="r")
            data = json.load(fh)
            fh.close()
        [setattr(self, key, value) for key, value in data.items()]
        self.records_dir.mkdir(parents=True, exist_ok=True) if self.records_dir else ...

    def account_info(self) -> dict[str, int | str]:
        """Returns Account login details as found in the config object if available

        Returns:
            dict: A dictionary of login details
        """
        return {"login": self.login, "password": self.password, "server": self.server}