import pytest
from aiomql import MetaTester, TestData, MetaTrader, Config
import MetaTrader5


@pytest.fixture(scope='session', autouse=True)
def config():
    config = Config(filename='test.json')
    return config


@pytest.fixture(scope='session', autouse=True)
def metatrader5(config):
    return MetaTrader5