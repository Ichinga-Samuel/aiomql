"""Exceptions for the aiomql package."""

__all__ = ['LoginError', 'VolumeError', 'SymbolError', 'OrderError']

class LoginError(Exception):
    """Raised when an error occurs when logging in."""
    pass

class VolumeError(Exception):
    """Raised when a volume is not valid or out of range for a symbol."""
    pass


class SymbolError(Exception):
    """Raised when a symbol is not provided where required or not available in the Market Watch."""


class OrderError(Exception):
    """Raised when an error occurs when working with the order class."""
