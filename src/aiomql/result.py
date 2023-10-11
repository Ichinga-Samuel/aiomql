import asyncio
import csv
from logging import getLogger

from .core import Config
from .core.models import OrderSendResult

logger = getLogger(__name__)


class Result:
    """A base class for handling trade results and strategy parameters for record keeping and reference purpose.
    The data property must be implemented in the subclass

    Attributes:
        config (Config): The configuration object
        name: Any desired name for the result file object
    """
    config = Config()
    data: dict

    def __init__(self, result: OrderSendResult, parameters: dict = None, name: str = ''):
        """
        Prepare result data
        Args:
            result:
            parameters:
            name:
        """
        self.parameters = parameters or {}
        self.result = result
        self.name = name or parameters.get('name', 'Strategy')

    def get_data(self) -> dict:
        result = self.result.get_dict(exclude={'retcode', 'retcode_external', 'request_id', 'request'})
        return self.parameters | result | {'actual_profit': 0, 'closed': False, 'win': False}

    def to_csv(self):
        """Record trade results and associated parameters as a csv file
        """
        try:
            self.data = self.get_data()
            file = self.config.records_dir / f"{self.name}.csv"
            exists = file.exists()
            with open(file, 'a', newline='') as fh:
                writer = csv.DictWriter(fh, fieldnames=sorted(list(self.data.keys())), extrasaction='ignore', restval=None)
                if not exists:
                    writer.writeheader()
                writer.writerow(self.data)
        except Exception as err:
            logger.error(f'Error: {err}. Unable to save trade results')

    async def save_csv(self):
        """Save trade results and associated parameters as a csv file in a separate thread
        """
        # exe = self.config.executor
        loop = asyncio.get_running_loop()
        loop.run_in_executor(None, self.to_csv)
