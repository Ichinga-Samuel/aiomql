import csv
from logging import getLogger
from threading import RLock
from pathlib import Path

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
    config: Config

    def __init__(self, result: OrderSendResult, parameters: dict = None, name: str = ''):
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
        self.name = name or parameters.get('name', 'Trades')
        if not Path(self.config.records_dir).exists():
            Path(self.config.records_dir).mkdir(parents=True, exist_ok=True)

    def get_data(self) -> dict:
        res = self.result.get_dict(exclude={'retcode', 'comment', 'retcode_external', 'request_id', 'request'})
        return self.parameters | res | {'actual_profit': 0, 'closed': False, 'win': False}

    async def to_csv(self):
        """Record trade results and associated parameters as a csv file
        """
        try:
            data = self.get_data()
            file = self.config.records_dir / f"{self.name}.csv"
            exists = file.exists()
            with RLock():
                with open(file, 'a', newline='') as fh:
                    f_names = sorted(list(data.keys()))
                    writer = csv.DictWriter(fh, fieldnames=f_names, extrasaction='ignore', restval=None)
                    if not exists:
                        writer.writeheader()
                    writer.writerow(data)
        except Exception as err:
            logger.error(f'Error: {err}. Unable to save trade results')
