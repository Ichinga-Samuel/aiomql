import logging

from aiomql.lib.bot import Bot
from aiomql.contrib.strategies import FingerTrap
from aiomql.contrib.symbols import ForexSymbol


def sample_bot():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    syms = ["Volatility 75 Index", "Volatility 100 Index", "Volatility 50 Index"]
    symbols = [ForexSymbol(name=sym) for sym in syms]
    strategies = [FingerTrap(symbol=symbol) for symbol in symbols]
    bot = Bot()
    bot.add_strategies(strategies=strategies)
    bot.execute()


sample_bot()
