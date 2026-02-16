from aiomql.lib.symbol import Symbol
import pytest


@pytest.fixture(scope="function")
def btc_usd():
    return Symbol(name="BTCUSD")


@pytest.fixture(scope="function")
def eth_usd():
    return Symbol(name="ETHUSD")


