import pytest
from aiomql import Config
import MetaTrader5


@pytest.fixture(scope='session', autouse=True)
def config():
    config = Config(filename='test.json')
    return config


@pytest.fixture(scope='session', autouse=True)
def metatrader5():
    return MetaTrader5
