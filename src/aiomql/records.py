"""This module contains the Records class, which is used to read and update trade records from csv files."""

import asyncio
from pathlib import Path
import csv
import logging
from typing import Iterable

from .core import Config, MetaTrader

logger = logging.getLogger(__name__)


class Records:
    """This utility class read trade records from csv files, and update them based on their closing positions.

    Attributes:
        config: Config object
        records_dir(Path): Absolute path to directory containing record of placed trades, If not given takes the default
        from the config
    """
    config: Config
    mt5: MetaTrader

    def __init__(self, records_dir: Path | str = ''):
        """Initialize the Records class. The main method of this class is update_records which you should call to update
        all the records specified in the records_dir.

        Keyword Args:
            records_dir (Path): Absolute path to directory containing record of placed trades.
        """
        self.config = Config()
        self.mt5 = MetaTrader()
        self.records_dir = records_dir or self.config.records_dir

    async def get_records(self):
        """Get trade records from records_dir folder

        Yields:
            files: Trade record files
        """
        for file in self.records_dir.iterdir():
            if file.is_file() and file.name.endswith('.csv'):
                yield file

    async def read_update(self, file: Path):
        """Read and update trade records

        Args:
            file: Trade record file
        """
        try:
            fr = open(file, mode='r', newline='')
            reader: Iterable[dict] | csv.DictReader = csv.DictReader(fr)
            rows = [row for row in reader]
            rows = await self.update_rows(rows)
            fr.close()
            fw = open(file, mode='w', newline='')
            writer = csv.DictWriter(fw, fieldnames=reader.fieldnames, extrasaction='ignore', restval=None)
            writer.writeheader()
            writer.writerows(rows)
            fw.close()
        except Exception as err:
            logger.error(f'Error: {err}. Unable to read and update trade records')

    async def update_row(self, row: dict) -> dict:
        """Update a single row of entered trade in the csv file with the actual profit.

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

    async def update_rows(self, rows: list[dict]) -> list[dict]:
        """Update the rows of entered trades in the csv file with the actual profit.

        Args:
            rows: A list of dictionaries from the dictionary writer object of the csv file.

        Returns:
            list[dict]: A list of dictionaries with the actual profit and win status.
        """
        closed, unclosed = [], []
        for row in rows:
            if (row.get('closed', 'FALSE')).title() == 'True':
                closed.append(row)
            else:
                unclosed.append(row)
        unclosed = await asyncio.gather(*[self.update_row(row) for row in unclosed])
        return closed + list(unclosed)

    async def update_records(self):
        """Update trade records in the records_dir folder."""
        records = [self.read_update(record) async for record in self.get_records()]
        await asyncio.gather(*records)

    async def update_record(self, file: Path | str):
        """Update a single trade record file."""
        await self.read_update(file)
