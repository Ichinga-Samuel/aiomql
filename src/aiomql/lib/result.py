"""Result module for recording and storing trade results.

This module provides the Result class for saving trade results and
strategy parameters to CSV, JSON, or SQL formats for record keeping
and analysis.

Example:
    Recording a trade result::

        result = Result(
            result=order_result,
            parameters={'volume': 0.1, 'magic': 12345},
            name='MyStrategy',
            time=1705312800000,
            expected_profit=50.0
        )
        await result.save()  # Saves to configured format (csv/json/sql)

    Recording synchronously::

        result.save_sync(trade_record_mode='csv')  # Force CSV format
"""

import csv
import json
from datetime import datetime
from logging import getLogger
from typing import Iterable, Literal
from threading import Lock

from ..core.config import Config
from ..core.models import OrderSendResult
from .result_db import ResultDB

logger = getLogger(__name__)


class Result:
    """Handler for trade results and strategy parameters for record keeping.

    Manages the recording of trade execution results and associated strategy
    parameters to various storage formats (CSV, JSON, or SQL database).
    Uses thread-safe locking for concurrent write operations.

    Attributes:
        config (Config): The configuration object for accessing settings.
        lock (Lock): Thread lock for safe concurrent file operations.
        parameters (dict): Strategy parameters associated with the trade.
        result (OrderSendResult): The trade execution result from the broker.
        name (str): Name for the result file/record.
        extra_params (dict): Additional parameters passed via kwargs.

    Example:
        Recording a trade result::

            result = Result(
                result=order_result,
                parameters={'symbol': 'EURUSD', 'strategy': 'MA_Cross'},
                name='MyStrategy'
            )
            await result.save()  # Saves to configured format
    """

    config: Config
    lock = Lock()

    def __init__(self, *, result: OrderSendResult, parameters: dict = None, name: str = "", **kwargs):
        """Initialize the Result instance with trade data and parameters.

        Args:
            result: The order execution result from the broker containing
                deal details, order ticket, prices, and status.
            parameters: Strategy parameters to associate with this trade.
                Defaults to empty dict if not provided.
            name: Name for the result file or record. If empty, uses
                the 'name' key from parameters or defaults to 'Trades'.
            **kwargs: Additional parameters to include in the record:
                - time (float): Trade timestamp in milliseconds.
                - expected_profit (float): Expected profit at entry.
                - Any other custom fields to store.

        Example:
            >>> result = Result(
            ...     result=order_result,
            ...     parameters={'magic': 12345, 'volume': 0.1},
            ...     name='ScalpingStrategy',
            ...     time=1705312800000,
            ...     expected_profit=25.5
            ... )
        """
        self.config = Config()
        self.parameters = parameters or {}
        self.result = result
        self.name = name or self.parameters.get("name", "Trades")
        self.extra_params = kwargs
        if not self.extra_params.get("time"):
            self.extra_params["time"] = datetime.now().timestamp() * 1000

    def to_sql(self):
        """Save trade result to a SQLite database.

        Creates a ResultDB record and persists it to the configured SQLite
        database. The record includes order details, parameters, and metadata.

        Note:
            Requires 'symbol' key to be present in parameters dict.
            Logs an error if the save operation fails.
        """
        try:
            data = self.get_data() | {"name": self.name}
            data = ResultDB.filter_dict(data)
            db = ResultDB(**data)
            db.save(commit=True)
        except Exception as err:
            logger.error("%s: Error occurred while saving", err)

    def get_data(self) -> dict:
        """Prepare trade data for storage.

        Combines the order result, strategy parameters, request details,
        and extra parameters into a single dictionary suitable for storage.

        Returns:
            dict: Combined dictionary containing:
                - Strategy parameters from self.parameters
                - Order result fields (deal, order, volume, price, bid, ask)
                - Request fields (symbol, type, sl, tp)
                - Default tracking fields (profit=0, closed=False, win=False)
                - Extra parameters (time, expected_profit, etc.)

        Note:
            Fields 'retcode', 'comment', 'retcode_external', 'request_id',
            and 'request' are excluded from the order result.
        """
        res = self.result.get_dict(exclude={"retcode", "comment", "retcode_external", "request_id", "request"})
        req = self.result.request.get_dict(include={"symbol", "type", "sl", "tp"})
        return res | {"profit": 0, "closed": False, "win": False, "parameters": self.parameters} | req |self.extra_params

    async def save(self, *, trade_record_mode: Literal["csv", "json", "sql"] = None):
        """Save trade results asynchronously to the configured storage format.

        Thread-safe method that records trade results to CSV, JSON, or SQL
        format based on configuration or explicit parameter.

        Args:
            trade_record_mode (Literal['csv', 'json', 'sql']): Storage format
                to use. If None, uses the mode from Config.trade_record_mode.

        Note:
            Uses a threading Lock to ensure thread-safe file operations.
            Logs an error for invalid trade record modes.
        """
        with self.lock:
            trade_record_mode = trade_record_mode or self.config.trade_record_mode
            if trade_record_mode == "csv":
                self.to_csv()
            elif trade_record_mode == "json":
                self.to_json()
            elif trade_record_mode == "sql":
                self.to_sql()
            else:
                logger.error(f"Invalid trade record mode: {trade_record_mode}")

    def save_sync(self, *, trade_record_mode: Literal["csv", "json", "sql"] = None):
        """Save trade results synchronously to the configured storage format.

        Thread-safe synchronous method that records trade results to CSV, JSON,
        or SQL format based on configuration or explicit parameter.

        Args:
            trade_record_mode (Literal['csv', 'json', 'sql']): Storage format
                to use. If None, uses the mode from Config.trade_record_mode.

        Note:
            Uses a threading Lock to ensure thread-safe file operations.
            Logs an error for invalid trade record modes.
        """
        with self.lock:
            trade_record_mode = trade_record_mode or self.config.trade_record_mode
            if trade_record_mode == "csv":
                self.to_csv()
            elif trade_record_mode == "json":
                self.to_json()
            elif trade_record_mode == "sql":
                self.to_sql()
            else:
                logger.error(f"Invalid trade record mode: {trade_record_mode}")

    def to_csv(self):
        """Save trade results and parameters to a CSV file.

        Appends the trade record to a CSV file in the configured records
        directory. Creates the file if it doesn't exist. Handles dynamic
        column headers by reading existing headers and merging with new data.

        The file is named '{self.name}.csv' and stored in config.records_dir.

        Note:
            Logs an error if the save operation fails.
        """
        try:
            data = self.get_data()
            data["time"] = data["time"] / 1000
            parameters = data.pop("parameters", {})
            data |= parameters
            file = self.config.records_dir / f"{self.name}.csv"
            file.touch(exist_ok=True) if not file.exists() else ...
            read_file = file.open("r", newline="")
            reader: Iterable[dict] = csv.DictReader(read_file)
            rows: list[dict] = []
            headers = set()
            [(rows.append(row), headers.update(row.keys())) for row in reader]
            rows.append(data)
            headers.update(data.keys())
            read_file.close()
            with file.open("w", newline="") as write_file:
                writer = csv.DictWriter(write_file, fieldnames=headers, restval=None, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(rows)
        except Exception as err:
            logger.error(f"Unable to save to csv: {err}")

    @staticmethod
    def serialize(value) -> str:
        """Serialize a value to string for JSON storage.

        Converts non-serializable values to their string representation
        for JSON compatibility.

        Args:
            value: Any value to serialize.

        Returns:
            str: String representation of the value, or empty string on error.
        """
        try:
            return str(value)
        except Exception as err:
            logger.error("%s: Unable to serialize value", err)
            return ""

    def to_json(self):
        """Save trade results and parameters to a JSON file.

        Appends the trade record to a JSON array file in the configured
        records directory. Creates the file with an empty array if it
        doesn't exist.

        The file is named '{self.name}.json' and stored in config.records_dir.
        Uses the serialize method as a default handler for non-JSON-serializable
        values.

        Note:
            Logs an error if the save operation fails.
        """
        try:
            file = self.config.records_dir / f"{self.name}.json"
            data = self.get_data()
            if not file.exists():
                file.touch()
                with file.open("w") as fh:
                    json.dump([], fh, indent=2)

            try:
                with file.open("r") as fh:
                    rows = json.load(fh)
                    rows.append(data)
            except json.decoder.JSONDecodeError as _:
                rows = [data]

            with file.open("w") as fh:
                json.dump(rows, fh, indent=2, skipkeys=True, default=self.serialize)
        except Exception as err:
            logger.error(f"Unable to save as json file: {err}")
