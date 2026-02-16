"""Comprehensive tests for the Store module.

Tests cover:
- Store initialization and configuration
- MutableMapping interface (dict-like operations)
- Key-value CRUD operations
- Iteration methods (keys, values, items)
- Autocommit functionality
- Data persistence
- Flush behavior
"""

import os
import pytest
import tempfile
import gc
from collections.abc import MutableMapping

from aiomql.core.store import Store


@pytest.fixture(autouse=True)
def reset_store_connection():
    """Reset Store class-level connection before each test."""
    # Reset the class-level cached connection
    Store._conn = None
    yield
    # Cleanup after test - force garbage collection to close any open connections
    gc.collect()
    if Store._conn is not None:
        try:
            Store._conn.close()
        except Exception:
            pass
    Store._conn = None


@pytest.fixture
def temp_db():
    """Creates a temporary database file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Force garbage collection to release any file handles
    gc.collect()
    # Try to remove the file multiple times with a small delay
    for _ in range(3):
        try:
            if os.path.exists(path):
                os.remove(path)
            break
        except PermissionError:
            gc.collect()
            import time
            time.sleep(0.1)


class TestStoreInitialization:
    """Tests for Store initialization."""

    def test_init_creates_store(self, temp_db):
        """Test Store can be initialized."""
        store = Store(db_name=temp_db)
        assert isinstance(store, Store)
        store.conn.close()

    def test_init_creates_table(self, temp_db):
        """Test Store creates table on initialization."""
        store = Store(db_name=temp_db, table_name="test_table")
        # Table should exist - verify by checking we can use the store
        store["key"] = "value"
        assert store["key"] == "value"
        store.conn.close()

    def test_init_with_initial_data(self, temp_db):
        """Test Store can be initialized with data."""
        initial_data = {"key1": "value1", "key2": "value2"}
        store = Store(db_name=temp_db, data=initial_data)
        assert store["key1"] == "value1"
        assert store["key2"] == "value2"
        store.conn.close()

    def test_init_with_flush(self, temp_db):
        """Test Store flush clears existing data."""
        # Create initial store with data (autocommit=True creates its own connection)
        store1 = Store(db_name=temp_db, data={"existing": "data"}, autocommit=True)
        store1.conn.close()

        # Create new store with flush
        store2 = Store(db_name=temp_db, flush=True, autocommit=True)
        assert "existing" not in store2
        store2.conn.close()

    def test_init_default_autocommit(self, temp_db):
        """Test Store has autocommit True by default."""
        store = Store(db_name=temp_db)
        assert store.autocommit is True
        store.conn.close()

    def test_init_autocommit_false(self, temp_db):
        """Test Store can be initialized with autocommit=False."""
        store = Store(db_name=temp_db, autocommit=False)
        assert store.autocommit is False
        store.conn.close()

    def test_init_default_table_name(self, temp_db):
        """Test Store uses 'store' as default table name."""
        store = Store(db_name=temp_db)
        assert store.table_name == "store"
        store.conn.close()

    def test_init_custom_table_name(self, temp_db):
        """Test Store can use custom table name."""
        store = Store(db_name=temp_db, table_name="custom_table")
        assert store.table_name == "custom_table"
        store.conn.close()


class TestStoreMutableMappingInterface:
    """Tests for MutableMapping interface implementation."""

    @pytest.fixture
    def store(self, temp_db):
        """Creates a Store instance."""
        s = Store(db_name=temp_db)
        yield s
        s.conn.close()

    def test_is_mutable_mapping(self, store):
        """Test Store implements MutableMapping."""
        assert isinstance(store, MutableMapping)

    def test_setitem_getitem(self, store):
        """Test setting and getting items."""
        store["key"] = "value"
        assert store["key"] == "value"

    def test_delitem(self, store):
        """Test deleting items."""
        store["key"] = "value"
        del store["key"]
        assert "key" not in store

    def test_delitem_raises_keyerror(self, store):
        """Test deleting nonexistent key raises KeyError."""
        with pytest.raises(KeyError):
            del store["nonexistent"]

    def test_len(self, store):
        """Test len returns correct count."""
        assert len(store) == 0
        store["key1"] = "value1"
        store["key2"] = "value2"
        assert len(store) == 2

    def test_contains(self, store):
        """Test 'in' operator."""
        store["key"] = "value"
        assert "key" in store
        assert "nonexistent" not in store

    def test_iter(self, store):
        """Test iteration over keys."""
        store["key1"] = "value1"
        store["key2"] = "value2"
        keys = list(store)
        assert "key1" in keys
        assert "key2" in keys

    def test_getitem_raises_keyerror(self, store):
        """Test getting nonexistent key raises KeyError."""
        with pytest.raises(KeyError):
            _ = store["nonexistent"]


class TestStoreOperations:
    """Tests for Store CRUD operations."""

    @pytest.fixture
    def store(self, temp_db):
        """Creates a Store instance."""
        s = Store(db_name=temp_db)
        yield s
        s.conn.close()

    def test_get_existing_key(self, store):
        """Test get returns value for existing key."""
        store["key"] = "value"
        assert store.get("key") == "value"

    def test_get_nonexistent_key_default(self, store):
        """Test get returns default for nonexistent key."""
        assert store.get("nonexistent") is None
        assert store.get("nonexistent", "default") == "default"

    def test_setdefault_existing_key(self, store):
        """Test setdefault returns existing value."""
        store["key"] = "existing"
        result = store.setdefault("key", "default")
        assert result == "existing"

    def test_setdefault_nonexistent_key(self, store):
        """Test setdefault sets and returns default."""
        result = store.setdefault("key", "default")
        assert result == "default"
        assert store["key"] == "default"

    def test_update_with_dict(self, store):
        """Test update with dictionary."""
        store.update({"key1": "value1", "key2": "value2"})
        assert store["key1"] == "value1"
        assert store["key2"] == "value2"

    def test_update_with_kwargs(self, store):
        """Test update with keyword arguments."""
        store.update(key1="value1", key2="value2")
        assert store["key1"] == "value1"
        assert store["key2"] == "value2"

    def test_pop_existing_key(self, store):
        """Test pop returns and removes value."""
        store["key"] = "value"
        result = store.pop("key")
        assert result == "value"
        assert "key" not in store

    def test_pop_nonexistent_key_default(self, store):
        """Test pop returns default for nonexistent key."""
        result = store.pop("nonexistent", "default")
        assert result == "default"

    def test_pop_nonexistent_key_raises(self, store):
        """Test pop raises KeyError without default."""
        with pytest.raises(KeyError):
            store.pop("nonexistent")

    def test_clear(self, store):
        """Test clear removes all items."""
        store["key1"] = "value1"
        store["key2"] = "value2"
        store.clear()
        assert len(store) == 0


class TestStoreIterationMethods:
    """Tests for Store iteration methods."""

    @pytest.fixture
    def store(self, temp_db):
        """Creates a Store with test data."""
        s = Store(db_name=temp_db, data={"key1": "value1", "key2": "value2"})
        yield s
        s.conn.close()

    def test_keys(self, store):
        """Test keys returns list of keys."""
        keys = store.keys()
        assert isinstance(keys, list)
        assert "key1" in keys
        assert "key2" in keys

    def test_values(self, store):
        """Test values returns list of values."""
        values = store.values()
        assert isinstance(values, list)
        assert "value1" in values
        assert "value2" in values

    def test_items(self, store):
        """Test items returns list of tuples."""
        items = store.items()
        assert isinstance(items, list)
        assert ("key1", "value1") in items
        assert ("key2", "value2") in items

    def test_iterkeys(self, store):
        """Test iterkeys yields keys."""
        keys = list(store.iterkeys())
        assert "key1" in keys
        assert "key2" in keys

    def test_itervalues(self, store):
        """Test itervalues yields values."""
        values = list(store.itervalues())
        assert "value1" in values
        assert "value2" in values

    def test_iteritems(self, store):
        """Test iteritems yields key-value tuples."""
        items = list(store.iteritems())
        assert ("key1", "value1") in items
        assert ("key2", "value2") in items


class TestStoreDataProperty:
    """Tests for Store data property."""

    def test_data_returns_dict(self, temp_db):
        """Test data property returns dictionary."""
        store = Store(db_name=temp_db, data={"key1": "value1"})
        data = store.data
        assert isinstance(data, dict)
        store.conn.close()

    def test_data_contains_all_items(self, temp_db):
        """Test data contains all stored items."""
        store = Store(db_name=temp_db, data={"key1": "value1", "key2": "value2"})
        data = store.data
        assert data == {"key1": "value1", "key2": "value2"}
        store.conn.close()


class TestStoreCommit:
    """Tests for Store commit functionality."""

    def test_commit_persists_data(self, temp_db):
        """Test commit persists data to database."""
        store = Store(db_name=temp_db, autocommit=False)
        store["key"] = "value"
        store.commit()
        store.conn.close()

        # Create new store instance and verify data persisted
        store2 = Store(db_name=temp_db, autocommit=True)
        assert store2["key"] == "value"
        store2.conn.close()

    def test_autocommit_persists_immediately(self, temp_db):
        """Test autocommit persists data immediately."""
        store = Store(db_name=temp_db, autocommit=True)
        store["key"] = "value"
        store.conn.close()

        # Create new store instance and verify data persisted
        store2 = Store(db_name=temp_db, autocommit=True)
        assert store2["key"] == "value"
        store2.conn.close()

    async def test_acommit(self, temp_db):
        """Test async commit."""
        store = Store(db_name=temp_db, autocommit=False)
        store["key"] = "value"
        await store.acommit()
        store.conn.close()

        store2 = Store(db_name=temp_db, autocommit=True)
        assert store2["key"] == "value"
        store2.conn.close()

    def test_classmethod_commit(self, temp_db):
        """Test commit as classmethod."""
        store = Store(db_name=temp_db, autocommit=False)
        store["key"] = "value"
        # Use the classmethod commit
        Store.commit()
        store.conn.close()

        store2 = Store(db_name=temp_db, autocommit=True)
        assert store2["key"] == "value"
        store2.conn.close()


class TestStoreRepr:
    """Tests for Store repr."""

    def test_repr(self, temp_db):
        """Test repr returns class name."""
        store = Store(db_name=temp_db)
        assert repr(store) == "Store()"
        store.conn.close()


class TestStoreConnectionHandling:
    """Tests for Store connection handling."""

    def test_autocommit_true_creates_own_connection(self, temp_db):
        """Test autocommit=True creates its own connection."""
        store = Store(db_name=temp_db, autocommit=True)
        assert store.conn is not None
        # With autocommit=True, it should NOT use the class-level _conn
        store["key"] = "value"
        assert store["key"] == "value"
        store.conn.close()

    def test_autocommit_false_uses_class_connection(self, temp_db):
        """Test autocommit=False uses class-level connection."""
        store = Store(db_name=temp_db, autocommit=False)
        assert store.conn is Store._conn
        store["key"] = "value"
        store.conn.commit()
        assert store["key"] == "value"
        store.conn.close()

    def test_connection_classmethod(self, temp_db):
        """Test connection classmethod caches connection."""
        conn1 = Store.connection(temp_db)
        conn2 = Store.connection(temp_db)
        assert conn1 is conn2
        conn1.close()
