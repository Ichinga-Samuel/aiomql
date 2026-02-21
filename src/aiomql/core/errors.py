"""MetaTrader5 error handling for the aiomql package.

This module provides the Error class for representing and inspecting
errors returned by the MetaTrader5 terminal.

Classes:
    Error: Wraps an MT5 error code with a human-readable description.
"""


class Error:
    """Represents an error returned by the MetaTrader5 terminal.

    Wraps a numeric error code with a human-readable description and
    provides helper methods for inspecting the error category.

    Attributes:
        code (int): The numeric error code.
        description (str): Human-readable description of the error.
        descriptions (dict[int, str]): Mapping of known error codes to
            their descriptions.
        conn_errors (tuple[int, ...]): Error codes that indicate a
            connection-level failure.
    """

    descriptions = {
        # common errors
        1: "successful",
        -1: "generic fail",
        -2: "invalid arguments/parameters",
        -3: "no memory condition",
        -4: "no history",
        -5: "invalid version",
        -6: "authorization failed",
        -7: "unsupported method",
        -8: "auto-trading disabled",
        # internal errors
        -10000: "internal IPC general error",
        -10001: "internal IPC send failed",
        -10002: "internal IPC recv failed",
        -10003: "internal IPC initialization fail",
        -10004: "internal IPC no ipc",
        -10005: "internal timeout",
    }

    conn_errors = (-10000, -10001, -10002, -10003, -10004, -10005, -6)

    def __init__(self, code: int = 1, description: str = ""):
        """Initializes an Error instance.

        Args:
            code: The numeric error code. Defaults to 1 (successful).
            description: Optional override description. If empty, the
                description is looked up from ``descriptions``.
        """
        self.code = code
        self.description = self.descriptions.get(code, description or "unknown error")

    def is_connection_error(self):
        """Checks whether this error indicates a connection failure.

        Returns:
            bool: True if the error code is in ``conn_errors``.
        """
        return self.code in self.conn_errors

    def __repr__(self):
        """Returns a string representation of the error.

        Returns:
            str: Formatted as ``"code: description"``.
        """
        return f"{self.code}: {self.description}"

