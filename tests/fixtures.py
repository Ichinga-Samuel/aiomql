import json
import os
from aiomql import MetaTrader as mt5, Config
import pytest


@pytest.fixture(scope="session")
def get_default_config():
    data = {"win_percentage": 0.90, "record_dir": "Trade Records"}
    obj = open('mt5.json', 'w')
    json.dump(data, obj)
    obj.close()
    yield
    os.remove('mt5.json')


@pytest.fixture(scope="session")
def get_config():
    data = {"win_percentage": 0.8, "record_dir": "Trade_Records"}
    obj = open('config.json', 'w')
    json.dump(data, obj)
    obj.close()
    yield
    os.remove('config.json')


@pytest.fixture(autouse=True, scope="session")
def init():
    config = Config(filename="test_config.json")
    mt5._initialize()
    mt5._login(login=config.account_number, password=config.password, server=config.server)
