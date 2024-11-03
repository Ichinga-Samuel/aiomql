import pytest
from aiomql.lib.account import Account


class TestAccount:
    @classmethod
    def setup_class(cls):
        cls.account = Account()

    @pytest.fixture(scope="class", autouse=True)
    async def refresh(self):
        await self.account.refresh()

    async def test_connected(self):
        assert self.account.connected is True

    async def test_account_info(self):
        acc_info = await self.account.mt5.account_info()
        assert acc_info.login == self.account.login
        assert acc_info.server == self.account.server
