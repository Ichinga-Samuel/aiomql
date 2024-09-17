from dataclasses import dataclass, asdict, field, fields
from typing import ClassVar

from ...core.constants import AccountTradeMode, AccountMarginMode, AccountStopOutMode


@dataclass
class AccountInfo:
    login: int = 0
    server: str = ''
    trade_mode: AccountTradeMode = AccountTradeMode.DEMO
    balance: float = 0
    leverage: float = 0
    profit: float = 0
    equity: float = 0
    credit: float = 0
    margin: float = 0
    margin_level: float = 0
    margin_free: float = 0
    margin_mode: AccountMarginMode = AccountMarginMode.EXCHANGE
    margin_so_mode: AccountStopOutMode = AccountStopOutMode.PERCENT
    margin_so_call: float = 0
    margin_so_so: float = 0
    margin_initial: float = 0
    margin_maintenance: float = 0
    fifo_close: bool = False
    limit_orders: float = 0
    currency: str = "USD"
    trade_allowed: bool = True
    trade_expert: bool = True
    currency_digits: int = 2
    assets: float = 0
    liabilities: float = 0
    commission_blocked: float = 0
    name: str = ''
    company: str = ''

    _fields: list[ClassVar[str]] = field(default_factory=list)

    def asdict(self):
        res = asdict(self)
        res.pop('_fields', None)
        return res

    def set_attrs(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items() if k in self.fields]

    @property
    def fields(self):
        return self._fields or [name for f in fields(self) if (name := f.name) != '_fields']
