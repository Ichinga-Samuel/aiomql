"""Result database module for SQL-based trade result storage.

This module provides the ResultDB dataclass for storing trade results
in a SQLite database. It extends the DB base class to provide ORM-style
operations for trade records.

Example:
    Saving a trade result to database::

        result_db = ResultDB(
            deal=12345,
            order=67890,
            name='MyStrategy',
            symbol='EURUSD',
            time=1705312800.0,
            volume=0.1,
            price=1.0850,
            type=0
        )
        result_db.save(commit=True)

    Querying trade results::

        # Get all results for a specific strategy
        results = ResultDB.filter(name='MyStrategy')

        # Get a specific trade by order number
        trade = ResultDB.get(order=67890)

        # Get all closed trades
        closed_trades = ResultDB.filter(closed=True)
"""

import pickle
from dataclasses import dataclass, field
from typing import ClassVar

from ..core.db import DB


@dataclass(kw_only=True)
class ResultDB(DB):
    """Dataclass for storing trade results in a SQLite database.

    Extends the DB base class to provide ORM-style persistence for trade
    execution results. Each record represents a single executed trade with
    its associated parameters and outcome tracking fields.

    Attributes:
        deal: The deal ticket number from the broker. Required.
        order: The order ticket number. Primary key, must be unique.
        name: Name of the strategy or result set. Required.
        symbol: Trading symbol (e.g., 'EURUSD'). Required.
        time: Timestamp of the trade in seconds. Required.
        volume: Trade volume in lots. Required.
        price: Execution/opening price. Required.
        type: Order type (e.g., ORDER_TYPE_BUY=0, ORDER_TYPE_SELL=1). Required.
        bid: Bid price at execution. Defaults to 0.
        ask: Ask price at execution. Defaults to 0.
        tp: Take profit price. Defaults to 0.
        sl: Stop loss price. Defaults to 0.
        price_close: Closing price of the trade. Defaults to 0.
        time_close: Timestamp of the trade closing in seconds. Defaults to 0.
        expected_profit: Expected profit at trade entry. Defaults to 0.
        win: Whether the trade was profitable. Defaults to False.
        closed: Whether the trade has been closed. Defaults to False.
        profit: Final profit/loss amount. Defaults to 0.
        comment: Optional trade comment. Defaults to empty string.
        parameters: Strategy parameters, stored as pickled bytes in the
            database. Can be dict, bytes, or str. Defaults to empty string.

    Class Attributes:
        _table: The database table name ('result').

    Example:
        >>> result = ResultDB(
        ...     deal=123, order=456, name='Test', symbol='EURUSD',
        ...     time=1705312800.0, volume=0.1, price=1.085, type=0
        ... )
        >>> result.save()
    """
    _table: ClassVar[str] = "result"
    deal: int = field(metadata={"NOT NULL": True})
    order: int = field(metadata={"PRIMARY KEY": True, "UNIQUE": True, "NOT NULL": True})
    name: str = field(metadata={"NOT NULL": True})
    symbol: str = field(metadata={"NOT NULL": True})
    time: float = field(metadata={"NOT NULL": True})
    volume: float
    price: float
    type: int
    bid: float = 0
    ask: float = 0
    tp: float = 0
    sl: float = 0
    price_close: float = 0
    time_close: float = 0
    expected_profit: float = 0
    win: bool = False
    closed: bool = False
    profit: float = 0
    comment: str = ""
    parameters: dict|bytes|str = ""

    def __post_init__(self):
        """Initialize the ResultDB instance after dataclass initialization.

        Calls the parent DB.__post_init__ and deserializes the parameters
        field if it was stored as pickled bytes.
        """
        if isinstance(self.parameters, bytes):
            params = pickle.loads(self.parameters)
            self.parameters = params if isinstance(params, dict) else {}
        else:
            self.parameters = self.parameters or {}
        self.comment = str() if self.comment is None else self.comment
        self.win = bool(self.win)
        self.closed = bool(self.closed)

    def get_data(self) -> dict:
        """Prepare the record data for database storage.

        Converts the dataclass to a dictionary and serializes the parameters
        field to pickled bytes for database storage.

        Returns:
            dict: Dictionary representation of the record with parameters
                serialized as bytes for SQLite blob storage.
        """
        data = self.asdict()
        if not isinstance(params:=data["parameters"], bytes):
            data["parameters"] = pickle.dumps(params, protocol=pickle.HIGHEST_PROTOCOL)
        return data

    @classmethod
    def dump_to_csv(cls, file_path: str = None, name: str = ""):
        """Dump all records from the database table to a CSV file.

        Args:
            file_path (str): The path to the CSV file to write.
        """
        import csv
        query = {"name": name} if name else {}
        records = cls.filter(**query)
        if not records:
            return

        data_to_write = [record.asdict() for record in records]
        # The 'parameters' field is a dict, which is not suitable for a single CSV cell.
        # We'll flatten it, adding 'param_' prefix to each key from the parameters.
        # This also handles records that might have different parameters.
        
        processed_data = []
        all_keys = set()

        for item in data_to_write:
            params = item.pop('parameters', {})
            if isinstance(params, dict):
                for p_key, p_value in params.items():
                    item[f'param_{p_key}'] = p_value
            processed_data.append(item)
            all_keys.update(item.keys())
            
        # Ensure all dictionaries have the same set of keys
        final_data = []
        sorted_keys = sorted(list(all_keys))
        for item in processed_data:
            row = {key: item.get(key) for key in sorted_keys}
            final_data.append(row)
        file_path = file_path or (f"{name}.csv" if name else "") or cls.config.db_dir_name / 'result_db.csv'
        with open(file_path, 'w', newline='') as output_file:
            writer = csv.DictWriter(output_file, fieldnames=sorted_keys)
            writer.writeheader()
            writer.writerows(final_data)



