# import pytest
# from aiomql import MetaTester, TestData, MetaTrader, Config
# import MetaTrader5 as mt5
#
#
# @pytest.fixture(scope='session', autouse=True)
# async def initialize():
#     config = Config()
#     acc = config.account_info()
#     mt5.initialize(**acc)
#     mt5.login(**acc)
