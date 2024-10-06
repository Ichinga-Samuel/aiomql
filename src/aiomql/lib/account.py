from logging import getLogger
from typing import Self

from ..core.base import _Base
from ..core.models import AccountInfo
from ..core.exceptions import LoginError

logger = getLogger(__name__)


class Account(_Base, AccountInfo):
    """A class for managing a trading account. A singleton class.
    A subclass of AccountInfo. All AccountInfo attributes are available in this class.

    Attributes:
        connected (bool): Status of connection to MetaTrader 5 Terminal

    Notes:
        Other Account properties are defined in the AccountInfo class.
    """
    _instance: Self
    connected: bool
    
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
            cls._instance.connected = False
        return cls._instance

    async def __aenter__(self) -> Self:
        """Connect to a trading account and return the account instance.
        Async context manager for the Account class.

        Returns:
            Account: An instance of the Account class

        Raises:
            LoginError: If login fails
        """
        await self.mt5.initialize()
        self.connected = await self.mt5.login()
        if not self:
            raise LoginError('Login failed')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.mt5.shutdown()
        self.connected = False

    async def refresh(self):
        """Refreshes the account instance with the latest account details from the MetaTrader 5 terminal"""
        account_info = await self.mt5.account_info()
        acc = account_info._asdict()
        self.connected = True
        self.set_attributes(**acc)
