"""Comprehensive tests for the Result module.

Tests cover:
- Result initialization with various parameters
- Auto-time behavior in __init__
- get_data method for preparing trade data
- save async method with different trade record modes
- save_sync method with different trade record modes
- to_csv method for CSV file storage
- to_json method for JSON file storage
- to_sql method for SQLite database storage
- serialize static method
- Thread safety with Lock
- Edge cases and error handling
- OrderSendResult None field filtering
"""

import asyncio
import csv
import json
from pathlib import Path
from datetime import datetime
from threading import Thread

import pytest

from aiomql.lib.result import Result
from aiomql.core.models import OrderSendResult, TradeRequest
from aiomql.core.config import Config


class TestResultInitialization:
    """Test Result class initialization."""

    @pytest.fixture(scope="class")
    def mock_order_result(self):
        """Create a mock OrderSendResult with TradeRequest."""
        request = TradeRequest(
            action=1,
            type=0,
            order=0,
            symbol="EURUSD",
            volume=0.01,
            sl=1.0800,
            tp=1.0900,
            price=1.0850,
            deviation=10,
            stop_limit=0,
            type_time=0,
            type_filling=0,
            expiration=0,
            position=0,
            position_by=0,
            comment="",
            magic=0
        )
        osr = OrderSendResult(
            retcode=10009,
            deal=12345,
            order=67890,
            volume=0.01,
            price=1.0850,
            bid=1.0849,
            ask=1.0851,
            comment="",
            request_id=0,
            retcode_external=0,
        )
        osr.request = request
        return osr

    def test_init_with_result_only(self, mock_order_result):
        """Test Result can be initialized with just a result."""
        result = Result(result=mock_order_result)
        assert result.result == mock_order_result
        assert result.parameters == {}
        assert result.name == "Trades"

    def test_init_with_parameters(self, mock_order_result):
        """Test Result initialized with parameters."""
        params = {"symbol": "EURUSD", "strategy": "MA_Cross"}
        result = Result(result=mock_order_result, parameters=params)
        assert result.parameters == params
        assert result.result == mock_order_result

    def test_init_with_name(self, mock_order_result):
        """Test Result initialized with explicit name."""
        result = Result(result=mock_order_result, name="MyStrategy")
        assert result.name == "MyStrategy"

    def test_init_name_from_parameters(self, mock_order_result):
        """Test Result name defaults to 'name' key in parameters."""
        params = {"name": "ParameterName", "symbol": "EURUSD"}
        result = Result(result=mock_order_result, parameters=params)
        assert result.name == "ParameterName"

    def test_init_explicit_name_overrides_parameters(self, mock_order_result):
        """Test explicit name overrides parameters name."""
        params = {"name": "ParameterName", "symbol": "EURUSD"}
        result = Result(result=mock_order_result, parameters=params, name="ExplicitName")
        assert result.name == "ExplicitName"

    def test_init_with_extra_params(self, mock_order_result):
        """Test Result initialized with extra keyword arguments."""
        result = Result(
            result=mock_order_result,
            time=1705312800000,
            expected_profit=10.5
        )
        assert result.extra_params["time"] == 1705312800000
        assert result.extra_params["expected_profit"] == 10.5

    def test_init_has_config(self, mock_order_result):
        """Test Result has Config instance."""
        result = Result(result=mock_order_result)
        assert hasattr(result, 'config')
        assert isinstance(result.config, Config)

    def test_init_auto_sets_time_in_extra_params(self, mock_order_result):
        """Test Result auto-sets time in extra_params when not provided."""
        result = Result(result=mock_order_result)
        assert "time" in result.extra_params
        assert isinstance(result.extra_params["time"], float)
        assert result.extra_params["time"] > 0

    def test_init_preserves_explicit_time_in_extra_params(self, mock_order_result):
        """Test Result preserves explicitly provided time."""
        explicit_time = 1705312800000
        result = Result(result=mock_order_result, time=explicit_time)
        assert result.extra_params["time"] == explicit_time

    def test_init_has_lock_class_attribute(self, mock_order_result):
        """Test Result class has Lock attribute."""
        assert hasattr(Result, 'lock')


class TestGetData:
    """Test get_data method."""

    @pytest.fixture(scope="class")
    def mock_order_result(self):
        """Create a mock OrderSendResult with TradeRequest."""
        request = TradeRequest(
            action=1,
            type=0,
            order=0,
            symbol="EURUSD",
            volume=0.01,
            sl=1.0800,
            tp=1.0900,
            price=1.0850,
            deviation=10,
            stop_limit=0,
            type_time=0,
            type_filling=0,
            expiration=0,
            position=0,
            position_by=0,
            comment="Test comment",
            magic=0
        )
        osr = OrderSendResult(
            retcode=10009,
            deal=12345,
            order=67890,
            volume=0.01,
            price=1.0850,
            bid=1.0849,
            ask=1.0851,
            comment="Test comment",
            request_id=100,
            retcode_external=0,
        )
        osr.request = request
        return osr

    def test_get_data_returns_dict(self, mock_order_result):
        """Test get_data returns a dictionary."""
        result = Result(result=mock_order_result)
        data = result.get_data()
        assert isinstance(data, dict)

    def test_get_data_includes_order_fields(self, mock_order_result):
        """Test get_data includes order result fields."""
        result = Result(result=mock_order_result)
        data = result.get_data()
        assert "deal" in data
        assert "order" in data
        assert "volume" in data
        assert "price" in data

    def test_get_data_excludes_retcode_fields(self, mock_order_result):
        """Test get_data excludes retcode and comment fields."""
        result = Result(result=mock_order_result)
        data = result.get_data()
        assert "retcode" not in data
        assert "comment" not in data
        assert "retcode_external" not in data
        assert "request_id" not in data

    def test_get_data_excludes_request_object(self, mock_order_result):
        """Test get_data excludes the request object."""
        result = Result(result=mock_order_result)
        data = result.get_data()
        assert "request" not in data

    def test_get_data_includes_request_fields(self, mock_order_result):
        """Test get_data includes symbol, type, sl, tp from request."""
        result = Result(result=mock_order_result)
        data = result.get_data()
        assert "symbol" in data
        assert "type" in data
        assert "sl" in data
        assert "tp" in data

    def test_get_data_includes_default_tracking_fields(self, mock_order_result):
        """Test get_data includes default tracking fields."""
        result = Result(result=mock_order_result)
        data = result.get_data()
        assert data["profit"] == 0
        assert data["closed"] == False
        assert data["win"] == False

    def test_get_data_includes_parameters_key(self, mock_order_result):
        """Test get_data includes parameters dict under 'parameters' key."""
        params = {"ema": 20, "rsi": 14}
        result = Result(result=mock_order_result, parameters=params)
        data = result.get_data()
        assert "parameters" in data
        assert data["parameters"] == params

    def test_get_data_includes_parameters(self, mock_order_result):
        """Test get_data includes strategy parameters."""
        params = {"symbol": "EURUSD", "ema": 20, "rsi": 14}
        result = Result(result=mock_order_result, parameters=params)
        data = result.get_data()
        assert data["symbol"] == "EURUSD"
        assert data["parameters"]["ema"] == 20
        assert data["parameters"]["rsi"] == 14

    def test_get_data_includes_time_key(self, mock_order_result):
        """Test get_data includes auto-set time from extra_params."""
        result = Result(result=mock_order_result)
        data = result.get_data()
        assert "time" in data
        assert isinstance(data["time"], float)

    def test_get_data_includes_extra_params(self, mock_order_result):
        """Test get_data includes extra parameters."""
        result = Result(
            result=mock_order_result,
            time=1705312800000,
            expected_profit=15.0
        )
        data = result.get_data()
        assert data["time"] == 1705312800000
        assert data["expected_profit"] == 15.0


class TestSerialize:
    """Test serialize static method."""

    def test_serialize_string(self):
        """Test serialize converts string."""
        assert Result.serialize("hello") == "hello"

    def test_serialize_integer(self):
        """Test serialize converts integer."""
        assert Result.serialize(42) == "42"

    def test_serialize_float(self):
        """Test serialize converts float."""
        assert Result.serialize(3.14) == "3.14"

    def test_serialize_list(self):
        """Test serialize converts list."""
        result = Result.serialize([1, 2, 3])
        assert result == "[1, 2, 3]"

    def test_serialize_dict(self):
        """Test serialize converts dict."""
        result = Result.serialize({"key": "value"})
        assert "key" in result
        assert "value" in result

    def test_serialize_datetime(self):
        """Test serialize converts datetime."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = Result.serialize(dt)
        assert "2024" in result
        assert "01" in result
        assert "15" in result

    def test_serialize_none(self):
        """Test serialize converts None."""
        assert Result.serialize(None) == "None"

    def test_serialize_boolean(self):
        """Test serialize converts boolean."""
        assert Result.serialize(True) == "True"
        assert Result.serialize(False) == "False"


class TestSaveAsync:
    """Test async save method with live trading."""

    @pytest.fixture(scope="class")
    def parameters(self):
        """Create test parameters."""
        return {"name": "test_result_async", "symbol": "BTCUSD", "ema": 20, "rsi": 14}

    @pytest.fixture(scope="function")
    async def order_result(self, mt, buy_order, parameters):
        """Create an order and return Result instance."""
        res = await mt.order_send(buy_order)
        return Result(result=OrderSendResult(**res._asdict()), parameters=parameters)

    async def test_save_csv_creates_file(self, order_result):
        """Test save with csv mode creates file."""
        await order_result.save(trade_record_mode="csv")
        file = order_result.config.records_dir / f"{order_result.name}.csv"
        assert file.exists()

    async def test_save_json_creates_file(self, order_result):
        """Test save with json mode creates file."""
        await order_result.save(trade_record_mode="json")
        file = order_result.config.records_dir / f"{order_result.name}.json"
        assert file.exists()

    async def test_save_sql_no_exception(self, order_result):
        """Test save with sql mode does not raise exception."""
        await order_result.save(trade_record_mode="sql")

    async def test_save_invalid_mode_no_exception(self, order_result):
        """Test save with invalid mode does not raise but logs error."""
        await order_result.save(trade_record_mode="invalid_mode")

    async def test_save_uses_default_mode(self, order_result):
        """Test save uses config default mode when not specified."""
        original_mode = order_result.config.trade_record_mode
        order_result.config.trade_record_mode = "csv"
        await order_result.save()
        file = order_result.config.records_dir / f"{order_result.name}.csv"
        assert file.exists()
        order_result.config.trade_record_mode = original_mode


class TestSaveSync:
    """Test sync save method with live trading."""

    @pytest.fixture(scope="class")
    def parameters(self):
        """Create test parameters."""
        return {"name": "test_result_sync", "symbol": "BTCUSD", "ema": 20}

    @pytest.fixture(scope="function")
    async def order_result(self, mt, sell_order, parameters):
        """Create an order and return Result instance."""
        res = await mt.order_send(sell_order)
        return Result(result=OrderSendResult(**res._asdict()), parameters=parameters)

    async def test_save_sync_csv(self, order_result):
        """Test save_sync with csv mode."""
        order_result.save_sync(trade_record_mode="csv")
        file = order_result.config.records_dir / f"{order_result.name}.csv"
        assert file.exists()

    async def test_save_sync_json(self, order_result):
        """Test save_sync with json mode."""
        order_result.save_sync(trade_record_mode="json")
        file = order_result.config.records_dir / f"{order_result.name}.json"
        assert file.exists()

    async def test_save_sync_sql_no_exception(self, order_result):
        """Test save_sync with sql mode does not raise exception."""
        order_result.save_sync(trade_record_mode="sql")


class TestToCsv:
    """Test to_csv method."""

    @pytest.fixture(scope="class")
    def parameters(self):
        """Create test parameters."""
        return {"name": "test_csv_method", "symbol": "EURUSD", "strategy": "test"}

    @pytest.fixture(scope="function")
    async def order_result(self, mt, buy_order, parameters):
        """Create an order and return Result instance."""
        res = await mt.order_send(buy_order)
        return Result(result=OrderSendResult(**res._asdict()), parameters=parameters)

    async def test_to_csv_creates_file(self, order_result):
        """Test to_csv creates CSV file."""
        order_result.to_csv()
        file = order_result.config.records_dir / f"{order_result.name}.csv"
        assert file.exists()

    async def test_to_csv_has_headers(self, order_result):
        """Test CSV file has headers."""
        order_result.to_csv()
        file = order_result.config.records_dir / f"{order_result.name}.csv"
        with file.open("r") as fh:
            reader = csv.DictReader(fh)
            headers = reader.fieldnames
            assert "deal" in headers
            assert "order" in headers

    async def test_to_csv_appends_rows(self, order_result):
        """Test to_csv appends rows to existing file."""
        order_result.to_csv()
        order_result.to_csv()  # Append second row
        file = order_result.config.records_dir / f"{order_result.name}.csv"
        with file.open("r") as fh:
            reader = list(csv.DictReader(fh))
            assert len(reader) >= 2

    async def test_to_csv_divides_time_by_1000(self, order_result):
        """Test to_csv divides time by 1000 for seconds conversion."""
        raw_time = order_result.get_data()["time"]
        order_result.to_csv()
        file = order_result.config.records_dir / f"{order_result.name}.csv"
        with file.open("r") as fh:
            reader = list(csv.DictReader(fh))
            last_row = reader[-1]
            assert float(last_row["time"]) == pytest.approx(raw_time / 1000, rel=1e-3)

    async def test_to_csv_flattens_parameters(self, order_result):
        """Test to_csv flattens parameters dict into row columns."""
        order_result.to_csv()
        file = order_result.config.records_dir / f"{order_result.name}.csv"
        with file.open("r") as fh:
            reader = list(csv.DictReader(fh))
            last_row = reader[-1]
            # 'parameters' key should not be in row (it's popped and flattened)
            assert "parameters" not in last_row
            # Strategy param keys should be present
            assert "strategy" in last_row


class TestToJson:
    """Test to_json method."""

    @pytest.fixture(scope="class")
    def parameters(self):
        """Create test parameters."""
        return {"name": "test_json_method", "symbol": "BTCUSD", "strategy": "json_test"}

    @pytest.fixture(scope="function")
    async def order_result(self, mt, sell_order, parameters):
        """Create an order and return Result instance."""
        res = await mt.order_send(sell_order)
        return Result(result=OrderSendResult(**res._asdict()), parameters=parameters)

    async def test_to_json_creates_file(self, order_result):
        """Test to_json creates JSON file."""
        order_result.to_json()
        file = order_result.config.records_dir / f"{order_result.name}.json"
        assert file.exists()

    async def test_to_json_creates_array(self, order_result):
        """Test JSON file contains array."""
        order_result.to_json()
        file = order_result.config.records_dir / f"{order_result.name}.json"
        with file.open("r") as fh:
            data = json.load(fh)
            assert isinstance(data, list)

    async def test_to_json_appends_records(self, order_result):
        """Test to_json appends records to array."""
        order_result.to_json()
        order_result.to_json()  # Append second record
        file = order_result.config.records_dir / f"{order_result.name}.json"
        with file.open("r") as fh:
            data = json.load(fh)
            assert len(data) >= 2

    async def test_to_json_record_has_required_fields(self, order_result):
        """Test JSON record has required fields."""
        order_result.to_json()
        file = order_result.config.records_dir / f"{order_result.name}.json"
        with file.open("r") as fh:
            data = json.load(fh)
            record = data[-1]  # Last record
            assert "deal" in record
            assert "order" in record
            assert "profit" in record
            assert "closed" in record
            assert "win" in record


class TestToSql:
    """Test to_sql method."""

    @pytest.fixture(scope="class")
    def parameters(self):
        """Create test parameters with required symbol."""
        return {"name": "test_sql_method", "symbol": "EURUSD", "strategy": "sql_test"}

    @pytest.fixture(scope="function")
    async def order_result(self, mt, buy_order, parameters):
        """Create an order and return Result instance."""
        res = await mt.order_send(buy_order)
        return Result(
            result=OrderSendResult(**res._asdict()),
            parameters=parameters,
            time=int(datetime.now().timestamp() * 1000)
        )

    async def test_to_sql_no_exception(self, order_result):
        """Test to_sql does not raise exception."""
        # Should not raise
        order_result.to_sql()

    async def test_to_sql_filters_data_to_result_db_fields(self, order_result):
        """Test to_sql uses filter_dict to pass only valid ResultDB fields."""
        from aiomql.lib.result_db import ResultDB
        data = order_result.get_data() | {"name": order_result.name}
        filtered = ResultDB.filter_dict(data)
        # Only ResultDB field names should be in filtered data
        valid_fields = set(ResultDB.fields())
        assert set(filtered.keys()).issubset(valid_fields)


class TestConcurrentSaves:
    """Test concurrent save operations."""

    @pytest.fixture(scope="class")
    def parameters(self):
        """Create test parameters."""
        return {"name": "test_concurrent", "symbol": "BTCUSD"}

    @pytest.fixture(scope="function")
    async def order_results(self, mt, buy_order, sell_order, parameters):
        """Create multiple orders and return Result instances."""
        res1 = await mt.order_send(buy_order)
        res2 = await mt.order_send(sell_order)
        result1 = Result(result=OrderSendResult(**res1._asdict()), parameters=parameters)
        result2 = Result(result=OrderSendResult(**res2._asdict()), parameters=parameters)
        return result1, result2

    async def test_concurrent_csv_saves(self, order_results):
        """Test concurrent CSV saves are thread-safe."""
        res1, res2 = order_results
        await asyncio.gather(
            res1.save(trade_record_mode="csv"),
            res2.save(trade_record_mode="csv")
        )
        file = res1.config.records_dir / f"{res1.name}.csv"
        assert file.exists()

    async def test_concurrent_json_saves(self, order_results):
        """Test concurrent JSON saves are thread-safe."""
        res1, res2 = order_results
        await asyncio.gather(
            res1.save(trade_record_mode="json"),
            res2.save(trade_record_mode="json")
        )
        file = res1.config.records_dir / f"{res1.name}.json"
        assert file.exists()


class TestResultIntegration:
    """Integration tests for Result with live trading."""

    @pytest.fixture(scope="class")
    def parameters(self):
        """Create test parameters."""
        return {"name": "test_integration", "symbol": "BTCUSD", "ema": 20, "rsi": 14}

    @pytest.fixture(scope="function")
    async def order_results(self, mt, buy_order, sell_order, parameters):
        """Create orders and return Result instances."""
        res1 = await mt.order_send(buy_order)
        res2 = await mt.order_send(sell_order)
        result1 = Result(result=OrderSendResult(**res1._asdict()), parameters=parameters)
        result2 = Result(result=OrderSendResult(**res2._asdict()), parameters=parameters)
        return result1, result2

    async def test_full_workflow_csv(self, order_results):
        """Test complete CSV workflow."""
        res1, res2 = order_results

        # Get data
        data1 = res1.get_data()
        data2 = res2.get_data()
        assert "deal" in data1
        assert "deal" in data2

        # Save both
        await asyncio.gather(res1.save(trade_record_mode="csv"), res2.save(trade_record_mode="csv"))

        # Verify file exists with data
        file = res1.config.records_dir / f"{res1.name}.csv"
        assert file.exists()
        with file.open("r") as fh:
            reader = list(csv.DictReader(fh))
            assert len(reader) >= 2

    async def test_full_workflow_json(self, order_results):
        """Test complete JSON workflow."""
        res1, res2 = order_results

        # Save both
        await asyncio.gather(res1.save(trade_record_mode="json"), res2.save(trade_record_mode="json"))

        # Verify file exists with data
        file = res1.config.records_dir / f"{res1.name}.json"
        assert file.exists()
        with file.open("r") as fh:
            data = json.load(fh)
            assert isinstance(data, list)
            assert len(data) >= 2


class TestResultEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture(scope="class")
    def mock_order_result(self):
        """Create a mock OrderSendResult with TradeRequest."""
        request = TradeRequest(
            action=1,
            type=0,
            order=0,
            symbol="EURUSD",
            volume=0.01,
            sl=1.0800,
            tp=1.0900,
            price=1.0850,
            deviation=10,
            stop_limit=0,
            type_time=0,
            type_filling=0,
            expiration=0,
            position=0,
            position_by=0,
            comment="",
            magic=0
        )
        osr = OrderSendResult(
            retcode=10009,
            deal=12345,
            order=67890,
            volume=0.01,
            price=1.0850,
            bid=1.0849,
            ask=1.0851,
            comment="",
            request_id=0,
            retcode_external=0,
        )
        osr.request = request
        return osr

    def test_empty_parameters(self, mock_order_result):
        """Test Result with empty parameters dict."""
        result = Result(result=mock_order_result, parameters={})
        assert result.parameters == {}
        assert result.name == "Trades"

    def test_none_parameters(self, mock_order_result):
        """Test Result with None parameters."""
        result = Result(result=mock_order_result, parameters=None)
        assert result.parameters == {}

    def test_empty_name(self, mock_order_result):
        """Test Result with empty name string."""
        result = Result(result=mock_order_result, name="")
        assert result.name == "Trades"

    def test_special_characters_in_name(self, mock_order_result):
        """Test Result with special characters in name."""
        result = Result(result=mock_order_result, name="Test_Strategy-123")
        assert result.name == "Test_Strategy-123"

    def test_large_parameters_dict(self, mock_order_result):
        """Test Result with large parameters dictionary."""
        large_params = {f"param_{i}": i for i in range(100)}
        large_params["name"] = "LargeParams"
        result = Result(result=mock_order_result, parameters=large_params)
        assert len(result.parameters) == 101

    def test_nested_parameters(self, mock_order_result):
        """Test Result with nested parameters."""
        nested_params = {
            "name": "Nested",
            "symbol": "EURUSD",
            "settings": {"ema": [10, 20, 50], "rsi": 14}
        }
        result = Result(result=mock_order_result, parameters=nested_params)
        assert result.parameters["settings"]["ema"] == [10, 20, 50]

    def test_multiple_extra_params(self, mock_order_result):
        """Test Result with multiple extra parameters."""
        result = Result(
            result=mock_order_result,
            time=1705312800000,
            expected_profit=15.0,
            custom1="value1",
            custom2=42,
            custom3=[1, 2, 3]
        )
        assert len(result.extra_params) == 5

    def test_get_data_preserves_order_values(self, mock_order_result):
        """Test get_data preserves original order values."""
        result = Result(result=mock_order_result)
        data = result.get_data()
        assert data["deal"] == 12345
        assert data["order"] == 67890
        assert data["volume"] == 0.01
        assert data["price"] == 1.0850

    def test_get_data_excludes_none_profit_loss(self, mock_order_result):
        """Test get_data excludes OrderSendResult fields with None values."""
        # OrderSendResult has profit=None and loss=None by default
        # get_dict filters out None values, so they should not appear
        result = Result(result=mock_order_result)
        res_dict = mock_order_result.get_dict(
            exclude={"retcode", "comment", "retcode_external", "request_id", "request"}
        )
        # profit and loss have None defaults and should be filtered out by get_dict
        assert "loss" not in res_dict
