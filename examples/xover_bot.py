import logging

from aiomql import Bot, ForexSymbol

from emaxover import EMAXOver

logging.basicConfig(level=logging.INFO)


def x_bot():
    syms = ["EURUSD", "GBPUSD", "USDJPY"]
    symbols = [ForexSymbol(name=sym) for sym in syms]
    strategies = [EMAXOver(symbol=symbol) for symbol in symbols]
    bot = Bot()
    bot.add_strategies(strategies=strategies)
    bot.execute()


x_bot()
