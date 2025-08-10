import os
import sqlite3
from typing import MutableMapping, Iterable, Any
from logging import getLogger
from pathlib import Path


SENTINEL = object()
logger = getLogger(__name__)


class Store(MutableMapping):
    autocommit: bool
    db_name: str
    cursor: sqlite3.Cursor
    conn: sqlite3.Connection

    def __init__(self, db_name: str | Path = "", data: dict = None, flush: bool = False, autocommit: bool = True):
        self.autocommit = autocommit
        self.db_name = db_name or os.environ.get("DB_NAME", "db.sqlite3")
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.conn.execute("CREATE TABLE IF NOT EXISTS store (key unique, value)")
        if flush:
            self.conn.execute("DELETE FROM store")
            self.commit()
        if data:
            self.conn.executemany("REPLACE INTO store VALUES(?, ?)", data.items())
            self.commit()

    def __len__(self):
        rows = self.cursor.execute('SELECT COUNT(*) FROM store').fetchone()[0]
        return rows if rows is not None else 0

    def __contains__(self, key):
        return self.cursor.execute('SELECT 1 FROM store WHERE key = ?', (key,)).fetchone() is not None

    def __getitem__(self, key):
        item = self.cursor.execute('SELECT value FROM store WHERE key = ?', (key,)).fetchone()
        if item is None:
            raise KeyError(key)
        return item[0]

    def __setitem__(self, key, value):
        self.cursor.execute('REPLACE INTO store (key, value) VALUES (?,?)', (key, value))
        if self.autocommit:
            self.conn.commit()

    def __delitem__(self, key):
        if key not in self:
            raise KeyError(key)
        self.cursor.execute('DELETE FROM store WHERE key = ?', (key,))
        if self.autocommit:
            self.commit()

    def __iter__(self):
        return self.iterkeys()

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def iterkeys(self):
        for row in self.cursor.execute('SELECT key FROM store'):
            yield row[0]

    def itervalues(self):
        for row in self.cursor.execute('SELECT value FROM store'):
            yield row[0]

    def iteritems(self):
        for row in self.cursor.execute('SELECT key, value FROM store'):
            yield row[0], row[1]

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def items(self):
        return list(self.iteritems())

    def update(self, data: MutableMapping | Iterable[Iterable[Any]] = None, /, **kwargs):
        data = (dict(data if data is not None else {}) or {}) | kwargs
        self.cursor.executemany("REPLACE INTO store VALUES(?, ?)", data.items())
        if self.autocommit:
            self.commit()

    def setdefault(self, key, default = None, /):
        if key in self:
            return self[key]
        self[key] = default
        return self[key]

    def get(self, key, /, default=None):
        try:
            value = self[key]
            return value
        except KeyError:
            return default

    def clear(self):
        self.cursor.execute("DELETE FROM store")
        if self.autocommit:
            self.commit()

    def pop(self, key, /, default=SENTINEL):
        try:
            value = self[key]
            del self[key]
            return value
        except KeyError as err:
            if default is SENTINEL:
                raise err
            return default

    def commit(self, conn: sqlite3.Connection = None, close: bool = False):
        conn = conn or self.conn
        conn.commit()
        if close:
            conn.close()

    async def acommit(self, conn: sqlite3.Connection = None, close: bool = False):
        self.commit(conn=conn, close=close)

    @property
    def data(self):
        res = self.cursor.execute("SELECT * FROM store").fetchall()
        return {key: value for key, value in res}
