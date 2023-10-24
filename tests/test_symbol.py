from aiomql.symbol import Symbol

from . import *


class TestSymbol(BaseTest):
    sym = Symbol(name="EURJPY")

    async def test_init(self):
        await self.sym.init()
        assert self.sym.select is True
