"""Store module for persistent key-value storage backed by SQLite.

This module provides the Store class, a persistent dictionary-like storage
backed by SQLite. Unlike the State class which stores all data as a single
pickled dictionary, Store saves each key-value pair as individual rows in
the database table, making it more suitable for larger datasets.

The Store class implements the MutableMapping interface, providing dict-like
access to data that is automatically persisted to the database.

Example:
    Basic usage::

        from aiomql.core.store import Store

        # Initialize store
        store = Store(db_name='app.db', table_name='settings')

        # Use like a dictionary
        store['api_key'] = 'your-api-key'
        store['timeout'] = 30

        # Data is persisted automatically (autocommit=True by default)
        print(store['api_key'])

        # Get all data as a dictionary
        all_data = store.data
"""

import os
import sqlite3
from threading import Lock
from typing import MutableMapping, Iterable, Any
from logging import getLogger
from pathlib import Path


SENTINEL = object()
logger = getLogger(__name__)


class Store(MutableMapping):
    """A persistent key-value store backed by SQLite.

    Implements the MutableMapping interface, allowing dict-like access to
    data that is automatically persisted to a SQLite database.

    Attributes:
        autocommit: If True, changes are committed immediately after each
            modification.
        db_name: Path to the SQLite database file.
        table_name: Name of the table used for storage.
        cursor: SQLite cursor for executing queries.
        conn: SQLite database connection.
    """

    autocommit: bool
    db_name: str
    table_name: str
    cursor: sqlite3.Cursor
    _conn: sqlite3.Connection = None
    conn: sqlite3.Connection
    lock: Lock = Lock()
    def __init__(self, db_name: str | Path = "", table_name="store", data: dict = None, flush: bool = False, autocommit: bool = True):
        """Initializes the Store with a SQLite database.

        Args:
            db_name: Path to the SQLite database file. Defaults to the
                DB_NAME environment variable or 'db.sqlite3'.
            table_name: Name of the table to use for storage.
                Defaults to 'store'.
            data: Initial data to populate the store with.
                Defaults to None.
            flush: If True, clears existing data before loading new data.
                Defaults to False.
            autocommit: If True, commits changes immediately after each
                modification. Defaults to True.
        """
        self.autocommit = autocommit
        self.db_name = db_name or os.environ.get("DB_NAME", "db.sqlite3")
        self.table_name = table_name
        if not self.autocommit:
            self.conn = self.connection(db_name)
        else:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        make_table_query = f"CREATE TABLE IF NOT EXISTS {self.table_name} (key unique, value)"
        self.conn.execute(make_table_query)
        if flush:
            flush_query = f"DELETE FROM {self.table_name}"
            self.conn.execute(flush_query)
            self.conn.commit()
        if data:
            load_query = f"REPLACE INTO {self.table_name} VALUES(?, ?)"
            self.conn.executemany(load_query, data.items())
            self.conn.commit()

    @classmethod
    def connection(cls, db_name: str | Path = ""):
        if cls._conn is not None:
            return cls._conn
        cls._conn = sqlite3.connect(db_name, check_same_thread=False)
        return cls._conn

    def __len__(self):
        """Returns the number of items in the store.

        Returns:
            int: The total count of key-value pairs in the store.
        """
        count_query = f"SELECT COUNT(*) FROM {self.table_name}"
        rows = self.cursor.execute(count_query).fetchone()[0]
        return rows if rows is not None else 0

    def __contains__(self, key):
        """Checks if a key exists in the store.

        Args:
            key: The key to check for.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        contains_query = f"SELECT 1 FROM {self.table_name} WHERE key = ?"
        return self.cursor.execute(contains_query, (key,)).fetchone() is not None

    def __getitem__(self, key):
        """Retrieves a value by its key.

        Args:
            key: The key to look up.

        Returns:
            The value associated with the key.

        Raises:
            KeyError: If the key does not exist in the store.
        """
        get_query = f"SELECT value FROM {self.table_name} WHERE key = ?"
        item = self.cursor.execute(get_query, (key,)).fetchone()
        if item is None:
            raise KeyError(key)
        return item[0]

    def __setitem__(self, key, value):
        """Sets a value for the given key.

        If the key already exists, its value is replaced.

        Args:
            key: The key to set.
            value: The value to associate with the key.
        """
        set_query = f"REPLACE INTO {self.table_name} VALUES (?, ?)"
        self.cursor.execute(set_query, (key, value))
        if self.autocommit:
            self.conn.commit()

    def __delitem__(self, key):
        """Deletes a key-value pair from the store.

        Args:
            key: The key to delete.

        Raises:
            KeyError: If the key does not exist in the store.
        """
        if key not in self:
            raise KeyError(key)
        delete_query = f"DELETE FROM {self.table_name} WHERE key = ?"
        self.cursor.execute(delete_query, (key,))
        if self.autocommit:
            self.conn.commit()

    def __iter__(self):
        """Returns an iterator over the keys in the store.

        Returns:
            Iterator: An iterator yielding keys.
        """
        return self.iterkeys()

    def __repr__(self):
        """Returns a string representation of the store.

        Returns:
            str: A string representation of the Store instance.
        """
        return f"{self.__class__.__name__}()"

    def iterkeys(self):
        """Yields keys from the store one at a time.

        Yields:
            Keys stored in the database.
        """
        key_query = f"SELECT key FROM {self.table_name}"
        for row in self.cursor.execute(key_query):
            yield row[0]

    def itervalues(self):
        """Yields values from the store one at a time.

        Yields:
            Values stored in the database.
        """
        value_query = f"SELECT value FROM {self.table_name}"
        for row in self.cursor.execute(value_query):
            yield row[0]

    def iteritems(self):
        """Yields key-value pairs from the store one at a time.

        Yields:
            tuple: A (key, value) pair.
        """
        item_query = f"SELECT key, value FROM {self.table_name}"
        for row in self.cursor.execute(item_query):
            yield row[0], row[1]

    def keys(self):
        """Returns a list of all keys in the store.

        Returns:
            list: A list containing all keys.
        """
        return list(self.iterkeys())

    def values(self):
        """Returns a list of all values in the store.

        Returns:
            list: A list containing all values.
        """
        return list(self.itervalues())

    def items(self):
        """Returns a list of all key-value pairs in the store.

        Returns:
            list[tuple]: A list of (key, value) tuples.
        """
        return list(self.iteritems())

    def update(self, data: MutableMapping | Iterable[Iterable[Any]] = None, /, **kwargs):
        """Updates the store with multiple key-value pairs.

        Args:
            data: A mapping or iterable of key-value pairs to add.
            **kwargs: Additional key-value pairs to add.
        """
        data = (dict(data if data is not None else {}) or {}) | kwargs
        update_query = f"REPLACE INTO {self.table_name} VALUES(?, ?)"
        self.conn.executemany(update_query, data.items())
        if self.autocommit:
            self.conn.commit()

    def setdefault(self, key, default = None, /):
        """Returns the value for key if it exists, otherwise sets and returns default.

        Args:
            key: The key to look up or set.
            default: The value to set if the key doesn't exist. Defaults to None.

        Returns:
            The existing value if the key exists, otherwise the default value.
        """
        if key in self:
            return self[key]
        self[key] = default
        return self[key]

    def get(self, key, /, default=None):
        """Returns the value for key if it exists, otherwise returns default.

        Args:
            key: The key to look up.
            default: The value to return if the key doesn't exist.
                Defaults to None.

        Returns:
            The value associated with the key, or default if not found.
        """
        try:
            value = self[key]
            return value
        except KeyError:
            return default

    def clear(self):
        """Removes all key-value pairs from the store."""
        clear_query = f"DELETE FROM {self.table_name}"
        self.cursor.execute(clear_query)
        if self.autocommit:
            self.conn.commit()

    def pop(self, key, /, default=SENTINEL):
        """Removes and returns the value for the given key.

        Args:
            key: The key to remove.
            default: The value to return if the key doesn't exist.
                If not provided and key doesn't exist, raises KeyError.

        Returns:
            The value that was associated with the key.

        Raises:
            KeyError: If the key doesn't exist and no default is provided.
        """
        try:
            value = self[key]
            del self[key]
            return value
        except KeyError as err:
            if default is SENTINEL:
                raise err
            return default

    @classmethod
    def commit(cls, conn: sqlite3.Connection = None, close: bool = False):
        """Commits pending changes to the database.

        Args:
            conn: The database connection to use. Defaults to self.conn.
            close: If True, closes the connection after committing.
                Defaults to False.
        """
        with cls.lock:
            conn = conn or cls.connection()
            conn.commit()
            if close:
                conn.close()

    async def acommit(self, conn: sqlite3.Connection = None, close: bool = False):
        """Asynchronously commits pending changes to the database.

        This is a convenience wrapper around commit() for async contexts.

        Args:
            conn: The database connection to use. Defaults to self.conn.
            close: If True, closes the connection after committing.
                Defaults to False.
        """
        self.commit(conn=conn, close=close)

    @property
    def data(self):
        """Returns all stored data as a dictionary.

        Returns:
            dict: A dictionary containing all key-value pairs in the store.
        """
        select_query = f"SELECT * FROM {self.table_name}"
        res = self.cursor.execute(select_query).fetchall()
        return {key: value for key, value in res}
