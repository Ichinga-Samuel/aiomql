"""Account module for trading account management.

This module provides the Account class, a singleton for managing the
trading account connection to MetaTrader 5. It supports both async
and sync context managers for connection handling.

Example:
    Using the account asynchronously::

        async with Account() as account:
            print(f"Balance: {account.balance}")
            print(f"Equity: {account.equity}")

    Using the account synchronously::

        with Account() as account:
            print(f"Balance: {account.balance}")
"""

from threading import Lock
from logging import getLogger
from typing import Self, ClassVar

from ..core.base import _Base
from ..core.models import AccountInfo
from ..core.exceptions import LoginError

logger = getLogger(__name__)


class Account(_Base, AccountInfo):
    """A singleton class for managing a trading account. A subclass of _Base and AccountInfo.

    Supports both asynchronous and synchronous context management protocols.

    Attributes:
        connected (bool): Status of connection to MetaTrader 5 Terminal.
        _instance (Self): The singleton instance.
        _lock (Lock): Thread lock for thread-safe singleton creation.

    Example:
        Async context manager::

            async with Account() as account:
                print(account.balance)

        Sync context manager::

            with Account() as account:
                print(account.balance)
    """

    _instance: Self
    _lock: ClassVar[Lock]
    connected: bool

    def __new__(cls, *args, **kwargs):
        with (lock := Lock()) as _:
            if not hasattr(cls, "_instance"):
                cls._lock = lock
                cls._instance = super().__new__(cls)
                cls._instance.connected = False
                cls._instance.exclude.add("_lock")
        return cls._instance

    async def __aenter__(self) -> Self:
        """Connects to a trading account asynchronously.

        Returns:
            Account: The connected account instance.

        Raises:
            LoginError: If login fails.
        """
        await self.mt5.initialize()
        self.connected = await self.mt5.login()
        if not self.connected:
            raise LoginError(f"Login failed: {self.mt5.error}")
        await self.refresh()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Disconnects from the trading account asynchronously."""
        await self.mt5.shutdown()
        self.connected = False

    def __enter__(self) -> Self:
        """Connects to a trading account synchronously.

        Returns:
            Account: The connected account instance.

        Raises:
            LoginError: If login fails.
        """
        self.mt5.initialize_sync()
        self.connected = self.mt5.login_sync()
        if not self.connected:
            raise LoginError(f"Login failed: {self.mt5.error}")
        self.refresh_sync()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Disconnects from the trading account synchronously."""
        self.mt5._shutdown()
        self.connected = False

    async def refresh(self):
        """Refreshes the account with the latest details from the terminal asynchronously."""
        account_info = await self.mt5.account_info()
        acc = account_info._asdict()
        self.connected = True
        self.set_attributes(**acc)

    def refresh_sync(self):
        """Refreshes the account with the latest details from the terminal synchronously."""
        account_info = self.mt5._account_info()
        acc = account_info._asdict()
        self.connected = True
        self.set_attributes(**acc)

