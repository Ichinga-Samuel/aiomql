from . import *
from aiomql import Terminal


class TestTerminal(BaseTest):
    terminal = Terminal()
    async def test_version(self):
        res = await self.terminal.version
        assert len(res) == 3

    async def test_info(self):
        res = await self.terminal.info()
        assert res.connected is True

    async def test_error(self):
        res = await self.terminal.last_error()
        assert res.code == 1

    async def test_symbols_get(self):
        res = await self.terminal.symbols_get()
        sym = next(res)
        assert isinstance(sym.name, str)
