"""Terminal related functions and properties"""

from typing import NamedTuple
from logging import getLogger
from .core.models import TerminalInfo

logger = getLogger()


class Terminal(TerminalInfo):
    """Terminal Class. Get information about the MetaTrader 5 terminal. The class is a subclass of the TerminalInfo
    class. It inherits all the attributes and methods of the TerminalInfo class and adds some useful methods.

    Notes:
        Other attributes are defined in the TerminalInfo Class
    """

    Version = NamedTuple("Version", (('version', str), ('build', int), ('release_date', str)))

    async def initialize(self) -> bool:
        """Establish a connection with the MetaTrader 5 terminal. There are three call options. Call without parameters.
        The terminal for connection is found automatically. Call specifying the path to the MetaTrader 5 terminal we
        want to connect to. word path as a keyword argument Call specifying the trading account path and parameters
        i.e login, password, server, as keyword arguments, path can be omitted.

        Returns:
            bool: True if successful else False
        """
        self.connected = await self.mt5.initialize(**self.config.account_info())

        if not self.connected:
            err = await self.mt5.last_error()
            logger.critical(f'Failed to initialize Terminal. Error Code: {err}')
            raise SystemExit
        return self.connected

    async def version(self):
        """Get the MetaTrader 5 terminal version. This method returns the terminal version, build and release date as
        a tuple of three values

        Returns:
            Version: version of tuple as Version object

        Raises:
            ValueError: If the terminal version cannot be obtained
        """
        res = await self.mt5.version()
        if res is None:
            raise ValueError('Failed to get terminal version')
        return self.Version(*res)

    async def info(self):
        """Get the connected MetaTrader 5 client terminal status and settings. gets terminal info in the form of a
        named tuple structure (namedtuple). Return None in case of an error. The info on the error can be
        obtained using last_error().

        Returns:
             Terminal: Terminal status and settings as a terminal object.
        """
        info = await self.mt5.terminal_info()
        self.set_attributes(**info._asdict())
        return self

    async def symbols_total(self) -> int:
        """Get the number of all financial instruments in the MetaTrader 5 terminal.

        Returns:
            int: Total number of available symbols
        """
        return await self.mt5.symbols_total()
