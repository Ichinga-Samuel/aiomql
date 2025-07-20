class Error:
    """Error class for handling errors"""

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
        self.code = code
        self.description = self.descriptions.get(code, description or "unknown error")

    def is_connection_error(self):
        return self.code in self.conn_errors

    def __repr__(self):
        return f"{self.code}: {self.description}"
