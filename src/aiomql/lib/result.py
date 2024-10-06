import csv
import json
from logging import getLogger
from typing import Iterable, Literal
from asyncio import Lock

from ..core.config import Config
from ..core.models import OrderSendResult

logger = getLogger(__name__)


class Result:
    """A base class for handling trade results and strategy parameters for record keeping and reference purpose.
    The data property must be implemented in the subclass

    Attributes:
        config (Config): The configuration object
        name: Any desired name for the result file object
    """
    config: Config

    def __init__(self, *, result: OrderSendResult, parameters: dict = None, name: str = ''):
        """
        Prepare result data
        Args:
            result:
            parameters:
            name:
        """
        self.config = Config()
        self.parameters = parameters or {}
        self.result = result
        self.name = name or self.parameters.get('name', 'Trades')
        self.lock = Lock()

    def get_data(self) -> dict:
        res = self.result.get_dict(exclude={'retcode', 'comment', 'retcode_external', 'request_id', 'request'})
        return self.parameters | res | {'actual_profit': 0, 'closed': False, 'win': False}

    async def save(self, *, trade_record_mode: Literal['csv', 'json'] = None):
        """Record trade results as a csv or json file
        Args:
            trade_record_mode (Literal['csv'|'json']): Mode of saving trade records
        """
        trade_record_mode = trade_record_mode or self.config.trade_record_mode
        if trade_record_mode == 'csv':
            await self.to_csv()
        elif trade_record_mode == 'json':
            await self.to_json()
        else:
            logger.error(f"Invalid trade record mode: {trade_record_mode}")

    async def to_csv(self):
        """Record trade results and associated parameters as a csv file
        """
        await self.lock.acquire()
        try:
            data = self.get_data()
            file = self.config.records_dir / f"{self.name}.csv"
            file.touch(exist_ok=True) if not file.exists() else ...
            read_file = file.open('r', newline='')
            reader: Iterable[dict] = csv.DictReader(read_file)
            rows: list[dict] = []
            headers = set()
            [(rows.append(row), headers.update(row.keys())) for row in reader]
            rows.append(data)
            headers.update(data.keys())
            read_file.close()
            with file.open('w', newline='') as write_file:
                writer = csv.DictWriter(write_file, fieldnames=headers, restval=None, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(rows)
        except Exception as err:
            logger.error(f'Unable to save to csv: {err}')

        finally:
            self.lock.release()

    @staticmethod
    def serialize(value) -> str:
        """Serialize the trade records and strategy parameters
        """
        try:
            return str(value)
        except (ValueError, TypeError) as _:
            return ""

    async def to_json(self):
        """Save trades and strategy parameters in a json file
        """
        await self.lock.acquire()
        try:
            file = self.config.records_dir / f"{self.name}.json"
            data = self.get_data()
            if not file.exists():
                file.touch()
                with file.open('w') as fh:
                    json.dump([], fh, indent=2)

            with file.open('r') as fh:
                rows = json.load(fh)
                rows.append(data)

            with file.open('w') as fh:
                json.dump(rows, fh, indent=2, skipkeys=True, default=self.serialize)

        except Exception as err:
            logger.error(f"Unable to save as json file: {err}")

        finally:
            self.lock.release()
