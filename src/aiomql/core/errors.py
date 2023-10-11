class Error:
    """Error class for handling errors from MetaTrader 5."""
    descriptions = {
        # common errors
        1: 'Successful',
        -1: 'generic fail',
        -2: 'invalid arguments/parameters',
        -3: 'no memory condition',
        -4: 'no history',
        -5: 'invalid version',
        -6: 'authorization failed',
        -7: 'unsupported method',
        -8: 'auto-trading disabled',
        # internal errors
        -10000: 'internal IPC general error',
        -10001: 'internal IPC send failed',
        -10002: 'internal IPC recv failed',
        -10003: 'internal IPC initialization fail',
        -10004: 'internal IPC no ipc',
        -10005: 'internal timeout',
    }
    def __init__(self, code: int, description: str = ''):
        self.code = code
        self.description = description or self.descriptions.get(code, 'Unknown Error')

    def __repr__(self):
        return f"""
        Error Code: {self.code}
        Error Description: {self.description}
        """