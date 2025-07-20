import pickle
from dataclasses import dataclass, field
from typing import ClassVar

from ..core.db import DB


@dataclass(kw_only=True)
class ResultDB(DB):
    _table: ClassVar[str] = "result"
    deal: int = field(metadata={"NOT NULL": True})
    order: int = field(metadata={"PRIMARY KEY": True, "UNIQUE": True, "NOT NULL": True})
    name: str = field(metadata={"NOT NULL": True})
    symbol: str = field(metadata={"NOT NULL": True})
    date: str = field(metadata={"NOT NULL": True})
    volume: float
    price: float
    bid: float
    ask: float
    tp: float = 0
    sl: float = 0
    actual_profit: float = 0
    expected_profit: float = 0
    win: bool = False
    closed: bool = False
    profit: float = 0
    loss: float = 0
    comment: str = field(default="''")
    parameters: dict|bytes|str = field(default="''")

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.parameters, bytes):
            self.parameters = pickle.loads(self.parameters)

    def get_data(self):
        data = self.asdict()
        if not isinstance(params:=data["parameters"], bytes):
            data["parameters"] = pickle.dumps(params, protocol=pickle.HIGHEST_PROTOCOL)
        return data
