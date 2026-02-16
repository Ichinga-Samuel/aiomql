"""Exceptions for the aiomql package."""

__all__ = ["LoginError", "VolumeError", "SymbolError", "OrderError", "StopTrading", "InvalidRequest"]

class LoginError(Exception):
    """Raised when an error occurs when logging in."""

    ...


class VolumeError(Exception):
    """Raised when a volume is not valid or out of range for a symbol."""

    ...


class SymbolError(Exception):
    """Raised when a symbol is not provided where required or not available in the Market Watch."""

    ...


class OrderError(Exception):
    """Raised when an error occurs when working with the order class."""

    ...


class StopTrading(Exception):
    """Raised when the user wants to stop trading."""

    ...

class InvalidRequest(Exception):
    """Raised when an error occurs when trying to query the market."""
    ...