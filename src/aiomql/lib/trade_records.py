"""Trade records module for managing trade result files.

This module provides the TradeRecords class for reading, updating, and
managing trade record files in CSV, JSON, and SQL formats. It updates trade
records with actual profit/loss data from closed positions.

Example:
    Updating trade records asynchronously::

        records = TradeRecords()
        await records.update_csv_records()
        await records.update_json_records()
        await records.update_sql_records()

    Updating trade records synchronously::

        records = TradeRecords()
        records.update_csv_records_sync()
        records.update_json_records_sync()
"""
from datetime import datetime
import asyncio
import json
from pathlib import Path
import csv
import logging
from typing import Iterable

from .result_db import ResultDB
from ..core.config import Config
from ..core.meta_trader import MetaTrader
from ..core.models import TradePosition

logger = logging.getLogger(__name__)


class TradeRecords:
    """Utility class for reading and updating trade records from various storage formats.

    Reads trade records from CSV, JSON files, or SQL database and updates them
    with actual profit/loss data from closed positions retrieved via MetaTrader 5.

    Attributes:
        config: Configuration object for accessing settings.
        mt5: MetaTrader instance for retrieving trade data.
        result_db: ResultDB class reference for SQL operations.
        records_dir: Path to directory containing trade record files.
        positions: Cached list of open positions, or None.

    Example:
        >>> records = TradeRecords(records_dir='/path/to/records')
        >>> await records.update_csv_records()
        >>> await records.update_sql_records()
    """
    config: Config
    mt5: MetaTrader
    result_db: type[ResultDB]
    positions: list[TradePosition] | None = None

    def __init__(self, *, records_dir: Path | str = ""):
        """Initialize the Records class. The main method of this class is update_records which you should call to update
        all the records specified in the records_dir.

        Keyword Args:
            records_dir (Path): Absolute path to directory containing record of placed trades.
        """
        self.config = Config()
        self.mt5 = MetaTrader()
        self.records_dir = records_dir or self.config.records_dir
        self.result_db = ResultDB

    def get_sql_records_unclosed(self):
        """Retrieve all unclosed trade records from the SQL database.

        Returns:
            list[ResultDB]: List of ResultDB instances where closed=False.
        """
        rows = self.result_db.execute_raw("select * from result where closed = 0")
        return rows

    async def update_sql_records(self):
        """Update SQL trade records with actual profit/loss from closed positions.

        Fetches unclosed records from the database, retrieves closing deals
        from MetaTrader history, and updates records with profit, win status,
        closing time, and closing price.

        Note:
            Uses batch processing for efficiency - all updates are committed
            together at the end.
        """
        conn = self.result_db.get_connection()
        rows = self.get_sql_records_unclosed()
        rows.sort(key=lambda r: r.time)
        start = datetime.fromtimestamp(rows[0].time/1000).replace(hour=0, minute=0)
        end = datetime.now().replace(hour=23, minute=59)
        deals = await self.mt5.history_deals_get(date_from=start, date_to=end)
        closing_deals = {deal.position_id: deal for deal in deals if deal.order != deal.position_id and deal.entry == self.mt5.DEAL_ENTRY_OUT}
        for row in rows:
            if row.order in closing_deals and not row.closed:
                deal = closing_deals[row.order]
                data = dict(profit=deal.profit, win=deal.profit > 0, closed=True, time_close=deal.time_msc, price_close=deal.price)
                row.save(conn=conn, update=True, data=data, commit=False)
        conn.commit()
        conn.close()

    def get_csv_records(self):
        """Get trade records saved as csv from records_dir folder

        Yields:
            files: Trade record files
        """
        for file in self.records_dir.iterdir():
            if file.is_file() and file.name.endswith(".csv"):
                yield file

    def get_json_records(self):
        """Get trade records from records_dir folder

        Yields:
            files (Path): Trade record files
        """
        for file in self.records_dir.iterdir():
            if file.is_file() and file.name.endswith(".json"):
                yield file

    async def read_update_csv(self, *, file: Path):
        """Read and update csv trade records

        Args:
            file: Trade record file in csv format
        """
        try:
            with open(file, mode="r", newline="") as fr:
                reader: Iterable[dict] | csv.DictReader = csv.DictReader(fr)
                rows = [row for row in reader]
                rows = await self.update_rows(rows=rows)

            with open(file, mode="w", newline="") as fw:
                writer = csv.DictWriter(fw, fieldnames=reader.fieldnames, extrasaction="ignore", restval=None)
                writer.writeheader()
                writer.writerows(rows)
        except Exception as err:
            logger.error(f"Error: {err}. Unable to read and update csv trade records")

    async def read_update_json(self, *, file: Path):
        """Read and update json trade records
        Args:
            file: Trade record file in csv format
        """
        try:
            with open(file, mode="r") as fh:
                data = json.load(fh)
                rows = [row for row in data]
                rows = await self.update_rows(rows=rows)

            with open(file, mode="w") as fh:
                json.dump(rows, fh, indent=2)
        except Exception as err:
            logger.error(f"Error: {err}. Unable to read and update json trade records")

    async def update_rows(self, rows: list[dict]) -> list[dict]:
        """Update multiple trade rows with actual profit/loss from closed positions.

        Retrieves historical deals from MetaTrader for the time range covered
        by the rows and updates each unclosed row with closing information.

        Args:
            rows: List of trade record dictionaries to update. Each dict must
                contain 'time' (in seconds) and 'order' keys.

        Returns:
            list[dict]: Updated list of trade records with profit, win status,
                time_close, and price_close fields populated for closed trades.

        Note:
            Time values in rows should be in seconds. The method converts
            them to milliseconds for the MetaTrader API.
        """
        rows.sort(key=lambda _row: _row["time"])
        start = datetime.fromtimestamp(float(rows[0]["time"]) / 1000).replace(hour=0, minute=0)
        end = datetime.now().replace(hour=23, minute=59)
        deals = await self.mt5.history_deals_get(date_from=start, date_to=end)
        closing_deals = {deal.position_id: deal for deal in deals if deal.order != deal.position_id and deal.entry == self.mt5.DEAL_ENTRY_OUT}
        for row in rows:
            if (self.str_to_bool(row["closed"])) is False  and (deal := closing_deals.get(int(row["order"]), 0)) and deal.order != deal.position_id and deal.entry == self.mt5.DEAL_ENTRY_OUT:
                row.update(profit=deal.profit, win=deal.profit > 0, closed=True, time_close=deal.time_msc/1000, price_close=deal.price)
        return rows

    @staticmethod
    def str_to_bool(val: bool | str):
        """Converts a string or boolean value to a Python bool.

        Args:
            val: The value to convert. Accepts ``True``, ``False``,
                ``"true"``, or ``"false"`` (case-insensitive).

        Returns:
            bool: The corresponding boolean value.

        Raises:
            TypeError: If ``val`` is not a recognised boolean string.
        """
        if isinstance(val, bool):
            return val
        elif val.lower() == "true":
            return True
        elif val.lower() == "false":
            return False
        else:
            raise TypeError(f"{val} is not a valid boolean value")

    async def update_csv_records(self):
        """Update csv trade records in the records_dir folder."""
        records = [self.read_update_csv(file=record) for record in self.get_csv_records()]
        await asyncio.gather(*records)

    async def update_json_records(self):
        """Update json trade records in the records_dir folder."""
        records = [self.read_update_json(file=record) for record in self.get_json_records()]
        await asyncio.gather(*records)

    async def update_csv_record(self, *, file: Path | str):
        """Update a single trade record csv file."""
        await self.read_update_csv(file=file)

    async def update_json_record(self, *, file: Path | str):
        """Update a single json trade record file"""
        await self.read_update_json(file=file)

    def read_update_csv_sync(self, *, file: Path):
        """Read and update csv trade records synchronously.

        Args:
            file: Trade record file in csv format
        """
        try:
            with open(file, mode="r", newline="") as fr:
                reader: Iterable[dict] | csv.DictReader = csv.DictReader(fr)
                rows = [row for row in reader]
                rows = self.update_rows_sync(rows=rows)

            with open(file, mode="w", newline="") as fw:
                writer = csv.DictWriter(fw, fieldnames=reader.fieldnames, extrasaction="ignore", restval=None)
                writer.writeheader()
                writer.writerows(rows)
        except Exception as err:
            logger.error(f"Error: {err}. Unable to read and update csv trade records")

    def read_update_json_sync(self, *, file: Path):
        """Read and update json trade records synchronously.

        Args:
            file: Trade record file in json format
        """
        try:
            with open(file, mode="r") as fh:
                data = json.load(fh)
                rows = [row for row in data]
                rows = self.update_rows_sync(rows=rows)

            with open(file, mode="w") as fh:
                json.dump(rows, fh, indent=2)
        except Exception as err:
            logger.error(f"Error: {err}. Unable to read and update json trade records")

    def update_rows_sync(self, *, rows: list[dict]) -> list[dict]:
        """Update the rows of entered trades in the csv or json file with the actual profit synchronously.

        Args:
            rows: A list of dictionaries.

        Returns:
            list[dict]: A list of dictionaries with the actual profit and win status.
        """
        rows.sort(key=lambda _row: _row["time"])
        start = datetime.fromtimestamp(float(rows[0]["time"]) / 1000).replace(hour=0, minute=0)
        end = datetime.now().replace(hour=23, minute=59)
        deals = self.mt5._history_deals_get(date_from=start, date_to=end)
        closing_deals = {deal.position_id: deal for deal in deals if
                         deal.order != deal.position_id and deal.entry == self.mt5.DEAL_ENTRY_OUT}
        for row in rows:
            if (self.str_to_bool(row["closed"])) is False and (deal := closing_deals.get(int(row["order"]),
                                                                                         0)) and deal.order != deal.position_id and deal.entry == self.mt5.DEAL_ENTRY_OUT:
                row.update(profit=deal.profit, win=deal.profit > 0, closed=True, time_close=deal.time_msc / 1000,
                           price_close=deal.price)
        return rows

    def update_csv_records_sync(self):
        """Update csv trade records in the records_dir folder synchronously."""
        for record in self.get_csv_records():
            self.read_update_csv_sync(file=record)

    def update_json_records_sync(self):
        """Update json trade records in the records_dir folder synchronously."""
        for record in self.get_json_records():
            self.read_update_json_sync(file=record)

    def update_csv_record_sync(self, *, file: Path | str):
        """Update a single trade record csv file synchronously."""
        self.read_update_csv_sync(file=file)

    def update_json_record_sync(self, *, file: Path | str):
        """Update a single json trade record file synchronously."""
        self.read_update_json_sync(file=file)
