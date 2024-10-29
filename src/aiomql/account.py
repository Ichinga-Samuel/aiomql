import asyncio
from logging import getLogger

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
    _instance: 'Account'
    connected: bool
    symbols = set()
    
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        acc = self.config.account_info()
        acc_details = {k: v for k, v in self.get_dict(include={'login', 'server', 'password'}).items() if v}
        acc |= acc_details
        self.config.set_attributes(**acc)
        self.set_attributes(**acc)

    async def refresh(self):
        """Refreshes the account instance with the latest account details from the MetaTrader 5 terminal"""
        account_info = await self.mt5.account_info()
        acc = account_info._asdict()
        self.set_attributes(**acc)

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
        acc = self.get_dict(include={'login', 'server', 'password'})
        self.connected = await self._login(acc=acc)
        if self.connected:
            await self.refresh()
            self.symbols = await self.symbols_get()
            return self.connected
        await self.mt5.shutdown()
        return False

    async def _login(self, *, acc: dict, tries=3):
        res = False
        if tries == 0:
            return False
        ini = await self.mt5.initialize(**acc, path=self.config.path)
        if ini:
            res = await self.mt5.login(**acc)
        if ini and res:
            return True
        else:
            await asyncio.sleep(5+tries)
            return await self._login(acc=acc, tries=tries-1)

    def has_symbol(self, symbol: str | SymbolInfo):
        """Checks to see if a symbol is available for a trading account.

        Args:
            symbol (str | SymbolInfo):

        Returns:
            bool: True if symbol is present otherwise False
        """
        try:
            return str(symbol) in {s.name for s in self.symbols}
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
