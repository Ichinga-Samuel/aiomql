import logging

from aiomql import Bot, ForexSymbol, auto_commit, OpenPositionsTracker

from .emaxover import EMAXOver

logging.basicConfig(level=logging.INFO)


def x_bot():
    syms = ["LTCUSD", "ETHUSD", "SOLUSD", "BTCUSD"]
    symbols = [ForexSymbol(name=sym) for sym in syms]
    strategies = [EMAXOver(symbol=symbol) for symbol in symbols]
    bot = Bot()
    bot.add_strategies(strategies=strategies)
    bot.add_coroutine(coroutine=OpenPositionsTracker(autocommit=True).track, on_separate_thread=True)
    # bot.add_coroutine(coroutine=auto_commit, on_separate_thread=True)
    bot.execute()


x_bot()
