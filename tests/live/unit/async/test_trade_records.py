"""Comprehensive tests for the TradeRecords module.

Tests cover:
- TradeRecords initialization with default and custom records_dir
- get_csv_records and get_json_records generators
- read_update_csv and read_update_json async methods
- update_rows async method for batch updating trades
- update_csv_records and update_json_records async methods
- Synchronous variants of all update methods
- get_sql_records_unclosed for database operations
- update_sql_records for SQL batch updates
- str_to_bool static method
- update_rows deal matching and update logic
- Edge cases and error handling
"""

import csv
import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from aiomql.lib.trade_records import TradeRecords
from aiomql.core.config import Config


class TestTradeRecordsInitialization:
    """Test TradeRecords class initialization."""

    def test_init_default_records_dir(self):
        """Test TradeRecords uses config records_dir by default."""
        records = TradeRecords()
        assert records.config is not None
        assert isinstance(records.config, Config)
        assert records.records_dir == records.config.records_dir

    def test_init_custom_records_dir(self, tmp_path):
        """Test TradeRecords with custom records_dir."""
        records = TradeRecords(records_dir=tmp_path)
        assert records.records_dir == tmp_path

    def test_init_string_records_dir(self, tmp_path):
        """Test TradeRecords with string records_dir."""
        records = TradeRecords(records_dir=str(tmp_path))
        assert records.records_dir == str(tmp_path)

    def test_init_has_mt5(self):
        """Test TradeRecords has MetaTrader instance."""
        records = TradeRecords()
        assert records.mt5 is not None

    def test_init_has_result_db(self):
        """Test TradeRecords has ResultDB class reference."""
        records = TradeRecords()
        assert records.result_db is not None

    def test_init_positions_is_none(self):
        """Test TradeRecords positions is None by default."""
        records = TradeRecords()
        assert records.positions is None


class TestGetCsvRecords:
    """Test get_csv_records method."""

    def test_get_csv_records_yields_csv_files(self, tmp_path):
        """Test get_csv_records yields only CSV files."""
        # Create test files
        (tmp_path / "trades1.csv").touch()
        (tmp_path / "trades2.csv").touch()
        (tmp_path / "trades.json").touch()
        (tmp_path / "readme.txt").touch()

        records = TradeRecords(records_dir=tmp_path)
        csv_files = list(records.get_csv_records())

        assert len(csv_files) == 2
        assert all(f.suffix == ".csv" for f in csv_files)

    def test_get_csv_records_empty_dir(self, tmp_path):
        """Test get_csv_records with empty directory."""
        records = TradeRecords(records_dir=tmp_path)
        csv_files = list(records.get_csv_records())
        assert len(csv_files) == 0

    def test_get_csv_records_ignores_directories(self, tmp_path):
        """Test get_csv_records ignores subdirectories."""
        (tmp_path / "trades.csv").touch()
        (tmp_path / "subdir.csv").mkdir()  # Directory with .csv name

        records = TradeRecords(records_dir=tmp_path)
        csv_files = list(records.get_csv_records())

        assert len(csv_files) == 1


class TestGetJsonRecords:
    """Test get_json_records method."""

    def test_get_json_records_yields_json_files(self, tmp_path):
        """Test get_json_records yields only JSON files."""
        # Create test files
        (tmp_path / "trades1.json").touch()
        (tmp_path / "trades2.json").touch()
        (tmp_path / "trades.csv").touch()

        records = TradeRecords(records_dir=tmp_path)
        json_files = list(records.get_json_records())

        assert len(json_files) == 2
        assert all(f.suffix == ".json" for f in json_files)

    def test_get_json_records_empty_dir(self, tmp_path):
        """Test get_json_records with empty directory."""
        records = TradeRecords(records_dir=tmp_path)
        json_files = list(records.get_json_records())
        assert len(json_files) == 0


class TestReadUpdateCsv:
    """Test read_update_csv async method."""

    @pytest.fixture
    def sample_csv_file(self, tmp_path):
        """Create a sample CSV file with trade records."""
        file = tmp_path / "trades.csv"
        rows = [
            {"order": "12345", "time": "1705312800", "profit": "0", "closed": "False", "win": "False"},
            {"order": "12346", "time": "1705312900", "profit": "0", "closed": "False", "win": "False"},
        ]
        with open(file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        return file

    async def test_read_update_csv_reads_file(self, sample_csv_file, tmp_path):
        """Test read_update_csv reads and processes CSV file."""
        records = TradeRecords(records_dir=tmp_path)
        
        # Mock update_rows to return rows unchanged
        records.update_rows = AsyncMock(return_value=[
            {"order": "12345", "time": "1705312800", "profit": "0", "closed": "False", "win": "False"},
            {"order": "12346", "time": "1705312900", "profit": "0", "closed": "False", "win": "False"},
        ])
        
        await records.read_update_csv(file=sample_csv_file)
        
        # Verify update_rows was called
        records.update_rows.assert_called_once()

    async def test_read_update_csv_writes_updated_data(self, sample_csv_file, tmp_path):
        """Test read_update_csv writes updated data back to file."""
        records = TradeRecords(records_dir=tmp_path)
        
        # Mock update_rows to simulate closed trade
        records.update_rows = AsyncMock(return_value=[
            {"order": "12345", "time": "1705312800", "profit": "50.0", "closed": "True", "win": "True"},
            {"order": "12346", "time": "1705312900", "profit": "0", "closed": "False", "win": "False"},
        ])
        
        await records.read_update_csv(file=sample_csv_file)
        
        # Read file and verify update
        with open(sample_csv_file, "r", newline="") as f:
            reader = list(csv.DictReader(f))
            assert reader[0]["profit"] == "50.0"
            assert reader[0]["closed"] == "True"

    async def test_read_update_csv_handles_error(self, tmp_path):
        """Test read_update_csv handles missing file gracefully."""
        records = TradeRecords(records_dir=tmp_path)
        nonexistent = tmp_path / "nonexistent.csv"
        
        # Should not raise, just log error
        await records.read_update_csv(file=nonexistent)


class TestReadUpdateJson:
    """Test read_update_json async method."""

    @pytest.fixture
    def sample_json_file(self, tmp_path):
        """Create a sample JSON file with trade records."""
        file = tmp_path / "trades.json"
        data = [
            {"order": 12345, "time": 1705312800, "profit": 0, "closed": False, "win": False},
            {"order": 12346, "time": 1705312900, "profit": 0, "closed": False, "win": False},
        ]
        with open(file, "w") as f:
            json.dump(data, f)
        return file

    async def test_read_update_json_reads_file(self, sample_json_file, tmp_path):
        """Test read_update_json reads and processes JSON file."""
        records = TradeRecords(records_dir=tmp_path)
        
        records.update_rows = AsyncMock(return_value=[
            {"order": 12345, "time": 1705312800, "profit": 0, "closed": False, "win": False},
            {"order": 12346, "time": 1705312900, "profit": 0, "closed": False, "win": False},
        ])
        
        await records.read_update_json(file=sample_json_file)
        
        records.update_rows.assert_called_once()

    async def test_read_update_json_writes_updated_data(self, sample_json_file, tmp_path):
        """Test read_update_json writes updated data back to file."""
        records = TradeRecords(records_dir=tmp_path)
        
        records.update_rows = AsyncMock(return_value=[
            {"order": 12345, "time": 1705312800, "profit": 50.0, "closed": True, "win": True},
            {"order": 12346, "time": 1705312900, "profit": 0, "closed": False, "win": False},
        ])
        
        await records.read_update_json(file=sample_json_file)
        
        with open(sample_json_file, "r") as f:
            data = json.load(f)
            assert data[0]["profit"] == 50.0
            assert data[0]["closed"] == True

    async def test_read_update_json_handles_error(self, tmp_path):
        """Test read_update_json handles missing file gracefully."""
        records = TradeRecords(records_dir=tmp_path)
        nonexistent = tmp_path / "nonexistent.json"
        
        # Should not raise
        await records.read_update_json(file=nonexistent)


class TestUpdateRows:
    """Test update_rows async method."""

    async def test_update_rows_sorts_by_time(self):
        """Test update_rows sorts rows by time."""
        records = TradeRecords()
        
        rows = [
            {"order": 12346, "time": 1705312900, "closed": False},
            {"order": 12345, "time": 1705312800, "closed": False},
        ]
        
        # Mock history_deals_get
        records.mt5.history_deals_get = AsyncMock(return_value=[])
        
        result = await records.update_rows(rows=rows)
        
        # Rows should be sorted by time
        assert result[0]["time"] == 1705312800
        assert result[1]["time"] == 1705312900

    async def test_update_rows_skips_already_closed(self):
        """Test update_rows skips already closed rows."""
        records = TradeRecords()
        
        rows = [
            {"order": 12345, "time": 1705312800, "closed": True, "profit": 25.0},
            {"order": 12346, "time": 1705312900, "closed": False},
        ]
        
        records.mt5.history_deals_get = AsyncMock(return_value=[])
        
        result = await records.update_rows(rows=rows)
        
        # First row should remain unchanged
        assert result[0]["closed"] == True
        assert result[0]["profit"] == 25.0

    async def test_update_rows_returns_list(self):
        """Test update_rows returns a list."""
        records = TradeRecords()
        
        rows = [{"order": 12345, "time": 1705312800, "closed": False}]
        records.mt5.history_deals_get = AsyncMock(return_value=[])
        
        result = await records.update_rows(rows=rows)
        
        assert isinstance(result, list)


class TestUpdateCsvRecords:
    """Test update_csv_records async method."""

    async def test_update_csv_records_processes_all_files(self, tmp_path):
        """Test update_csv_records processes all CSV files."""
        # Create multiple CSV files
        for i in range(3):
            file = tmp_path / f"trades{i}.csv"
            rows = [{"order": f"1234{i}", "time": "1705312800", "profit": "0", "closed": "False", "win": "False"}]
            with open(file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

        records = TradeRecords(records_dir=tmp_path)
        records.read_update_csv = AsyncMock()
        
        await records.update_csv_records()
        
        assert records.read_update_csv.call_count == 3


class TestUpdateJsonRecords:
    """Test update_json_records async method."""

    async def test_update_json_records_processes_all_files(self, tmp_path):
        """Test update_json_records processes all JSON files."""
        # Create multiple JSON files
        for i in range(3):
            file = tmp_path / f"trades{i}.json"
            data = [{"order": 12340 + i, "time": 1705312800, "profit": 0, "closed": False, "win": False}]
            with open(file, "w") as f:
                json.dump(data, f)

        records = TradeRecords(records_dir=tmp_path)
        records.read_update_json = AsyncMock()
        
        await records.update_json_records()
        
        assert records.read_update_json.call_count == 3


class TestSyncMethods:
    """Test synchronous update methods."""

    def test_read_update_csv_sync(self, tmp_path):
        """Test read_update_csv_sync reads and updates CSV file."""
        # Create sample CSV file
        file = tmp_path / "trades.csv"
        rows = [{"order": "12345", "time": "1705312800", "profit": "0", "closed": "False", "win": "False"}]
        with open(file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        records = TradeRecords(records_dir=tmp_path)
        records.update_rows_sync = MagicMock(return_value=rows)
        
        records.read_update_csv_sync(file=file)
        
        records.update_rows_sync.assert_called_once()

    def test_read_update_json_sync(self, tmp_path):
        """Test read_update_json_sync reads and updates JSON file."""
        file = tmp_path / "trades.json"
        data = [{"order": 12345, "time": 1705312800, "profit": 0, "closed": False, "win": False}]
        with open(file, "w") as f:
            json.dump(data, f)

        records = TradeRecords(records_dir=tmp_path)
        records.update_rows_sync = MagicMock(return_value=data)
        
        records.read_update_json_sync(file=file)
        
        records.update_rows_sync.assert_called_once()

    def test_update_csv_records_sync(self, tmp_path):
        """Test update_csv_records_sync processes all CSV files."""
        # Create CSV files
        for i in range(2):
            file = tmp_path / f"trades{i}.csv"
            rows = [{"order": f"1234{i}", "time": "1705312800"}]
            with open(file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

        records = TradeRecords(records_dir=tmp_path)
        records.read_update_csv_sync = MagicMock()
        
        records.update_csv_records_sync()
        
        assert records.read_update_csv_sync.call_count == 2

    def test_update_json_records_sync(self, tmp_path):
        """Test update_json_records_sync processes all JSON files."""
        # Create JSON files
        for i in range(2):
            file = tmp_path / f"trades{i}.json"
            data = [{"order": 12340 + i, "time": 1705312800}]
            with open(file, "w") as f:
                json.dump(data, f)

        records = TradeRecords(records_dir=tmp_path)
        records.read_update_json_sync = MagicMock()
        
        records.update_json_records_sync()
        
        assert records.read_update_json_sync.call_count == 2


class TestSingleFileUpdates:
    """Test single file update methods."""

    async def test_update_csv_record(self, tmp_path):
        """Test update_csv_record updates a single CSV file."""
        file = tmp_path / "single.csv"
        file.touch()

        records = TradeRecords(records_dir=tmp_path)
        records.read_update_csv = AsyncMock()
        
        await records.update_csv_record(file=file)
        
        records.read_update_csv.assert_called_once_with(file=file)

    async def test_update_json_record(self, tmp_path):
        """Test update_json_record updates a single JSON file."""
        file = tmp_path / "single.json"
        file.touch()

        records = TradeRecords(records_dir=tmp_path)
        records.read_update_json = AsyncMock()
        
        await records.update_json_record(file=file)
        
        records.read_update_json.assert_called_once_with(file=file)

    def test_update_csv_record_sync(self, tmp_path):
        """Test update_csv_record_sync updates a single CSV file."""
        file = tmp_path / "single.csv"
        file.touch()

        records = TradeRecords(records_dir=tmp_path)
        records.read_update_csv_sync = MagicMock()
        
        records.update_csv_record_sync(file=file)
        
        records.read_update_csv_sync.assert_called_once_with(file=file)

    def test_update_json_record_sync(self, tmp_path):
        """Test update_json_record_sync updates a single JSON file."""
        file = tmp_path / "single.json"
        file.touch()

        records = TradeRecords(records_dir=tmp_path)
        records.read_update_json_sync = MagicMock()
        
        records.update_json_record_sync(file=file)
        
        records.read_update_json_sync.assert_called_once_with(file=file)


class TestGetSqlRecordsUnclosed:
    """Test get_sql_records_unclosed method."""

    def test_get_sql_records_unclosed_calls_execute_raw(self):
        """Test get_sql_records_unclosed calls ResultDB.execute_raw with correct query."""
        records = TradeRecords()
        records.result_db = MagicMock()
        records.result_db.execute_raw = MagicMock(return_value=[])

        result = records.get_sql_records_unclosed()

        records.result_db.execute_raw.assert_called_once_with("select * from result where closed = 0")
        assert result == []

    def test_get_sql_records_unclosed_returns_list(self):
        """Test get_sql_records_unclosed returns a list."""
        records = TradeRecords()
        mock_rows = [MagicMock(), MagicMock()]
        records.result_db = MagicMock()
        records.result_db.execute_raw = MagicMock(return_value=mock_rows)

        result = records.get_sql_records_unclosed()

        assert len(result) == 2


class TestUpdateRowsSync:
    """Test update_rows_sync method."""

    def test_update_rows_sync_sorts_by_time(self):
        """Test update_rows_sync sorts rows by time."""
        records = TradeRecords()
        
        rows = [
            {"order": 12346, "time": 1705312900, "closed": False},
            {"order": 12345, "time": 1705312800, "closed": False},
        ]
        
        records.mt5._history_deals_get = MagicMock(return_value=[])
        
        result = records.update_rows_sync(rows=rows)
        
        assert result[0]["time"] == 1705312800
        assert result[1]["time"] == 1705312900

    def test_update_rows_sync_returns_list(self):
        """Test update_rows_sync returns a list."""
        records = TradeRecords()

        rows = [{"order": 12345, "time": 1705312800, "closed": False}]
        records.mt5._history_deals_get = MagicMock(return_value=[])

        result = records.update_rows_sync(rows=rows)

        assert isinstance(result, list)


class TestStrToBool:
    """Test str_to_bool static method."""

    def test_str_to_bool_true_string(self):
        """Test str_to_bool converts 'True' string to True."""
        assert TradeRecords.str_to_bool("True") is True

    def test_str_to_bool_false_string(self):
        """Test str_to_bool converts 'False' string to False."""
        assert TradeRecords.str_to_bool("False") is False

    def test_str_to_bool_true_lowercase(self):
        """Test str_to_bool converts 'true' lowercase to True."""
        assert TradeRecords.str_to_bool("true") is True

    def test_str_to_bool_false_lowercase(self):
        """Test str_to_bool converts 'false' lowercase to False."""
        assert TradeRecords.str_to_bool("false") is False

    def test_str_to_bool_bool_true(self):
        """Test str_to_bool passes through bool True."""
        assert TradeRecords.str_to_bool(True) is True

    def test_str_to_bool_bool_false(self):
        """Test str_to_bool passes through bool False."""
        assert TradeRecords.str_to_bool(False) is False

    def test_str_to_bool_invalid_raises_type_error(self):
        """Test str_to_bool raises TypeError for invalid value."""
        with pytest.raises(TypeError):
            TradeRecords.str_to_bool("maybe")

    def test_str_to_bool_mixed_case(self):
        """Test str_to_bool handles mixed case strings."""
        assert TradeRecords.str_to_bool("TRUE") is True
        assert TradeRecords.str_to_bool("FALSE") is False


class TestUpdateRowsDealMatching:
    """Test update_rows and update_rows_sync deal matching logic."""

    async def test_update_rows_updates_closed_deal(self):
        """Test update_rows updates a row when matching closing deal is found."""
        records = TradeRecords()

        rows = [
            {"order": 12345, "time": 1705312800, "closed": False, "profit": 0, "win": False},
        ]

        # Mock a closing deal
        mock_deal = MagicMock()
        mock_deal.position_id = 12345
        mock_deal.order = 99999  # Different from position_id → closing deal
        mock_deal.entry = records.mt5.DEAL_ENTRY_OUT
        mock_deal.profit = 50.0
        mock_deal.time_msc = 1705316400000
        mock_deal.price = 1.0900

        records.mt5.history_deals_get = AsyncMock(return_value=[mock_deal])

        result = await records.update_rows(rows=rows)

        assert result[0]["closed"] is True
        assert result[0]["profit"] == 50.0
        assert result[0]["win"] is True
        assert result[0]["price_close"] == 1.0900

    async def test_update_rows_no_match_leaves_unchanged(self):
        """Test update_rows leaves row unchanged when no matching deal."""
        records = TradeRecords()

        rows = [
            {"order": 12345, "time": 1705312800, "closed": False, "profit": 0},
        ]

        records.mt5.history_deals_get = AsyncMock(return_value=[])

        result = await records.update_rows(rows=rows)

        assert result[0]["closed"] is False
        assert result[0]["profit"] == 0

    async def test_update_rows_skips_string_closed_true(self):
        """Test update_rows skips rows with string 'True' closed value."""
        records = TradeRecords()

        rows = [
            {"order": "12345", "time": "1705312800", "closed": "True", "profit": "25.0"},
        ]

        records.mt5.history_deals_get = AsyncMock(return_value=[])

        result = await records.update_rows(rows=rows)

        # Should remain unchanged since already closed
        assert result[0]["closed"] == "True"

    def test_update_rows_sync_updates_closed_deal(self):
        """Test update_rows_sync updates a row when matching closing deal is found."""
        records = TradeRecords()

        rows = [
            {"order": 12345, "time": 1705312800, "closed": False, "profit": 0, "win": False},
        ]

        mock_deal = MagicMock()
        mock_deal.position_id = 12345
        mock_deal.order = 99999
        mock_deal.entry = records.mt5.DEAL_ENTRY_OUT
        mock_deal.profit = -10.0
        mock_deal.time_msc = 1705316400000
        mock_deal.price = 1.0800

        records.mt5._history_deals_get = MagicMock(return_value=[mock_deal])

        result = records.update_rows_sync(rows=rows)

        assert result[0]["closed"] is True
        assert result[0]["profit"] == -10.0
        assert result[0]["win"] is False
        assert result[0]["price_close"] == 1.0800


class TestUpdateSqlRecords:
    """Test update_sql_records async method."""

    async def test_update_sql_records_updates_matching_deals(self):
        """Test update_sql_records updates rows with matching closing deals."""
        records = TradeRecords()

        # Mock unclosed rows
        mock_row = MagicMock()
        mock_row.time = 1705312800000
        mock_row.order = 12345
        mock_row.closed = False

        records.get_sql_records_unclosed = MagicMock(return_value=[mock_row])
        records.result_db = MagicMock()
        mock_conn = MagicMock()
        records.result_db.get_connection = MagicMock(return_value=mock_conn)

        # Mock closing deal
        mock_deal = MagicMock()
        mock_deal.position_id = 12345
        mock_deal.order = 99999
        mock_deal.entry = records.mt5.DEAL_ENTRY_OUT
        mock_deal.profit = 75.0
        mock_deal.time_msc = 1705316400000
        mock_deal.price = 1.0900

        records.mt5.history_deals_get = AsyncMock(return_value=[mock_deal])

        await records.update_sql_records()

        # Verify row.save was called with update data
        mock_row.save.assert_called_once()
        call_kwargs = mock_row.save.call_args
        assert call_kwargs.kwargs["update"] is True
        assert call_kwargs.kwargs["commit"] is False
        assert call_kwargs.kwargs["data"]["profit"] == 75.0
        assert call_kwargs.kwargs["data"]["win"] is True
        assert call_kwargs.kwargs["data"]["closed"] is True

        # Verify batch commit
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    async def test_update_sql_records_skips_already_closed(self):
        """Test update_sql_records skips rows that are already closed."""
        records = TradeRecords()

        mock_row = MagicMock()
        mock_row.time = 1705312800000
        mock_row.order = 12345
        mock_row.closed = True  # Already closed

        records.get_sql_records_unclosed = MagicMock(return_value=[mock_row])
        records.result_db = MagicMock()
        mock_conn = MagicMock()
        records.result_db.get_connection = MagicMock(return_value=mock_conn)

        mock_deal = MagicMock()
        mock_deal.position_id = 12345
        mock_deal.order = 99999
        mock_deal.entry = records.mt5.DEAL_ENTRY_OUT
        mock_deal.profit = 50.0
        mock_deal.time_msc = 1705316400000
        mock_deal.price = 1.0900

        records.mt5.history_deals_get = AsyncMock(return_value=[mock_deal])

        await records.update_sql_records()

        # row.save should not be called since row is already closed
        mock_row.save.assert_not_called()


class TestSyncWriteVerification:
    """Test that sync methods correctly write back to files."""

    def test_read_update_csv_sync_writes_updated_data(self, tmp_path):
        """Test read_update_csv_sync writes updated data back to file."""
        file = tmp_path / "trades.csv"
        rows = [
            {"order": "12345", "time": "1705312800", "profit": "0", "closed": "False", "win": "False"},
        ]
        with open(file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        records = TradeRecords(records_dir=tmp_path)
        records.update_rows_sync = MagicMock(return_value=[
            {"order": "12345", "time": "1705312800", "profit": "50.0", "closed": "True", "win": "True"},
        ])

        records.read_update_csv_sync(file=file)

        # Verify file was written with updated data
        with open(file, "r", newline="") as f:
            reader = list(csv.DictReader(f))
            assert reader[0]["profit"] == "50.0"
            assert reader[0]["closed"] == "True"

    def test_read_update_json_sync_writes_updated_data(self, tmp_path):
        """Test read_update_json_sync writes updated data back to file."""
        file = tmp_path / "trades.json"
        data = [{"order": 12345, "time": 1705312800, "profit": 0, "closed": False}]
        with open(file, "w") as f:
            json.dump(data, f)

        records = TradeRecords(records_dir=tmp_path)
        records.update_rows_sync = MagicMock(return_value=[
            {"order": 12345, "time": 1705312800, "profit": 50.0, "closed": True},
        ])

        records.read_update_json_sync(file=file)

        with open(file, "r") as f:
            result = json.load(f)
            assert result[0]["profit"] == 50.0
            assert result[0]["closed"] is True

    def test_read_update_csv_sync_handles_error(self, tmp_path):
        """Test read_update_csv_sync handles missing file gracefully."""
        records = TradeRecords(records_dir=tmp_path)
        nonexistent = tmp_path / "nonexistent.csv"
        # Should not raise, just log error
        records.read_update_csv_sync(file=nonexistent)

    def test_read_update_json_sync_handles_error(self, tmp_path):
        """Test read_update_json_sync handles missing file gracefully."""
        records = TradeRecords(records_dir=tmp_path)
        nonexistent = tmp_path / "nonexistent.json"
        # Should not raise, just log error
        records.read_update_json_sync(file=nonexistent)
