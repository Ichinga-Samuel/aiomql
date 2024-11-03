import pytest

from aiomql.lib.terminal import Terminal


class TestTerminal:
    @pytest.fixture(scope="class", autouse=True)
    async def init_terminal(self):
        terminal = Terminal()
        init = await terminal.initialize()
        return init, terminal

    async def test_terminal(self, init_terminal):
        init, terminal = init_terminal
        assert init is True
        assert terminal.connected is True
        assert terminal.version is not None
