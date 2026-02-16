"""Comprehensive tests for the ResultDB module.

Tests cover:
- ResultDB initialization with required and optional fields
- __post_init__ method for parameter deserialization
- get_data method for preparing data for storage
- Database operations (save, get, filter, update, all, execute_raw)
- Pickle serialization/deserialization of parameters
- Field metadata and constraints
- dump_to_csv functionality
- Edge cases and error handling
"""

import csv
import os
import pickle
from datetime import datetime

import pytest

from aiomql.lib.result_db import ResultDB
from aiomql.core.db import DB


class TestResultDBInitialization:
    """Test ResultDB class initialization."""

    def test_init_with_required_fields(self):
        """Test ResultDB can be initialized with required fields."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="TestStrategy",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0
        )
        assert result.deal == 12345
        assert result.order == 67890
        assert result.name == "TestStrategy"
        assert result.symbol == "EURUSD"
        assert result.time == 1705312800.0
        assert result.volume == 0.1
        assert result.price == 1.0850
        assert result.type == 0

    def test_init_default_values(self):
        """Test ResultDB default values."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="TestStrategy",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0
        )
        assert result.bid == 0
        assert result.ask == 0
        assert result.tp == 0
        assert result.sl == 0
        assert result.price_close == 0
        assert result.time_close == 0
        assert result.expected_profit == 0
        assert result.win is False
        assert result.closed is False
        assert result.profit == 0
        assert result.comment == ""
        assert result.parameters == {}

    def test_init_with_all_fields(self):
        """Test ResultDB with all fields provided."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="TestStrategy",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            bid=1.0849,
            ask=1.0851,
            tp=1.0900,
            sl=1.0800,
            price_close=1.0875,
            time_close=1705316400.0,
            expected_profit=45.0,
            win=True,
            closed=True,
            profit=50.0,
            comment="Test trade",
            parameters={"ema": 20, "rsi": 14}
        )
        assert result.tp == 1.0900
        assert result.sl == 1.0800
        assert result.price_close == 1.0875
        assert result.time_close == 1705316400.0
        assert result.expected_profit == 45.0
        assert result.win is True
        assert result.closed is True
        assert result.profit == 50.0
        assert result.comment == "Test trade"
        assert result.parameters == {"ema": 20, "rsi": 14}

    def test_init_inherits_from_db(self):
        """Test ResultDB inherits from DB."""
        assert issubclass(ResultDB, DB)

    def test_class_has_table_name(self):
        """Test ResultDB has _table class variable."""
        assert hasattr(ResultDB, '_table')
        assert ResultDB._table == "result"


class TestPostInit:
    """Test __post_init__ method."""

    def test_post_init_deserializes_bytes_parameters(self):
        """Test __post_init__ deserializes pickled bytes."""
        params = {"ema": 20, "rsi": 14}
        pickled_params = pickle.dumps(params, protocol=pickle.HIGHEST_PROTOCOL)

        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            parameters=pickled_params
        )
        # Should be deserialized back to dict
        assert result.parameters == params
        assert isinstance(result.parameters, dict)

    def test_post_init_keeps_dict_parameters(self):
        """Test __post_init__ keeps dict parameters as is."""
        params = {"strategy": "MA_Cross", "timeframe": "H1"}
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            parameters=params
        )
        assert result.parameters == params
        assert isinstance(result.parameters, dict)

    def test_post_init_empty_string_becomes_empty_dict(self):
        """Test __post_init__ converts empty string parameters to empty dict."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            parameters=""
        )
        # Empty string is falsy, so self.parameters = self.parameters or {} → {}
        assert result.parameters == {}

    def test_post_init_non_dict_pickled_bytes_becomes_empty_dict(self):
        """Test __post_init__ converts non-dict pickled bytes to empty dict."""
        pickled_string = pickle.dumps("not a dict", protocol=pickle.HIGHEST_PROTOCOL)
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            parameters=pickled_string
        )
        assert result.parameters == {}

    def test_post_init_none_comment_becomes_empty_string(self):
        """Test __post_init__ converts None comment to empty string."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            comment=None
        )
        assert result.comment == ""

    def test_post_init_win_bool_coercion(self):
        """Test __post_init__ coerces win to bool."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            win=1
        )
        assert result.win is True
        assert isinstance(result.win, bool)

    def test_post_init_closed_bool_coercion(self):
        """Test __post_init__ coerces closed to bool."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            closed=1
        )
        assert result.closed is True
        assert isinstance(result.closed, bool)

    def test_post_init_win_false_coercion(self):
        """Test __post_init__ coerces 0 to False for win."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            win=0
        )
        assert result.win is False
        assert isinstance(result.win, bool)


class TestGetData:
    """Test get_data method."""

    def test_get_data_returns_dict(self):
        """Test get_data returns a dictionary."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0
        )
        data = result.get_data()
        assert isinstance(data, dict)

    def test_get_data_contains_all_fields(self):
        """Test get_data contains all required fields."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0
        )
        data = result.get_data()
        assert "deal" in data
        assert "order" in data
        assert "name" in data
        assert "symbol" in data
        assert "time" in data
        assert "volume" in data
        assert "price" in data
        assert "type" in data

    def test_get_data_serializes_dict_parameters(self):
        """Test get_data serializes dict parameters to bytes."""
        params = {"ema": 20, "rsi": 14}
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            parameters=params
        )
        data = result.get_data()
        assert isinstance(data["parameters"], bytes)
        # Verify it can be unpickled back
        unpickled = pickle.loads(data["parameters"])
        assert unpickled == params

    def test_get_data_keeps_bytes_parameters(self):
        """Test get_data keeps already-pickled parameters."""
        params = {"ema": 20}
        pickled = pickle.dumps(params, protocol=pickle.HIGHEST_PROTOCOL)

        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            parameters=pickled
        )
        # parameters is deserialized in __post_init__, then serialized again in get_data
        data = result.get_data()
        assert isinstance(data["parameters"], bytes)

    def test_get_data_preserves_field_values(self):
        """Test get_data preserves all field values."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            tp=1.0900,
            sl=1.0800,
            expected_profit=30.0,
            win=True,
            closed=True,
            profit=25.5
        )
        data = result.get_data()
        assert data["deal"] == 12345
        assert data["order"] == 67890
        assert data["tp"] == 1.0900
        assert data["sl"] == 1.0800
        assert data["expected_profit"] == 30.0
        assert data["win"] is True
        assert data["closed"] is True

    def test_get_data_serializes_empty_dict_parameters(self):
        """Test get_data serializes empty dict parameters to bytes."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            parameters={}
        )
        data = result.get_data()
        assert isinstance(data["parameters"], bytes)
        assert pickle.loads(data["parameters"]) == {}


class TestDatabaseOperations:
    """Test database CRUD operations."""

    @pytest.fixture(scope="function")
    def result_db(self):
        """Create a ResultDB instance."""
        return ResultDB(
            deal=int(datetime.now().timestamp() * 1000),  # Unique deal
            order=int(datetime.now().timestamp() * 1000) + 1,  # Unique order
            name="TestDBOps",
            symbol="BTCUSD",
            time=datetime.now().timestamp(),
            volume=0.01,
            price=50000.0,
            type=0,
            parameters={"test": "value"}
        )

    def test_save_creates_record(self, result_db):
        """Test save creates a record in database."""
        order_id = result_db.order
        result_db.save(commit=True)

        # Retrieve and verify
        retrieved = ResultDB.get(order=order_id)
        assert retrieved is not None
        assert retrieved.order == order_id
        assert retrieved.symbol == "BTCUSD"

    def test_get_retrieves_record(self, result_db):
        """Test get retrieves a record by criteria."""
        result_db.save(commit=True)

        retrieved = ResultDB.get(order=result_db.order)
        assert retrieved is not None
        assert retrieved.deal == result_db.deal
        assert retrieved.name == result_db.name

    def test_get_nonexistent_returns_none(self, result_db):
        """Test get returns None for nonexistent record."""
        result = ResultDB.get(order=999999999)
        assert result is None

    def test_filter_retrieves_records(self, result_db):
        """Test filter retrieves multiple records."""
        result_db.save(commit=True)

        results = ResultDB.filter(name="TestDBOps")
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_filter_by_symbol(self, result_db):
        """Test filter by symbol."""
        result_db.save(commit=True)

        results = ResultDB.filter(symbol="BTCUSD")
        assert all(r.symbol == "BTCUSD" for r in results)

    def test_update_modifies_record(self, result_db):
        """Test update modifies an existing record."""
        result_db.save(commit=True)

        # Update the record
        ResultDB.update({"profit": 100.0, "win": True, "closed": True}, order=result_db.order)

        # Verify update
        retrieved = ResultDB.get(order=result_db.order)
        assert retrieved.profit == 100.0
        assert retrieved.win is True
        assert retrieved.closed is True

    def test_all_retrieves_records(self, result_db):
        """Test all() retrieves records."""
        result_db.save(commit=True)

        results = ResultDB.all()
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_all_with_limit(self, result_db):
        """Test all() with limit parameter."""
        result_db.save(commit=True)

        results = ResultDB.all(limit=1)
        assert isinstance(results, list)
        assert len(results) <= 1

    def test_save_with_update(self, result_db):
        """Test save with update=True updates existing record."""
        result_db.save(commit=True)

        result_db.profit = 75.0
        result_db.win = True
        result_db.save(commit=True, update=True)

        retrieved = ResultDB.get(order=result_db.order)
        assert retrieved.profit == 75.0
        assert retrieved.win is True


class TestPrimaryKey:
    """Test primary key functionality."""

    def test_pk_property_returns_order(self):
        """Test pk property returns order field as primary key."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0
        )
        pk_name, pk_value = result.pk
        assert pk_name == "order"
        assert pk_value == 67890


class TestFieldsMethod:
    """Test fields class method."""

    def test_fields_returns_list(self):
        """Test fields returns a list."""
        field_list = ResultDB.fields()
        assert isinstance(field_list, list)

    def test_fields_contains_required_fields(self):
        """Test fields contains all required field names."""
        field_list = ResultDB.fields()
        assert "deal" in field_list
        assert "order" in field_list
        assert "name" in field_list
        assert "symbol" in field_list
        assert "time" in field_list
        assert "type" in field_list

    def test_fields_contains_optional_fields(self):
        """Test fields contains optional field names."""
        field_list = ResultDB.fields()
        assert "tp" in field_list
        assert "sl" in field_list
        assert "expected_profit" in field_list
        assert "win" in field_list
        assert "closed" in field_list
        assert "parameters" in field_list


class TestParametersSerialization:
    """Test parameters pickle serialization/deserialization."""

    def test_empty_dict_serialization(self):
        """Test empty dict parameters."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            parameters={}
        )
        data = result.get_data()
        assert isinstance(data["parameters"], bytes)
        assert pickle.loads(data["parameters"]) == {}

    def test_complex_dict_serialization(self):
        """Test complex nested dict parameters."""
        complex_params = {
            "strategy": "MA_Cross",
            "settings": {
                "ema_periods": [10, 20, 50],
                "rsi": 14,
                "enabled": True
            },
            "symbols": ["EURUSD", "GBPUSD"],
            "risk": 0.02
        }
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            parameters=complex_params
        )
        data = result.get_data()
        unpickled = pickle.loads(data["parameters"])
        assert unpickled == complex_params
        assert unpickled["settings"]["ema_periods"] == [10, 20, 50]

    def test_round_trip_serialization(self):
        """Test parameters survive save and retrieve."""
        params = {"strategy": "test", "value": 42}
        unique_order = int(datetime.now().timestamp() * 1000000)

        result = ResultDB(
            deal=unique_order,
            order=unique_order,
            name="TestRoundTrip",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            parameters=params
        )
        result.save(commit=True)

        # Retrieve and check
        retrieved = ResultDB.get(order=unique_order)
        assert retrieved is not None
        assert retrieved.parameters == params


class TestDumpToCsv:
    """Test dump_to_csv method."""

    @pytest.fixture
    def csv_records(self, tmp_path):
        """Create test records and return (csv_path, records)."""
        unique_base = int(datetime.now().timestamp() * 1000000)
        records = []
        for i in range(3):
            r = ResultDB(
                deal=unique_base + i,
                order=unique_base + i,
                name="CSVTest",
                symbol="EURUSD",
                time=1705312800.0 + i * 3600,
                volume=0.1 * (i + 1),
                price=1.0850 + i * 0.001,
                type=0,
                parameters={"index": i}
            )
            r.save(commit=True)
            records.append(r)
        csv_path = str(tmp_path / "test_dump.csv")
        return csv_path, records

    def test_dump_to_csv_creates_file(self, csv_records):
        """Test dump_to_csv creates a CSV file."""
        csv_path, _ = csv_records
        ResultDB.dump_to_csv(file_path=csv_path, name="CSVTest")
        assert os.path.exists(csv_path)

    def test_dump_to_csv_contains_data(self, csv_records):
        """Test dump_to_csv file contains records."""
        csv_path, records = csv_records
        ResultDB.dump_to_csv(file_path=csv_path, name="CSVTest")

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) >= 3

    def test_dump_to_csv_no_records_no_file(self, tmp_path):
        """Test dump_to_csv with no matching records does not create file."""
        csv_path = str(tmp_path / "empty_dump.csv")
        ResultDB.dump_to_csv(file_path=csv_path, name="NonexistentStrategyXYZ")
        assert not os.path.exists(csv_path)

    def test_dump_to_csv_flattens_parameters(self, csv_records):
        """Test dump_to_csv flattens parameters dict into columns."""
        csv_path, _ = csv_records
        ResultDB.dump_to_csv(file_path=csv_path, name="CSVTest")

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Parameters should be flattened with 'param_' prefix
        assert any("param_index" in row for row in rows)


class TestExecuteRaw:
    """Test execute_raw class method."""

    @pytest.fixture
    def saved_record(self):
        """Save a record for querying."""
        unique_order = int(datetime.now().timestamp() * 1000000) + 500
        result = ResultDB(
            deal=unique_order,
            order=unique_order,
            name="RawQueryTest",
            symbol="GBPUSD",
            time=1705312800.0,
            volume=0.5,
            price=1.2600,
            type=1
        )
        result.save(commit=True)
        return result

    def test_execute_raw_select(self, saved_record):
        """Test execute_raw with SELECT query."""
        results = ResultDB.execute_raw(
            f"SELECT * FROM result WHERE \"order\" = ?",
            (saved_record.order,)
        )
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_execute_raw_select_with_named_params(self, saved_record):
        """Test execute_raw with named parameters."""
        results = ResultDB.execute_raw(
            f"SELECT * FROM result WHERE name = :name",
            {"name": "RawQueryTest"}
        )
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_execute_raw_empty_sql_raises_error(self):
        """Test execute_raw with empty SQL raises ValueError."""
        with pytest.raises(ValueError):
            ResultDB.execute_raw("")

    def test_execute_raw_dangerous_pattern_raises_error(self):
        """Test execute_raw with dangerous SQL pattern raises ValueError."""
        with pytest.raises(ValueError):
            ResultDB.execute_raw("SELECT * FROM result; DROP TABLE result")

    def test_execute_raw_write_without_permission_raises_error(self):
        """Test execute_raw write operation without allow_write raises PermissionError."""
        with pytest.raises(PermissionError):
            ResultDB.execute_raw(
                "UPDATE result SET profit = ? WHERE name = ?",
                (999.0, "RawQueryTest")
            )

    def test_execute_raw_write_with_permission(self, saved_record):
        """Test execute_raw write operation with allow_write=True."""
        affected = ResultDB.execute_raw(
            f"UPDATE result SET profit = ? WHERE \"order\" = ?",
            (999.0, saved_record.order),
            allow_write=True
        )
        assert isinstance(affected, int)

    def test_execute_raw_invalid_params_type_raises_error(self):
        """Test execute_raw with invalid params type raises ValueError."""
        with pytest.raises(ValueError):
            ResultDB.execute_raw("SELECT * FROM result", "invalid_params")


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_values(self):
        """Test ResultDB with zero values."""
        result = ResultDB(
            deal=0,
            order=1,  # Must be unique
            name="Zero",
            symbol="EURUSD",
            time=0.0,
            volume=0.0,
            price=0.0,
            type=0
        )
        assert result.deal == 0
        assert result.volume == 0.0

    def test_negative_profit(self):
        """Test ResultDB with negative profit."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Loss",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            profit=-25.0,
            win=False
        )
        assert result.profit == -25.0
        assert result.win is False

    def test_large_volume(self):
        """Test ResultDB with large volume."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Large",
            symbol="EURUSD",
            time=1705312800.0,
            volume=100.0,
            price=1.0850,
            type=0
        )
        assert result.volume == 100.0

    def test_long_comment(self):
        """Test ResultDB with long comment."""
        long_comment = "A" * 1000
        result = ResultDB(
            deal=12345,
            order=67890,
            name="LongComment",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0,
            comment=long_comment
        )
        assert result.comment == long_comment
        assert len(result.comment) == 1000

    def test_special_characters_in_name(self):
        """Test ResultDB with special characters in name."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test_Strategy-v2.1",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0
        )
        assert result.name == "Test_Strategy-v2.1"

    def test_high_precision_prices(self):
        """Test ResultDB with high precision prices."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="HighPrecision",
            symbol="USDJPY",
            time=1705312800.0,
            volume=0.1,
            price=110.12345678,
            type=0,
            bid=110.12345677,
            ask=110.12345679,
            tp=110.20000000,
            sl=110.00000000
        )
        assert result.price == 110.12345678

    def test_asdict_method(self):
        """Test asdict method inherited from DB."""
        result = ResultDB(
            deal=12345,
            order=67890,
            name="Test",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0
        )
        data = result.asdict()
        assert isinstance(data, dict)
        assert data["deal"] == 12345
        assert data["order"] == 67890


class TestTableOperations:
    """Test table-level operations."""

    def test_clear_table(self):
        """Test clearing the table."""
        # Create a test record
        unique_order = int(datetime.now().timestamp() * 1000000) + 100
        result = ResultDB(
            deal=unique_order,
            order=unique_order,
            name="ClearTest",
            symbol="EURUSD",
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0
        )
        result.save(commit=True)

        # Note: clear() would delete all records, so we don't call it in tests
        # to avoid affecting other tests. Just verify the method exists.
        assert hasattr(ResultDB, 'clear')

    def test_get_columns(self):
        """Test get_columns class method."""
        columns = ResultDB.get_columns()
        assert isinstance(columns, str)
        assert "deal" in columns
        assert "order" in columns

    def test_drop_table_method_exists(self):
        """Test drop_table method exists."""
        assert hasattr(ResultDB, 'drop_table')

    def test_filter_dict_method(self):
        """Test filter_dict class method."""
        data = {"deal": 123, "order": 456, "name": "Test", "extra": "value"}
        filtered = ResultDB.filter_dict(data, include={"deal", "order", "name"})
        assert "deal" in filtered
        assert "order" in filtered
        assert "name" in filtered
        assert "extra" not in filtered

    def test_filter_dict_with_exclude(self):
        """Test filter_dict with exclude parameter."""
        data = {"deal": 123, "order": 456, "name": "Test"}
        filtered = ResultDB.filter_dict(data, exclude={"name"})
        assert "deal" in filtered
        assert "order" in filtered
        assert "name" not in filtered
