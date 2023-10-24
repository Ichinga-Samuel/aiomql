from aiomql import MetaTrader
import pytest

from .fixtures import *


@pytest.mark.asyncio
class BaseTest:
    """"""
    mt5 = MetaTrader()
