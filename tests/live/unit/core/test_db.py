"""Comprehensive tests for the DB ORM module.

Tests cover:
- DB initialization with dataclass
- Table creation and column definitions
- CRUD operations (save, get, filter, update, delete)
- Type mapping (Python to SQLite)
- Primary key handling
- Raw SQL execution with validation
- Data sanitization
"""

import os
import pytest
import tempfile
from dataclasses import dataclass, field

from aiomql.core.db import DB


@pytest.fixture
def temp_db_path():
    """Creates a temporary database file path."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def setup_db_config(temp_db_path, monkeypatch):
    """Sets up DB config with temp database."""
    from aiomql.core.config import Config
    config = Config()
    config.db_name = temp_db_path
    monkeypatch.setenv("DB_NAME", temp_db_path)
    yield temp_db_path


@dataclass
class TestModel(DB):
    """Test model for DB tests."""
    id: int = field(metadata={"PRIMARY KEY": True})
    name: str = ""
    value: float = 0.0


@dataclass
class SimpleModel(DB):
    """Simple model without primary key."""
    name: str = ""
    count: int = 0


class TestDBInitialization:
    """Tests for DB initialization."""

    def test_dataclass_model_creates_table(self, setup_db_config):
        """Test dataclass model creates table on instantiation."""
        record = TestModel(id=1, name="test", value=1.0)
        assert record is not None

    def test_init_sets_config(self, setup_db_config):
        """Test __new__ sets config."""
        record = TestModel(id=1, name="test", value=1.0)
        assert hasattr(record, "config")

    def test_table_name_defaults_to_class_name(self, setup_db_config):
        """Test table name defaults to lowercase class name."""
        record = TestModel(id=1, name="test", value=1.0)
        assert TestModel._table == "testmodel"


class TestDBTypeMapping:
    """Tests for Python to SQLite type mapping."""

    def test_str_maps_to_text(self):
        """Test str maps to TEXT."""
        assert DB.types(str) == "TEXT"

    def test_int_maps_to_integer(self):
        """Test int maps to INTEGER."""
        assert DB.types(int) == "INTEGER"

    def test_float_maps_to_real(self):
        """Test float maps to REAL."""
        assert DB.types(float) == "REAL"

    def test_bool_maps_to_boolean(self):
        """Test bool maps to BOOLEAN."""
        assert DB.types(bool) == "BOOLEAN"

    def test_bytes_maps_to_blob(self):
        """Test bytes maps to BLOB."""
        assert DB.types(bytes) == "BLOB"

    def test_unknown_type_maps_to_text(self):
        """Test unknown type maps to TEXT."""
        assert DB.types(list) == "TEXT"


class TestDBSanitize:
    """Tests for SQL identifier sanitization."""

    def test_valid_identifier(self):
        """Test valid identifier is quoted."""
        result = DB.sanitize("valid_name")
        assert result == '"valid_name"'

    def test_identifier_starting_with_underscore(self):
        """Test identifier starting with underscore."""
        result = DB.sanitize("_valid")
        assert result == '"_valid"'

    def test_invalid_identifier_raises(self):
        """Test invalid identifier raises ValueError."""
        with pytest.raises(ValueError):
            DB.sanitize("invalid-name")

    def test_identifier_with_numbers(self):
        """Test identifier with numbers."""
        result = DB.sanitize("name123")
        assert result == '"name123"'

    def test_identifier_starting_with_number_raises(self):
        """Test identifier starting with number raises."""
        with pytest.raises(ValueError):
            DB.sanitize("123invalid")


class TestDBCRUDOperations:
    """Tests for DB CRUD operations."""

    @pytest.fixture(autouse=True)
    def setup_model(self, setup_db_config):
        """Reset model state before each test."""
        TestModel._initialized = False
        TestModel._table = ""
        yield

    def test_save_inserts_record(self, setup_db_config):
        """Test save inserts new record."""
        record = TestModel(id=1, name="test", value=1.0)
        record.save()

        result = TestModel.get(id=1)
        assert result is not None
        assert result.name == "test"

    def test_get_returns_record(self, setup_db_config):
        """Test get returns matching record."""
        record = TestModel(id=1, name="test", value=1.0)
        record.save()

        result = TestModel.get(id=1)
        assert result.id == 1
        assert result.name == "test"

    def test_get_returns_none_for_no_match(self, setup_db_config):
        """Test get returns None for no match."""
        TestModel(id=1, name="test", value=1.0)  # Initialize table
        result = TestModel.get(id=999)
        assert result is None

    def test_filter_returns_all_matching(self, setup_db_config):
        """Test filter returns all matching records."""
        TestModel(id=1, name="test", value=1.0).save()
        TestModel(id=2, name="test", value=2.0).save()
        TestModel(id=3, name="other", value=3.0).save()

        results = TestModel.filter(name="test")
        assert len(results) == 2

    def test_filter_returns_all_when_no_criteria(self, setup_db_config):
        """Test filter returns all records when no criteria."""
        TestModel(id=1, name="test", value=1.0).save()
        TestModel(id=2, name="other", value=2.0).save()

        results = TestModel.filter()
        assert len(results) == 2

    def test_all_returns_all_records(self, setup_db_config):
        """Test all returns all records."""
        TestModel(id=1, name="test1", value=1.0).save()
        TestModel(id=2, name="test2", value=2.0).save()

        results = TestModel.all()
        assert len(results) == 2

    def test_all_with_limit(self, setup_db_config):
        """Test all with limit returns limited records."""
        TestModel(id=1, name="test1", value=1.0).save()
        TestModel(id=2, name="test2", value=2.0).save()
        TestModel(id=3, name="test3", value=3.0).save()

        results = TestModel.all(limit=2)
        assert len(results) == 2

    def test_clear_removes_all_records(self, setup_db_config):
        """Test clear removes all records."""
        TestModel(id=1, name="test1", value=1.0).save()
        TestModel(id=2, name="test2", value=2.0).save()

        TestModel.clear()
        results = TestModel.all()
        assert len(results) == 0

    def test_update_modifies_records(self, setup_db_config):
        """Test update modifies matching records."""
        TestModel(id=1, name="old", value=1.0).save()

        TestModel.update({"name": "new"}, id=1)
        result = TestModel.get(id=1)
        assert result.name == "new"


class TestDBPrimaryKey:
    """Tests for primary key handling."""

    @pytest.fixture(autouse=True)
    def setup_model(self, setup_db_config):
        """Reset model state before each test."""
        TestModel._initialized = False
        TestModel._table = ""
        yield

    def test_pk_property_returns_pk_field(self, setup_db_config):
        """Test pk property returns primary key field name and value."""
        record = TestModel(id=42, name="test", value=1.0)
        pk_name, pk_value = record.pk
        assert pk_name == "id"
        assert pk_value == 42


class TestDBAsDict:
    """Tests for asdict functionality."""

    @pytest.fixture(autouse=True)
    def setup_model(self, setup_db_config):
        """Reset model state before each test."""
        TestModel._initialized = False
        TestModel._table = ""
        yield

    def test_asdict_returns_dict(self, setup_db_config):
        """Test asdict returns dictionary."""
        record = TestModel(id=1, name="test", value=1.0)
        result = record.asdict()
        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["name"] == "test"
        assert result["value"] == 1.0


class TestDBFields:
    """Tests for fields class method."""

    @pytest.fixture(autouse=True)
    def setup_model(self, setup_db_config):
        """Reset model state before each test."""
        TestModel._initialized = False
        TestModel._table = ""
        yield

    def test_fields_returns_field_names(self, setup_db_config):
        """Test fields returns list of field names."""
        TestModel(id=1, name="test", value=1.0)  # Initialize
        field_names = TestModel.fields()
        assert "id" in field_names
        assert "name" in field_names
        assert "value" in field_names


class TestDBDropTable:
    """Tests for drop_table functionality."""

    @pytest.fixture(autouse=True)
    def setup_model(self, setup_db_config):
        """Reset model state before each test."""
        TestModel._initialized = False
        TestModel._table = ""
        yield

    def test_drop_table_removes_table(self, setup_db_config):
        """Test drop_table removes the table."""
        record = TestModel(id=1, name="test", value=1.0)
        record.save()

        TestModel.drop_table()

        # Re-initializing should create fresh table
        TestModel._initialized = False
        TestModel._table = ""
        record2 = TestModel(id=1, name="new", value=2.0)
        record2.save()
        assert TestModel.all()[0].name == "new"


class TestDBExecuteRaw:
    """Tests for execute_raw SQL execution."""

    @pytest.fixture(autouse=True)
    def setup_model(self, setup_db_config):
        """Reset model state before each test."""
        TestModel._initialized = False
        TestModel._table = ""
        TestModel(id=1, name="test1", value=1.0).save()
        TestModel(id=2, name="test2", value=2.0).save()
        yield

    def test_execute_raw_select(self, setup_db_config):
        """Test execute_raw with SELECT query."""
        results = TestModel.execute_raw(
            "SELECT * FROM testmodel WHERE id = ?",
            (1,)
        )
        assert len(results) == 1
        assert results[0].name == "test1"

    def test_execute_raw_with_named_params(self, setup_db_config):
        """Test execute_raw with named parameters."""
        results = TestModel.execute_raw(
            "SELECT * FROM testmodel WHERE name = :name",
            {"name": "test1"}
        )
        assert len(results) == 1

    def test_execute_raw_write_requires_flag(self, setup_db_config):
        """Test execute_raw write operations require allow_write."""
        with pytest.raises(PermissionError):
            TestModel.execute_raw(
                "UPDATE testmodel SET name = ? WHERE id = ?",
                ("updated", 1)
            )

    def test_execute_raw_write_with_flag(self, setup_db_config):
        """Test execute_raw write with allow_write=True."""
        affected = TestModel.execute_raw(
            "UPDATE testmodel SET name = ? WHERE id = ?",
            ("updated", 1),
            allow_write=True
        )
        assert affected == 1

        result = TestModel.get(id=1)
        assert result.name == "updated"

    def test_execute_raw_rejects_dangerous_patterns(self, setup_db_config):
        """Test execute_raw rejects dangerous SQL patterns."""
        with pytest.raises(ValueError):
            TestModel.execute_raw("SELECT * FROM testmodel; DROP TABLE testmodel")

    def test_execute_raw_rejects_comments(self, setup_db_config):
        """Test execute_raw rejects SQL comments."""
        with pytest.raises(ValueError):
            TestModel.execute_raw("SELECT * FROM testmodel -- comment")

    def test_execute_raw_rejects_multiple_statements(self, setup_db_config):
        """Test execute_raw rejects multiple statements."""
        with pytest.raises(ValueError):
            TestModel.execute_raw("SELECT 1; SELECT 2")

    def test_execute_raw_empty_query_raises(self, setup_db_config):
        """Test execute_raw with empty query raises."""
        with pytest.raises(ValueError):
            TestModel.execute_raw("")

    def test_execute_raw_invalid_params_type_raises(self, setup_db_config):
        """Test execute_raw with invalid params type raises."""
        with pytest.raises(ValueError):
            TestModel.execute_raw("SELECT * FROM testmodel", "invalid")

    def test_execute_raw_unsupported_statement_raises(self, setup_db_config):
        """Test execute_raw with unsupported statement raises."""
        with pytest.raises(ValueError):
            TestModel.execute_raw("CREATE TABLE newtable (id INTEGER)")


class TestDBDictFactory:
    """Tests for dict_factory row conversion."""

    @pytest.fixture(autouse=True)
    def setup_model(self, setup_db_config):
        """Reset model state before each test."""
        TestModel._initialized = False
        TestModel._table = ""
        yield

    def test_dict_factory_returns_class_instances(self, setup_db_config):
        """Test dict_factory converts rows to class instances."""
        TestModel(id=1, name="test", value=1.0).save()

        results = TestModel.all()
        assert isinstance(results[0], TestModel)
