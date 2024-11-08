import logging

from aiomql.lib.bot import Bot
from aiomql.contrib.strategies import Chaos
from aiomql.contrib.symbols import ForexSymbol


def test_bot_sync():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    syms = ["BTCUSD", "SOLUSD", "ETHUSD"]
    symbols = [ForexSymbol(name=sym) for sym in syms]
    strategies = [Chaos(symbol=symbol, name="test_chaos") for symbol in symbols]
    bot = Bot()
    assert bot.config.shutdown is False
    bot.executor.timeout = 10
    bot.add_strategies(strategies=strategies)
    bot.initialize_sync()
    bot.executor.execute()
    assert len(bot.executor.strategy_runners) == 3
    assert len(bot.executor.coroutines) == 1
    assert len(bot.executor.coroutine_threads) == 1
    assert bot.config.shutdown is True
