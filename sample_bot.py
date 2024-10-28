import logging

from aiomql.lib.bot import Bot
from aiomql.core import Config
from aiomql.contrib.strategies import FingerTrap, Chaos
from aiomql.contrib.symbols import ForexSymbol


def bot():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    syms = ['Volatility 75 Index', 'Volatility 100 Index', 'Volatility 50 Index']
    symbols = [ForexSymbol(name=sym) for sym in syms]
    stgs = [Chaos(symbol=symbol) for symbol in symbols]
    config = Config()
    bot = Bot()
    bot.executor.timeout = 60
    bot.add_strategies(strategies=stgs)
    bot.execute()


bot()
print("Bot executed successfully")
