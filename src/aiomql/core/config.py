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
    trade_record_mode: Literal['csv', 'json'] = 'csv'
    password: str = ""
    server: str = ""
    path: str | Path = ""
    timeout: int = 60000
    record_trades: bool = True
    filename: str = "aiomql.json"
    _initialize = True
    state: dict = {}
    root: Path
    root_dir: Path
    records_dir: Path
    config_dir: str = ''
    task_queue: TaskQueue = TaskQueue()
    bot: Bot = None
    _instance: 'Config'

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        reload = kwargs.pop('reload', False)
        self.load_config(reload=reload, **kwargs)

    def set_root(self, *, root: str | Path):
        root = Path(root) if str else root
        self.root = root.absolute().resolve()
        self.root_dir = self.root

    def __setattr__(self, key, value):
        if key == 'path':
            value = str(self.root_dir / Path(value).absolute().resolve())
        super().__setattr__(key, value)

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

    def create_records_dir(self, *, records_dir: str | Path = 'records'):
        """Create records directory if it does not exist. By default, it is relative to the root directory of the
         project unless an absolute path is provided.

        Keyword Args:
            records_dir (str|Path): The directory to save trade records. Default is 'records'
        """
        try:
            if isinstance(records_dir, str):
                records_dir = self.root_dir / records_dir
            elif isinstance(records_dir, Path):
                records_dir = records_dir.absolute().resolve()
            records_dir.mkdir(parents=True, exist_ok=True)
            self.records_dir = records_dir
        except Exception as err:
            logger.warning(f"{err}: Unable to create records directory")

    def load_config(self, *, file: str = None, reload: bool = True, filename: str = None,
                    config_dir: str = '', **kwargs):
        """Load configuration settings from a file.
        Keyword Args:
            file (str): The path to the file to load. If not provided, the file is searched for
            reload (bool): Whether to reload the config object. Default is True
            filename (str): The name of the file to load. If not provided, the default filename is used
            config_dir (str): The name of the directory to search for the file. Default is the root directory
            root_dir (str): The root directory of the project
            kwargs: Additional keyword arguments
        """
        if not (self._initialize or reload):
            return
        data = {}
        self.filename = filename or self.filename
        self.config_dir = config_dir or self.config_dir
        root_dir = kwargs.pop('root_dir', None)
        records_dir = kwargs.pop('records_dir', 'records')
        if self._initialize or (root_dir is not None):
            self.set_root(root=(root_dir or '.'))
            self.create_records_dir(records_dir=records_dir)

        if (file := (file or self.find_config())) is None:
            logger.warning("No Config File Found")
        else:
            fh = open(file, mode="r")
            data = json.load(fh)
            fh.close()
        data |= kwargs
        self.set_attributes(**data)
        self._initialize = False

    def account_info(self) -> dict[str, int | str]:
        """Returns Account login details as found in the config object if available

        Returns:
            dict: A dictionary of login details
        """
        return {"login": self.login, "password": self.password, "server": self.server}
