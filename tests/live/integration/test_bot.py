import logging

from aiomql.lib.bot import Bot
from aiomql.contrib.strategies import Chaos
from aiomql.contrib.symbols import ForexSymbol

logger = logging.getLogger(__name__)

async def test_bot():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    syms = ["BTCUSD", "SOLUSD", "ETHUSD"]
    symbols = [ForexSymbol(name=sym) for sym in syms]
    strategies = [Chaos(symbol=symbol, name="test_chaos", params={"interval": 3}) for symbol in symbols]
    bot = Bot()
    bot.executor.timeout = 10
    bot.add_strategies(strategies=strategies)
    await bot.initialize()
    bot.executor.execute()
    assert len(bot.executor.coroutines) == 1
    assert len(bot.executor.coroutine_threads) == 1
    assert len(bot.executor.strategy_runners) == 3

    assert bot.config.shutdown is True
