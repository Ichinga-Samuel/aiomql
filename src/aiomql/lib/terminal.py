"""Terminal related functions and properties"""
from typing import NamedTuple
from logging import getLogger

from ..core.models import TerminalInfo
from ..core.base import _Base

logger = getLogger(__name__)

Version = NamedTuple(
    "Version", (("version", str), ("build", int), ("release_date", str))
)


class Terminal(_Base, TerminalInfo):
    """Terminal Class. Get information about the MetaTrader 5 terminal. The class is a subclass of the TerminalInfo
    class. It inherits all the attributes and methods of the TerminalInfo class and adds some useful methods.
    """

    version: Version | None = None

    async def initialize(self) -> bool:
        """Establish a connection with the MetaTrader 5 terminal. There are three call options. Call without parameters.
        The terminal for connection is found automatically. Call specifying the path to the MetaTrader 5 terminal we
        want to connect to. word path as a keyword argument Call specifying the trading account path and parameters
        i.e. login, password, server, as keyword arguments, path can be omitted.

        Returns:
            bool: True if successful else False
        """
        self.connected = await self.mt5.initialize()
        if not self.connected:
            err = await self.mt5.last_error()
            logger.warning(f"Failed to initialize Terminal. Error Code: {err}")
        info = await self.info()
        await self.get_version()
        return bool(self.connected and info and self.version)

    async def get_version(self) -> Version | None:
        """Get the MetaTrader 5 terminal version. This method returns the terminal version, build and release date as
        a tuple of three values

        Returns:
            Version: version of tuple as Version object
        """
        res = await self.mt5.version()
        if res is None:
            logger.error("Failed to get terminal version")
            return None
        self.version = Version(*res)
        return self.version

    async def info(self) -> TerminalInfo | None:
        """Get the connected MetaTrader 5 client terminal status and settings. gets terminal info in the form of a
        named tuple structure (namedtuple). Return None in case of an error. The info on the error can be
        obtained using last_error().

        Returns:
             Terminal: Terminal status and settings as a terminal object.
        """
        info = await self.mt5.terminal_info()
        if info:
            self.set_attributes(**info._asdict())
        return info

    async def symbols_total(self) -> int:
        """Get the number of all financial instruments in the MetaTrader 5 terminal.

        Returns:
            int: Total number of available symbols
        """
        return await self.mt5.symbols_total()
