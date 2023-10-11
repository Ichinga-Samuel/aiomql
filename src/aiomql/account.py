from logging import getLogger
from typing import Type

from .core.models import AccountInfo, SymbolInfo
from .core.exceptions import LoginError

logger = getLogger(__name__)


class Account(AccountInfo):
    """A class for managing a trading account. A singleton class.
    A subclass of AccountInfo. All AccountInfo attributes are available in this class.

    Attributes:
        connected (bool): Status of connection to MetaTrader 5 Terminal
        symbols (set[SymbolInfo]): A set of available symbols for the financial market.

    Notes:
        Other Account properties are defined in the AccountInfo class.
    """
    connected: bool
    symbols = set()
    
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    async def refresh(self):
        """
        Refreshes the account instance with the latest account details from the MetaTrader 5 terminal
        """
        account_info = await self.mt5.account_info()
        acc = account_info._asdict()
        self.set_attributes(**acc)

    @property
    def account_info(self) -> dict:
        """Get account login, server and password details. If the login attribute of the account instance returns
         a falsy value, the config instance is used to get the account details.

        Returns:
            dict: A dict of login, server and password details

        Note:
            This method will only look for config details in the config instance if the login attribute of the
            account Instance returns a falsy value
        """
        acc_info = self.get_dict(include={'login', 'server', 'password'})
        return acc_info if acc_info['login'] else self.config.account_info()

    async def __aenter__(self) -> 'Account':
        """Connect to a trading account and return the account instance.
        Async context manager for the Account class.

        Returns:
            Account: An instance of the Account class

        Raises:
            LoginError: If login fails
        """
        res = await self.sign_in()
        if not res:
            raise LoginError('Login failed')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.mt5.shutdown()
        self.connected = False

    async def sign_in(self) -> bool:
        """Connect to a trading account.

        Returns:
            bool: True if login was successful else False
        """
        await self.mt5.initialize(**self.account_info)
        self.connected = await self.mt5.login(**self.account_info)
        if self.connected:
            await self.refresh()
            self.symbols = await self.symbols_get()
            return self.connected
        await self.mt5.shutdown()
        return False

    def has_symbol(self, symbol: str | Type[SymbolInfo]):
        """Checks to see if a symbol is available for a trading account

        Args:
            symbol (str | SymbolInfo):

        Returns:
            bool: True if symbol is present otherwise False
        """
        try:
            symbol = SymbolInfo(name=str(symbol)) if not isinstance(symbol, SymbolInfo) else symbol
            return symbol in self.symbols
        except Exception as err:
            logger.warning(f'Error: {err}; {symbol} not available in this market')
            return False

    async def symbols_get(self) -> set[SymbolInfo]:
        """Get all financial instruments from the MetaTrader 5 terminal available for the current account.

        Returns:
            set[Symbol]: A set of available symbols.
        """
        syms = await self.mt5.symbols_get()
        return {SymbolInfo(name=sym.name) for sym in syms}
