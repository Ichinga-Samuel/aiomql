from dataclasses import dataclass
from typing import ClassVar

from ..constants import AccountTradeMode, AccountMarginMode, AccountStopOutMode


@dataclass
class BackTestAccount:
    login: int = 0
    trade_mode: AccountTradeMode = AccountTradeMode.DEMO
    leverage: float = 1
    limit_orders: float = 0
    margin_so_mode: AccountStopOutMode = AccountStopOutMode.PERCENT
    trade_allowed: bool = True
    trade_expert: bool = True
    margin_mode: AccountMarginMode = AccountMarginMode.EXCHANGE
    currency_digits: int = 2
    fifo_close: bool = False
    balance: float = 0
    credit: float = 0
    profit: float = 0
    equity: float = 0
    margin: float = 0
    margin_free: float = 0
    margin_level: float = 0
    margin_so_call: float = 0
    margin_so_so: float = 0
    margin_initial: float = 0
    margin_maintenance: float = 0
    assets: float = 0
    liabilities: float = 0
    commission_blocked: float = 0
    name: str = ""
    server: str = ""
    currency: str = "USD"
    company: str = ""

    __match_args__: ClassVar[tuple]

    def get_dict(self, exclude: set = None, include: set = None):
        exclude, include = exclude or set(), include or set()
        filter_ = include or set(self.__match_args__).difference(exclude)
        return {key: value for key, value in self.asdict().items() if key in filter_}

    def asdict(self):
        res = {key: getattr(self, key) for key in self.__match_args__}
        return res

    def set_attrs(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items() if k in self.__match_args__]
