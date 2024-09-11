"""This module contains the Records class, which is used to read and update trade records from csv files."""

import asyncio
import json
from pathlib import Path
import csv
import logging
from typing import Iterable

from .core.config import Config
from .core.meta_trader import MetaTrader
from .contrib.backtester.meta_tester import MetaTester

logger = logging.getLogger(__name__)


class TradeRecords:
    """This utility class read trade records from csv files, and update them based on their closing positions.

    Attributes:
        config: Config object
        records_dir(Path): Absolute path to directory containing record of placed trades, If not given takes the default
        from the config
    """
    config: Config
    mt5: MetaTrader | MetaTester

    def __init__(self, *, records_dir: Path | str = ''):
        """Initialize the Records class. The main method of this class is update_records which you should call to update
        all the records specified in the records_dir.

        Keyword Args:
            records_dir (Path): Absolute path to directory containing record of placed trades.
        """
        self.config = Config()
        self.mt5 = MetaTrader() if self.config.mode == 'live' else MetaTester()
        self.records_dir = records_dir or self.config.records_dir

    async def get_csv_records(self):
        """Get trade records saved as csv from records_dir folder

        Yields:
            files: Trade record files
        """
        for file in self.records_dir.iterdir():
            if file.is_file() and file.name.endswith('.csv'):
                yield file

    async def get_json_records(self):
        """Get trade records from records_dir folder

        Yields:
            files: Trade record files
        """
        for file in self.records_dir.iterdir():
            if file.is_file() and file.name.endswith('.json'):
                yield file

    async def read_update_csv(self, *, file: Path):
        """Read and update csv trade records

        Args:
            file: Trade record file in csv format
        """
        try:
            fr = open(file, mode='r', newline='')
            reader: Iterable[dict] | csv.DictReader = csv.DictReader(fr)
            rows = [row for row in reader]
            rows = await self.update_rows(rows=rows)
            fr.close()
            fw = open(file, mode='w', newline='')
            writer = csv.DictWriter(fw, fieldnames=reader.fieldnames, extrasaction='ignore', restval=None)
            writer.writeheader()
            writer.writerows(rows)
            fw.close()
        except Exception as err:
            logger.error(f'Error: {err}. Unable to read and update csv trade records')

    async def read_update_json(self, *, file: Path):
        """Read and update json trade records
        Args:
            file: Trade record file in csv format
        """
        try:
            fh = open(file, mode='r')
            data = json.load(fh)
            rows = [row for row in data]
            rows = await self.update_rows(rows=rows)
            fh.close()
            fh = open(file, mode='w')
            json.dump(rows, fh, indent=2)
            fh.close()
        except Exception as err:
            logger.error(f'Error: {err}. Unable to read and update json trade records')

    async def update_row(self, *, row: dict) -> dict:
        """Update a single row of entered trade in the csv or json file with the actual profit.

        Args:
            row: A dictionary from the dictionary writer object of the csv file.

        Returns:
            dict: A dictionary with the actual profit and win status.
        """
        try:
            order = int(row['order'])
            deals = await self.mt5.history_deals_get(position=order)
            if not deals or len(deals) <= 1:
                return row
            deals = [deal for deal in deals if (deal.order != deal.position_id and deal.position_id == order
                                                and deal.entry == 1)]
            deals.sort(key=lambda x: x.time_msc)
            deal = deals[-1]
            row.update(actual_profit=deal.profit, win=deal.profit > 0, closed=True)
            return row
        except Exception as err:
            logging.error(f'Error: {err}. Unable to update trade record')
            return row

    async def update_rows(self, *, rows: list[dict]) -> list[dict]:
        """Update the rows of entered trades in the csv or json file with the actual profit.

        Args:
            rows: A list of dictionaries.

        Returns:
            list[dict]: A list of dictionaries with the actual profit and win status.
        """
        closed, unclosed = [], []
        for row in rows:
            closed_ = row.get('closed', False)
            closed_ = closed_.title() == 'True' if isinstance(closed_, str) else closed_
            if closed_:
                closed.append(row)
            else:
                unclosed.append(row)
        unclosed = await asyncio.gather(*[self.update_row(row=row) for row in unclosed])
        return closed + list(unclosed)

    async def update_csv_records(self):
        """Update csv trade records in the records_dir folder."""
        records = [self.read_update_csv(file=record) async for record in self.get_csv_records()]
        await asyncio.gather(*records)

    async def update_json_records(self):
        """Update json trade records in the records_dir folder."""
        records = [self.read_update_json(file=record) async for record in self.get_json_records()]
        await asyncio.gather(*records)

    async def update_csv_record(self, *, file: Path | str):
        """Update a single trade record csv file."""
        await self.read_update_csv(file=file)

    async def update_json_record(self, *, file: Path | str):
        """Update a single json trade record file"""
        await self.read_update_json(file=file)
