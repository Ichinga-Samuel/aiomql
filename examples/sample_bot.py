import logging
import asyncio

from aiomql.lib.bot import Bot
from aiomql.contrib.strategies import FingerTrap, Chaos
from aiomql.contrib.symbols import ForexSymbol


def sample_bot():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    syms = ["Volatility 75 Index", "Volatility 100 Index", "Volatility 50 Index"]
    symbols = [ForexSymbol(name=sym) for sym in syms]
    strategies = [Chaos(symbol=symbol) for symbol in symbols]
    bot = Bot()
    bot.executor.timeout = 10
    bot.add_coroutine(coroutine=sleep_run)
    bot.add_strategies(strategies=strategies)
    bot.execute()


async def sleep_run():
    while True:
        print("Sleeping for 5 seconds")
        await asyncio.sleep(5)
        print("Hello World")

sample_bot()
