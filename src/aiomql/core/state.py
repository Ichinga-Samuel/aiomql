import os
import pickle
import sqlite3
from threading import Lock
from typing import Self
from typing import MutableMapping, Iterable, Any, ClassVar
from logging import getLogger

SENTINEL = object()
logger = getLogger(__name__)
sqlite3.register_converter("pickle", pickle.loads)
sqlite3.register_adapter(dict, pickle.dumps)

class State(MutableMapping):
    _data: ClassVar
    _instance: Self
    _lock: Lock
    db_name: str
    autocommit: bool
    _initialized = False

    def __new__(cls, *args, **kwargs):
        with (lock := Lock()) as _:
            if not hasattr(cls, '_instance'):
                cls._data = {}
                cls._lock = lock
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_name: str = "", data: dict = None, flush: bool = False, autocommit: bool = False):
        with self._lock:
            self.autocommit = autocommit
            self.init(data=data, flush=flush, db_name=db_name)

    @property
    def data(self):
        return self.__class__._data

    @data.setter
    def data(self, value):
        assert isinstance(value, dict)
        self.__class__._data = value

    def __repr__(self):
        return repr(self.data)

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return key in self.data

    def __setitem__(self, key, value):
        self.data[key] = value
        if self.autocommit:
            self.commit()

    def __getitem__(self, key):
        value = self.data[key]
        return value

    def __delitem__(self, key):
        del self.data[key]
        if self.autocommit:
            self.commit()

    def pop(self, key, default=SENTINEL):
        if default is SENTINEL:
            value = self.data.pop(key)
        else:
            value = self.data.pop(key, default)
        if self.autocommit:
            self.commit()
        return value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def update(self, data: MutableMapping | Iterable[Iterable[Any]] = None, /, **kwargs):
        self.data.update(data, **kwargs)
        if self.autocommit:
            self.commit()

    def setdefault(self, key, default = None, /):
        value = self.data.setdefault(key, default)
        if self.autocommit:
            self.commit()
        return value

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    def load(self, *, conn = None, db_name: str = "", data: dict = None):
        try:
            db_name = db_name or self.db_name
            conn = conn or self.conn
            res = conn.execute("SELECT value FROM state where key = 'data'").fetchone()
            db_data = pickle.loads(res[0]) if res else {}
            db_data |= (data or {})
            self.update(db_data)
        except Exception as err:
            logger.error("%s: Failed to load data from database", err)

    def init(self, data: dict = None, flush: bool = False, db_name: str = ""):
        if not self._initialized:
            self.db_name = db_name or os.environ.get("DB_NAME", "db.sqlite3")
            conn = self.conn
            conn.execute("CREATE TABLE IF NOT EXISTS state (key text unique, value blob)")
            self._initialized = True
            if flush:
                self.data = data or {}
                self.commit(conn=conn)
            else:
                self.load(conn=conn, data=data)
                conn.close()

        if flush:
            self.data = data or {}
            self.commit()

    def commit(self, *, conn: sqlite3.Connection = None, close: bool = True):
        value = pickle.dumps(self.data, protocol=pickle.HIGHEST_PROTOCOL)
        value = sqlite3.Binary(value)
        conn = conn or self.conn
        conn.execute("REPLACE INTO state (key, value) VALUES ('data', ?)", (value,))
        conn.commit()
        if close:
            conn.close()

    @property
    def conn(self):
        return sqlite3.connect(self.db_name)

    async def acommit(self, conn=None, close=True):
        conn = conn or self.conn
        value = pickle.dumps(self.data, protocol=pickle.HIGHEST_PROTOCOL)
        value = sqlite3.Binary(value)
        conn.execute("REPLACE INTO state (key, value) VALUES ('data', ?)", (value,))
        conn.commit()
        if close:
            conn.close()
