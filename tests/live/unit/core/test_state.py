"""Comprehensive tests for the State module.

Tests cover:
- State initialization (singleton pattern)
- MutableMapping interface
- Key-value CRUD operations
- Data persistence via commit/load
- Singleton behavior
- Autocommit functionality
- Flush behavior
"""

import os
import pytest
import tempfile
from collections.abc import MutableMapping

from aiomql.core.state import State


@pytest.fixture(autouse=True)
def reset_state_singleton():
    """Reset State singleton before each test."""
    # Remove singleton instance to ensure clean state for each test
    if hasattr(State, "_instance"):
        delattr(State, "_instance")
    if hasattr(State, "_data"):
        delattr(State, "_data")
    State._initialized = False
    yield
    # Cleanup after test
    if hasattr(State, "_instance"):
        delattr(State, "_instance")
    if hasattr(State, "_data"):
        delattr(State, "_data")
    State._initialized = False


class TestStateInitialization:
    """Tests for State initialization."""

    @pytest.fixture
    def temp_db(self):
        """Creates a temporary database file."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.remove(path)

    def test_init_creates_state(self, temp_db):
        """Test State can be initialized."""
        state = State(db_name=temp_db)
        assert isinstance(state, State)

    def test_init_with_initial_data(self, temp_db):
        """Test State can be initialized with data."""
        initial_data = {"key1": "value1", "key2": "value2"}
        state = State(db_name=temp_db, data=initial_data, flush=True)
        assert state["key1"] == "value1"
        assert state["key2"] == "value2"

    def test_init_with_flush(self, temp_db):
        """Test State flush clears existing data."""
        # Create initial state with data
        state1 = State(db_name=temp_db, data={"existing": "data"}, flush=True)
        state1.commit()

        # Reset singleton
        delattr(State, "_instance")
        delattr(State, "_data")
        State._initialized = False

        # Create new state with flush
        state2 = State(db_name=temp_db, flush=True)
        assert "existing" not in state2

    def test_init_default_autocommit(self, temp_db):
        """Test State has autocommit True by default."""
        state = State(db_name=temp_db)
        assert state.autocommit is True

    def test_init_autocommit_true(self, temp_db):
        """Test State can be initialized with autocommit=True."""
        state = State(db_name=temp_db, autocommit=True)
        assert state.autocommit is True


class TestStateSingleton:
    """Tests for State singleton behavior."""

    @pytest.fixture
    def temp_db(self):
        """Creates a temporary database file."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.remove(path)

    def test_singleton_returns_same_instance(self, temp_db):
        """Test State returns same instance."""
        state1 = State(db_name=temp_db)
        state2 = State(db_name=temp_db)
        assert state1 is state2

    def test_singleton_shares_data(self, temp_db):
        """Test State instances share data."""
        state1 = State(db_name=temp_db)
        state1["key"] = "value"
        state2 = State(db_name=temp_db)
        assert state2["key"] == "value"


class TestStateMutableMappingInterface:
    """Tests for MutableMapping interface implementation."""

    @pytest.fixture
    def temp_db(self):
        """Creates a temporary database file."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.remove(path)

    @pytest.fixture
    def state(self, temp_db):
        """Creates a State instance."""
        return State(db_name=temp_db)

    def test_is_mutable_mapping(self, state):
        """Test State implements MutableMapping."""
        assert isinstance(state, MutableMapping)

    def test_setitem_getitem(self, state):
        """Test setting and getting items."""
        state["key"] = "value"
        assert state["key"] == "value"

    def test_delitem(self, state):
        """Test deleting items."""
        state["key"] = "value"
        del state["key"]
        assert "key" not in state

    def test_delitem_raises_keyerror(self, state):
        """Test deleting nonexistent key raises KeyError."""
        with pytest.raises(KeyError):
            del state["nonexistent"]

    def test_len(self, state):
        """Test len returns correct count."""
        assert len(state) == 0
        state["key1"] = "value1"
        state["key2"] = "value2"
        assert len(state) == 2

    def test_contains(self, state):
        """Test 'in' operator."""
        state["key"] = "value"
        assert "key" in state
        assert "nonexistent" not in state

    def test_iter(self, state):
        """Test iteration over keys."""
        state["key1"] = "value1"
        state["key2"] = "value2"
        keys = list(state)
        assert "key1" in keys
        assert "key2" in keys

    def test_getitem_raises_keyerror(self, state):
        """Test getting nonexistent key raises KeyError."""
        with pytest.raises(KeyError):
            _ = state["nonexistent"]


class TestStateOperations:
    """Tests for State CRUD operations."""

    @pytest.fixture
    def temp_db(self):
        """Creates a temporary database file."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.remove(path)

    @pytest.fixture
    def state(self, temp_db):
        """Creates a State instance."""
        return State(db_name=temp_db)

    def test_get_existing_key(self, state):
        """Test get returns value for existing key."""
        state["key"] = "value"
        assert state.get("key") == "value"

    def test_get_nonexistent_key_default(self, state):
        """Test get returns default for nonexistent key."""
        assert state.get("nonexistent") is None
        assert state.get("nonexistent", "default") == "default"

    def test_setdefault_existing_key(self, state):
        """Test setdefault returns existing value."""
        state["key"] = "existing"
        result = state.setdefault("key", "default")
        assert result == "existing"

    def test_setdefault_nonexistent_key(self, state):
        """Test setdefault sets and returns default."""
        result = state.setdefault("key", "default")
        assert result == "default"
        assert state["key"] == "default"

    def test_update_with_dict(self, state):
        """Test update with dictionary."""
        state.update({"key1": "value1", "key2": "value2"})
        assert state["key1"] == "value1"
        assert state["key2"] == "value2"

    def test_update_with_kwargs(self, state):
        """Test update with keyword arguments."""
        state.update({"key1": "value1"}, key2="value2")
        assert state["key1"] == "value1"
        assert state["key2"] == "value2"

    def test_pop_existing_key(self, state):
        """Test pop returns and removes value."""
        state["key"] = "value"
        result = state.pop("key")
        assert result == "value"
        assert "key" not in state

    def test_pop_nonexistent_key_default(self, state):
        """Test pop returns default for nonexistent key."""
        result = state.pop("nonexistent", "default")
        assert result == "default"

    def test_pop_nonexistent_key_raises(self, state):
        """Test pop raises KeyError without default."""
        with pytest.raises(KeyError):
            state.pop("nonexistent")

    def test_keys(self, state):
        """Test keys returns dict_keys."""
        state["key1"] = "value1"
        state["key2"] = "value2"
        keys = state.keys()
        assert "key1" in keys
        assert "key2" in keys

    def test_values(self, state):
        """Test values returns dict_values."""
        state["key1"] = "value1"
        state["key2"] = "value2"
        values = state.values()
        assert "value1" in values
        assert "value2" in values

    def test_items(self, state):
        """Test items returns dict_items."""
        state["key1"] = "value1"
        items = state.items()
        assert ("key1", "value1") in items


class TestStateDataProperty:
    """Tests for State data property."""

    @pytest.fixture
    def temp_db(self):
        """Creates a temporary database file."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.remove(path)

    def test_data_returns_dict(self, temp_db):
        """Test data property returns dictionary."""
        state = State(db_name=temp_db)
        state["key1"] = "value1"
        data = state.data
        assert isinstance(data, dict)

    def test_data_setter(self, temp_db):
        """Test data property can be set."""
        state = State(db_name=temp_db)
        state.data = {"key": "value"}
        assert state["key"] == "value"

    def test_data_setter_requires_dict(self, temp_db):
        """Test data setter raises on non-dict."""
        state = State(db_name=temp_db)
        with pytest.raises(AssertionError):
            state.data = "not a dict"


class TestStatePersistence:
    """Tests for State persistence functionality."""

    @pytest.fixture
    def temp_db(self):
        """Creates a temporary database file."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.remove(path)

    def test_commit_persists_data(self, temp_db):
        """Test commit persists data to database."""
        state1 = State(db_name=temp_db)
        state1["key"] = "value"
        state1.commit()

        # Reset singleton
        delattr(State, "_instance")
        delattr(State, "_data")
        State._initialized = False

        # Create new state and verify data loaded
        state2 = State(db_name=temp_db)
        assert state2["key"] == "value"

    def test_flush_clears_and_sets_data(self, temp_db):
        """Test flush clears and optionally sets new data."""
        state = State(db_name=temp_db)
        state["key1"] = "value1"
        state.flush({"key2": "value2"})
        assert "key1" not in state
        assert state["key2"] == "value2"

    def test_flush_with_no_data(self, temp_db):
        """Test flush with no data clears state."""
        state = State(db_name=temp_db)
        state["key"] = "value"
        state.flush()
        assert len(state) == 0

    async def test_acommit(self, temp_db):
        """Test async commit."""
        state1 = State(db_name=temp_db)
        state1["key"] = "value"
        await state1.acommit()

        # Reset singleton
        delattr(State, "_instance")
        delattr(State, "_data")
        State._initialized = False

        state2 = State(db_name=temp_db)
        assert state2["key"] == "value"


class TestStateRepr:
    """Tests for State repr."""

    @pytest.fixture
    def temp_db(self):
        """Creates a temporary database file."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.remove(path)

    def test_repr(self, temp_db):
        """Test repr returns data representation."""
        state = State(db_name=temp_db)
        state["key"] = "value"
        assert "key" in repr(state)
        assert "value" in repr(state)


class TestStateAutocommit:
    """Tests for State autocommit functionality."""

    @pytest.fixture
    def temp_db(self):
        """Creates a temporary database file."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.remove(path)

    def test_autocommit_on_setitem(self, temp_db):
        """Test autocommit commits on setitem."""
        state = State(db_name=temp_db, autocommit=True)
        state["key"] = "value"

        # Reset singleton
        delattr(State, "_instance")
        delattr(State, "_data")
        State._initialized = False

        state2 = State(db_name=temp_db)
        assert state2.get("key") == "value"

    def test_autocommit_on_delitem(self, temp_db):
        """Test autocommit commits on delitem."""
        state = State(db_name=temp_db, autocommit=True, data={"key": "value"}, flush=True)
        del state["key"]

        # Reset singleton
        delattr(State, "_instance")
        delattr(State, "_data")
        State._initialized = False

        state2 = State(db_name=temp_db)
        assert "key" not in state2
