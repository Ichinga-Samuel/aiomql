import logging

from aiomql.lib.bot import Bot
from aiomql.core import Config
from aiomql.contrib.strategies import FingerTrap, Chaos
from aiomql.contrib.symbols import ForexSymbol


async def test_bot():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    syms = ['Volatility 75 Index', 'Volatility 100 Index', 'Volatility 50 Index']
    symbols = [ForexSymbol(name=sym) for sym in syms]
    stgs = [Chaos(symbol=symbol, name='test_chaos') for symbol in symbols]
    bot = Bot()
    assert bot.config.shutdown is False
    bot.executor.timeout = 30
    bot.add_strategies(strategies=stgs)
    await bot.initialize()
    assert bot.executor.no_of_running_strategies == 3
    assert len(bot.executor.coroutines) == 1
    assert len(bot.executor.coroutine_threads) == 1
    assert len(bot.executor.tasks) == 5
    assert bot.config.shutdown is True

