"""State management module for persistent singleton key-value storage.

This module provides the State class, a singleton implementation of a
persistent dictionary-like storage backed by SQLite. The State class
implements the MutableMapping interface, providing dict-like access to
data that is automatically persisted to a database.

The entire state is stored as a single pickled dictionary in the database,
making it suitable for storing application-wide configuration and state
that needs to persist across sessions.

Example:
    Basic usage::

        from aiomql.core.state import State

        # Initialize state (singleton - same instance returned each time)
        state = State()

        # Use like a dictionary
        state['key'] = 'value'
        print(state['key'])

        # Persist changes to database
        state.commit()
"""

import os
import pickle
import sqlite3
from pathlib import Path
from threading import Lock
from typing import Self
from typing import MutableMapping, Iterable, Any, ClassVar
from logging import getLogger

SENTINEL = object()
logger = getLogger(__name__)
sqlite3.register_converter("pickle", pickle.loads)
sqlite3.register_adapter(dict, pickle.dumps)

class State(MutableMapping):
    """A singleton persistent key-value store backed by SQLite.

    Implements the MutableMapping interface, providing dict-like access to
    data that is automatically persisted to a SQLite database. The entire
    state is stored as a single pickled dictionary, making it suitable for
    application-wide state management.

    This class uses the singleton pattern - all instances share the same
    underlying data and database connection.

    Attributes:
        _data (ClassVar[dict]): The shared dictionary storing all state data.
        _instance (Self): The singleton instance.
        _lock (Lock): Thread lock for thread-safe operations.
        db_name (str): Path to the SQLite database file.
        autocommit (bool): If True, changes are committed immediately.
        _initialized (bool): Whether the state has been initialized.

    Example:
        >>> state = State(db_name='app.db')
        >>> state['user'] = {'name': 'John', 'id': 123}
        >>> state.commit()
        >>> print(state['user']['name'])
        John
    """

    _data: ClassVar
    _instance: Self
    _lock: Lock
    db_name: str
    autocommit: bool
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Creates or returns the singleton instance.

        Returns:
            State: The singleton State instance.
        """
        with (lock := Lock()) as _:
            if not hasattr(cls, '_instance'):
                cls._data = {}
                cls._lock = lock
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_name: str | Path = "", data: dict = None, flush: bool = False, autocommit: bool = True):
        """Initializes the State instance.

        Args:
            db_name: Path to the SQLite database file. Defaults to the
                DB_NAME environment variable or 'db.sqlite3'.
            data: Initial data to merge into the state. Defaults to None.
            flush: If True, clears existing data and replaces with provided
                data. Defaults to False.
            autocommit: If True, commits changes immediately after each
                modification. Defaults to False.
        """
        with self._lock:
            self.autocommit = autocommit
            self.init(data=data, flush=flush, db_name=db_name)

    @property
    def data(self):
        """Returns the shared state dictionary.

        Returns:
            dict: The state data dictionary.
        """
        return self.__class__._data

    @data.setter
    def data(self, value):
        """Sets the state dictionary.

        Args:
            value: The dictionary to set as state data.

        Raises:
            AssertionError: If value is not a dictionary.
        """
        assert isinstance(value, dict)
        self.__class__._data = value

    def __repr__(self):
        """Returns a string representation of the state.

        Returns:
            str: String representation of the state dictionary.
        """
        return repr(self.data)

    def __iter__(self):
        """Returns an iterator over the state keys.

        Returns:
            Iterator: An iterator yielding state keys.
        """
        return iter(self.data)

    def __len__(self):
        """Returns the number of items in the state.

        Returns:
            int: The number of key-value pairs in the state.
        """
        return len(self.data)

    def __contains__(self, key):
        """Checks if a key exists in the state.

        Args:
            key: The key to check for.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return key in self.data

    def __setitem__(self, key, value):
        """Sets a value for the given key.

        Args:
            key: The key to set.
            value: The value to associate with the key.
        """
        self.data[key] = value
        if self.autocommit:
            self.commit()

    def __getitem__(self, key):
        """Retrieves a value by its key.

        Args:
            key: The key to look up.

        Returns:
            The value associated with the key.

        Raises:
            KeyError: If the key does not exist.
        """
        value = self.data[key]
        return value

    def __delitem__(self, key):
        """Deletes a key-value pair from the state.

        Args:
            key: The key to delete.

        Raises:
            KeyError: If the key does not exist.
        """
        del self.data[key]
        if self.autocommit:
            self.commit()

    def pop(self, key, default=SENTINEL):
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
        if default is SENTINEL:
            value = self.data.pop(key)
        else:
            value = self.data.pop(key, default)
        if self.autocommit:
            self.commit()
        return value

    def get(self, key, default=None):
        """Returns the value for key if it exists, otherwise returns default.

        Args:
            key: The key to look up.
            default: The value to return if the key doesn't exist.
                Defaults to None.

        Returns:
            The value associated with the key, or default if not found.
        """
        return self.data.get(key, default)

    def update(self, data: MutableMapping | Iterable[Iterable[Any]] = None, /, **kwargs):
        """Updates the state with multiple key-value pairs.

        Args:
            data: A mapping or iterable of key-value pairs to add.
            **kwargs: Additional key-value pairs to add.
        """
        self.data.update(data, **kwargs)
        if self.autocommit:
            self.commit()

    def setdefault(self, key, default = None, /):
        """Returns the value for key if it exists, otherwise sets and returns default.

        Args:
            key: The key to look up or set.
            default: The value to set if the key doesn't exist. Defaults to None.

        Returns:
            The existing value if the key exists, otherwise the default value.
        """
        value = self.data.setdefault(key, default)
        if self.autocommit:
            self.commit()
        return value

    def keys(self):
        """Returns a view of the state's keys.

        Returns:
            dict_keys: A view of the keys in the state.
        """
        return self.data.keys()

    def values(self):
        """Returns a view of the state's values.

        Returns:
            dict_values: A view of the values in the state.
        """
        return self.data.values()

    def items(self):
        """Returns a view of the state's key-value pairs.

        Returns:
            dict_items: A view of the (key, value) pairs in the state.
        """
        return self.data.items()

    def load(self, *, conn = None, data: dict = None):
        """Loads state data from the database.

        Retrieves the persisted state from the database and merges it with
        any provided data. The merged result is then committed back.

        Args:
            conn: An existing database connection to use. If None, a new
                connection is created.
            data: Additional data to merge into the loaded state.
        """
        try:
            conn = conn or self.conn
            res = conn.execute("SELECT value FROM state where key = 'data'").fetchone()
            db_data = pickle.loads(res[0]) if res else {}
            db_data |= (data or {})
            self.update(db_data)
            self.commit(conn=conn)
        except Exception as err:
            logger.error("%s: Failed to load state data from database", err)

    def init(self, data: dict = None, flush: bool = False, db_name: str = ""):
        """Initializes the state with the database.

        Creates the state table if it doesn't exist and loads or flushes
        the data based on the flush parameter.

        Args:
            data: Initial data to populate the state with.
            flush: If True, clears existing data and uses only provided data.
                If False, loads existing data and merges with provided data.
            db_name: Path to the SQLite database file.
        """
        if self._initialized:
            return
        self.db_name = db_name or os.environ.get("DB_NAME", "db.sqlite3")
        conn = self.conn
        conn.execute("CREATE TABLE IF NOT EXISTS state (key text unique, value blob)")
        self._initialized = True
        if flush:
            self.data = data or {}
            self.commit(conn=conn)
        else:
            self.load(conn=conn, data=data)
    
    def flush(self, data: dict = None):
        """Clears the state and optionally sets new data.

        Args:
            data: New data to set after clearing. Defaults to empty dict.
        """
        self.data = data or {}
        self.commit()

    def commit(self, *, conn: sqlite3.Connection = None, close: bool = True):
        """Commits the current state to the database.

        Serializes the state dictionary using pickle and saves it to the
        SQLite database.

        Args:
            conn: An existing database connection to use. If None, a new
                connection is created.
            close: If True, closes the connection after committing.
                Defaults to True.
        """
        value = pickle.dumps(self.data, protocol=pickle.HIGHEST_PROTOCOL)
        value = sqlite3.Binary(value)
        conn = conn or self.conn
        conn.execute("REPLACE INTO state (key, value) VALUES ('data', ?)", (value,))
        conn.commit()
        if close:
            conn.close()

    @property
    def conn(self):
        """Creates and returns a new database connection.

        Returns:
            sqlite3.Connection: A new connection to the state database.
        """
        return sqlite3.connect(self.db_name)

    async def acommit(self, conn=None, close=True):
        """Asynchronously commits the current state to the database.

        This is a convenience wrapper for async contexts.

        Args:
            conn: An existing database connection to use. If None, a new
                connection is created.
            close: If True, closes the connection after committing.
                Defaults to True.
        """
        conn = conn or self.conn
        value = pickle.dumps(self.data, protocol=pickle.HIGHEST_PROTOCOL)
        value = sqlite3.Binary(value)
        conn.execute("REPLACE INTO state (key, value) VALUES ('data', ?)", (value,))
        conn.commit()
        if close:
            conn.close()
